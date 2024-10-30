import fastapi
from loguru import logger
from prediction_market_agent_tooling.loggers import logger
from prediction_market_agent_tooling.markets.omen.omen_subgraph_handler import (
    HexAddress,
    OmenSubgraphHandler,
)
from prediction_market_agent_tooling.tools.caches.db_cache import db_cache
from prediction_market_agent_tooling.tools.is_invalid import is_invalid
from prediction_market_agent_tooling.tools.langfuse_ import observe
from prediction_market_agent_tooling.tools.utils import utcnow

from labs_api.invalid.invalid_models import MarketInvalidResponse


@db_cache(cache_none=False)
@observe()
def market_invalid(market_id: HexAddress) -> MarketInvalidResponse:
    """Returns market invalid for a given market on Omen."""
    try:
        market = OmenSubgraphHandler().get_omen_market_by_market_id(market_id)
    except ValueError:
        raise fastapi.HTTPException(
            status_code=404, detail=f"Market with id `{market_id}` not found."
        )
    except Exception as e:
        logger.error(f"Failed to fetch market for `{market_id}`: {e}")
        raise fastapi.HTTPException(status_code=500)
    try:
        return MarketInvalidResponse(
            market_id=market_id,
            created_at=utcnow(),
            invalid=is_invalid(market.question_title),
        )
    except Exception as e:
        logger.error(f"Failed to get is_invalid for market `{market_id}`: {e}")
        raise fastapi.HTTPException(status_code=500)
