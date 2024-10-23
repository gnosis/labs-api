from labs_api.cache import ResponseCache, ResponseCacheModel, ResponseCacheSQLModel


class MarketInvalidResponse(ResponseCacheModel):
    invalid: bool | None

    @property
    def has_invalid(self) -> bool:
        return self.invalid is not None


class MarketInvalidResponseCacheModel(ResponseCacheSQLModel, table=True):
    __tablename__ = "market_invalid_response_cache"


class MarketInvalidResponseCache(
    ResponseCache[MarketInvalidResponse, MarketInvalidResponseCacheModel]
):
    RESPONSE_CACHE_MODEL = MarketInvalidResponse
    RESPONSE_CACHE_SQL_MODEL = MarketInvalidResponseCacheModel
