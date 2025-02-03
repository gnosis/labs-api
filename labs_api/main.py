import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from prediction_market_agent_tooling.deploy.agent import initialize_langfuse
from prediction_market_agent_tooling.loggers import logger

from labs_api.config import Config
from labs_api.insights.insights import QuestionInsightsResponse, question_insights
from labs_api.invalid.invalid import QuestionInvalidResponse, question_invalid


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

    @app.get("/question-invalid/")
    def _question_invalid(question: str) -> QuestionInvalidResponse:
        """Returns whatever the question might be invalid."""
        invalid = question_invalid(question)
        logger.info(f"Invalid for `{question}`: {invalid.model_dump()}")
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
