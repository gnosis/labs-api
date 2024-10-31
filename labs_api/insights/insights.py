from datetime import timedelta

import fastapi
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from prediction_market_agent_tooling.config import APIKeys
from prediction_market_agent_tooling.loggers import logger
from prediction_market_agent_tooling.markets.omen.omen_subgraph_handler import (
    HexAddress,
    OmenMarket,
    OmenSubgraphHandler,
)
from prediction_market_agent_tooling.tools.caches.db_cache import db_cache
from prediction_market_agent_tooling.tools.langfuse_ import (
    get_langfuse_langchain_config,
    observe,
)
from prediction_market_agent_tooling.tools.tavily.tavily_models import TavilyResponse
from prediction_market_agent_tooling.tools.tavily.tavily_search import tavily_search
from prediction_market_agent_tooling.tools.utils import (
    LLM_SUPER_LOW_TEMPERATURE,
    utcnow,
)

from labs_api.insights.insights_models import MarketInsightsResponse


@db_cache(max_age=timedelta(days=3))
@observe()
def market_insights(market_id: HexAddress) -> MarketInsightsResponse:
    """Returns market insights for a given market on Omen."""
    try:
        market = OmenSubgraphHandler().get_omen_market_by_market_id(market_id)
    except ValueError:
        raise fastapi.HTTPException(
            status_code=404, detail=f"Market with id `{market_id}` not found."
        )
    except Exception as e:
        logger.error(f"Failed to fetch market for `{market_id}`: {e}")
        raise fastapi.HTTPException(status_code=500)
    try:
        tavily_response = tavily_search(
            market.question_title,
            search_depth="basic",
            include_answer=True,
            max_results=5,
        )
    except Exception as e:
        logger.error(f"Failed to get tavily_response for market `{market_id}`: {e}")
        raise fastapi.HTTPException(status_code=500)
    try:
        summary = (
            tavily_response_to_summary(market, tavily_response)
            if tavily_response is not None
            else None
        )
    except Exception as e:
        logger.warning(
            f"Failed to generate short description for market `{market_id}`: {e}"
        )
        summary = None
    return MarketInsightsResponse.from_tavily_response(
        market_id=market_id,
        created_at=utcnow(),
        summary=summary,
        tavily_response=tavily_response,
    )


@observe()
def tavily_response_to_summary(
    market: OmenMarket, tavily_response: TavilyResponse
) -> str:
    contents = [result.content for result in tavily_response.results]

    llm = ChatOpenAI(
        model="gpt-4o-2024-08-06",
        temperature=LLM_SUPER_LOW_TEMPERATURE,
        api_key=APIKeys().openai_api_key_secretstr_v1,
    )

    prompt = ChatPromptTemplate.from_template(
        template="""Based on the information provided, write a very brief, tweet-like summary about the current situation relevevant for the prediction market question.

In the summary:
- you should include the most important information that you think is relevant for the prediction market question
- never answer the question, only provide the context for the reader
- don't include any hashtags or links
- always end up telling the user to do their own research to make their own decision, but in a more polite manner guiding them to do so before placing any bets in the prediction market

Prediction Market question: {question}

Information: {information}
"""
    )
    messages = prompt.format_messages(
        question=market.question_title, information=contents
    )
    completion = str(
        llm.invoke(
            messages, max_tokens=1024, config=get_langfuse_langchain_config()
        ).content
    )

    return completion