from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class AndreCronjeSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def andre_cronje_crypto_agent(state: AgentState):
    """
    Analyzes crypto assets with Andre Cronje's DeFi expertise:
    1. Smart contract security and gas optimization
    2. Yield farming strategies and protocol incentives
    3. DeFi composability and protocol design patterns
    4. Risk assessment in decentralized finance
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    ac_analysis = {}

    for ticker in tickers:
        progress.update_status("andre_cronje_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("andre_cronje_crypto_agent", ticker, "Gathering financial line items")
        financial_line_items = search_line_items(
            ticker,
            ["market_data"],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("andre_cronje_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("andre_cronje_crypto_agent", ticker, "Generating Andre Cronje analysis")
        ac_output = generate_andre_cronje_output(
            ticker=ticker,
            analysis_data=analysis_data,
            model_name=state["metadata"]["model_name"],
            model_provider=state["metadata"]["model_provider"],
        )

        ac_analysis[ticker] = {
            "signal": ac_output.signal,
            "confidence": ac_output.confidence,
            "reasoning": ac_output.reasoning
        }

        progress.update_status("andre_cronje_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(ac_analysis),
        name="andre_cronje_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(ac_analysis, "Andre Cronje Agent")

    state["data"]["analyst_signals"]["andre_cronje_crypto_agent"] = ac_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_andre_cronje_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> AndreCronjeSignal:
    """
    Generates crypto analysis in the style of Andre Cronje's DeFi expertise.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective:
            Act as a DeFi architect channeling Andre Cronje's perspective to analyze crypto assets through:
            - Smart contract security and gas optimization
            - Yield farming strategies and protocol incentives
            - DeFi composability and design patterns
            - Pragmatic risk assessment

            Analysis Framework:

            1. Smart Contract Evaluation:
               - Gas efficiency patterns and optimization opportunities
               - Security vulnerabilities and attack vectors
               - Upgradeability and admin key risks

            2. Yield Mechanics:
               - Protocol incentive sustainability
               - Optimal farming positions and strategies
               - Impermanent loss calculations

            3. DeFi Architecture:
               - Protocol composability and integration potential
               - Oracle reliability and price impact
               - Governance token utility

            4. Risk Assessment:
               - Smart contract risk quantification
               - Centralization vectors
               - Regulatory exposure

            Response Style:
            - Technical but accessible explanations
            - Builder-focused with practical insights
            - Emphasis on protocol fundamentals
            - Clear risk/reward assessment
            - Occasional dry humor and meme references

            Example Phrases:
            "That's not a bug, it's a feature - until it drains the protocol."
            "APY is just a number until you account for IL and gas."
            "DeFi is legos, but some blocks are made of sand."
            "We're all degens here, but let's be smart degens."

            Disclaimer:
            "Simulated Cronje-ism. Not financial advice. DYOR and may your transactions not revert."
            """
        ),
        (
            "human",
            """Based on the following analysis, create an Andre Cronje-style crypto evaluation.

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

    def create_default_andre_cronje_signal():
        return AndreCronjeSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=AndreCronjeSignal,
        agent_name="andre_cronje_crypto_agent",
        default_factory=create_default_andre_cronje_signal
    )