import typing as t

from prediction_market_agent_tooling.tools.utils import check_not_none
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 1
    RELOAD: bool = True
    SQLALCHEMY_DB_URL: t.Optional[SecretStr] = None

    @property
    def sqlalchemy_db_url(self) -> SecretStr:
        return check_not_none(
            self.SQLALCHEMY_DB_URL, "SQLALCHEMY_DB_URL missing in the environment."
        )
