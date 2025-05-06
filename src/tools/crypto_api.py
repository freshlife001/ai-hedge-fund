import os
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any, Optional
from functools import lru_cache

from data.cache import get_cache
from data.models import (
    CompanyNews,
    CompanyNewsResponse,
    FinancialMetrics,
    FinancialMetricsResponse,
    Price,
    PriceResponse,
    LineItem,
    LineItemResponse,
    InsiderTrade,
    InsiderTradeResponse,
)

# Global cache instance
_cache = get_cache()

# Define API keys and fallback order
def get_api_keys():
    """Get all available API keys with fallback options."""
    return {
        "coingecko": os.environ.get("COINGECKO_API_KEY"),
        "cryptocompare": os.environ.get("CRYPTOCOMPARE_API_KEY"),
    }

def is_crypto(ticker: str) -> bool:
    """Check if crypto is enabled in the environment variables."""
    return ticker.lower().startswith("crypto:")

# Add new function for crypto prices
def get_crypto_prices(ticker: str, start_date: str, end_date: str) -> list[Price]:
    symbol = ticker.replace("crypto:", "")
    cache_key = f"crypto_{ticker}"
    if cached_data := _cache.get_prices(cache_key):
        filtered_data = [Price(**price) for price in cached_data if start_date <= price["time"] <= end_date]
        if filtered_data:
            return filtered_data
    """Fetch cryptocurrency price data from multiple sources with fallback strategy."""
    prices = []
    
    # Convert dates to unix timestamps for APIs that require it
    start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
    
    # Try CoinCap API first (completely free, no API key required)
    try:
        # Normalize ticker symbol and get the appropriate coin ID
        coin_id = get_coingecko_coin_id(symbol)
        
        # Calculate interval in days for history API
        interval = "d1"  # daily interval
        
        # CoinCap API for historical data
        url = f"https://api.coincap.io/v2/assets/{coin_id}/history"
        params = {
            "interval": interval,
            "start": start_timestamp * 1000,  # Convert to milliseconds
            "end": end_timestamp * 1000,
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                price_data = data["data"]
                
                # Group data by day to create OHLC
                daily_data = {}
                
                for item in price_data:
                    timestamp_ms = int(item["time"])
                    price = float(item["priceUsd"])
                    date_str = datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d')
                    
                    if start_date <= date_str <= end_date:
                        if date_str not in daily_data:
                            daily_data[date_str] = {
                                "open": price,
                                "high": price,
                                "low": price,
                                "close": price,
                                "prices": [price]
                            }
                        else:
                            daily_data[date_str]["high"] = max(daily_data[date_str]["high"], price)
                            daily_data[date_str]["low"] = min(daily_data[date_str]["low"], price)
                            daily_data[date_str]["close"] = price
                            daily_data[date_str]["prices"].append(price)
                
                # Get volume data from asset endpoint
                volume_url = f"https://api.coincap.io/v2/assets/{coin_id}"
                volume_response = requests.get(volume_url)
                volume_data = {}
                
                if volume_response.status_code == 200:
                    asset_data = volume_response.json()
                    if "data" in asset_data and asset_data["data"]:
                        volume = float(asset_data["data"]["volumeUsd24Hr"])
                        # Use the same volume for all days as an approximation
                        for date_str in daily_data:
                            volume_data[date_str] = volume
                
                # Create price objects from the daily data
                for date_str, data in daily_data.items():
                    price_obj = Price(
                        open=data["open"],
                        close=data["close"],
                        high=data["high"],
                        low=data["low"],
                        volume=volume_data.get(date_str, 0),
                        time=date_str
                    )
                    prices.append(price_obj)
                
                if prices:
                    # Sort by date for consistency
                    prices.sort(key=lambda x: x.time)
                    # Cache the results
                    _cache.set_prices(f"crypto_{ticker}", [p.model_dump() for p in prices])
                    return prices
    except Exception as e:
        print(f"CoinCap error for {ticker}: {str(e)}")
    
    # Fallback to other APIs as they were already implemented
    # ... existing code for CoinGecko, CryptoCompare, and Binance ...

# Module-level cache for crypto mappings
_crypto_mappings = None

def _load_crypto_mappings():
    """Load the crypto mappings from available_cryptos.json into memory."""
    global _crypto_mappings
    if _crypto_mappings is not None:
        return _crypto_mappings
    
    try:
        with open("./webui/public/available_cryptos.json", "r") as f:
            _crypto_mappings = json.load(f)
        return _crypto_mappings
    except Exception as e:
        print(f"Error loading crypto mapping: {str(e)}")
        return []

def get_coingecko_coin_id(symbol: str) -> str:
    """Get the CoinGecko ID for a given ticker using the available_cryptos.json mapping."""
    # Normalize the symbol first
    normalized_symbol = symbol.lower().replace("-usd", "").replace("/usd", "")
    
    # Try to get the mapping from the cached crypto mappings
    cryptos = _load_crypto_mappings()
    if cryptos:
        for crypto in cryptos:
            if crypto.get("symbol", "").lower() == normalized_symbol:
                return crypto.get("id", normalized_symbol)
    
    # Fallback to hardcoded mapping if file can't be loaded or symbol not found
    if normalized_symbol == "btc":
        return "bitcoin"
    elif normalized_symbol == "eth":
        return "ethereum"
    elif normalized_symbol == "sol":
        return "solana"
    
    # If no mapping found, return the normalized symbol
    return normalized_symbol

def compareDateStr(date_str1: str, date_str2: str) -> bool:
    """Compare two date strings."""
    date1 = datetime.strptime(date_str1, "%Y-%m-%d")
    date2 = datetime.strptime(date_str2, "%Y-%m-%d")
    return date1 <= date2


# Add new function for crypto metrics
def get_crypto_metrics(
    ticker: str,
    end_date: str,
    period: str = "ttm",
    limit: int = 10
) -> list[FinancialMetrics]:
    """Fetch cryptocurrency metrics from CoinGecko or other sources."""
    # Check cache first
    symbol = ticker.replace("crypto:", "")
    cache_key = f"crypto_{ticker}"
    if cached_data := _cache.get_financial_metrics(cache_key):
        # Filter cached data by date and limit
        filtered_data = [FinancialMetrics(**metric) for metric in cached_data if compareDateStr(metric["report_period"], end_date)]
        filtered_data.sort(key=lambda x: x.report_period, reverse=True)
        if filtered_data:
            return filtered_data[:limit]
    
    # Normalize ticker symbol
    coin_id = get_coingecko_coin_id(symbol)
    try:
        # Get coin data from CoinGecko
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "true",
            "developer_data": "true"
        }
        
        # Add API key if available
        api_keys = get_api_keys()
        if api_key := api_keys.get("coingecko"):
            params["x_cg_demo_api_key"] = api_key
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print('coingecko', response.status_code, response.json())
        if response.status_code == 200:
            data = response.json()
            market_data = data.get("market_data", {})
            
            report_date = datetime.now().strftime('%Y-%m-%d')
            
            # Create a financial metrics object with cryptocurrency-specific data
            metrics = FinancialMetrics(
                ticker=ticker,
                report_period=report_date,
                period="ttm",
                currency="USD",
                market_cap=market_data.get("market_cap", {}).get("usd"),
                enterprise_value=market_data.get("market_cap", {}).get("usd"),  # Same as market cap for crypto
                price_to_earnings_ratio=None,  # Not applicable for most crypto
                price_to_book_ratio=None,  # Not applicable for most crypto
                price_to_sales_ratio=None,  # Not applicable for most crypto
                enterprise_value_to_ebitda_ratio=None,  # Not applicable for most crypto
                enterprise_value_to_revenue_ratio=None,  # Not applicable for most crypto
                free_cash_flow_yield=None,  # Not applicable for most crypto
                peg_ratio=None,  # Not applicable for most crypto
                gross_margin=None,  # Not applicable for most crypto
                operating_margin=None,  # Not applicable for most crypto
                net_margin=None,  # Not applicable for most crypto
                return_on_equity=None,  # Not applicable for most crypto
                return_on_assets=None,  # Not applicable for most crypto
                return_on_invested_capital=None,  # Not applicable for most crypto
                asset_turnover=None,  # Not applicable for most crypto
                inventory_turnover=None,  # Not applicable for most crypto
                receivables_turnover=None,  # Not applicable for most crypto
                days_sales_outstanding=None,  # Not applicable for most crypto
                operating_cycle=None,  # Not applicable for most crypto
                working_capital_turnover=None,  # Not applicable for most crypto
                current_ratio=None,  # Not applicable for most crypto
                quick_ratio=None,  # Not applicable for most crypto
                cash_ratio=None,  # Not applicable for most crypto
                operating_cash_flow_ratio=None,  # Not applicable for most crypto
                debt_to_equity=None,  # Not applicable for most crypto
                debt_to_assets=None,  # Not applicable for most crypto
                interest_coverage=None,  # Not applicable for most crypto
                revenue_growth=market_data.get("price_change_percentage_30d"),
                earnings_growth=market_data.get("price_change_percentage_1y"),
                book_value_growth=None,  # Not applicable for most crypto
                earnings_per_share_growth=None,  # Not applicable for most crypto
                free_cash_flow_growth=None,  # Not applicable for most crypto
                operating_income_growth=None,  # Not applicable for most crypto
                ebitda_growth=None,  # Not applicable for most crypto
                payout_ratio=None,  # Not applicable for most crypto
                earnings_per_share=None,  # Not applicable for most crypto
                book_value_per_share=None,  # Not applicable for most crypto
                free_cash_flow_per_share=None,  # Not applicable for most crypto
            )
            
            # Cache the result
            _cache.set_financial_metrics(cache_key, [metrics.model_dump()])
            
            return [metrics]
    except Exception as e:
        print(f"CoinGecko metrics error for {symbol}: {str(e)}")
        raise e
    
    # Create an empty metrics object if no data was found
    empty_metrics = FinancialMetrics(
        ticker=ticker,
        report_period=datetime.now().strftime('%Y-%m-%d'),
        period="ttm",
        currency="USD",
        market_cap=None,
        enterprise_value=None,
        price_to_earnings_ratio=None,
        # ... all other fields default to None
    )
    
    return [empty_metrics]


def search_crypto_line_items(
    ticker: str,
    line_items: list[str],
    end_date: str,
    period: str = "ttm",
    limit: int = 10
) -> list[LineItem]:
    """Create appropriate line items for cryptocurrencies."""
    # Normalize ticker symbol
    symbol = ticker.replace("crypto:", "")
    coin_id = get_coingecko_coin_id(symbol)
    try:
        # Get coin data from CoinGecko
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "true",
            "developer_data": "true"
        }
        
        # Add API key if available
        api_keys = get_api_keys()
        if api_key := api_keys.get("coingecko"):
            params["x_cg_demo_api_key"] = api_key
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            market_data = data.get("market_data", {})
            
            # Create a result for today
            result = LineItem(
                ticker=ticker,
                report_period=datetime.now().strftime('%Y-%m-%d'),
                period=period,
                currency="USD"
            )
            
            # Map requested line items to available crypto data
            for item in line_items:
                if item == "revenue":
                    # For crypto, use trading volume as a proxy for revenue
                    result.revenue = market_data.get("total_volume", {}).get("usd")
                
                elif item == "net_income":
                    # For crypto, there's no real net income, but can use market cap change
                    price_change_24h = market_data.get("price_change_24h", 0)
                    circulating_supply = market_data.get("circulating_supply", 0)
                    if price_change_24h and circulating_supply:
                        result.net_income = price_change_24h * circulating_supply
                
                elif item == "outstanding_shares":
                    # Use circulating supply as equivalent to outstanding shares
                    result.outstanding_shares = market_data.get("circulating_supply")
                
                elif item == "total_assets":
                    # Use market cap as a proxy for total assets
                    result.total_assets = market_data.get("market_cap", {}).get("usd")
                
                elif item == "free_cash_flow":
                    # Not directly applicable for crypto
                    result.free_cash_flow = None
                
                elif item == "capital_expenditure":
                    # Not applicable for crypto
                    result.capital_expenditure = None
                
                elif item == "working_capital":
                    # Not applicable for crypto
                    result.working_capital = None
                
                elif item == "research_and_development":
                    # Could use developer metrics as a very rough proxy
                    result.research_and_development = None
                
                elif item == "total_liabilities":
                    # Not applicable for crypto
                    result.total_liabilities = None
                
                elif item == "current_assets":
                    # Not applicable for crypto
                    result.current_assets = None
                
                elif item == "current_liabilities":
                    # Not applicable for crypto
                    result.current_liabilities = None
                
                elif item == "depreciation_and_amortization":
                    # Not applicable for crypto
                    result.depreciation_and_amortization = None
                
                elif item == "dividends_and_other_cash_distributions":
                    # Not applicable for most crypto, though some have staking rewards
                    result.dividends_and_other_cash_distributions = None
                
                elif item == "book_value_per_share":
                    # Not applicable for crypto
                    result.book_value_per_share = None
                
                elif item == "goodwill_and_intangible_assets":
                    # Not applicable for crypto
                    result.goodwill_and_intangible_assets = None
                
                elif item == "ebit":
                    # Not applicable for crypto
                    result.ebit = None
                elif item == "ebitda":
                    # Not applicable for crypto
                    result.ebitda = None
                elif item == "total_debt":
                    # Not applicable for crypto
                    result.total_debt = None
                elif item == "cash_and_equivalents":
                    # Not applicable for crypto
                    result.cash_and_equivalents = None
                elif item == "operating_margin":
                    # Not applicable for crypto
                    result.operating_margin = None
                elif item == "earnings_per_share":
                    # Not applicable for crypto
                    result.earnings_per_share = None
                elif item == "debt_to_equity":
                    # Not applicable for crypto
                    result.debt_to_equity = None
                elif item == "shareholders_equity":
                    # Not applicable for crypto
                    result.shareholders_equity = None
                    
                
            return [result]
    except Exception as e:
        print(f"Error getting crypto line items for {symbol}: {str(e)}")
    
    # Return empty result if we couldn't get data
    result = LineItem(
        ticker=ticker,
        report_period=datetime.now().strftime('%Y-%m-%d'),
        period=period,
        currency="USD"
    )
    
    return [result]


def get_crypto_news(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 100
) -> list[CompanyNews]:
    """Fetch news articles for a cryptocurrency."""
    # Normalize ticker symbol
    symbol = ticker.replace("crypto:", "")
    
    # Default start date to 30 days ago if not specified
    if not start_date:
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = (end_date_dt - timedelta(days=30)).strftime("%Y-%m-%d")
    
    try:
        # CryptoCompare News API (free tier)
        url = "https://data-api.coindesk.com/news/v1/article/list"
        params = {
            "categories": symbol,
            "lang": "EN",
            "limit": "10"
        }
        
        # Add API key if available
        api_keys = get_api_keys()
        if api_key := api_keys.get("cryptocompare"):
            params["api_key"] = api_key
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if "Data" in data:
                news_list = []
                
                for article in data["Data"]:
                    # Convert published timestamp to date string
                    published_date = datetime.fromtimestamp(article["PUBLISHED_ON"]).strftime("%Y-%m-%d")
                    
                    # Check if within date range
                    if start_date <= published_date <= end_date:
                        # Determine sentiment (basic approach)
                        title_lower = article["TITLE"].lower()
                        if any(word in title_lower for word in ["surge", "soar", "jump", "rally", "bullish", "high"]):
                            sentiment = "positive"
                        elif any(word in title_lower for word in ["drop", "fall", "crash", "bearish", "low", "down"]):
                            sentiment = "negative"
                        else:
                            sentiment = "neutral"
                        
                        news = CompanyNews(
                            ticker=ticker,
                            title=article["TITLE"],
                            author=article.get("AUTHORS", "Unknown"),
                            source=article.get("SOURCE_DATA", {"NAME": "CryptoCompare"}).get("NAME", "Unknown"),
                            date=published_date,
                            url=article["URL"],
                            sentiment=article.get("SENTIMENT", sentiment).lower(),
                        )
                        
                        news_list.append(news)
                        
                        if len(news_list) >= limit:
                            break
                return news_list
    except Exception as e:
        print(f"CryptoCompare news error for {ticker}: {str(e)}")
    
    # Fallback to empty list if no news found
    return []


def get_crypto_market_cap(
    ticker: str,
    end_date: str,
) -> float | None:
    """Fetch market cap from Yahoo Finance."""
    symbol = ticker.replace("crypto:", "")
    coin_id = get_coingecko_coin_id(symbol)
    cache_key = f"crypto_{ticker}"
    if cached_data := _cache.get_financial_metrics(cache_key):
        filtered_data = [FinancialMetrics(**metric) for metric in cached_data if compareDateStr(metric["report_period"], end_date)]
        filtered_data.sort(key=lambda x: x.report_period, reverse=True)
        if filtered_data and len(filtered_data) > 0:
            return filtered_data[0].market_cap
    try:
        yf_ticker = yf.Ticker(coin_id)
        info = yf_ticker.info
        
        # Get market cap directly
        market_cap = info.get('marketCap')
        
        if market_cap:
            return float(market_cap)
            
        # If not available, try to calculate from price * shares outstanding
        prev_close = info.get('previousClose')
        shares_outstanding = info.get('sharesOutstanding')
        
        if prev_close and shares_outstanding:
            return float(prev_close * shares_outstanding)
            
        return None
        
    except Exception as e:
        print(f"Error fetching market cap for {ticker}: {str(e)}")
            
        return None