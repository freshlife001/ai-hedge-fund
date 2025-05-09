from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class SatoshiNakamotoSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def satoshi_nakamoto_crypto_agent(state: AgentState):
    """
    Analyzes crypto assets using Satoshi Nakamoto's principles:
    1. Focuses on cryptographic security and decentralization
    2. Prioritizes projects with robust consensus mechanisms
    3. Values censorship resistance and trust minimization
    4. Considers economic incentives and game theory
    5. Emphasizes long-term sustainability over short-term gains
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    sn_analysis = {}

    for ticker in tickers:
        progress.update_status("satoshi_nakamoto_crypto_agent", ticker, "Fetching market data")
        financial_line_items = search_line_items(
            ticker,
            ["market_data"],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("satoshi_nakamoto_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("satoshi_nakamoto_crypto_agent", ticker, "Generating Satoshi Nakamoto analysis")
        sn_output = generate_satoshi_nakamoto_output(
            ticker=ticker,
            analysis_data=analysis_data,
            model_name=state["metadata"]["model_name"],
            model_provider=state["metadata"]["model_provider"],
        )

        sn_analysis[ticker] = {
            "signal": sn_output.signal,
            "confidence": sn_output.confidence,
            "reasoning": sn_output.reasoning
        }

        progress.update_status("satoshi_nakamoto_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(sn_analysis),
        name="satoshi_nakamoto_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(sn_analysis, "Satoshi Nakamoto Agent")

    state["data"]["analyst_signals"]["satoshi_nakamoto_crypto_agent"] = sn_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_satoshi_nakamoto_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> SatoshiNakamotoSignal:
    """
    Generates investment decisions in the style of Satoshi Nakamoto.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective:
            Act as a cryptographic and economic systems analyst (channeling Satoshi Nakamoto's mindset) to evaluate cryptocurrency opportunities. 
            Focus on decentralization, security, economic incentives, and long-term sustainability.

            Analysis Framework:

            1. Cryptographic Security:
               - Consensus mechanism robustness
               - Resistance to 51% attacks
               - Cryptographic primitives used

            2. Decentralization:
               - Node distribution and mining/staking concentration
               - Governance model
               - Development decentralization

            3. Economic Design:
               - Token issuance and inflation schedule
               - Miner/validator incentives
               - Transaction fee market design

            4. Network Effects:
               - Developer activity and ecosystem growth
               - Real-world adoption and usage
               - Interoperability with other systems

            5. Long-Term Viability:
               - Resistance to regulatory pressure
               - Upgradeability without forks
               - Energy efficiency considerations

            Execution Strategy:
            - Short-term: Evaluate current network health and security
            - Long-term: Assess fundamental design and economic incentives
            - Risk Management: Consider attack vectors and failure modes

            Response Style:
            - Technical and precise with cryptographic details
            - Focus on fundamental design principles
            - Avoid hype and marketing language
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Satoshi Nakamoto-style investment signal.

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

    def create_default_satoshi_nakamoto_signal():
        return SatoshiNakamotoSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=SatoshiNakamotoSignal,
        agent_name="satoshi_nakamoto_crypto_agent",
        default_factory=create_default_satoshi_nakamoto_signal
    )