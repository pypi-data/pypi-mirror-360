"""Tests for data models."""

import pytest
from pydantic import ValidationError
from src.refinire_tool_tavily.models import SearchRequest, SearchResponse, SearchResult


class TestSearchRequest:
    """Test cases for SearchRequest model."""
    
    def test_valid_search_request(self):
        """Test creating a valid search request."""
        request = SearchRequest(query="test query")
        assert request.query == "test query"
        assert request.max_results == 5
        assert request.include_domains is None
        assert request.exclude_domains is None
        assert request.include_answer is False
        assert request.include_raw_content is False
    
    def test_search_request_with_parameters(self):
        """Test creating search request with all parameters."""
        request = SearchRequest(
            query="python programming",
            max_results=10,
            include_domains=["python.org", "docs.python.org"],
            exclude_domains=["spam.com"],
            include_answer=True,
            include_raw_content=True
        )
        assert request.query == "python programming"
        assert request.max_results == 10
        assert request.include_domains == ["python.org", "docs.python.org"]
        assert request.exclude_domains == ["spam.com"]
        assert request.include_answer is True
        assert request.include_raw_content is True
    
    def test_empty_query_validation(self):
        """Test that empty query raises validation error."""
        with pytest.raises(ValidationError):
            SearchRequest(query="")
    
    def test_whitespace_query_validation(self):
        """Test that whitespace-only query raises validation error."""
        with pytest.raises(ValidationError):
            SearchRequest(query="   ")
    
    def test_dangerous_characters_validation(self):
        """Test that dangerous characters in query raise validation error."""
        dangerous_queries = [
            "test<script>",
            "test & malicious",
            'test"injection',
            "test'injection",
            "test>redirect",
            "test;command"
        ]
        
        for query in dangerous_queries:
            with pytest.raises(ValidationError):
                SearchRequest(query=query)
    
    def test_max_results_validation(self):
        """Test max_results validation."""
        with pytest.raises(ValidationError):
            SearchRequest(query="test", max_results=0)
        
        with pytest.raises(ValidationError):
            SearchRequest(query="test", max_results=21)
        
        # Valid values should work
        request = SearchRequest(query="test", max_results=1)
        assert request.max_results == 1
        
        request = SearchRequest(query="test", max_results=20)
        assert request.max_results == 20


class TestSearchResult:
    """Test cases for SearchResult model."""
    
    def test_valid_search_result(self):
        """Test creating a valid search result."""
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            content="Test content"
        )
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.content == "Test content"
        assert result.score is None
        assert result.raw_content is None
    
    def test_search_result_with_optional_fields(self):
        """Test creating search result with optional fields."""
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            content="Test content",
            score=0.95,
            raw_content="Raw content here"
        )
        assert result.score == 0.95
        assert result.raw_content == "Raw content here"


class TestSearchResponse:
    """Test cases for SearchResponse model."""
    
    def test_valid_search_response(self):
        """Test creating a valid search response."""
        results = [
            SearchResult(
                title="Test Title",
                url="https://example.com",
                content="Test content"
            )
        ]
        
        response = SearchResponse(
            query="test query",
            results=results,
            total_results=1
        )
        assert response.query == "test query"
        assert len(response.results) == 1
        assert response.total_results == 1
        assert response.answer is None
        assert response.follow_up_questions is None
        assert response.search_time is None
    
    def test_search_response_with_optional_fields(self):
        """Test creating search response with optional fields."""
        results = [
            SearchResult(
                title="Test Title",
                url="https://example.com",
                content="Test content"
            )
        ]
        
        response = SearchResponse(
            query="test query",
            results=results,
            total_results=1,
            answer="AI generated answer",
            follow_up_questions=["Question 1", "Question 2"],
            search_time=0.5
        )
        assert response.answer == "AI generated answer"
        assert response.follow_up_questions == ["Question 1", "Question 2"]
        assert response.search_time == 0.5