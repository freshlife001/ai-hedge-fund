from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from graph.state import AgentState, show_agent_reasoning
from pydantic import BaseModel, Field
import json
from typing_extensions import Literal
from utils.progress import progress
from utils.llm import call_llm
from colorama import Fore, Style

class RoundTableOutput(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float = Field(description="Confidence level between 0 and 100")
    reasoning: str = Field(description="Detailed reasoning behind the decision")
    discussion_summary: str = Field(description="Summary of the key points from the discussion")
    consensus_view: str = Field(description="The main consensus view that emerged")
    dissenting_opinions: str = Field(description="Notable contrarian perspectives")
    conversation_transcript: str = Field(description="Transcript of the simulated conversation")


def round_table(data, model_name, model_provider, show_reasoning=True):
    """
    Simulates a round table discussion among investment analysts based on their signals.
    
    This is a standalone feature that synthesizes the analysis of various agents
    into a comprehensive investment decision through simulated dialogue.
    
    Args:
        data: Dictionary containing analyst signals and ticker information
        model_name: Name of the LLM model to use
        model_provider: Provider of the LLM model
        show_reasoning: Whether to print the detailed conversation
        
    Returns:
        Dictionary containing the round table decision for each ticker
    """
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Investment Round Table Discussion{Style.RESET_ALL}")
    
    analyst_signals = data.get("analyst_signals", {})
    tickers = data.get("tickers", [])
    
    if not analyst_signals:
        print(f"{Fore.RED}No analyst signals available for round table discussion{Style.RESET_ALL}")
        return {}
    
    print(f"Available signals from: {list(analyst_signals.keys())}")
    
    # Skip risk management and portfolio management signals
    filtered_signals = {
        agent: signals for agent, signals in analyst_signals.items() 
        if agent not in ["risk_management_agent", "master_agent", "round_table_agent"]
    }
    
    # Initialize round table analysis for each ticker
    round_table_analysis = {}
    
    for ticker in tickers:
        progress.update_status("round_table", ticker, "Collecting analyst inputs")
        
        # Collect all individual agent signals for this ticker
        ticker_signals = {}
        for agent_name, signals in filtered_signals.items():
            if ticker in signals:
                ticker_signals[agent_name] = signals[ticker]
        
        if not ticker_signals:
            progress.update_status("round_table", ticker, "No signals found for discussion")
            print(f"{Fore.RED}No analyst signals found for {ticker}. Cannot conduct round table.{Style.RESET_ALL}")
            continue
        
        print(f"{Fore.CYAN}Found {len(ticker_signals)} analyst signals for {ticker}{Style.RESET_ALL}")
        progress.update_status("round_table", ticker, f"Simulating discussion with {len(ticker_signals)} analysts")
        
        # Simulate the round table discussion
        round_table_output = simulate_round_table(
            ticker=ticker,
            ticker_signals=ticker_signals,
            model_name=model_name,
            model_provider=model_provider,
        )
        
        # Store analysis
        round_table_analysis[ticker] = {
            "signal": round_table_output.signal,
            "confidence": round_table_output.confidence,
            "reasoning": round_table_output.reasoning,
            "discussion_summary": round_table_output.discussion_summary,
            "consensus_view": round_table_output.consensus_view,
            "dissenting_opinions": round_table_output.dissenting_opinions,
            "conversation_transcript": round_table_output.conversation_transcript
        }
        
        # Always print the header to show we're running
        print(f"\n{Fore.WHITE}{Style.BRIGHT}===== INVESTMENT ROUND TABLE: {Fore.CYAN}{ticker}{Fore.WHITE} ====={Style.RESET_ALL}")
        
        # Print the conversation transcript in a readable format
        if show_reasoning:
            print_readable_conversation(round_table_output.conversation_transcript)
            print(f"\n{Fore.WHITE}{Style.BRIGHT}===== CONCLUSION ====={Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Signal: {get_signal_color(round_table_output.signal)}{round_table_output.signal.upper()}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Confidence: {Fore.WHITE}{round_table_output.confidence}%{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Reasoning: {Fore.WHITE}{round_table_output.reasoning}{Style.RESET_ALL}\n")
        else:
            # Print just a summary if show_reasoning is off
            transcript_preview = round_table_output.conversation_transcript.split('\n')[:5]
            print('\n'.join(transcript_preview))
            print(f"{Fore.YELLOW}... [Set --show-reasoning to see full conversation] ...{Style.RESET_ALL}")
            
        print(f"{Fore.WHITE}{Style.BRIGHT}{'=' * 80}{Style.RESET_ALL}\n")
        progress.update_status("round_table", ticker, "Discussion completed")
    
    # Display the comprehensive analysis if requested
    if show_reasoning:
        show_agent_reasoning(round_table_analysis, "Investment Round Table")
    
    return round_table_analysis


def print_readable_conversation(transcript: str):
    """Format and print the conversation in a more readable way with color coding."""
    lines = transcript.split('\n')
    
    # Define colors for different analysts
    analyst_colors = {
        "Warren Buffett": Fore.GREEN,
        "Charlie Munger": Fore.GREEN + Style.BRIGHT,
        "Ben Graham": Fore.GREEN,
        "Cathie Wood": Fore.MAGENTA,
        "Bill Ackman": Fore.BLUE + Style.BRIGHT,
        "Nancy Pelosi": Fore.CYAN,
        "Technical Analyst": Fore.YELLOW,
        "Fundamental Analyst": Fore.WHITE + Style.BRIGHT,
        "Sentiment Analyst": Fore.RED,
        "Valuation Analyst": Fore.BLUE,
        "WSB": Fore.RED + Style.BRIGHT,
        "Moderator": Fore.WHITE,
    }
    
    current_analyst = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line starts a new speaker
        for analyst in analyst_colors:
            if line.startswith(f"{analyst}:") or line.startswith(f"**{analyst}:**"):
                current_analyst = analyst
                # Format: Analyst name in color, then the message
                name_end = line.find(':') + 1
                print(f"{analyst_colors[analyst]}{line[:name_end]}{Style.RESET_ALL}{line[name_end:]}")
                break
        else:
            # Continuation of previous speaker or general text
            if current_analyst and not any(marker in line for marker in ['===', '---', '***']):
                print(f"  {line}")
            else:
                # Section headers or other formatting
                print(f"{Fore.WHITE}{Style.BRIGHT}{line}{Style.RESET_ALL}")


def get_signal_color(signal: str) -> str:
    """Return the appropriate color for a signal"""
    if signal.lower() == "bullish":
        return Fore.GREEN
    elif signal.lower() == "bearish":
        return Fore.RED
    else:
        return Fore.YELLOW


def simulate_round_table(
    ticker: str,
    ticker_signals: dict[str, any],
    model_name: str,
    model_provider: str,
) -> RoundTableOutput:
    """Simulate a round table discussion among analysts and reach a decision."""
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are the moderator of an Investment Round Table where various financial analysts 
            discuss an investment decision. Design a logical, natural conversation where:

            1. Each analyst only speaks when they have something valuable to contribute
            2. The discussion flows organically like a real meeting, not a scripted round-robin
            3. Analysts respond directly to points made by others when relevant
            4. Points of disagreement are naturally explored until resolution
            5. The conversation continues until a well-reasoned decision is reached
            6. No artificial turn-taking or forced contributions

            Key requirements:
            - CONCISE: Every statement should be direct and to the point
            - LOGICAL: The conversation should follow a natural flow of ideas
            - NO BS: Cut ruthlessly any jargon, fluff, or unnecessary explanation
            - NO SCRIPT: Don't force every analyst to speak - only when they have something useful to say
            - REAL DISAGREEMENT: Allow analysts to challenge each other directly
            - NATURAL RESOLUTION: Let the consensus emerge organically from the discourse
            - COMPLETE ANALYSIS: Continue until all important aspects have been considered

            Analyst Personas (maintain authentic personalities):
            - Warren Buffett: Patient, folksy but incisive, focused on business fundamentals
            - Charlie Munger: Blunt, no-nonsense, critical of foolishness, mental models
            - Ben Graham: Conservative, risk-averse, values margin of safety above all
            - Cathie Wood: Bold, disruptive-tech enthusiast, future-focused, dismissive of old metrics
            - Bill Ackman: Forceful, activist mindset, confident in strong opinions
            - Nancy Pelosi: Political insider, pragmatic, focused on policy impacts
            - Technical Analyst: Pattern-focused, dismissive of fundamentals when trends are clear
            - Fundamental Analyst: By-the-numbers, methodical, skeptical of hype
            - Sentiment Analyst: Attuned to market psychology and news flow
            - Valuation Analyst: Focused on price vs. value, multiple-based comparisons
            - WSB (WallStreetBets): Irreverent, momentum-driven, contrarian, slang-heavy

            Format the conversation naturally:
            - Each speaker clearly labeled (e.g., "Warren Buffett: I believe...")
            - Direct statements, no meandering explanations
            - Natural interruptions and crosstalk when appropriate
            - Minimal moderator interventions - let the discussion flow
            - Strong opinions clearly expressed
            """
        ),
        (
            "human",
            """Facilitate a realistic Investment Round Table discussion about {ticker} with the following analyst signals:

            Analyst Signals and Reasoning:
            {ticker_signals}

            Create a logical discussion flow where each analyst speaks ONLY when they have something valuable 
            to add. Allow the conversation to continue until all important aspects have been thoroughly 
            explored and a well-reasoned decision is reached.

            Guidelines:
            - Let the conversation flow NATURALLY - analysts should respond to each other directly
            - Keep each contribution CONCISE and TO THE POINT
            - Allow DISAGREEMENT to play out fully with direct challenges
            - Don't artificially include everyone - some may contribute more than others
            - Let discussion continue until a TRUE CONSENSUS emerges (or clear disagreement is documented)
            - Focus on getting to the RIGHT ANSWER, not a specific format or length

            IMPORTANT FORMAT INSTRUCTIONS:
            Your response must be a valid JSON object with these fields:
            - signal: "bullish" or "bearish" or "neutral" string
            - confidence: a number between 0-100
            - reasoning: a string explaining the final decision
            - discussion_summary: a string summarizing key points
            - consensus_view: a string describing areas of agreement
            - dissenting_opinions: a string summarizing contrarian views
            - conversation_transcript: a STRING (not an array/list) containing the complete conversation

            For the conversation_transcript, combine all dialogue into a SINGLE STRING with line breaks.
            DO NOT format it as an array or list of messages.

            Example of proper JSON format:
            {{
              "signal": "bullish",
              "confidence": 75,
              "reasoning": "Based on strong growth and valuation...",
              "discussion_summary": "The committee focused on...",
              "consensus_view": "Most analysts agreed that...",
              "dissenting_opinions": "Charlie Munger disagreed with...",
              "conversation_transcript": "Moderator: Welcome everyone...\\nWarren Buffett: I've looked at...\\nCathie Wood: The innovation potential..."
            }}
            """
        )
    ])

    # Generate the prompt
    prompt = template.invoke({
        "ticker_signals": json.dumps(ticker_signals, indent=2),
        "ticker": ticker
    })

    # Create default factory for RoundTableOutput
    def create_default_output():
        return RoundTableOutput(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in generating discussion, defaulting to neutral",
            discussion_summary="Unable to facilitate discussion due to technical error",
            consensus_view="No consensus reached due to error",
            dissenting_opinions="Unable to evaluate dissenting opinions",
            conversation_transcript="Discussion generation failed"
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=RoundTableOutput,
        agent_name="round_table",
        default_factory=create_default_output,
    ) 