#!/usr/bin/env python3
import os
import sys
import hashlib
import json
import traceback
import io
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from functools import wraps

from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Load environment variables from .env file
load_dotenv()

# Configuration
WEBUI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webui")
DEFAULT_PORT = 3000
DEFAULT_HOST = "localhost"
API_PORT = 5000

# Add src directory to Python path
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.append(SRC_DIR)

# Initialize colorama for colored terminal output
init(autoreset=True)

# Define request models using Pydantic
class AnalysisRequest(BaseModel):
    tickers: str = Field(..., description="Comma-separated list of ticker symbols")
    selectedAnalysts: List[str] = Field(default=[], description="List of selected analyst agents")
    modelName: str = Field(..., description="Name of the LLM model to use")
    startDate: Optional[str] = Field(None, description="Start date for analysis (YYYY-MM-DD)")
    endDate: Optional[str] = Field(None, description="End date for analysis (YYYY-MM-DD)")
    initialCash: float = Field(100000, description="Initial cash amount for portfolio")
    isCrypto: bool = Field(False, description="Whether the tickers are cryptocurrencies")

# Dictionary to store locks for each cache key
_cache_locks = {}

# Custom caching decorator that persists cache indefinitely with special handling for error responses
def custom_cache_with_status_check(*, expire: int = None, max_age: int = 60 * 60 * 24):
    """Custom caching decorator that persists cache indefinitely, with shorter timeout only for error responses
    
    Args:
        expire: Default expiration time in seconds for error responses
        max_age: Maximum age of cached results in seconds before they're considered stale
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Add a 2-second delay for all requests
            await asyncio.sleep(2)
            
            # Generate a cache key based on the request body
            request = kwargs.get('request')
            if request and hasattr(request, 'json'):
                try:
                    body = await request.json()
                    cache_key = f"analysis_{hashlib.md5(json.dumps(body or {}, sort_keys=True).encode()).hexdigest()}"
                except:
                    cache_key = f"analysis_{id(request)}"
            else:
                cache_key = f"analysis_{id(args)}"
            
            # Create a lock for this cache key if it doesn't exist
            if cache_key not in _cache_locks:
                _cache_locks[cache_key] = asyncio.Lock()
            
            # Try to get from cache using the backend instance
            backend = FastAPICache.get_backend()
            cached_result = await backend.get(cache_key)
            
            # Check if we have a valid cached result with timestamp
            if cached_result is not None:
                # If it's a dict with a timestamp, check if it's still valid
                if isinstance(cached_result, dict) and "_timestamp" in cached_result:
                    current_time = datetime.now().timestamp()
                    cache_time = cached_result["_timestamp"]
                    cache_age = current_time - cache_time
                    
                    # If max_age is specified and the cache is older than max_age, consider it expired
                    if max_age is not None and cache_age > max_age:
                        print(f"Cache expired (age: {cache_age:.2f}s, max: {max_age}s): {cache_key}")
                        cached_result = None
                    else:
                        print(f"Using cached result (age: {cache_age:.2f}s): {cache_key}")
                        return cached_result["_data"]
                else:
                    # Legacy cache format without timestamp
                    return cached_result
            
            print(f"Acquire lock for cache key: {cache_key}")
            # Acquire lock for this cache key to prevent duplicate processing
            async with _cache_locks[cache_key]:
                print(f"Lock acquired for cache key: {cache_key}")
                # Check cache again after acquiring the lock in case another request populated it
                cached_result = await backend.get(cache_key)
                if cached_result is not None:
                    if isinstance(cached_result, dict) and "_timestamp" in cached_result:
                        print(f"Using cached result (populated by another request): {cache_key}")
                        return cached_result["_data"]
                    else:
                        return cached_result
                
                # Execute the function
                print(f"Executing analysis for cache key: {cache_key}")
                result = await func(*args, **kwargs)
                
                # Add timestamp to the result
                timestamp = datetime.now().timestamp()
                cache_data = {
                    "_timestamp": timestamp,
                    "_data": result
                }
                
                # Set cache with appropriate timeout using the backend instance
                if isinstance(result, tuple) and len(result) > 1 and isinstance(result[1], int) and result[1] != 200:
                    # Shorter timeout for error responses
                    error_expire = expire if expire is not None else 60  # Default 1 minute for errors
                    print(f"Setting shorter timeout for error response: {cache_key}")
                    await backend.set(cache_key, cache_data, expire=error_expire)
                else:
                    # No expiration for successful responses (persist indefinitely)
                    print(f"Setting cache with no expiration: {cache_key}")
                    await backend.set(cache_key, cache_data, expire= 60 * 60 * 24 * 7)
                
                return result
        return wrapper
    return decorator

# Add a global function for server-wide logging (placeholder for WebSocket implementation)
def broadcast_log(message, level="info"):
    # In a real implementation, this would send to WebSocket clients
    # For now, just print to console
    print(f"[{level.upper()}] {message}")

# Create a custom progress handler that forwards to websocket
class WebUIProgressHandler:
    def __init__(self):
        pass
        
    def update_status(self, agent, ticker, status):
        # Format the status message
        if ticker:
            message = f"[{agent}] {ticker}: {status}"
        else:
            message = f"[{agent}] {status}"
        
        # Broadcast to all websocket clients
        broadcast_log(message, "info")
        
    def start(self):
        broadcast_log("Starting analysis process", "info")
        
    def complete(self):
        broadcast_log("Analysis process completed", "success")

# Create FastAPI application
def create_app():
    # Try importing the main hedge fund modules
    try:
        from src.main import run_hedge_fund
        from src.llm.models import LLM_ORDER, get_model_info
        from src.utils.analysts import ANALYST_ORDER
    except ImportError as e:
        print(f"Error importing modules from src: {e}")
        traceback.print_exc()
        return None

    app = FastAPI(
        title="AI Hedge Fund API",
        description="API for AI Hedge Fund analysis",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow requests from any origin
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize cache
    @app.on_event("startup")
    async def startup():
        FastAPICache.init(InMemoryBackend())
        
        # Initialize progress handler
        try:
            from utils.progress import progress
            progress.handler = WebUIProgressHandler()
        except ImportError:
            try:
                from src.utils.progress import progress
                progress.handler = WebUIProgressHandler()
            except ImportError:
                print("Warning: Could not import progress module")
    
    # API endpoints
    @app.post("/api/analysis")
    @custom_cache_with_status_check()
    async def run_analysis(request: Request, analysis_req: AnalysisRequest):
        """Run hedge fund analysis"""
        try:
            print("Received analysis request")
            print(f"Request data: {analysis_req.dict()}")
            
            ticker_list = analysis_req.tickers.split(',')
            selected_analysts = analysis_req.selectedAnalysts
            model_name = analysis_req.modelName
            
            print(f"Processing analysis for tickers: {ticker_list}")
            print(f"Selected analysts: {selected_analysts}")
            print(f"Using model: {model_name}")
            
            # Run the web-specific analysis function
            # Run in thread pool and await completion
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                _executor,
                run_hedge_fund_for_web,
                ticker_list,
                selected_analysts,
                model_name,
                analysis_req.startDate,
                analysis_req.endDate,
                analysis_req.initialCash,
                analysis_req.isCrypto
            )
            
            print(f"Analysis completed successfully {result}")
            return result
        
        except Exception as e:
            print(f"API error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

from concurrent.futures import ThreadPoolExecutor
import threading

# Global thread pool executor
_executor = ThreadPoolExecutor(max_workers=4)

def run_hedge_fund_for_web(tickers, selected_analysts, model_name, start_date=None, end_date=None, initial_cash=100000, is_crypto=False):
    """
    Special version of run_hedge_fund optimized for web UI integration.
    This bypasses some of the CLI-specific code and analyst selection logic.
    Now runs in a thread pool to avoid blocking the event loop.
    """
    # Import necessary modules
    from src.main import create_workflow
    from src.graph.state import AgentState, show_agent_reasoning
    from src.llm.models import get_model_info
    
    # Import progress tracker from the correct location
    try:
        from src.utils.progress import progress
    except ImportError:
        from utils.progress import progress
    
    # Initialize progress
    try:
        progress.start()
    except:
        # Fallback if no start method exists
        pass
        
    broadcast_log("Starting analysis process", "info")
    
    # Get model info
    model_info = get_model_info(model_name)
    model_provider = model_info.provider.value if model_info else "Unknown"
    broadcast_log(f"Using model: {model_name} ({model_provider})", "info")
    
    # Create portfolio
    portfolio = {
        "cash": initial_cash,
        "positions": {},
        "cost_basis": {}, 
        "realized_gains": {ticker: {"long": 0.0, "short": 0.0} for ticker in tickers}
    }
    
    default_date = datetime.now().strftime("%Y-%m-%d")
    # Create initial state
    initial_state = {
        "messages": [],
        "data": {
            "tickers": tickers,
            "portfolio": portfolio,
            "start_date": start_date if start_date else default_date,
            "end_date": end_date if end_date else default_date,
            "analyst_signals": {},
            "is_crypto": is_crypto
        },
        "metadata": {
            "show_reasoning": True,
            "model_name": model_name,
            "model_provider": model_provider
        }
    }
    
    broadcast_log(f"Analyzing tickers: {tickers}", "info")
    broadcast_log(f"Using analysts: {selected_analysts}", "info")
    
    # Process each analyst manually to bypass the workflow issues
    from src.agents.warren_buffett import warren_buffett_agent
    from src.agents.bill_ackman import bill_ackman_agent
    from src.agents.ben_graham import ben_graham_agent
    from src.agents.charlie_munger import charlie_munger_agent
    from src.agents.cathie_wood import cathie_wood_agent
    from src.agents.stanley_druckenmiller import stanley_druckenmiller_agent
    from src.agents.michael_burry import michael_burry_agent
    from src.agents.peter_lynch import peter_lynch_agent
    from src.agents.phil_fisher import phil_fisher_agent
    from src.agents.nancy_pelosi import nancy_pelosi_agent
    from src.agents.wsb_agent import wsb_agent
    from src.agents.fundamentals import fundamentals_agent
    from src.agents.technicals import technical_analyst_agent
    from src.agents.sentiment import sentiment_agent
    from src.agents.valuation import valuation_agent
    from src.agents.risk_manager import risk_management_agent
    from src.agents.portfolio_manager import portfolio_management_agent
    
    # Map of available agents
    agent_map = {
        "warren_buffett_agent": warren_buffett_agent,
        "bill_ackman_agent": bill_ackman_agent,
        "ben_graham_agent": ben_graham_agent,
        "charlie_munger_agent": charlie_munger_agent,
        "stanley_druckenmiller_agent": stanley_druckenmiller_agent,
        "cathie_wood_agent": cathie_wood_agent,
        "phil_fisher_agent": phil_fisher_agent,
        "peter_lynch_agent": peter_lynch_agent,
        "michael_burry_agent": michael_burry_agent,
        "nancy_pelosi_agent": nancy_pelosi_agent,
        "wsb_agent": wsb_agent,
        "fundamentals_agent": fundamentals_agent,
        "technical_analyst_agent": technical_analyst_agent,
        "sentiment_agent": sentiment_agent,
        "valuation_agent": valuation_agent,
        "risk_management_agent": risk_management_agent,
        "portfolio_management_agent": portfolio_management_agent
    }
    
    # Current state
    state = initial_state
    
    # Run each selected analyst
    for analyst_name in selected_analysts:
        if analyst_name in agent_map:
            broadcast_log(f"Running analyst: {analyst_name}", "info")
            try:
                agent_fn = agent_map[analyst_name]
                result = agent_fn(AgentState(state))
                
                if result:
                    # Update state with results
                    if "messages" in result:
                        state["messages"] = result["messages"]
                    if "data" in result:
                        state["data"] = result["data"]
                    
                    # Display output in CLI-style with colors
                    if analyst_name in state["data"]["analyst_signals"]:
                        analyst_output = state["data"]["analyst_signals"][analyst_name]
                        formatted_name = analyst_name.replace("_agent", "").replace("_", " ").title()
                        
                        # Print formatted analysis like in CLI with colors
                        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 10}     {formatted_name} Agent     {'=' * 10}{Style.RESET_ALL}")
                        print(json.dumps(analyst_output, indent=2))
                        print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 48}{Style.RESET_ALL}\n")
                        
                        # Also broadcast to WebSocket
                        broadcast_log(f"===== {formatted_name} Analysis =====", "info")
                        broadcast_log(json.dumps(analyst_output, indent=2), "info")
                
                broadcast_log(f"Completed {analyst_name} analysis", "success")
            except Exception as e:
                broadcast_log(f"Error in {analyst_name}: {str(e)}", "error")
                broadcast_log(traceback.format_exc(), "error")
                raise e
    
    # Prepare the final output
    result = {
        "ticker_analyses": state["data"].get("ticker_analyses", {}),
        "portfolio": state["data"].get("portfolio", portfolio),
        "portfolio_decision": state["data"].get("portfolio_decision", {})
    }
    
    # If there's no ticker_analyses yet, create it from analyst_signals
    if not result["ticker_analyses"] and state["data"].get("analyst_signals"):
        result["ticker_analyses"] = {}
        for ticker in tickers:
            result["ticker_analyses"][ticker] = {
                "signals": {},
                "reasoning": {}
            }
            for agent_name, signals in state["data"]["analyst_signals"].items():
                if ticker in signals:
                    signal_data = signals[ticker]
                    if "signal" in signal_data:
                        result["ticker_analyses"][ticker]["signals"][agent_name] = signal_data["signal"]
                    if "confidence" in signal_data:
                        result["ticker_analyses"][ticker]["signals"][f"{agent_name}_confidence"] = signal_data["confidence"]
                    if "reasoning" in signal_data:
                        result["ticker_analyses"][ticker]["reasoning"][agent_name] = signal_data["reasoning"]
    
    # Ensure signal consistency in the ticker_analyses
    if result["ticker_analyses"] and len(selected_analysts) == 1:
        for ticker, analysis in result["ticker_analyses"].items():
            # If there's only one analyst, use their signal as the overall signal
            analyst_name = selected_analysts[0]
            if "signals" in analysis and analyst_name in analysis["signals"]:
                # Get the analyst's signal 
                analyst_signal = analysis["signals"][analyst_name]
                # Set it as the overall signal
                analysis["signals"]["overall"] = analyst_signal
                # Set confidence too
                if f"{analyst_name}_confidence" in analysis["signals"]:
                    analysis["signals"]["confidence"] = analysis["signals"][f"{analyst_name}_confidence"]
    
    broadcast_log("Analysis completed successfully", "success")
    return result

def main():
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description="Hedge Fund AI Web UI with FastAPI")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host to run the API server on (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=API_PORT, help=f"Port to run the API server on (default: {API_PORT})")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (default: 1)")
    
    args = parser.parse_args()
    
    app = create_app()
    if app is None:
        print("Failed to create FastAPI application")
        return 1
    
    print(f"Starting API server at http://{args.host}:{args.port}")
    uvicorn.run("fastapi_webui:create_app", host=args.host, port=args.port, workers=args.workers, factory=True, limit_concurrency=100)
    return 0

if __name__ == "__main__":
    sys.exit(main())