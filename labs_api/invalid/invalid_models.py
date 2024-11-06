from prediction_market_agent_tooling.markets.omen.omen_subgraph_handler import (
    HexAddress,
)
from prediction_market_agent_tooling.tools.datetime_utc import DatetimeUTC
from pydantic import BaseModel


class MarketInvalidResponse(BaseModel):
    market_id: HexAddress
    created_at: DatetimeUTC
    invalid: bool
