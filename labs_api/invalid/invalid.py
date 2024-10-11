import fastapi
from loguru import logger
from prediction_market_agent_tooling.loggers import logger
from prediction_market_agent_tooling.markets.omen.omen_subgraph_handler import (
    HexAddress,
    OmenSubgraphHandler,
)
from prediction_market_agent_tooling.tools.is_invalid import is_invalid
from prediction_market_agent_tooling.tools.langfuse_ import observe
from prediction_market_agent_tooling.tools.utils import utcnow

from labs_api.invalid.invalid_cache import (
    MarketInvalidResponse,
    MarketInvalidResponseCache,
)


# Don't observe the cached version, as it will always return the same thing that's already been observed.
def market_invalid_cached(
    market_id: HexAddress, cache: MarketInvalidResponseCache
) -> MarketInvalidResponse:
    """Returns `market_invalid`, but cached daily."""
    if (cached := cache.find(market_id)) is not None:
        return cached

    else:
        new = market_invalid(market_id)
        if new.has_invalid:
            cache.save(new)
        return new


@observe()
def market_invalid(market_id: HexAddress) -> MarketInvalidResponse:
    """Returns market invalid for a given market on Omen."""
    try:
        market = OmenSubgraphHandler().get_omen_market_by_market_id(market_id)
    except ValueError:
        raise fastapi.HTTPException(
            status_code=404, detail=f"Market with id `{market_id}` not found."
        )
    try:
        invalid = is_invalid(market.question_title)
    except Exception as e:
        logger.error(f"Failed to get is_invalid for market `{market_id}`: {e}")
        invalid = None
    return MarketInvalidResponse(
        market_id=market_id,
        created_at=utcnow(),
        invalid=invalid,
    )
