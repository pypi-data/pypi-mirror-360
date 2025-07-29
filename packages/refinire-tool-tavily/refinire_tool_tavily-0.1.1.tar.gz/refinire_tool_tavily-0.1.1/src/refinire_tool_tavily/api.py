"""Refinire tool API for web search functionality."""

import logging
from typing import Dict, Any, Optional, List
from .models import SearchRequest, SearchResponse
from .service import TavilyService, TavilyServiceError


logger = logging.getLogger(__name__)


def search_web(
    query: str,
    max_results: int = 5,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    include_answer: bool = False,
    include_raw_content: bool = False
) -> Dict[str, Any]:
    """Web search tool for RefinireAgent using Tavily API.
    
    This function provides web search capabilities to RefinireAgent through the Tavily API.
    It validates input parameters, performs the search, and returns structured results.
    
    Args:
        query: Search query string (required)
        max_results: Maximum number of results to return (default: 5, max: 20)
        include_domains: List of domains to include in search (optional)
        exclude_domains: List of domains to exclude from search (optional)
        include_answer: Include AI-generated answer in response (default: False)
        include_raw_content: Include raw content of web pages (default: False)
    
    Returns:
        Dictionary containing search results with the following structure:
        {
            "success": bool,
            "query": str,
            "results": [
                {
                    "title": str,
                    "url": str,
                    "content": str,
                    "score": float (optional),
                    "raw_content": str (optional)
                }
            ],
            "answer": str (optional),
            "follow_up_questions": List[str] (optional),
            "total_results": int,
            "search_time": float (optional),
            "error": str (optional)
        }
    
    Raises:
        ValueError: If query is empty or contains invalid characters
        TavilyServiceError: If search fails due to API issues
    """
    try:
        # Validate and create search request
        search_request = SearchRequest(
            query=query,
            max_results=max_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_answer=include_answer,
            include_raw_content=include_raw_content
        )
        
        # Initialize service and perform search
        service = TavilyService()
        response: SearchResponse = service.search(search_request)
        
        # Convert to dictionary format for tool response
        results = []
        for result in response.results:
            result_dict = {
                "title": result.title,
                "url": result.url,
                "content": result.content
            }
            if result.score is not None:
                result_dict["score"] = result.score
            if result.raw_content is not None:
                result_dict["raw_content"] = result.raw_content
            results.append(result_dict)
        
        response_dict = {
            "success": True,
            "query": response.query,
            "results": results,
            "total_results": response.total_results
        }
        
        # Add optional fields if present
        if response.answer:
            response_dict["answer"] = response.answer
        if response.follow_up_questions:
            response_dict["follow_up_questions"] = response.follow_up_questions
        if response.search_time:
            response_dict["search_time"] = response.search_time
        
        logger.info(f"Web search completed successfully for query: {query}")
        return response_dict
        
    except ValueError as e:
        logger.error(f"Invalid search parameters: {str(e)}")
        return {
            "success": False,
            "query": query,
            "results": [],
            "total_results": 0,
            "error": f"Invalid parameters: {str(e)}"
        }
    
    except TavilyServiceError as e:
        logger.error(f"Tavily service error: {str(e)}")
        return {
            "success": False,
            "query": query,
            "results": [],
            "total_results": 0,
            "error": f"Search service error: {str(e)}"
        }
    
    except Exception as e:
        logger.error(f"Unexpected error in web search: {str(e)}")
        return {
            "success": False,
            "query": query,
            "results": [],
            "total_results": 0,
            "error": f"Unexpected error: {str(e)}"
        }


def get_search_context(query: str, max_results: int = 5) -> str:
    """Get search context as formatted text for RefinireAgent.
    
    This is a convenience function that returns search results as a formatted string,
    useful for providing context to language models.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to include (default: 5)
    
    Returns:
        Formatted search context string
    """
    try:
        service = TavilyService()
        return service.get_search_context(query, max_results)
    except Exception as e:
        logger.error(f"Failed to get search context: {str(e)}")
        return f"Search failed: {str(e)}"