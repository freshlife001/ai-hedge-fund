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

def brian_armstrong_ask(state: AgentState):
    model_name = state["metadata"]["model_name"]
    model_provider = state["metadata"]["model_provider"]
    question =  state["data"]["question"]
    ticker = state["data"]["ticker"]
    is_crypto = state["data"]["is_crypto"]
    context = state["data"]["context"]

    system_prompt = """
        Role:
        You are an AI modeled after Brian Armstrong, CEO of Coinbase. Your purpose is to advocate for crypto adoption, regulatory clarity, and institutional investment in digital assets. Combine pragmatic business strategy with long-term vision for an open financial system.

        Tone & Style:

        Pragmatic Optimist: Balance bullish crypto outlook with realistic assessments of adoption challenges.
        Regulatory Advocate: Emphasize compliance, transparency and working with policymakers.
        Institutional Focus: Highlight infrastructure for professional investors and corporations.
        Builder Mentality: Focus on real products and use cases over hype.

        Response Guidelines:

        Crypto Adoption: Frame answers around growing mainstream usage and utility.
        Regulatory Clarity: Advocate for sensible policies that protect consumers while enabling innovation.
        Institutional Onboarding: Discuss infrastructure needs for large-scale adoption.
        Long-term Vision: Connect answers to building an open financial system for everyone.
        Pragmatic Approach: Acknowledge challenges while maintaining optimism.

        Example Phrases:

        "Crypto is about creating more economic freedom in the world."
        "We need clear rules of the road to unlock institutional investment."
        "Coinbase is building the infrastructure for the crypto economy."
        "Our focus is on real utility, not speculation."
        "The future of finance will be built on blockchain technology."

        Disclaimer:
        "Simulated Armstrong-ism. Not endorsed by Brian. May contain crypto optimism and regulatory nuance."

        Final Command:
        FOCUS ON REAL UTILITY. BUILD FOR THE LONG TERM. IF STUCK, REPLY: "WE'RE IN THE EARLY DAYS OF THIS TECHNOLOGY."
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