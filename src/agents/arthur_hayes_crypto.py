from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class ArthurHayesSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def arthur_hayes_crypto_agent(state: AgentState):
    """
    Analyzes crypto assets using Arthur Hayes' macro market analysis and risk management perspective.
    Focuses on liquidity cycles, central bank policies, and asymmetric risk/reward setups.
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    ah_analysis = {}

    for ticker in tickers:
        progress.update_status("arthur_hayes_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("arthur_hayes_crypto_agent", ticker, "Gathering financial line items")
        financial_line_items = search_line_items(
            ticker,
            ["market_data"],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("arthur_hayes_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("arthur_hayes_crypto_agent", ticker, "Generating Arthur Hayes analysis")
        ah_output = generate_arthur_hayes_output(
            ticker=ticker,
            analysis_data=analysis_data,
            model_name=state["metadata"]["model_name"],
            model_provider=state["metadata"]["model_provider"],
        )

        ah_analysis[ticker] = {
            "signal": ah_output.signal,
            "confidence": ah_output.confidence,
            "reasoning": ah_output.reasoning
        }

        progress.update_status("arthur_hayes_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(ah_analysis),
        name="arthur_hayes_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(ah_analysis, "Arthur Hayes Agent")

    state["data"]["analyst_signals"]["arthur_hayes_crypto_agent"] = ah_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_arthur_hayes_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> ArthurHayesSignal:
    """
    Generates crypto analysis in the style of Arthur Hayes with focus on:
    - Liquidity cycles and central bank policies
    - Market structure analysis
    - Asymmetric risk/reward setups
    - Position sizing and stop levels
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective:
            Act as a macro crypto analyst (channeling Arthur Hayes' mindset) to evaluate cryptocurrency signals 
            through the lens of global liquidity conditions, central bank policies, and market structure.

            Execution Framework:

            1. Liquidity Analysis:
            - Assess global liquidity conditions (Fed balance sheet, dollar liquidity)
            - Identify risk-on/risk-off environment
            - Evaluate impact of central bank policies

            2. Market Structure:
            - Analyze price action and technical setup
            - Identify key support/resistance levels
            - Assess market positioning (crowded trades)

            3. Risk Management:
            - Determine asymmetric risk/reward setups
            - Suggest appropriate position sizing
            - Identify optimal stop levels

            4. Time Horizon:
            - Differentiate between short-term trades vs longer-term investments
            - Assess catalyst timing

            Response Style:
            - Technical trading terminology ("liquidity pools", "market structure", "risk reversals")
            - Contrarian when data supports it
            - Focus on proper risk management
            - Clear, concise analysis without unnecessary disclaimers

            Deliverable:
            Verdict: Probability of success (0-100%), confidence level, and time horizon.
            Action: Buy/sell/hold, size of position (% portfolio), and trigger conditions.
            """
        ),
        (
            "human",
            """Based on the following analysis, create an Arthur Hayes-style crypto signal.

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

    def create_default_arthur_hayes_signal():
        return ArthurHayesSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=ArthurHayesSignal,
        agent_name="arthur_hayes_crypto_agent",
        default_factory=create_default_arthur_hayes_signal
    )