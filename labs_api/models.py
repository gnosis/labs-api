import typing as t
from datetime import datetime

from prediction_market_agent_tooling.gtypes import HexAddress
from prediction_market_agent_tooling.tools.tavily_storage.tavily_models import (
    TavilyResponse,
    TavilyResult,
)
from pydantic import BaseModel


class MarketInsightResult(BaseModel):
    url: str
    title: str

    @staticmethod
    def from_tavily_result(tavily_result: TavilyResult) -> "MarketInsightResult":
        return MarketInsightResult(url=tavily_result.url, title=tavily_result.title)


class MarketInsightsResponse(BaseModel):
    market_id: HexAddress
    created_at: datetime
    summary: str | None
    results: list[MarketInsightResult]

    @property
    def has_insights(self) -> bool:
        return bool(self.summary or self.results)

    @staticmethod
    def from_tavily_response(
        market_id: HexAddress,
        created_at: datetime,
        summary: str | None,
        tavily_response: t.Union[TavilyResponse, None],
    ) -> "MarketInsightsResponse":
        return MarketInsightsResponse(
            market_id=market_id,
            created_at=created_at,
            summary=summary,
            results=(
                [
                    MarketInsightResult.from_tavily_result(result)
                    for result in tavily_response.results
                ]
                if tavily_response
                else []
            ),
        )
