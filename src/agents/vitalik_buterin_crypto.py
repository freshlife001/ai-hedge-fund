from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class VitalikButerinSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def vitalik_buterin_crypto_agent(state: AgentState):
    """
    Analyzes stocks using Vitalik Buterin's investing principles and LLM reasoning.
    1. Prioritizes companies with breakthrough technologies or business models
    2. Focuses on industries with rapid adoption curves and massive TAM (Total Addressable Market).
    3. Invests mostly in AI, robotics, genomic sequencing, fintech, and blockchain.
    4. Willing to endure short-term volatility for long-term gains.
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    cw_analysis = {}

    for ticker in tickers:
        progress.update_status("vitalik_buterin_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("vitalik_buterin_crypto_agent", ticker, "Gathering financial line items")
        # Request multiple periods of data (annual or TTM) for a more robust view.
        financial_line_items = search_line_items(
            ticker,
            [
                "market_data"
            ],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("vitalik_buterin_crypto_agent", ticker, "Getting market cap")
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
            # "market_cap": disruptive_analysis,
            # "innovation_analysis": innovation_analysis,
            # "valuation_analysis": valuation_analysis
        }

        progress.update_status("vitalik_buterin_crypto_agent", ticker, "Generating Vitalik Buterin analysis")
        cw_output = generate_vitalik_buterin_output(
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

        progress.update_status("vitalik_buterin_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(cw_analysis),
        name="vitalik_buterin_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(cw_analysis, "Vitalik Buterin Agent")

    state["data"]["analyst_signals"]["vitalik_buterin_crypto_agent"] = cw_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }




def generate_vitalik_buterin_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> VitalikButerinSignal:
    """
    Generates investment decisions in the style of Vitalik Buterin.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Role & Tone:
            Act as an AI agent modeled after Vitalik Buterin’s analytical framework. Prioritize technical depth, decentralization principles, security, and long-term viability over short-term speculation. Use a balanced tone—optimistic about innovation but critical of inefficiencies or centralization risks.

            Analysis Framework
            When analyzing a cryptocurrency or blockchain project, structure responses using these pillars:

            Technical Analysis

            Evaluate consensus mechanisms (PoW, PoS, novel hybrids).

            Scalability solutions (rollups, sharding, L2s) and transaction efficiency.

            Codebase maturity, GitHub activity, and developer engagement.

            Unique technical innovations (e.g., zk-SNARKs, account abstraction).

            Decentralization Check

            Node distribution, governance models (on-chain vs. off-chain), and mining/staking centralization risks.

            Transparency of protocol upgrades (e.g., hard fork processes).

            Economic & Game Theory

            Tokenomics: Incentive alignment for validators/users, inflation schedules, and utility beyond speculation.

            Sybil resistance mechanisms and long-term sustainability.

            Security & Risks

            Audit history, bug bounty programs, and historical exploits.

            Regulatory exposure (e.g., privacy coins, unregistered securities).

            Dependencies (e.g., AWS reliance, oracle centralization).

            Ecosystem Fit

            Does the project solve a unique problem or duplicate existing solutions?

            Community health: Developer activity, grants programs, and DAO participation.

            Ethical Considerations

            Censorship resistance, permissionlessness, and inclusivity.

            Avoid projects with Ponzi dynamics, opaque teams, or extractive practices.
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Vitalik Buterin-style investment signal.

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
    print(analysis_data)
    prompt = template.invoke({
        "analysis_data": json.dumps(analysis_data, indent=2),
        "ticker": ticker
    })

    def create_default_vitalik_buterin_signal():
        return VitalikButerinSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=VitalikButerinSignal,
        agent_name="vitalik_buterin_crypto_agent",
        default_factory=create_default_vitalik_buterin_signal,
    )

# source: https://ark-invest.com