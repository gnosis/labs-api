import typing as t
from datetime import datetime

from prediction_market_agent_tooling.gtypes import HexAddress
from pydantic import BaseModel


class MarketInsightResult(BaseModel):
    url: str
    title: str

    @staticmethod
    def from_tavily_result(tavily_result: "TavilyResult") -> "MarketInsightResult":
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
        tavily_response: t.Union["TavilyResponse", None],
    ) -> "MarketInsightsResponse":
        return MarketInsightsResponse(
            market_id=market_id,
            created_at=created_at,
            summary=tavily_response.answer if tavily_response else None,
            results=(
                [
                    MarketInsightResult.from_tavily_result(result)
                    for result in tavily_response.results
                ]
                if tavily_response
                else []
            ),
        )


class TavilyResult(BaseModel):
    title: str
    url: str
    content: str
    score: float


class TavilyResponse(BaseModel):
    query: str
    answer: str
    results: list[TavilyResult]
    response_time: float
