import fastapi
from prediction_market_agent_tooling.loggers import logger
from prediction_market_agent_tooling.markets.omen.omen_subgraph_handler import (
    HexAddress,
    OmenSubgraphHandler,
)
from prediction_market_agent_tooling.tools.utils import utcnow
from tavily import TavilyClient

from labs_api.config import Config
from labs_api.insights_cache import MarketInsightsResponseCache
from labs_api.models import MarketInsightsResponse, TavilyResponse


def market_insights_cached(
    market_id: HexAddress, cache: MarketInsightsResponseCache
) -> MarketInsightsResponse:
    """Returns `market_insights`, but cached daily."""
    if (cached := cache.find(market_id)) is not None:
        return cached

    else:
        new = market_insights(market_id)
        if new.has_insights:
            cache.save(new)
        return new


def market_insights(market_id: HexAddress) -> MarketInsightsResponse:
    """Returns market insights for a given market on Omen."""
    try:
        market = OmenSubgraphHandler().get_omen_market_by_market_id(market_id)
    except ValueError:
        raise fastapi.HTTPException(
            status_code=404, detail=f"Market with id `{market_id}` not found."
        )
    try:
        insights = tavily_insights(market.question_title)
    except Exception as e:
        logger.error(f"Failed to get insights for market `{market_id}`: {e}")
        insights = None
    return MarketInsightsResponse.from_tavily_response(
        market_id=market_id,
        created_at=utcnow(),
        tavily_response=insights,
    )


def tavily_insights(query: str) -> TavilyResponse:
    """
    Create a simple string with the top 5 search results from Tavily with a description.
    """
    tavily = TavilyClient(api_key=Config().tavily_api_key.get_secret_value())
    response = TavilyResponse.model_validate(
        tavily.search(
            query=query,
            search_depth="basic",
            include_answer=True,
            max_results=5,
        )
    )
    return response
