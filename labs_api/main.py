import fastapi
import uvicorn
from config import Config
from fastapi.middleware.cors import CORSMiddleware

from labs_api.config import Config


def create_app() -> fastapi.FastAPI:
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
        return "pong"

    @app.get("/market-insights")
    def _market_insights(market_id: str) -> str:
        """Returns markdown formatted market insights for a given market on Omen."""
        return f"hello {market_id}"

    return app


if __name__ == "__main__":
    config = Config()
    uvicorn.run(
        "labs_api.main:create_app",
        factory=True,
        host=config.HOST,
        port=config.PORT,
        workers=config.WORKERS,
        reload=False,
        log_level="info",
    )
