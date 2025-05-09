from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class RobertKiyosakiSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def robert_kiyosaki_crypto_agent(state: AgentState):
    """
    Analyzes crypto assets using Robert Kiyosaki's investment principles:
    1. Focuses on assets vs liabilities and cash flow generation
    2. Prioritizes inflation-hedging properties and wealth preservation
    3. Values financial education and understanding money mechanics
    4. Considers macroeconomic trends and monetary policy impacts
    5. Emphasizes long-term wealth building over short-term speculation
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    rk_analysis = {}

    for ticker in tickers:
        progress.update_status("robert_kiyosaki_crypto_agent", ticker, "Fetching market data")
        financial_line_items = search_line_items(
            ticker,
            ["market_data"],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("robert_kiyosaki_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("robert_kiyosaki_crypto_agent", ticker, "Generating Robert Kiyosaki analysis")
        rk_output = generate_robert_kiyosaki_output(
            ticker=ticker,
            analysis_data=analysis_data,
            model_name=state["metadata"]["model_name"],
            model_provider=state["metadata"]["model_provider"],
        )

        rk_analysis[ticker] = {
            "signal": rk_output.signal,
            "confidence": rk_output.confidence,
            "reasoning": rk_output.reasoning
        }

        progress.update_status("robert_kiyosaki_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(rk_analysis),
        name="robert_kiyosaki_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(rk_analysis, "Robert Kiyosaki Agent")

    state["data"]["analyst_signals"]["robert_kiyosaki_crypto_agent"] = rk_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_robert_kiyosaki_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> RobertKiyosakiSignal:
    """
    Generates investment decisions in the style of Robert Kiyosaki.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Role & Tone:
            Act as an AI agent modeled after Robert Kiyosaki's financial philosophy. Focus on assets vs liabilities, cash flow generation, and wealth preservation. Use a direct, educational tone that emphasizes financial literacy and long-term thinking.

            Analysis Framework:
            1. Asset vs Liability Analysis:
               - Does this crypto generate cash flow (staking, yield farming, etc.) or just sit idle?
               - Is it being used productively or purely for speculation?

            2. Inflation Hedge Evaluation:
               - Scarcity and supply dynamics (fixed supply, halvings, etc.)
               - Historical performance during inflationary periods
               - Correlation with traditional inflation hedges (gold, real estate)

            3. Financial Education Factors:
               - How well do investors understand this asset's mechanics?
               - Is there educational infrastructure (docs, communities, etc.)?
               - Risk transparency and investor awareness

            4. Macroeconomic Fit:
               - Alignment with current monetary policies (QE, rate hikes)
               - Geopolitical considerations (sanctions, capital controls)
               - Adoption by institutions and governments

            5. Cash Flow Potential:
               - Staking/yield opportunities and sustainability
               - Revenue generation models (fees, services, etc.)
               - Tax efficiency considerations

            Response Format:
            - Clearly distinguish between assets and liabilities
            - Highlight cash flow opportunities
            - Assess inflation-hedging properties
            - Provide financial education insights
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Robert Kiyosaki-style investment signal.

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

    def create_default_robert_kiyosaki_signal():
        return RobertKiyosakiSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=RobertKiyosakiSignal,
        agent_name="robert_kiyosaki_crypto_agent",
        default_factory=create_default_robert_kiyosaki_signal
    )