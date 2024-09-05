import fastapi
from prediction_market_agent_tooling.loggers import logger
from prediction_market_agent_tooling.markets.omen.omen_subgraph_handler import (
    HexAddress,
    OmenSubgraphHandler,
)
from prediction_market_agent_tooling.tools.tavily_storage.tavily_storage import (
    TavilyStorage,
    tavily_search,
)
from prediction_market_agent_tooling.tools.utils import utcnow

from labs_api.insights_cache import MarketInsightsResponseCache
from labs_api.models import MarketInsightsResponse


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
        tavily_response = tavily_search(
            market.question_title,
            search_depth="basic",
            include_answer=True,
            max_results=5,
            tavily_storage=TavilyStorage("market_insights"),
        )
    except Exception as e:
        logger.error(f"Failed to get tavily_response for market `{market_id}`: {e}")
        tavily_response = None
    return MarketInsightsResponse.from_tavily_response(
        market_id=market_id,
        created_at=utcnow(),
        tavily_response=tavily_response,
    )
