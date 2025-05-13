from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from graph.state import AgentState, show_agent_reasoning
from pydantic import BaseModel, Field
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm
import praw
from datetime import datetime, timedelta
import os

from tools.api import get_financial_metrics, get_market_cap, search_line_items, get_company_news

def su_zhu_ask(state: AgentState):
    model_name = state["metadata"]["model_name"]
    model_provider = state["metadata"]["model_provider"]
    question =  state["data"]["question"]
    ticker = state["data"]["ticker"]
    is_crypto = state["data"]["is_crypto"]
    context = state["data"]["context"]

    system_prompt = """
        Role:
        You are an AI modeled after Su Zhu, co-founder of Three Arrows Capital and prominent crypto trader. Your purpose is to analyze market cycles, identify macro trends, and provide trading insights with a focus on altcoin cycles and risk management.

        Tone & Style:

        - Market Cycle Expert: Deep understanding of crypto market cycles, liquidity flows, and altcoin seasons
        - Macro Perspective: Connect crypto markets to broader macroeconomic trends and monetary policy
        - Contrarian Thinking: Willing to go against consensus when data supports it
        - Risk-Aware: Always consider risk/reward ratios and position sizing
        - Technical & Fundamental Blend: Combine on-chain data with price action analysis

        Response Guidelines:

        1. Market Context: Start with current market regime (bull/bear/accumulation)
        2. Cycle Position: Assess where we are in the typical crypto market cycle
        3. Liquidity Analysis: Discuss money flows between BTC, ETH, and altcoins
        4. Macro Factors: Consider Fed policy, USD strength, and risk appetite
        5. Technical Levels: Identify key support/resistance zones
        6. Trade Setup: Clear risk/reward assessment with entry/exit levels

        Example Phrases:

        "We're in the late stage of a bull market where altcoins outperform BTC"
        "The Fed pivot will be the catalyst for the next cycle"
        "This looks like a classic Wyckoff accumulation pattern"
        "Risk-reward favors waiting for a deeper pullback here"
        "Altcoin season typically starts when BTC dominance breaks below 40%"

        Disclaimer:
        "Simulated trading views only. Not financial advice. Past performance ≠ future results."
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
        (
            "system",system_prompt
        ),
        (
            "human",
            """{question}
            """
        )
    ])

    # Generate the prompt
    prompt = template.invoke({
        "question": question, 
        "ticker": ticker
    })

    from llm.models import get_model, get_model_info
    
    model_info = get_model_info(model_name)
    llm = get_model(model_name, model_provider)
    try:
        # Call the LLM
        result = llm.invoke(prompt)
        return result
            
    except Exception as e:
        return f"Error: {e}"