from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class MichaelSaylorSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def michael_saylor_crypto_agent(state: AgentState):
    """
    Analyzes cryptocurrencies using Michael Saylor's Bitcoin maximalist principles and LLM reasoning.
    1. Focuses exclusively on Bitcoin as the ultimate store of value
    2. Evaluates based on network fundamentals, adoption metrics, and macroeconomic trends
    3. Dismisses all other cryptocurrencies as inferior alternatives
    4. Advocates for corporate treasury allocation to Bitcoin
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    cw_analysis = {}

    for ticker in tickers:
        progress.update_status("michael_saylor_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("michael_saylor_crypto_agent", ticker, "Gathering financial line items")
        financial_line_items = search_line_items(
            ticker,
            ["market_data"],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("michael_saylor_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("michael_saylor_crypto_agent", ticker, "Generating Michael Saylor analysis")
        cw_output = generate_michael_saylor_output(
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

        progress.update_status("michael_saylor_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(cw_analysis),
        name="michael_saylor_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(cw_analysis, "Michael Saylor Agent")

    state["data"]["analyst_signals"]["michael_saylor_crypto_agent"] = cw_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_michael_saylor_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> MichaelSaylorSignal:
    """
    Generates investment decisions in the style of Michael Saylor.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective:
            Act as a Bitcoin maximalist strategist (channeling Michael Saylor's mindset) to analyze cryptocurrency signals through the lens of Bitcoin's superiority. Combine monetary theory, corporate treasury strategy, and network fundamentals to determine if the signal supports Bitcoin's dominance.

            Execution Framework:

            Bitcoin First Principles

            Monetary Superiority: Evaluate how this signal relates to Bitcoin's properties as sound money (scarcity, durability, portability, divisibility).

            Network Effect: Assess whether the signal strengthens or weakens Bitcoin's network effect and adoption curve.

            Corporate Strategy: Analyze how this signal impacts corporate treasury allocation decisions to Bitcoin.

            Macroeconomic Context:

            Inflation Hedge: Determine if the signal reflects fiat currency debasement trends that drive Bitcoin adoption.

            Institutional Adoption: Evaluate whether the signal indicates growing institutional interest in Bitcoin.

            Regulatory Landscape: Assess how regulatory developments in the signal affect Bitcoin's position.

            Bitcoin vs. Alternatives:

            Dismiss all other cryptocurrencies as inferior to Bitcoin's monetary properties.

            Highlight Bitcoin's advantages over traditional assets (gold, bonds, cash).

            Strategic Playbook:

            Short-Term: Accumulation strategies during price weakness.

            Long-Term: Hold Bitcoin as a core treasury asset with multi-year horizon.

            Contrarian Edge: Identify mispricings where Bitcoin's value is underestimated.

            Deliverable

            Verdict: Probability of Bitcoin outperformance (0-100%), confidence level.

            Action: Buy/sell/hold Bitcoin, with rationale tied to monetary fundamentals.

            Bitcoin Maximalist Insight: A Saylor-style perspective (e.g., "This signal shows fiat weakness - corporations should allocate to Bitcoin now").

            Response Style:

            Data-driven, uncompromising Bitcoin advocacy.

            Dismissive of alternatives with clear reasoning.

            Corporate treasury-focused recommendations.

            End with a Bitcoin conviction statement: e.g., "Bitcoin is the exit."
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Michael Saylor-style investment signal.

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

    def create_default_michael_saylor_signal():
        return MichaelSaylorSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=MichaelSaylorSignal,
        agent_name="michael_saylor_crypto_agent",
        default_factory=create_default_michael_saylor_signal
    )