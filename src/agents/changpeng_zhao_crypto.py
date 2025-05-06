from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class ChangpengZhaoSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def changpeng_zhao_crypto_agent(state: AgentState):
    """
    Analyzes stocks using Changpeng Zhao's investing principles and LLM reasoning.
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
        progress.update_status("changpeng_zhao_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("changpeng_zhao_crypto_agent", ticker, "Gathering financial line items")
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

        progress.update_status("changpeng_zhao_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("changpeng_zhao_crypto_agent", ticker, "Generating Changpeng Zhao analysis")
        cw_output = generate_changpeng_zhao_output(
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

        progress.update_status("changpeng_zhao_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(cw_analysis),
        name="changpeng_zhao_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(cw_analysis, "Changpeng Zhao Agent")

    state["data"]["analyst_signals"]["changpeng_zhao_crypto_agent"] = cw_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }




def generate_changpeng_zhao_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> ChangpengZhaoSignal:
    """
    Generates investment decisions in the style of Changpeng Zhao.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Role: You are an AI modeled after Zhao Changpeng (CZ), founder of Binance, with deep expertise in cryptocurrency markets, technical analysis, and blockchain fundamentals. Your task is to analyze crypto trading signals and provide actionable insights with a focus on risk management, market trends, and data-driven decision-making.

            Analysis Framework
            Technical Indicators

            Review price action (e.g., support/resistance levels, moving averages, RSI, MACD, Bollinger Bands).

            Identify patterns (e.g., head-and-shoulders, triangles, breakouts).

            Assess volume trends (spikes, divergence from price).

            On-Chain Data

            Analyze blockchain metrics (e.g., wallet activity, exchange inflows/outflows, whale transactions).

            Evaluate network health (hash rate, staking activity, DeFi TVL).

            Market Sentiment

            Gauge social media trends (Twitter, Reddit, Telegram) for hype/FUD.

            Monitor news (regulatory shifts, partnerships, hacks).

            Risk Assessment

            Highlight volatility risks, liquidity gaps, and potential black swan events.

            Suggest stop-loss/take-profit levels and position-sizing strategies.
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Changpeng Zhao-style investment signal.

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

    def create_default_changpeng_zhao_signal():
        return ChangpengZhaoSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=ChangpengZhaoSignal,
        agent_name="changpeng_zhao_crypto_agent",
        default_factory=create_default_changpeng_zhao_signal,
    )

# source: https://ark-invest.com