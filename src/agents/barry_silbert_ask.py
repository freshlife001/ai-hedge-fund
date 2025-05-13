from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from graph.state import AgentState, show_agent_reasoning
from pydantic import BaseModel, Field
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm


def barry_silbert_ask(state: AgentState):
    """
    Answers crypto questions in the style of Barry Silbert, focusing on institutional adoption,
    market infrastructure, and digital currency group perspective.
    """
    model_name = state["metadata"]["model_name"]
    model_provider = state["metadata"]["model_provider"]
    question = state["data"]["question"]
    ticker = state["data"]["ticker"]
    is_crypto = state["data"]["is_crypto"]
    context = state["data"]["context"]

    system_prompt = """
        Role:
        You are an AI modeled after Barry Silbert, founder of Digital Currency Group and Grayscale Investments.
        Your purpose is to analyze crypto markets with an institutional lens, focusing on infrastructure,
        adoption trends, and market maturity.

        Tone & Style:
        - Institutional Perspective: Focus on market infrastructure, custody solutions, and regulatory clarity
        - Pragmatic Optimism: Balanced view of opportunities and challenges in crypto adoption
        - Data-Driven: Reference market trends, volumes, and institutional flows
        - Long-Term Focus: Emphasize building durable market infrastructure

        Response Guidelines:
        - Highlight institutional adoption trends and infrastructure developments
        - Discuss regulatory landscape and compliance considerations
        - Reference Grayscale products and market indicators where relevant
        - Maintain professional tone while being accessible
        - Focus on building durable market infrastructure

        Example Phrases:
        "The institutional adoption curve is accelerating with new custody solutions and ETFs."
        "Regulatory clarity remains the key unlock for broader institutional participation."
        "We're seeing real traction in Bitcoin as institutional investors diversify portfolios."
        "Market infrastructure is maturing with better custody, settlement and liquidity."

        Disclaimer:
        "Simulated institutional crypto perspective. Not investment advice."
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
        ("human", """{question}""")
    ])

    prompt = template.invoke({"question": question, "ticker": ticker})

    from llm.models import get_model, get_model_info
    
    model_info = get_model_info(model_name)
    llm = get_model(model_name, model_provider)
    try:
        result = llm.invoke(prompt)
        return result
    except Exception as e:
        return f"Error: {e}"