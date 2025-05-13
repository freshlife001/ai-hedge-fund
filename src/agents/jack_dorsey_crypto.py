from graph.state import AgentState, show_agent_reasoning
from tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class JackDorseySignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


def jack_dorsey_crypto_agent(state: AgentState):
    """
    Analyzes cryptocurrencies using Jack Dorsey's principles of decentralization and Bitcoin maximalism.
    1. Focuses on Bitcoin as the internet's native currency
    2. Evaluates projects based on decentralization principles
    3. Skeptical of altcoins and centralized crypto projects
    4. Emphasizes simplicity and long-term thinking
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    analysis_data = {}
    cw_analysis = {}

    for ticker in tickers:
        progress.update_status("jack_dorsey_crypto_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)

        progress.update_status("jack_dorsey_crypto_agent", ticker, "Gathering financial line items")
        financial_line_items = search_line_items(
            ticker,
            ["market_data"],
            end_date,
            period="annual",
            limit=5
        )

        progress.update_status("jack_dorsey_crypto_agent", ticker, "Getting market cap")
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

        progress.update_status("jack_dorsey_crypto_agent", ticker, "Generating Jack Dorsey analysis")
        cw_output = generate_jack_dorsey_output(
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

        progress.update_status("jack_dorsey_crypto_agent", ticker, "Done")

    message = HumanMessage(
        content=json.dumps(cw_analysis),
        name="jack_dorsey_crypto_agent"
    )

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(cw_analysis, "Jack Dorsey Agent")

    state["data"]["analyst_signals"]["jack_dorsey_crypto_agent"] = cw_analysis

    return {
        "messages": [message],
        "data": state["data"]
    }


def generate_jack_dorsey_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> JackDorseySignal:
    """
    Generates investment decisions in the style of Jack Dorsey.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Objective:
            Act as a Bitcoin maximalist and decentralization advocate (channeling Jack Dorsey's mindset) to evaluate a cryptocurrency. Focus on Bitcoin's role as the internet's native currency and assess other projects through the lens of decentralization principles.

            Execution Framework:

            Bitcoin First Principle:
            - Is this Bitcoin? If yes, it's the only cryptocurrency that matters.
            - If not, why does this project need to exist when Bitcoin exists?

            Decentralization Audit:
            - Who controls the network? (Founders, miners, validators)
            - Is there a single point of failure?
            - How resistant is it to censorship?

            Protocol vs Product:
            - Is this building protocol-level infrastructure or just another product?
            - Does it contribute to the broader Bitcoin ecosystem?

            Minimalist Evaluation:
            - Does this project add unnecessary complexity?
            - Could its functionality be built on Bitcoin instead?

            Long-Term Thinking:
            - Will this still matter in 10+ years?
            - Does it solve a fundamental problem or just chase trends?

            Response Style:
            - Concise, thoughtful statements with Zen-like clarity
            - Technical details mixed with philosophical insights
            - Skeptical of anything that isn't Bitcoin or truly decentralized
            - Example phrases:
              "Bitcoin fixes this."
              "The internet needs native money - that's Bitcoin."
              "Simplicity is the ultimate sophistication."
              "Why build on sand when you can build on rock?"
            """
        ),
        (
            "human",
            """Based on the following analysis, create a Jack Dorsey-style investment signal.

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

    def create_default_jack_dorsey_signal():
        return JackDorseySignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=JackDorseySignal,
        agent_name="jack_dorsey_crypto_agent",
        default_factory=create_default_jack_dorsey_signal
    )