import fastapi
from loguru import logger
from prediction_market_agent_tooling.loggers import logger
from prediction_market_agent_tooling.tools.caches.db_cache import db_cache
from prediction_market_agent_tooling.tools.is_invalid import is_invalid
from prediction_market_agent_tooling.tools.langfuse_ import observe
from prediction_market_agent_tooling.tools.utils import utcnow

from labs_api.invalid.invalid_models import QuestionInvalidResponse


@db_cache
@observe()
def question_invalid(question: str) -> QuestionInvalidResponse:
    """Returns invalid for a given question."""
    try:
        return QuestionInvalidResponse(
            question=question,
            created_at=utcnow(),
            invalid=is_invalid(question),
        )
    except Exception as e:
        logger.error(f"Failed to get is_invalid for question `{question}`: {e}")
        raise fastapi.HTTPException(status_code=500)
