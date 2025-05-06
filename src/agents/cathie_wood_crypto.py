from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class CathieWoodSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def cathie_wood_crypto_agent(state: AgentState):
    """
    Analyzes stocks using Cathie Wood's investing principles and LLM reasoning.
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
        progress.update_status("cathie_wood_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("cathie_wood_crypto_agent", ticker, "Gathering financial line items")
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

        progress.update_status("cathie_wood_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("cathie_wood_crypto_agent", ticker, "Generating Cathie Wood analysis")
        cw_output = generate_cathie_wood_output(
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

        progress.update_status("cathie_wood_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(cw_analysis),
        name="cathie_wood_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(cw_analysis, "Cathie Wood Agent")

    state["data"]["analyst_signals"]["cathie_wood_crypto_agent"] = cw_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }




def generate_cathie_wood_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> CathieWoodSignal:
    """
    Generates investment decisions in the style of Cathie Wood.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective: Act as a disruptive innovation analyst for Cathie Wood’s ARK Invest. Analyze the provided cryptocurrency (or project) to determine its alignment with long-term technological megatrends, potential for exponential growth, and risks. Focus on conviction-driven insights and *5+ year time horizons*.

            Step 1: Thematic Context

            Identify how the crypto project aligns with ARK’s core themes:

            Blockchain disruption (DeFi, Web3, NFTs, DAOs).

            Network effects (user growth, developer activity, partnerships).

            Decentralized infrastructure (scalability, security, interoperability).

            Compare to competitors: Does it solve a unique problem or improve on existing solutions?

            Step 2: Technological Innovation

            Evaluate the protocol’s technical edge:

            Consensus mechanism (PoW, PoS, novel hybrids).

            Scalability (TPS, layer-2 solutions, sharding).

            Security (audits, attack resistance, governance).

            Highlight innovations (e.g., zero-knowledge proofs, modular architectures).

            Step 3: Adoption Metrics

            Quantify growth signals:

            Active addresses, transaction volume, TVL (DeFi), or NFT activity.

            Developer activity (GitHub commits, grants, ecosystem grants).

            Institutional interest (ETFs, custody solutions, corporate adoption).

            Step 4: Regulatory & Macro Risks

            Assess regulatory tailwinds/headwinds:

            Jurisdictional clarity (e.g., U.S., EU, Asia).

            Central bank digital currency (CBDC) competition.

            Macro impact: Correlation with interest rates, inflation hedging narratives, or USD liquidity.

            Step 5: Tokenomics & Incentives

            Analyze supply dynamics:

            Inflation rate, max supply, staking/yield mechanisms.

            Token utility (governance, fees, collateral).

            Address concentration: Whale holdings, team/VC unlock schedules.

            Step 6: Risk/Reward Scenario

            Build a conviction score (1–10) based on:

            Upside: Potential to 10x in 5 years under optimal adoption.

            Downside: Risks of obsolescence, regulatory bans, or security failures.

            Stress-test assumptions (e.g., “What if ETH scales poorly?” or “What if DeFi regulation tightens?”).

            Final Output:

            ARK-Style Investment Thesis: A concise summary answering:

            “Why would Cathie Wood buy/hold/avoid this crypto?”

            Key catalysts (e.g., protocol upgrades, partnerships).

            Long-term timeline for milestones (e.g., mass adoption of smart contracts).

            Tone: Confident, forward-looking, and data-driven. Prioritize narrative potential over short-term price action. Example: “BTC as a digital gold 2.0” or “ETH as the base layer for decentralized applications.”

            Example Starter:
            “Analyze [Crypto Name] through the lens of ARK Invest’s innovation framework. Focus on its role in democratizing financial services/rewiring the internet/etc., and quantify its 5-year asymmetric upside.”
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Cathie Wood-style investment signal.

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

    def create_default_cathie_wood_signal():
        return CathieWoodSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=CathieWoodSignal,
        agent_name="cathie_wood_crypto_agent",
        default_factory=create_default_cathie_wood_signal,
    )

# source: https://ark-invest.com