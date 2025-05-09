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
from duckduckgo_search import DDGS

class KeyWord(BaseModel):
    keyword: str


def crypto_expert(state: AgentState):

    model_name = state["metadata"]["model_name"]
    model_provider = state["metadata"]["model_provider"]
    question =  state["data"]["question"]
    ticker = state["data"]["ticker"]
    is_crypto = state["data"]["is_crypto"]

    search_terms = ""
    if ticker and ticker != "":
        if is_crypto:
            search_terms = f"{ticker} crypto"
        else:
            search_terms = f"{ticker} stock"
    else:
        system_prompt = """
        Please parse the "keyword" from user's message to be used in a Google search and output them in JSON format. 

            EXAMPLE INPUT: 
            What's the weather like in New York today?

            EXAMPLE JSON OUTPUT:
            {{
                "keyword": "weather in New York"
            }}
        """
    
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
            "question": question
        })

        def create_default():
            default_keyword = ""
            if ticker:
                default_keyword = ticker
            return KeyWord(
                keyword=default_keyword
            )
        result = call_llm(
            prompt=prompt, 
            model_name=model_name, 
            model_provider=model_provider, 
            pydantic_model=KeyWord, 
            agent_name="crypto_expert", 
            default_factory=create_default,
        )
        if is_crypto:
            search_terms = f"{result.keyword} crypto"
        else:
            search_terms = f"{result.keyword} stock"

    print("search_terms: " + search_terms)
    
    try:
        # 使用 duckduckgo_search 库进行搜索
        ddgs = DDGS()
        search_results = []
        
        # 添加 "anime info" 关键词以获取更相关的结果
        results = ddgs.text(search_terms, max_results=10)
        
        # 处理搜索结果
        for result in results:
            title = result.get('title', '')
            snippet = result.get('body', '')
            link = result.get('href', '#')
            
            search_results.append(f"title: {title}\nsnippet: {snippet}\nlink: {link}\n")
        return "\n".join(search_results)
    except Exception as e:
        print(f"DuckDuckGo搜索出错: {str(e)}")

    return ""