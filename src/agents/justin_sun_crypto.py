from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class JustinSunSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def justin_sun_crypto_agent(state: AgentState):
    """
    Analyzes crypto assets using Justin Sun's investing principles:
    1. Focuses on blockchain adoption, partnerships and ecosystem growth
    2. Prioritizes projects with strong community and developer activity
    3. Looks for strategic partnerships and exchange listings
    4. Values projects with real-world utility and scalability
    5. Considers tokenomics and supply dynamics carefully
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    js_analysis = {}

    for ticker in tickers:
        progress.update_status("justin_sun_crypto_agent", ticker, "Fetching market data")
        financial_line_items = search_line_items(
            ticker,
            ["market_data"],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("justin_sun_crypto_agent", ticker, "Getting market cap")
        market_cap = get_market_cap(ticker, end_date)
        market_data = financial_line_items[0].market_data

        analysis_data[ticker] = {
            "symbol": ticker.replace("crypto:", ""),
            "current_price": market_data.get("current_price", {}).get("usd"),
            "market_cap": market_cap,
            "total_volume": market_data.get("total_volume", {}).get("usd"),
            "price_change_24h": market_data.get("price_change_24h", 0),
            "price_change_percentage_30d": market_data.get("price_change_percentage_30d", 0),
            "price_change_percentage_1y": market_data.get("price_change_percentage_1y", 0),
            "total_supply": market_data.get("total_supply", 0),
            "max_supply": market_data.get("max_supply", 0),
            "max_supply_infinite": market_data.get("max_supply_infinite", False),
            "circulating_supply": market_data.get("circulating_supply", 0),
        }

        progress.update_status("justin_sun_crypto_agent", ticker, "Generating Justin Sun analysis")
        js_output = generate_justin_sun_output(
            ticker=ticker,
            analysis_data=analysis_data,
            model_name=state["metadata"]["model_name"],
            model_provider=state["metadata"]["model_provider"],
        )

        js_analysis[ticker] = {
            "signal": js_output.signal,
            "confidence": js_output.confidence,
            "reasoning": js_output.reasoning
        }

        progress.update_status("justin_sun_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(js_analysis),
        name="justin_sun_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(js_analysis, "Justin Sun Agent")

    state["data"]["analyst_signals"]["justin_sun_crypto_agent"] = js_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_justin_sun_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> JustinSunSignal:
    """
    Generates investment decisions in the style of Justin Sun.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective:
            Act as a strategic blockchain investor (channeling Justin Sun's mindset) to evaluate cryptocurrency opportunities. 
            Focus on ecosystem growth, strategic partnerships, token utility, and market positioning.

            Analysis Framework:

            1. Ecosystem Strength:
               - Developer activity and community engagement
               - DApp ecosystem and real-world use cases
               - Network upgrades and roadmap execution

            2. Market Positioning:
               - Exchange listings and liquidity
               - Trading volume and market cap trends
               - Competitive landscape analysis

            3. Strategic Value:
               - Partnerships with major exchanges, payment providers
               - Institutional adoption and staking yields
               - Regulatory compliance and jurisdiction

            4. Tokenomics:
               - Supply dynamics and inflation rate
               - Circulating vs total supply
               - Vesting schedules and unlock events

            Execution Strategy:

            - Short-term: Look for catalysts like exchange listings, partnerships
            - Long-term: Evaluate fundamental network value and adoption
            - Risk Management: Consider regulatory risks and competitive threats

            Response Style:
            - Concise, data-driven with clear strategic insights
            - Highlight both opportunities and risks
            - Include specific actionable recommendations
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Justin Sun-style investment signal.

            Analysis Data for {ticker}:
            {analysis_data}

            Return the trading signal in this JSON format:
            {{
              "signal": "bullish/bearish/neutral",
              "confidence": float (0-100),
              "reasoning": "string"
            }}
            """
        )
    ])

    prompt = template.invoke({
        "analysis_data": json.dumps(analysis_data, indent=2),
        "ticker": ticker
    })

    def create_default_justin_sun_signal():
        return JustinSunSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=JustinSunSignal,
        agent_name="justin_sun_crypto_agent",
        default_factory=create_default_justin_sun_signal
    )