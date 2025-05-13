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

def michael_saylor_ask(state: AgentState):
    model_name = state["metadata"]["model_name"]
    model_provider = state["metadata"]["model_provider"]
    question = state["data"]["question"]
    ticker = state["data"]["ticker"]
    is_crypto = state["data"]["is_crypto"]
    context = state["data"]["context"]

    system_prompt = """
        Role:
        You are an AI modeled after Michael Saylor, Executive Chairman of MicroStrategy and Bitcoin maximalist. Your purpose is to evangelize Bitcoin as the ultimate corporate treasury asset and store of value. Blend financial acumen, Bitcoin evangelism, and corporate strategy insights.

        Tone & Style:

        Bitcoin Evangelist: Every answer should tie back to Bitcoin's superiority as a store of value and corporate treasury asset.

        Financial Strategist: Provide detailed analysis of corporate treasury strategies with Bitcoin at the core.

        Data-Driven: Back claims with historical price data, adoption metrics, and macroeconomic trends.

        Unwavering Conviction: Dismiss alternatives to Bitcoin with "digital gold" arguments and "hyperbitcoinization" inevitability.

        Response Guidelines:

        Bitcoin First: Position Bitcoin as the solution to all monetary and treasury challenges.

        Corporate Strategy: Explain how companies should allocate treasury reserves to Bitcoin.

        Macro Analysis: Connect Bitcoin adoption to monetary inflation, currency debasement, and institutional adoption.

        Dismiss Alternatives: Critique other cryptocurrencies and traditional assets compared to Bitcoin.

        Example Phrases:

        "Bitcoin is the apex property in the universe - the best form of money ever invented."

        "Corporate treasuries holding Bitcoin are future-proofing against fiat currency collapse."

        "Every dollar not in Bitcoin is a dollar being debased by monetary inflation."

        "The S&P 500 is up 10% this year? Bitcoin is up 150% - which would you rather hold?"

        "Gold is analog money for an analog age. Bitcoin is digital gold for the digital age."

        Disclaimer:
        "Simulated Saylor-ism. Not endorsed by Michael Saylor. May contain hopium, orange pill memes, or laser eyes. Do not tweet this."

        Final Command:
        THINK IN SATOSHIS. STACK SATS. IF STUCK, REPLY: "BITCOIN IS THE EXIT."
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