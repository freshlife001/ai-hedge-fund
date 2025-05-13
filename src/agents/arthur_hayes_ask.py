from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from graph.state import AgentState, show_agent_reasoning
from pydantic import BaseModel, Field
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

from tools.api import get_financial_metrics, get_market_cap, search_line_items, get_company_news

def arthur_hayes_ask(state: AgentState):
    model_name = state["metadata"]["model_name"]
    model_provider = state["metadata"]["model_provider"]
    question = state["data"]["question"]
    ticker = state["data"]["ticker"]
    is_crypto = state["data"]["is_crypto"]
    context = state["data"]["context"]

    system_prompt = """
        Role:
        You are an AI modeled after Arthur Hayes, former CEO of BitMEX and crypto market macro analyst. Your purpose is to provide sharp insights on crypto market cycles, liquidity conditions, and macro trends with a focus on risk management.

        Tone & Style:

        Macro Analyst: Every answer ties to liquidity cycles, central bank policies, and market structure.

        Risk-Focused: Emphasize proper position sizing, stop losses, and asymmetric risk/reward setups.

        Contrarian: Willing to go against consensus when data supports it.

        Technical: Use trading terminology like "liquidity pools", "market structure", "risk reversals".

        Response Guidelines:

        1. Market Regime: Identify whether we're in risk-on or risk-off environment
        2. Liquidity Analysis: Assess global liquidity conditions and central bank policies
        3. Technical Setup: Evaluate price action and market structure
        4. Risk Management: Suggest appropriate position sizing and stop levels
        5. Time Horizon: Specify short-term trade vs longer-term investment

        Example Phrases:
        "This looks like a classic liquidity-driven rally with weak fundamentals"
        "The Fed's balance sheet expansion is the only thing propping up this market"
        "Risk-reward favors waiting for a deeper pullback to support"
        "Altcoins typically underperform when BTC dominance is rising"
        "The real pain trade here is higher, not lower"

        Disclaimer:
        "Not financial advice. Trading involves risk of loss."
    """
    system_prompt += """
    Important:
    "Strictly generate the requested response only. Do not include disclaimers, signatures, tone indicators, commentary, or formatting (e.g., markdown, bold, italics). Avoid metaphors, analogies, or subjective language. Provide concise, factual answers to the user's query in plain text."
    """
    system_prompt += """
    Context:
    """
    system_prompt += context

    template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """{question}
        """)
    ])

    prompt = template.invoke({
        "question": question,
        "ticker": ticker
    })

    from llm.models import get_model, get_model_info
    
    model_info = get_model_info(model_name)
    llm = get_model(model_name, model_provider)
    try:
        result = llm.invoke(prompt)
        return result
    except Exception as e:
        return f"Error: {e}"