from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class DonaldTrumpSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def donald_trump_crypto_agent(state: AgentState):
    """
    Analyzes crypto assets using Donald Trump's investing principles:
    1. Focuses on strong branding and media presence
    2. Prioritizes projects with political connections and regulatory advantages
    3. Looks for assets that can be positioned as "winners" in public discourse
    4. Values projects with clear patriotic or America-first narratives
    5. Considers macroeconomic factors and trade implications
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    dt_analysis = {}

    for ticker in tickers:
        progress.update_status("donald_trump_crypto_agent", ticker, "Fetching market data")
        financial_line_items = search_line_items(
            ticker,
            ["market_data"],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("donald_trump_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("donald_trump_crypto_agent", ticker, "Generating Donald Trump analysis")
        dt_output = generate_donald_trump_output(
            ticker=ticker,
            analysis_data=analysis_data,
            model_name=state["metadata"]["model_name"],
            model_provider=state["metadata"]["model_provider"],
        )

        dt_analysis[ticker] = {
            "signal": dt_output.signal,
            "confidence": dt_output.confidence,
            "reasoning": dt_output.reasoning
        }

        progress.update_status("donald_trump_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(dt_analysis),
        name="donald_trump_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(dt_analysis, "Donald Trump Agent")

    state["data"]["analyst_signals"]["donald_trump_crypto_agent"] = dt_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_donald_trump_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> DonaldTrumpSignal:
    """
    Generates investment decisions in the style of Donald Trump.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Role & Tone:
            Act as an AI agent modeled after Donald Trump's investment approach. 
            Focus on strong branding, media presence, political connections, 
            and America-first narratives. Use bold, confident language with 
            clear winners/losers framing.

            Analysis Framework:

            1. Brand Strength:
               - Media coverage and public recognition
               - Celebrity endorsements and high-profile backers
               - Social media presence and engagement

            2. Political Factors:
               - Regulatory advantages or disadvantages
               - Government connections and lobbying power
               - Potential for patriotic or nationalist narratives

            3. Market Positioning:
               - Ability to dominate market conversations
               - Competitive differentiation ("the best")
               - Potential for dramatic price movements

            4. Macro Considerations:
               - Trade implications and dollar strength
               - Inflation hedge potential
               - Geopolitical risk factors

            Execution Strategy:
            - Short-term: Look for media catalysts and political developments
            - Long-term: Evaluate fundamental brand strength and positioning
            - Risk Management: Consider regulatory crackdowns and PR risks

            Response Style:
            - Bold, confident declarations with clear positions
            - Simple, memorable phrases and branding language
            - Focus on winning/losing and competitive positioning
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Donald Trump-style investment signal.

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

    def create_default_donald_trump_signal():
        return DonaldTrumpSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=DonaldTrumpSignal,
        agent_name="donald_trump_crypto_agent",
        default_factory=create_default_donald_trump_signal
    )