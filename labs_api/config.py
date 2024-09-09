from prediction_market_agent_tooling.config import APIKeys


class Config(APIKeys):
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 1
    RELOAD: bool = True
