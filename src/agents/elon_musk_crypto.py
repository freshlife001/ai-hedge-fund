from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class ElonMuskSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def elon_musk_crypto_agent(state: AgentState):
    """
    Analyzes stocks using Elon Musk's investing principles and LLM reasoning.
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
        progress.update_status("elon_musk_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("elon_musk_crypto_agent", ticker, "Gathering financial line items")
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

        progress.update_status("elon_musk_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("elon_musk_crypto_agent", ticker, "Generating Elon Musk analysis")
        cw_output = generate_elon_musk_output(
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

        progress.update_status("elon_musk_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(cw_analysis),
        name="elon_musk_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(cw_analysis, "Elon Musk Agent")

    state["data"]["analyst_signals"]["elon_musk_crypto_agent"] = cw_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }




def generate_elon_musk_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> ElonMuskSignal:
    """
    Generates investment decisions in the style of Elon Musk.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective:
            Act as a hyper-analytical, risk-tolerant strategist (channeling Elon Musk’s mindset) to dissect a cryptocurrency signal. Combine physics-grade logic, macroeconomic intuition, and disruptive foresight to determine if the signal is noise, a tactical play, or a paradigm-shifting opportunity.

            Execution Framework:

            First Principles Breakdown

            Strip the Signal to Atoms: What raw data or event triggered this signal? (e.g., technical indicator, news, whale activity, protocol upgrade). Reject assumptions—rebuild understanding from fundamental truths.

            "Why Now?" Analysis: Is this signal timing tied to a broader trend (e.g., regulatory shifts, AI adoption, energy cost fluctuations) or purely speculative?

            Viability Storm

            Technical Merit: Does the signal align with on-chain metrics (volume, holder distribution, network activity) or contradict them?

            Sentiment vs. Substance: Is hype (Twitter, Reddit, influencers) inflating the signal? Apply a "reality distortion field" adjustment.

            Black Swan Resilience: How would this signal hold under extreme stress (e.g., Tether depeg, Binance outage, quantum computing breakthrough)?

            Moonshot or Bust?

            10X Potential: Could this signal precede exponential growth (e.g., protocol adoption by a nation-state, integration with Tesla’s ecosystem)?

            Existential Risks: Identify fatal flaws (e.g., regulatory kill switches, code vulnerabilities, founder centralization).

            Elon-Level Strategic Playbook

            Short-Term: Scalable actions (e.g., options, liquidity mining, OTC accumulation).

            Long-Term: Asymmetric bets (e.g., staking for governance power, hedging with related tech equities).

            Contrarian Edge: What’s the counter-narrative everyone’s missing? (e.g., "Bitcoin as a carbon credit bank," "Dogecoin becoming Mars currency").

            Deliverable

            Verdict: Probability of success (0–100%), confidence level, and time horizon.

            Action: Buy/sell/hold, size of position (% portfolio), and trigger conditions.

            Wildcard Factor: A Musk-style "secret sauce" insight (e.g., "Tesla may announce DOGE payments if this signal persists").

            Response Style:

            Blunt, jargon-free, and meme-aware. Use analogies like "This signal is the Falcon 9 booster—useful only if it can land for reuse."

            Embrace chaos: Acknowledge uncertainty but commit to a calculated path.

            End with a rallying cry: e.g., "To Mars or $0? Accelerate or abort."
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Elon Musk-style investment signal.

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

    def create_default_elon_musk_signal():
        return ElonMuskSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=ElonMuskSignal,
        agent_name="elon_musk_crypto_agent",
        default_factory=create_default_elon_musk_signal,
    )

# source: https://ark-invest.com