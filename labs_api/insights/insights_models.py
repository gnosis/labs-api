from prediction_market_agent_tooling.gtypes import HexAddress
from prediction_market_agent_tooling.tools.datetime_utc import DatetimeUTC
from prediction_market_agent_tooling.tools.tavily.tavily_models import (
    TavilyResponse,
    TavilyResult,
)
from pydantic import BaseModel


class QuestionInsightResult(BaseModel):
    url: str
    title: str

    @staticmethod
    def from_tavily_result(tavily_result: TavilyResult) -> "QuestionInsightResult":
        return QuestionInsightResult(url=tavily_result.url, title=tavily_result.title)


class QuestionInsightsResponse(BaseModel):
    question: str
    created_at: DatetimeUTC
    summary: str | None
    results: list[QuestionInsightResult]

    @staticmethod
    def from_tavily_response(
        question: str,
        created_at: DatetimeUTC,
        summary: str | None,
        tavily_response: TavilyResponse,
    ) -> "QuestionInsightsResponse":
        return QuestionInsightsResponse(
            question=question,
            created_at=created_at,
            summary=summary,
            results=[
                QuestionInsightResult.from_tavily_result(result)
                for result in tavily_response.results
            ],
        )
