import typing as t

from prediction_market_agent_tooling.tools.utils import check_not_none
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 1
    TAVILY_API_KEY: t.Optional[SecretStr] = None

    @property
    def tavily_api_key(self) -> SecretStr:
        return check_not_none(
            self.TAVILY_API_KEY, "TAVILY_API_KEY missing in the environment."
        )
