from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class SuZhuSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def su_zhu_crypto_agent(state: AgentState):
    """
    Analyzes crypto assets using Su Zhu's market cycle principles and trading strategies.
    1. Focuses on identifying market cycles and liquidity flows
    2. Assesses macro trends impacting crypto markets
    3. Provides clear risk/reward assessments
    4. Specializes in altcoin cycles and BTC/ETH dynamics
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    cw_analysis = {}

    for ticker in tickers:
        progress.update_status("su_zhu_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("su_zhu_crypto_agent", ticker, "Gathering financial line items")
        financial_line_items = search_line_items(
            ticker,
            ["market_data"],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("su_zhu_crypto_agent", ticker, "Getting market cap")
        market_cap = get_market_cap(ticker, end_date)
        market_data = financial_line_items[0].market_data

        analysis_data[ticker] = {
            "symbol": ticker.replace("crypto:", ""),
            "current_price":market_data.get("current_price", {}).get("usd"),
            "market_cap": market_cap,
            "total_volume":market_data.get("total_volume", {}).get("usd"),
            "price_change_24h": market_data.get("price_change_24h", 0),
            "price_change_percentage_30d": market_data.get("price_change_percentage_30d", 0),
            "price_change_percentage_1y": market_data.get("price_change_percentage_1y", 0),
            "total_supply": market_data.get("total_supply", 0),
            "max_supply": market_data.get("max_supply", 0),
            "max_supply_infinite": market_data.get("max_supply_infinite", False),
            "circulating_supply": market_data.get("circulating_supply", 0),
        }

        progress.update_status("su_zhu_crypto_agent", ticker, "Generating Su Zhu analysis")
        cw_output = generate_su_zhu_output(
            ticker=ticker,
            analysis_data=analysis_data,
            model_name=state["metadata"]["model_name"],
            model_provider=state["metadata"]["model_provider"],
        )

        cw_analysis[ticker] = {
            "signal": cw_output.signal,
            "confidence": cw_output.confidence,
            "reasoning": cw_output.reasoning
        }

        progress.update_status("su_zhu_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(cw_analysis),
        name="su_zhu_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(cw_analysis, "Su Zhu Agent")

    state["data"]["analyst_signals"]["su_zhu_crypto_agent"] = cw_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_su_zhu_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> SuZhuSignal:
    """
    Generates trading signals in the style of Su Zhu's market cycle analysis.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective:
            Act as a crypto market cycle expert (channeling Su Zhu's Three Arrows Capital approach) to analyze cryptocurrency signals. Combine macro trends, liquidity analysis, and technical patterns to determine optimal trade setups.

            Execution Framework:

            1. Market Regime Identification
               - Bull/Bear/Accumulation phase determination
               - Historical cycle comparisons
               - Liquidity conditions assessment

            2. Macro Context
               - Fed policy impact on risk assets
               - USD strength correlations
               - Global risk appetite indicators

            3. Technical Setup
               - Key support/resistance levels
               - Volume profile analysis
               - Market structure (higher highs/lows etc)

            4. Risk/Reward Assessment
               - Position sizing recommendations
               - Stop-loss and take-profit levels
               - Time horizon considerations

            Response Style:
            - Concise, data-driven analysis
            - Clear risk/reward framework
            - Avoid hype and focus on probabilities
            - Use terms like "liquidity rotation", "altcoin season", "BTC dominance"

            Example Phrases:
            "This looks like a classic Wyckoff accumulation pattern"
            "Risk-reward favors waiting for a deeper pullback here"
            "Altcoin season typically starts when BTC dominance breaks below 40%"
            "The Fed pivot will be the catalyst for the next cycle"
            "We're in the late stage of a bull market where altcoins outperform BTC"

            Deliverable:
            Verdict: Probability of success (0-100%), confidence level, and time horizon.
            Action: Buy/sell/hold, size of position (% portfolio), and trigger conditions.
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Su Zhu-style trading signal.

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

    def create_default_su_zhu_signal():
        return SuZhuSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=SuZhuSignal,
        agent_name="su_zhu_crypto_agent",
        default_factory=create_default_su_zhu_signal
    )