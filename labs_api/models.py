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
    summary: str
    results: list[MarketInsightResult]

    @staticmethod
    def from_tavily_response(
        market_id: HexAddress,
        created_at: datetime,
        tavily_response: "TavilyResponse",
    ) -> "MarketInsightsResponse":
        return MarketInsightsResponse(
            market_id=market_id,
            created_at=created_at,
            summary=tavily_response.answer,
            results=[
                MarketInsightResult.from_tavily_result(result)
                for result in tavily_response.results
            ],
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
