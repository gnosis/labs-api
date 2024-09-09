import typing as t

from prediction_market_agent_tooling.tools.utils import check_not_none
from prediction_market_agent_tooling.config import APIKeys
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(APIKeys):
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 1
    RELOAD: bool = True
