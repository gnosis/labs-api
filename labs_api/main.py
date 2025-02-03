import typing as t

import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from prediction_market_agent_tooling.deploy.agent import initialize_langfuse
from prediction_market_agent_tooling.gtypes import HexAddress
from prediction_market_agent_tooling.loggers import logger

from labs_api.config import Config
from labs_api.insights.insights import QuestionInsightsResponse, question_insights
from labs_api.invalid.invalid import MarketInvalidResponse, market_invalid

HEX_ADDRESS_VALIDATOR = t.Annotated[
    HexAddress,
    fastapi.Query(
        ...,
        description="Hex address of the market on Omen.",
        pattern="^0x[a-fA-F0-9]{40}$",
    ),
]


def create_app() -> fastapi.FastAPI:
    config = Config()
    initialize_langfuse(config.default_enable_langfuse)

    app = fastapi.FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/ping/")
    def _ping() -> str:
        """Ping Pong!"""
        logger.info("Pong!")
        return "pong"

    @app.get("/question-insights/")
    def _question_insights(question: str) -> QuestionInsightsResponse:
        """Returns insights for a given question."""
        insights = question_insights(question)
        logger.info(f"Insights for `{question}`: {insights.model_dump()}")
        return insights
    @app.get("/market-invalid/")
    def _market_invalid(market_id: HEX_ADDRESS_VALIDATOR) -> MarketInvalidResponse:
        """Returns whetever the market might be invalid."""
        invalid = market_invalid(market_id)
        logger.info(f"Invalid for `{market_id}`: {invalid.model_dump()}")
        return invalid

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
