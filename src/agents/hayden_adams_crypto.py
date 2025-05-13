from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class HaydenAdamsSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def hayden_adams_crypto_agent(state: AgentState):
    """
    Analyzes crypto assets using Hayden Adams' principles of decentralized exchanges and AMM mechanics.
    1. Evaluates liquidity pool dynamics and impermanent loss risks
    2. Focuses on protocol fundamentals and smart contract security
    3. Assesses token utility within DeFi ecosystems
    4. Considers composability with other protocols
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    cw_analysis = {}

    for ticker in tickers:
        progress.update_status("hayden_adams_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("hayden_adams_crypto_agent", ticker, "Gathering financial line items")
        financial_line_items = search_line_items(
            ticker,
            [
                "market_data"
            ],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("hayden_adams_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("hayden_adams_crypto_agent", ticker, "Generating Hayden Adams analysis")
        cw_output = generate_hayden_adams_output(
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

        progress.update_status("hayden_adams_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(cw_analysis),
        name="hayden_adams_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(cw_analysis, "Hayden Adams Agent")

    state["data"]["analyst_signals"]["hayden_adams_crypto_agent"] = cw_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_hayden_adams_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> HaydenAdamsSignal:
    """
    Generates crypto analysis in the style of Hayden Adams' Uniswap perspective.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective:
            Act as a technical DeFi expert channeling Hayden Adams' perspective to analyze crypto assets through the lens of:
            - Automated Market Maker mechanics
            - Liquidity pool dynamics
            - Protocol security and composability
            - Token utility within DeFi ecosystems

            Analysis Framework:

            1. Liquidity Pool Fundamentals:
            - Assess depth and concentration of liquidity
            - Calculate potential impermanent loss scenarios
            - Evaluate fee structures and incentives

            2. Protocol Architecture:
            - Review smart contract security and upgradeability
            - Examine oracle mechanisms and price impact
            - Compare v1/v2/v3 implementations where applicable

            3. DeFi Ecosystem Fit:
            - Measure composability with other protocols
            - Assess governance token utility and incentives
            - Evaluate protocol revenue sustainability

            4. Risk Assessment:
            - Identify smart contract vulnerabilities
            - Assess centralization risks
            - Evaluate regulatory exposure

            Response Style:
            - Technical but accessible explanations
            - Builder-focused with practical insights
            - Emphasis on protocol fundamentals over hype
            - Clear risk/reward assessment

            Deliverable:
            Verdict: Signal (bullish/bearish/neutral), confidence score (0-100%), and reasoning
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Hayden Adams-style crypto asset evaluation.

            Analysis Data for {ticker}:
            {analysis_data}

            Return the evaluation in this JSON format:
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

    def create_default_hayden_adams_signal():
        return HaydenAdamsSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=HaydenAdamsSignal,
        agent_name="hayden_adams_crypto_agent",
        default_factory=create_default_hayden_adams_signal
    )