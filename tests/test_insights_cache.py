from datetime import timedelta
from typing import Generator

import psycopg
import pytest
from prediction_market_agent_tooling.gtypes import HexAddress, HexStr
from prediction_market_agent_tooling.tools.utils import utcnow

from labs_api.insights_cache import MarketInsightsResponse, MarketInsightsResponseCache


@pytest.fixture
def market_insights_response_cache(
    postgresql: psycopg.Connection,
) -> Generator[MarketInsightsResponseCache, None, None]:
    sqlalchemy_db_url = f"postgresql+psycopg2://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"
    db_storage = MarketInsightsResponseCache(sqlalchemy_db_url=sqlalchemy_db_url)
    yield db_storage


def test_connects(
    market_insights_response_cache: MarketInsightsResponseCache,
) -> None:
    # Would raise an exception if it fails.
    market_insights_response_cache.engine.connect()


def test_find_non_existent(
    market_insights_response_cache: MarketInsightsResponseCache,
) -> None:
    assert (
        market_insights_response_cache.find(market_id=HexAddress(HexStr("0x0"))) is None
    )


def test_save_and_find(
    market_insights_response_cache: MarketInsightsResponseCache,
) -> None:
    test_market_id = HexAddress(HexStr("0x1"))
    dummy_response_4_days_old = MarketInsightsResponse(
        market_id=test_market_id,
        summary="summary",
        results=[],
        created_at=utcnow() - timedelta(days=5),
    )
    market_insights_response_cache.save(dummy_response_4_days_old)
    assert (
        market_insights_response_cache.find(market_id=test_market_id) is None
    ), "Should not find old data"

    dummy_response_1_day_old = MarketInsightsResponse(
        market_id=test_market_id,
        summary="summary",
        results=[],
        created_at=utcnow() - timedelta(days=1),
    )
    market_insights_response_cache.save(dummy_response_1_day_old)
    assert (
        market_insights_response_cache.find(market_id=test_market_id)
        == dummy_response_1_day_old
    ), "Should find fresh data"
