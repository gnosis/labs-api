from prediction_market_agent_tooling.gtypes import HexAddress
from prediction_market_agent_tooling.tools.datetime_utc import DatetimeUTC
from prediction_market_agent_tooling.tools.tavily.tavily_models import (
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
    created_at: DatetimeUTC
    summary: str | None
    results: list[MarketInsightResult]

    @staticmethod
    def from_tavily_response(
        market_id: HexAddress,
        created_at: DatetimeUTC,
        summary: str | None,
        tavily_response: TavilyResponse,
    ) -> "MarketInsightsResponse":
        return MarketInsightsResponse(
            market_id=market_id,
            created_at=created_at,
            summary=summary,
            results=[
                MarketInsightResult.from_tavily_result(result)
                for result in tavily_response.results
            ],
        )
