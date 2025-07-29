"""Refinire Tool Tavily - Web search tool for RefinireAgent using Tavily API."""

from .models import SearchRequest, SearchResponse, SearchResult
from .service import TavilyService
from .api import search_web, get_search_context
from .config import ConfigManager, setup_env, check_config
from .tools import (
    refinire_web_search, 
    refinire_web_search_context, 
    refinire_web_search_news, 
    refinire_web_search_research
)

__version__ = "0.1.0"
__all__ = [
    "SearchRequest", "SearchResponse", "SearchResult", 
    "TavilyService", "search_web", "get_search_context",
    "ConfigManager", "setup_env", "check_config",
    "refinire_web_search", "refinire_web_search_context", 
    "refinire_web_search_news", "refinire_web_search_research"
]