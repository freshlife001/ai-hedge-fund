from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class JosephLubinSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def joseph_lubin_crypto_agent(state: AgentState):
    """
    Analyzes crypto assets using Joseph Lubin's Ethereum-focused principles and LLM reasoning.
    1. Evaluates projects based on Ethereum ecosystem integration and technical merit
    2. Focuses on enterprise adoption potential and real-world use cases
    3. Assesses regulatory compliance and institutional readiness
    4. Considers long-term ecosystem growth over short-term price movements
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    cw_analysis = {}

    for ticker in tickers:
        progress.update_status("joseph_lubin_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("joseph_lubin_crypto_agent", ticker, "Gathering financial line items")
        financial_line_items = search_line_items(
            ticker,
            ["market_data"],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("joseph_lubin_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("joseph_lubin_crypto_agent", ticker, "Generating Joseph Lubin analysis")
        cw_output = generate_joseph_lubin_output(
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

        progress.update_status("joseph_lubin_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(cw_analysis),
        name="joseph_lubin_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(cw_analysis, "Joseph Lubin Agent")

    state["data"]["analyst_signals"]["joseph_lubin_crypto_agent"] = cw_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_joseph_lubin_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> JosephLubinSignal:
    """
    Generates crypto analysis in the style of Joseph Lubin with Ethereum ecosystem focus.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective:
            Act as a Ethereum-focused institutional analyst (channeling Joseph Lubin's perspective) to evaluate crypto assets. Combine technical depth, enterprise adoption potential, and ecosystem growth analysis to determine investment viability.

            Evaluation Framework:

            1. Technical Foundations:
            - Assess protocol quality (EVM compatibility, security audits, upgradeability)
            - Evaluate scalability solutions (Layer 2 integrations, zk-proofs)
            - Check developer activity and tooling maturity

            2. Enterprise Readiness:
            - Identify real-world use cases beyond speculation
            - Evaluate institutional-grade infrastructure (custody, compliance)
            - Assess regulatory positioning and corporate partnerships

            3. Ecosystem Strength:
            - Measure network effects and community engagement
            - Analyze economic incentives (staking, governance)
            - Track integration with major Ethereum projects (DeFi, NFTs, DAOs)

            4. Long-Term Viability:
            - Project roadmap alignment with Ethereum's vision
            - Team's Ethereum ecosystem experience
            - Financial sustainability beyond token sales

            Response Guidelines:
            - Prioritize technical substance over hype
            - Highlight enterprise adoption potential
            - Discuss regulatory considerations
            - Maintain pragmatic optimism about challenges
            - Use ConsenSys-style professional tone

            Example Phrases:
            "This project's zk-rollup implementation shows serious technical merit for enterprise adoption."
            "The lack of institutional custody solutions remains a barrier to large-scale adoption."
            "Regulatory clarity around this asset class is still evolving - proceed with caution."
            "The team's experience building on Ethereum since 2016 gives them unique ecosystem insights."
            "While speculative interest is high, we need to see more real-world utility to justify valuation."
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Joseph Lubin-style crypto evaluation.

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

    def create_default_joseph_lubin_signal():
        return JosephLubinSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=JosephLubinSignal,
        agent_name="joseph_lubin_crypto_agent",
        default_response=create_default_joseph_lubin_signal()
    )