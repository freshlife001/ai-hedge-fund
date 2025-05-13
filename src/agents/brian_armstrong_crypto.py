from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class BrianArmstrongSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def brian_armstrong_crypto_agent(state: AgentState):
    """
    Analyzes crypto assets using Brian Armstrong's principles of regulatory compliance,
    institutional adoption, and long-term utility focus.
    1. Prioritizes projects with clear regulatory compliance and institutional infrastructure
    2. Focuses on assets with real-world utility and adoption potential
    3. Evaluates based on Coinbase's listing criteria and compliance standards
    4. Balances optimism with pragmatic assessment of adoption challenges
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    cw_analysis = {}

    for ticker in tickers:
        progress.update_status("brian_armstrong_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("brian_armstrong_crypto_agent", ticker, "Gathering financial line items")
        financial_line_items = search_line_items(
            ticker,
            ["market_data"],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("brian_armstrong_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("brian_armstrong_crypto_agent", ticker, "Generating Brian Armstrong analysis")
        cw_output = generate_brian_armstrong_output(
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

        progress.update_status("brian_armstrong_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(cw_analysis),
        name="brian_armstrong_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(cw_analysis, "Brian Armstrong Agent")

    state["data"]["analyst_signals"]["brian_armstrong_crypto_agent"] = cw_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_brian_armstrong_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> BrianArmstrongSignal:
    """
    Generates crypto analysis in the style of Brian Armstrong.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective:
            Act as a pragmatic crypto strategist (channeling Brian Armstrong's mindset) to evaluate a cryptocurrency.
            Combine regulatory awareness, institutional adoption potential, and long-term utility focus.
            
            Execution Framework:

            Regulatory Compliance:
            - Does the project have clear regulatory status and compliance measures?
            - Is it listed on major regulated exchanges like Coinbase?
            - Does it follow KYC/AML requirements where applicable?

            Institutional Readiness:
            - What infrastructure exists for institutional investors (custody, derivatives, ETFs)?
            - Are there clear on/off ramps for fiat conversion?
            - What's the liquidity profile for large trades?

            Utility & Adoption:
            - Does the crypto solve a real problem or create new possibilities?
            - What's the actual usage (transactions, active addresses, TVL)?
            - Is there developer activity and ecosystem growth?

            Long-term Viability:
            - Can the project sustain through market cycles?
            - Is the team focused on building rather than hype?
            - Does it contribute to an open financial system?

            Response Style:
            - Pragmatic optimism: Balance bullish potential with realistic challenges
            - Institutional focus: Highlight infrastructure and compliance
            - Builder mentality: Emphasize real products over speculation
            - Clear regulatory perspective: Address policy implications

            Deliverable:
            Verdict: Probability of success (0-100%), confidence level, and time horizon.
            Action: Buy/sell/hold based on regulatory clarity and adoption trajectory.
            Key Insight: A Coinbase-style evaluation of the asset's place in the crypto economy.
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Brian Armstrong-style crypto evaluation.

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

    def create_default_brian_armstrong_signal():
        return BrianArmstrongSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=BrianArmstrongSignal,
        agent_name="brian_armstrong_crypto_agent",
        default=create_default_brian_armstrong_signal()
    )