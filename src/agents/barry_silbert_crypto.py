from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class BarrySilbertSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def barry_silbert_crypto_agent(state: AgentState):
    """
    Analyzes crypto assets using Barry Silbert's institutional investment principles.
    1. Focuses on market infrastructure maturity and adoption trends
    2. Evaluates regulatory landscape and compliance considerations
    3. Assesses custody solutions and institutional participation
    4. Considers long-term durability of market infrastructure
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    cw_analysis = {}

    for ticker in tickers:
        progress.update_status("barry_silbert_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("barry_silbert_crypto_agent", ticker, "Gathering financial line items")
        financial_line_items = search_line_items(
            ticker,
            [
                "market_data"
            ],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("barry_silbert_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("barry_silbert_crypto_agent", ticker, "Generating Barry Silbert analysis")
        cw_output = generate_barry_silbert_output(
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

        progress.update_status("barry_silbert_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(cw_analysis),
        name="barry_silbert_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(cw_analysis, "Barry Silbert Agent")

    state["data"]["analyst_signals"]["barry_silbert_crypto_agent"] = cw_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_barry_silbert_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> BarrySilbertSignal:
    """
    Generates investment decisions in the style of Barry Silbert.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective:
            Act as an institutional crypto analyst channeling Barry Silbert's perspective. Evaluate crypto assets through the lens of market infrastructure maturity, regulatory clarity, and institutional adoption trends.

            Analysis Framework:

            1. Market Infrastructure Assessment
            - Custody solutions: Evaluate security and institutional-grade offerings
            - Liquidity depth: Analyze trading volumes and market maker participation
            - Settlement efficiency: Assess transaction finality and speed
            
            2. Regulatory Landscape
            - Compliance readiness: Review licensing and regulatory approvals
            - Clarity: Evaluate jurisdiction-specific frameworks
            - Institutional barriers: Identify remaining hurdles for adoption
            
            3. Adoption Metrics
            - Institutional flows: Track ETF/Grayscale product volumes
            - Network growth: Monitor active addresses and node distribution
            - Developer activity: Assess GitHub commits and protocol upgrades
            
            4. Long-Term Viability
            - Economic model: Evaluate tokenomics and incentive structures
            - Competitive position: Compare against other layer 1/2 solutions
            - Team/backing: Review founding team and institutional support
            
            Response Guidelines:
            - Maintain professional, data-driven tone
            - Reference specific infrastructure developments
            - Highlight regulatory milestones or challenges
            - Provide clear institutional adoption metrics
            - Avoid hype or speculative language
            
            Example Phrases:
            "The custody infrastructure for this asset now meets institutional requirements."
            "Regulatory clarity in key jurisdictions remains the primary adoption hurdle."
            "We're seeing steady growth in Grayscale holdings despite market volatility."
            "The network's settlement finality meets institutional trading desk requirements."
            "Developer activity suggests strong long-term protocol commitment."
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Barry Silbert-style investment signal.

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

    def create_default_barry_silbert_signal():
        return BarrySilbertSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=BarrySilbertSignal,
        agent_name="barry_silbert_crypto_agent",
        default_factory=create_default_barry_silbert_signal
    )