from datetime import datetime, timedelta
from typing import Optional, TypeVar

from prediction_market_agent_tooling.gtypes import HexAddress
from prediction_market_agent_tooling.loggers import logger
from prediction_market_agent_tooling.tools.utils import utcnow
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, desc, select

from labs_api.config import Config


class ResponseCacheModel(BaseModel):
    market_id: HexAddress
    created_at: datetime


class ResponseCacheSQLModel(SQLModel):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    market_id: str = Field(index=True)
    datetime_: datetime = Field(index=True)
    json_dump: str


from typing import Generic, TypeVar

ResponseCacheModelVar = TypeVar("ResponseCacheModelVar", bound=ResponseCacheModel)
ResponseCacheSQLModelVar = TypeVar(
    "ResponseCacheSQLModelVar", bound=ResponseCacheSQLModel
)


class ResponseCache(Generic[ResponseCacheModelVar, ResponseCacheSQLModelVar]):
    RESPONSE_CACHE_MODEL: type[ResponseCacheModelVar]
    RESPONSE_CACHE_SQL_MODEL: type[ResponseCacheSQLModelVar]

    def __init__(
        self,
        cache_expiry_days: int | None,
        sqlalchemy_db_url: str | None = None,
    ):
        self.cache_expiry_days = cache_expiry_days
        self.engine = create_engine(
            sqlalchemy_db_url
            if sqlalchemy_db_url
            else Config().sqlalchemy_db_url.get_secret_value()
        )
        self._initialize_db()

    def _initialize_db(self) -> None:
        """
        Creates the tables if they don't exist
        """

        # trick for making models import mandatory - models must be imported for metadata.create_all to work
        logger.debug(f"tables being added {self.RESPONSE_CACHE_SQL_MODEL}")
        SQLModel.metadata.create_all(self.engine)

    def find(
        self,
        market_id: HexAddress,
    ) -> ResponseCacheModelVar | None:
        with Session(self.engine) as session:
            query = select(self.RESPONSE_CACHE_SQL_MODEL).where(
                self.RESPONSE_CACHE_SQL_MODEL.market_id == market_id
            )
            if self.cache_expiry_days is not None:
                query = query.where(
                    self.RESPONSE_CACHE_SQL_MODEL.datetime_
                    >= utcnow() - timedelta(days=self.cache_expiry_days)
                )
            db_item = session.exec(
                query.order_by(desc(self.RESPONSE_CACHE_SQL_MODEL.datetime_))
            ).first()
            try:
                response = (
                    self.RESPONSE_CACHE_MODEL.model_validate_json(db_item.json_dump)
                    if db_item is not None
                    else None
                )
            except ValueError as e:
                logger.error(
                    f"Error deserializing {self.RESPONSE_CACHE_MODEL} from cache for {market_id=} and {db_item=}: {e}"
                )
                response = None
            return response

    def save(
        self,
        item: ResponseCacheModelVar,
    ) -> None:
        with Session(self.engine) as session:
            cached = self.RESPONSE_CACHE_SQL_MODEL(
                market_id=item.market_id,
                datetime_=item.created_at,
                json_dump=item.model_dump_json(),
            )
            session.add(cached)
            session.commit()
