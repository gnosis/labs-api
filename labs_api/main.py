import typing as t
from contextlib import asynccontextmanager

import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from prediction_market_agent_tooling.deploy.agent import initialize_langfuse
from prediction_market_agent_tooling.gtypes import HexAddress
from prediction_market_agent_tooling.loggers import logger

from labs_api.config import Config
from labs_api.insights import MarketInsightsResponse, market_insights_cached
from labs_api.insights_cache import MarketInsightsResponseCache

HEX_ADDRESS_VALIDATOR = t.Annotated[
    HexAddress,
    fastapi.Query(
        ...,
        description="Hex address of the market on Omen.",
        pattern="^0x[a-fA-F0-9]{40}$",
    ),
]


def create_app() -> fastapi.FastAPI:
    @asynccontextmanager
    async def lifespan(app: fastapi.FastAPI) -> t.AsyncIterator[None]:
        # At start of the service.
        yield
        # At end of the service.
        market_insights_cache.engine.dispose()

    config = Config()
    initialize_langfuse(config.default_enable_langfuse)

    app = fastapi.FastAPI(lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    market_insights_cache = MarketInsightsResponseCache()

    @app.get("/ping/")
    def _ping() -> str:
        """Ping Pong!"""
        logger.info("Pong!")
        return "pong"

    @app.get("/market-insights/")
    def _market_insights(market_id: HEX_ADDRESS_VALIDATOR) -> MarketInsightsResponse:
        """Returns market insights for a given market on Omen."""
        insights = market_insights_cached(market_id, market_insights_cache)
        logger.info(f"Insights for `{market_id}`: {insights.model_dump()}")
        return insights

    logger.info("API created.")

    return app


if __name__ == "__main__":
    config = Config()
    uvicorn.run(
        "labs_api.main:create_app",
        factory=True,
        host=config.HOST,
        port=config.PORT,
        workers=config.WORKERS,
        reload=config.RELOAD,
        log_level="error",
    )
