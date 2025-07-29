"""Tests for API functions."""

import pytest
from unittest.mock import Mock, patch
from src.refinire_tool_tavily.api import search_web, get_search_context
from src.refinire_tool_tavily.models import SearchResponse, SearchResult
from src.refinire_tool_tavily.service import TavilyServiceError


class TestSearchWeb:
    """Test cases for search_web function."""
    
    @patch('src.refinire_tool_tavily.api.TavilyService')
    def test_successful_search(self, mock_service_class):
        """Test successful web search."""
        # Mock service response
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_response = SearchResponse(
            query="test query",
            results=[
                SearchResult(
                    title="Test Title",
                    url="https://example.com",
                    content="Test content",
                    score=0.95
                )
            ],
            total_results=1,
            search_time=0.5
        )
        mock_service.search.return_value = mock_response
        
        # Execute search
        result = search_web("test query", max_results=5)
        
        # Verify result
        assert result["success"] is True
        assert result["query"] == "test query"
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Test Title"
        assert result["results"][0]["url"] == "https://example.com"
        assert result["results"][0]["content"] == "Test content"
        assert result["results"][0]["score"] == 0.95
        assert result["total_results"] == 1
        assert result["search_time"] == 0.5
    
    @patch('src.refinire_tool_tavily.api.TavilyService')
    def test_search_with_answer(self, mock_service_class):
        """Test search with AI-generated answer."""
        # Mock service response
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_response = SearchResponse(
            query="test query",
            results=[],
            total_results=0,
            answer="AI generated answer",
            follow_up_questions=["Question 1", "Question 2"]
        )
        mock_service.search.return_value = mock_response
        
        # Execute search
        result = search_web("test query", include_answer=True)
        
        # Verify result
        assert result["success"] is True
        assert result["answer"] == "AI generated answer"
        assert result["follow_up_questions"] == ["Question 1", "Question 2"]
    
    def test_invalid_query_validation(self):
        """Test validation of invalid query."""
        result = search_web("")
        
        assert result["success"] is False
        assert "Invalid parameters" in result["error"]
        assert result["total_results"] == 0
        assert len(result["results"]) == 0
    
    def test_dangerous_query_validation(self):
        """Test validation of dangerous query characters."""
        result = search_web("test<script>alert('xss')</script>")
        
        assert result["success"] is False
        assert "Invalid parameters" in result["error"]
        assert result["total_results"] == 0
        assert len(result["results"]) == 0
    
    @patch('src.refinire_tool_tavily.api.TavilyService')
    def test_service_error_handling(self, mock_service_class):
        """Test handling of service errors."""
        # Mock service to raise error
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.search.side_effect = TavilyServiceError("API key invalid")
        
        # Execute search
        result = search_web("test query")
        
        # Verify error handling
        assert result["success"] is False
        assert "Search service error" in result["error"]
        assert "API key invalid" in result["error"]
        assert result["total_results"] == 0
        assert len(result["results"]) == 0
    
    @patch('src.refinire_tool_tavily.api.TavilyService')
    def test_unexpected_error_handling(self, mock_service_class):
        """Test handling of unexpected errors."""
        # Mock service to raise unexpected error
        mock_service_class.side_effect = Exception("Unexpected error")
        
        # Execute search
        result = search_web("test query")
        
        # Verify error handling
        assert result["success"] is False
        assert "Unexpected error" in result["error"]
        assert result["total_results"] == 0
        assert len(result["results"]) == 0


class TestGetSearchContext:
    """Test cases for get_search_context function."""
    
    @patch('src.refinire_tool_tavily.api.TavilyService')
    def test_successful_context_retrieval(self, mock_service_class):
        """Test successful context retrieval."""
        # Mock service
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_search_context.return_value = "Formatted search context"
        
        # Execute function
        result = get_search_context("test query", max_results=3)
        
        # Verify result
        assert result == "Formatted search context"
        mock_service.get_search_context.assert_called_once_with("test query", 3)
    
    @patch('src.refinire_tool_tavily.api.TavilyService')
    def test_context_error_handling(self, mock_service_class):
        """Test error handling in context retrieval."""
        # Mock service to raise error
        mock_service_class.side_effect = Exception("Service error")
        
        # Execute function
        result = get_search_context("test query")
        
        # Verify error handling
        assert "Search failed" in result
        assert "Service error" in result