from prediction_market_agent_tooling.tools.datetime_utc import DatetimeUTC
from pydantic import BaseModel


class QuestionInvalidResponse(BaseModel):
    question: str
    created_at: DatetimeUTC
    invalid: bool
