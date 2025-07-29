"""Data models for Tavily search functionality."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """Search request parameters."""
    
    query: str = Field(..., description="Search query string", min_length=1)
    max_results: int = Field(default=5, description="Maximum number of results to return", ge=1, le=20)
    include_domains: Optional[List[str]] = Field(default=None, description="List of domains to include in search")
    exclude_domains: Optional[List[str]] = Field(default=None, description="List of domains to exclude from search")
    include_answer: bool = Field(default=False, description="Include AI-generated answer in response")
    include_raw_content: bool = Field(default=False, description="Include raw content of web pages")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        """Validate search query for security."""
        if not v.strip():
            raise ValueError("Search query cannot be empty")
        
        # Basic security check - prevent potential injection
        dangerous_chars = ['<', '>', '"', "'", '&', ';']
        if any(char in v for char in dangerous_chars):
            raise ValueError("Search query contains potentially dangerous characters")
        
        return v.strip()


class SearchResult(BaseModel):
    """Individual search result."""
    
    title: str = Field(..., description="Title of the web page")
    url: str = Field(..., description="URL of the web page")
    content: str = Field(..., description="Content snippet from the web page")
    score: Optional[float] = Field(default=None, description="Relevance score")
    raw_content: Optional[str] = Field(default=None, description="Raw content of the web page")


class SearchResponse(BaseModel):
    """Search response containing results and metadata."""
    
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="List of search results")
    answer: Optional[str] = Field(default=None, description="AI-generated answer")
    follow_up_questions: Optional[List[str]] = Field(default=None, description="Suggested follow-up questions")
    total_results: int = Field(..., description="Total number of results found")
    search_time: Optional[float] = Field(default=None, description="Search execution time in seconds")