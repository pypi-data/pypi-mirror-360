"""Tavily service implementation for web search functionality."""

import os
import time
import logging
from typing import List, Optional, Dict, Any
from tavily import TavilyClient
from .models import SearchRequest, SearchResponse, SearchResult
from .config import check_config


logger = logging.getLogger(__name__)


class TavilyServiceError(Exception):
    """Custom exception for Tavily service errors."""
    pass


class TavilyService:
    """Service class for interacting with Tavily API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Tavily service.
        
        Args:
            api_key: Tavily API key. If not provided, will use TAVILY_API_KEY environment variable.
        """
        # Check configuration if api_key is not provided
        if not api_key and not check_config():
            raise TavilyServiceError("Configuration is invalid. Please set up your environment variables.")
        
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise TavilyServiceError("Tavily API key is required. Set TAVILY_API_KEY environment variable or provide api_key parameter.")
        
        self.client = TavilyClient(api_key=self.api_key)
    
    def search(self, request: SearchRequest) -> SearchResponse:
        """Perform web search using Tavily API.
        
        Args:
            request: Search request parameters
            
        Returns:
            SearchResponse containing search results and metadata
            
        Raises:
            TavilyServiceError: If search fails
        """
        try:
            start_time = time.time()
            
            # Prepare search parameters
            search_params = {
                "query": request.query,
                "max_results": request.max_results,
                "include_answer": request.include_answer,
                "include_raw_content": request.include_raw_content,
            }
            
            # Add domain filters if provided
            if request.include_domains:
                search_params["include_domains"] = request.include_domains
            if request.exclude_domains:
                search_params["exclude_domains"] = request.exclude_domains
            
            logger.info(f"Performing Tavily search for query: {request.query}")
            
            # Execute search
            response = self.client.search(**search_params)
            
            search_time = time.time() - start_time
            
            # Parse results
            results = []
            for result in response.get("results", []):
                search_result = SearchResult(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    content=result.get("content", ""),
                    score=result.get("score"),
                    raw_content=result.get("raw_content") if request.include_raw_content else None
                )
                results.append(search_result)
            
            # Build response
            search_response = SearchResponse(
                query=request.query,
                results=results,
                answer=response.get("answer") if request.include_answer else None,
                follow_up_questions=response.get("follow_up_questions"),
                total_results=len(results),
                search_time=search_time
            )
            
            logger.info(f"Search completed successfully. Found {len(results)} results in {search_time:.2f}s")
            
            return search_response
            
        except Exception as e:
            logger.error(f"Tavily search failed: {str(e)}")
            raise TavilyServiceError(f"Search failed: {str(e)}") from e
    
    def get_search_context(self, query: str, max_results: int = 5) -> str:
        """Get search context as a formatted string.
        
        Args:
            query: Search query
            max_results: Maximum number of results to include
            
        Returns:
            Formatted search context string
        """
        try:
            request = SearchRequest(
                query=query,
                max_results=max_results,
                include_answer=True
            )
            
            response = self.search(request)
            
            # Format context
            context_parts = []
            
            if response.answer:
                context_parts.append(f"Answer: {response.answer}")
                context_parts.append("")
            
            if response.results:
                context_parts.append("Search Results:")
                for i, result in enumerate(response.results, 1):
                    context_parts.append(f"{i}. {result.title}")
                    context_parts.append(f"   URL: {result.url}")
                    context_parts.append(f"   Content: {result.content}")
                    context_parts.append("")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to get search context: {str(e)}")
            return f"Search failed: {str(e)}"