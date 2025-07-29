"""Easier access to Google Ads API for SEO purposes.

Useful documentation:
    - https://developers.google.com/google-ads/api/samples/generate-keyword-ideas
    - https://developers.google.com/google-ads/api/reference/rpc/v20/GenerateKeywordIdeasRequest
    - https://developers.google.com/google-ads/api/docs/keyword-planning/generate-historical-metrics
    - https://developers.google.com/google-ads/api/reference/rpc/v20/GenerateKeywordHistoricalMetricsRequest
    - https://developers.google.com/google-ads/api/data/codes-formats#expandable-7
    - https://developers.google.com/google-ads/api/data/geotargets

"""

from collections.abc import Iterable
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Literal

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.v20.enums.types import MonthOfYearEnum
from google.ads.googleads.v20.services import (
    GenerateKeywordHistoricalMetricsRequest,
    GenerateKeywordIdeasRequest,
    KeywordSeed,
)
from pandas import DataFrame, Series

from .. import resources, utils
from ..context import AnyContext
from ..prompt import Prompt
from ..response import Field, Response, ResponseSet
from ..task import Task
from ..utils import dedent

CUSTOMER = "6560490700"


def year_month_from_date(date: str | datetime) -> tuple[int, MonthOfYearEnum.MonthOfYear]:
    """Convert a datetime object to a YearMonth string.

    Month enum values 0 and 1 are "UNSPECIFIED" and "UNKNOWN". January is 2 etc.
    """
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m")

    y = date.year
    m = MonthOfYearEnum.MonthOfYear(date.month + 1)
    return y, m


@lru_cache(maxsize=3)
def fetch_keywords(  # noqa: PLR0913
    credentials: str | Path,
    customer: str,
    keywords: tuple[str, ...],
    ideas: bool = False,
    max_ideas: int | None = None,
    language: str = "en",
    geo_target: str = "us",
    metrics_start: str | None = None,
    metrics_end: str | None = None,
):
    """Fetch metrics for a fixed list of keywords or generated keyword ideas from Google Ads API."""
    client = GoogleAdsClient.load_from_storage(credentials)
    ads_service = client.get_service("GoogleAdsService")
    kwd_service = client.get_service("KeywordPlanIdeaService")

    request: GenerateKeywordIdeasRequest | GenerateKeywordHistoricalMetricsRequest

    if ideas:
        request = GenerateKeywordIdeasRequest()
        keyword_seed = KeywordSeed()
        keyword_seed.keywords.extend(keywords)
        request.keyword_seed = keyword_seed
        request.page_size = max_ideas or 100
    else:
        request = GenerateKeywordHistoricalMetricsRequest()
        request.keywords = list(keywords)
        request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH

    request.customer_id = customer

    lang_id = resources.google_lang_id(language)
    request.language = ads_service.language_constant_path(lang_id)

    geo_target = resources.google_country_id(geo_target)
    request.geo_target_constants.append(ads_service.geo_target_constant_path(geo_target))

    request.historical_metrics_options.include_average_cpc = True

    if metrics_start is not None:
        y, m = year_month_from_date(metrics_start)
        request.historical_metrics_options.year_month_range.start.year = y
        request.historical_metrics_options.year_month_range.start.month = m

    if metrics_end is not None:
        y, m = year_month_from_date(metrics_end)
        request.historical_metrics_options.year_month_range.end.year = y
        request.historical_metrics_options.year_month_range.end.month = m

    if ideas:
        return kwd_service.generate_keyword_ideas(request=request)

    return kwd_service.generate_keyword_historical_metrics(request=request)


def collect_columns(df: DataFrame, columns: list[str]) -> Series:
    """Collects values in specified columns into a Series of lists."""
    matrix = df[columns].values
    return Series([row for row in matrix])


def collect_volume_columns(df: DataFrame):
    """Mutates monthly search volume columns into two list columns containing values and dates."""
    vol_cols = [col for col in df.columns if "search_volume_" in col]
    df["search_volume"] = collect_columns(df, vol_cols)

    def col_to_date(col):
        """Convert column name to datetime."""
        dt = datetime(*map(int, col.split("_")[-2:]), 1) if "_" in col else None
        return dt.isoformat() if dt else None

    sv_dt = [col_to_date(col) for col in vol_cols]
    df["search_volume_date"] = [sv_dt] * len(df)
    return df.drop(columns=vol_cols)


def process_keywords(response: Iterable, collect_volumes: bool = True) -> DataFrame:
    keywords = []
    for kwd in response.results:
        record = {
            "keyword": kwd.text,
        }

        metrics = getattr(kwd, "keyword_idea_metrics", None) or getattr(
            kwd, "keyword_metrics", None
        )
        if metrics is not None:
            record["avg_monthly_searches"] = getattr(metrics, "avg_monthly_searches", None)
            record["competition"] = getattr(metrics, "competition", None)
            record["competition_index"] = getattr(metrics, "competition_index", None)

            record["low_top_of_page_bid_micros"] = getattr(
                metrics, "low_top_of_page_bid_micros", None
            )
            record["high_top_of_page_bid_micros"] = getattr(
                metrics, "high_top_of_page_bid_micros", None
            )

            if volumes := getattr(metrics, "monthly_search_volumes", None):
                for volume in volumes:
                    year = volume.year
                    month = volume.month
                    date = datetime.strptime(f"{year}-{month.name.capitalize()}", "%Y-%B")
                    record[f"search_volume_{date.year}_{date.month:02}"] = volume.monthly_searches

        keywords.append(record)

    df = DataFrame(keywords)
    if collect_volumes:
        df = collect_volume_columns(df)

    return df


SYSTEM_PROMPT = dedent("""
You're an expert SEO specialist analyzing google keyword searches for a specific domain.

Your task is to simplify a list of search keywords (short phrases) into a smaller group of clean
keywords that make sense to later group, aggregate and analyze together. The idea is to remove
duplicate keywords that are identical in meaning but are spelled differently
(misspelling, singular vs. plural etc.), while preserving different search intents and
meaningful variations.

The keywords come from a dataset of '%(domain)s'. %(extra)s
""")

USER_PROMPT = dedent("""
Extract a clean, deduplicated list of search keywords of no more than %(n_max)s items
from the following list.

# Keywords

{{keywords}}
""")

ASSIGNMENT_PROMPT_SYSTEM = dedent("""
You're task is to use the following list of clean keywords,
and select and return the best semantically matching keyword for a given input phrase.

# Keywords

%(keywords)s
""")

ASSIGNMENT_PROMPT_USER = dedent("""
Assign the correct keyword to the following phrase: {{text}}.
""")


class KeywordCleaner:
    """A class to clean and deduplicate search keywords from a list of texts."""

    def __init__(
        self,
        domain: str,
        n_max: int = 10,
        extra: str | None = None,
    ):
        prompt = Prompt(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT % {"domain": domain, "extra": extra},
                },
                {
                    "role": "user",
                    "content": USER_PROMPT % {"n_max": n_max},
                },
            ],  # type: ignore
            required=["keywords"],
        )

        class Keywords(Response):
            keywords: list[str] = Field(
                ...,
                description="A list of clean google search keywords.",
                max_length=n_max,
            )

        self.task = Task(prompt=prompt, response=Keywords)

    async def __call__(
        self,
        keywords: Iterable[str],
        model: str,
        max_dollars: float,
        max_tokens: float | None = None,
        max_texts: float | None = None,
    ) -> Response:
        """Extracts a two-level topic hierarchy from a list of texts."""
        text = utils.concat_up_to(
            keywords,
            model=model,
            max_dollars=max_dollars,
            max_tokens=max_tokens,
            max_texts=max_texts,
            separator="\n",
        )
        responses = await self.task.call(context={"keywords": text}, model=model)
        return responses[0]


class KeywordAssigner:
    """Enforce correct clean keyword assignment."""

    def __init__(self, keywords: Response):
        keywords = keywords.to_dict()["keywords"]
        prompt = Prompt(
            messages=[
                {"role": "system", "content": ASSIGNMENT_PROMPT_SYSTEM % {"keywords": keywords}},
                {"role": "user", "content": ASSIGNMENT_PROMPT_USER},
            ],  # type: ignore
            required=["text"],
        )

        class Match(Response):
            keyword: Literal[*keywords]

        self.task = Task(prompt=prompt, response=Match)

    async def __call__(self, texts: AnyContext, model: str, **kwds) -> ResponseSet:
        return await self.task(context=texts, model=model, **kwds)
