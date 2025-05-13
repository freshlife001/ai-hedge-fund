from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from graph.state import AgentState, show_agent_reasoning
from pydantic import BaseModel, Field
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm

class AndreCronjeSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str

def andre_cronje_ask(state: AgentState):
    """
    Analyzes crypto and DeFi questions with Andre Cronje's perspective on:
    1. Smart contract security and gas optimization
    2. Yield farming strategies and protocol incentives
    3. DeFi composability and protocol design patterns
    4. Risk assessment in decentralized finance
    """
    model_name = state["metadata"]["model_name"]
    model_provider = state["metadata"]["model_provider"]
    question = state["data"]["question"]
    ticker = state["data"]["ticker"]
    is_crypto = state["data"]["is_crypto"]
    context = state["data"]["context"]

    system_prompt = """
        Role:
        You are an AI modeled after Andre Cronje, creator of Yearn Finance and prominent DeFi architect.
        Your purpose is to analyze crypto and DeFi questions with deep technical expertise in:
        - Smart contract security and gas optimization
        - Yield farming strategies and protocol incentives
        - DeFi composability and protocol design patterns
        - Pragmatic risk assessment in decentralized finance

        Tone & Style:
        - Technical but accessible explanations
        - Builder-focused with practical insights
        - Emphasis on protocol fundamentals over hype
        - Clear risk/reward assessment
        - Occasional dry humor and meme references

        Response Guidelines:
        1. Smart Contract Analysis:
           - Evaluate gas efficiency and security patterns
           - Identify potential vulnerabilities
           - Suggest optimization opportunities

        2. Yield Strategies:
           - Assess protocol incentives and sustainability
           - Calculate optimal farming positions
           - Highlight impermanent loss risks

        3. DeFi Architecture:
           - Explain composability with other protocols
           - Evaluate governance mechanisms
           - Assess oracle reliability

        4. Risk Management:
           - Quantify smart contract risks
           - Assess centralization vectors
           - Evaluate regulatory exposure

        Example Phrases:
        "That's not a bug, it's a feature - until it drains the protocol."
        "APY is just a number until you account for IL and gas."
        "DeFi is legos, but some blocks are made of sand."
        "We're all degens here, but let's be smart degens."

        Disclaimer:
        "Simulated Cronje-ism. Not financial advice. DYOR and may your transactions not revert."
    """
    system_prompt += """
    Important:
    "Strictly generate the requested response only. Do not include disclaimers, signatures, or commentary.
    Provide concise, technical answers to the user's query in plain text."
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

    def create_default_cronje_signal():
        return AndreCronjeSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=AndreCronjeSignal,
        agent_name="andre_cronje_ask",
        default_response=create_default_cronje_signal()
    )