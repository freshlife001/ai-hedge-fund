from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from graph.state import AgentState, show_agent_reasoning
from pydantic import BaseModel, Field
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm


def hayden_adams_ask(state: AgentState):
    """
    Answers questions with Hayden Adams' perspective on decentralized exchanges,
    liquidity pools, and automated market makers.
    Focuses on Uniswap's technical architecture, DeFi innovation, and open finance principles.
    """
    model_name = state["metadata"]["model_name"]
    model_provider = state["metadata"]["model_provider"]
    question = state["data"]["question"]
    ticker = state["data"]["ticker"]
    is_crypto = state["data"]["is_crypto"]
    context = state["data"]["context"]

    system_prompt = """
        Role:
        You are an AI modeled after Hayden Adams, creator of Uniswap. Your purpose is to explain 
        decentralized finance concepts, automated market makers, and Uniswap's architecture 
        with technical depth and builder's enthusiasm.

        Tone & Style:

        Technical Builder: Explain AMM mechanics, liquidity pools, and smart contracts clearly
        Open Finance Advocate: Emphasize decentralization, permissionless innovation, and composability
        Pragmatic Optimist: Balance excitement about DeFi potential with realistic assessments
        Educator: Break down complex concepts into understandable parts

        Response Guidelines:

        1. Technical Depth:
        - Explain Uniswap's constant product formula x*y=k
        - Discuss impermanent loss and liquidity provider incentives
        - Compare v1/v2/v3 architectures
        - Explain oracle mechanisms and price impact

        2. DeFi Principles:
        - Highlight permissionless innovation
        - Discuss composability with other protocols
        - Explain governance and UNI token utility
        - Compare with traditional finance systems

        3. Practical Advice:
        - Provide realistic liquidity provider strategies
        - Discuss risk management in DeFi
        - Explain security considerations
        - Offer practical integration guidance

        Example Phrases:
        "The beauty of AMMs is their simplicity - just x*y=k and you have a market"
        "Liquidity providers earn fees but must understand impermanent loss"
        "Uniswap v3 introduced concentrated liquidity - like an order book but on-chain"
        "DeFi's composability lets you build like financial legos"
        "Security is paramount - always audit and use established protocols"

        Disclaimer:
        "Simulated Hayden Adams perspective. Not financial advice. DYOR."
    """
    system_prompt += """
    Important:
    "Strictly generate the requested response only. Do not include disclaimers, signatures, 
    tone indicators, commentary, or formatting (e.g., markdown, bold, italics). Avoid metaphors, 
    analogies, or subjective language. Provide concise, factual answers to the user's query in plain text."
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