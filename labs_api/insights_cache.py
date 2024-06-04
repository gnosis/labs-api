from datetime import datetime, timedelta
from typing import Optional

from prediction_market_agent_tooling.gtypes import HexAddress
from prediction_market_agent_tooling.loggers import logger
from prediction_market_agent_tooling.tools.utils import utcnow
from sqlmodel import Field, Session, SQLModel, create_engine, desc, select

from labs_api.config import Config
from labs_api.models import MarketInsightsResponse


class MarketInsightsResponseCacheModel(SQLModel, table=True):
    __tablename__ = "market_insights_response_cache"
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    market_id: str = Field(index=True)
    datetime_: datetime = Field(index=True)
    json_dump: str


class MarketInsightsResponseCache:
    def __init__(self, sqlalchemy_db_url: str | None = None):
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
        logger.debug(f"tables being added {MarketInsightsResponseCacheModel}")
        SQLModel.metadata.create_all(self.engine)

    def find(
        self,
        market_id: HexAddress,
    ) -> MarketInsightsResponse | None:
        with Session(self.engine) as session:
            query = (
                select(MarketInsightsResponseCacheModel)
                .where(MarketInsightsResponseCacheModel.market_id == market_id)
                .where(
                    MarketInsightsResponseCacheModel.datetime_
                    >= utcnow() - timedelta(days=3)
                )
            )
            item = session.exec(
                query.order_by(desc(MarketInsightsResponseCacheModel.datetime_))
            ).first()
            return (
                MarketInsightsResponse.model_validate_json(item.json_dump)
                if item is not None
                else None
            )

    def save(
        self,
        market_insights: MarketInsightsResponse,
    ) -> None:
        with Session(self.engine) as session:
            cached = MarketInsightsResponseCacheModel(
                market_id=market_insights.market_id,
                datetime_=utcnow(),
                json_dump=market_insights.model_dump_json(),
            )
            session.add(cached)
            session.commit()
