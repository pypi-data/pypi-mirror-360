"""Web search tool implementation."""

import asyncio
import json
from typing import Any, Dict, List, Optional

import aiohttp
from pydantic import BaseModel

from .base import BaseTool, ToolParameter, ToolResult
from ..utils.exceptions import ToolError


class SearchResult(BaseModel):
    """Web search result."""
    
    title: str
    url: str
    snippet: str
    rank: int


class WebSearchTool(BaseTool):
    """Tool for web search functionality."""
    
    def __init__(
        self,
        search_engine: str = "duckduckgo",
        max_results: int = 10,
        **kwargs
    ):
        self.search_engine = search_engine
        self.max_results = max_results
        
        parameters = [
            ToolParameter(
                name="query",
                type="string",
                description="Search query to execute",
                required=True
            ),
            ToolParameter(
                name="num_results",
                type="integer",
                description="Number of results to return",
                required=False,
                default=5
            ),
            ToolParameter(
                name="safe_search",
                type="boolean",
                description="Enable safe search",
                required=False,
                default=True
            )
        ]
        
        super().__init__(
            name="web_search",
            description="Search the web for information using various search engines",
            parameters=parameters,
            **kwargs
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute web search."""
        query = kwargs["query"]
        num_results = min(kwargs.get("num_results", 5), self.max_results)
        safe_search = kwargs.get("safe_search", True)
        
        try:
            if self.search_engine == "duckduckgo":
                results = await self._search_duckduckgo(query, num_results, safe_search)
            elif self.search_engine == "google":
                results = await self._search_google(query, num_results, safe_search)
            else:
                raise ToolError(f"Unsupported search engine: {self.search_engine}")
            
            return ToolResult(
                success=True,
                result={
                    "query": query,
                    "results": [result.dict() for result in results],
                    "total_results": len(results)
                },
                metadata={
                    "search_engine": self.search_engine,
                    "safe_search": safe_search
                },
                execution_time=0.0  # Will be set by base class
            )
            
        except Exception as e:
            raise ToolError(f"Web search failed: {e}")
    
    async def _search_duckduckgo(
        self,
        query: str,
        num_results: int,
        safe_search: bool
    ) -> List[SearchResult]:
        """Search using DuckDuckGo."""
        try:
            # Use duckduckgo-search library if available
            try:
                from duckduckgo_search import AsyncDDGS
                
                async with AsyncDDGS() as ddgs:
                    results = []
                    search_results = ddgs.text(
                        query,
                        max_results=num_results,
                        safesearch="on" if safe_search else "off"
                    )
                    
                    async for i, result in enumerate(search_results):
                        if i >= num_results:
                            break
                        
                        results.append(SearchResult(
                            title=result.get("title", ""),
                            url=result.get("href", ""),
                            snippet=result.get("body", ""),
                            rank=i + 1
                        ))
                    
                    return results
                    
            except ImportError:
                # Fallback to direct API call
                return await self._search_duckduckgo_api(query, num_results, safe_search)
                
        except Exception as e:
            raise ToolError(f"DuckDuckGo search failed: {e}")
    
    async def _search_duckduckgo_api(
        self,
        query: str,
        num_results: int,
        safe_search: bool
    ) -> List[SearchResult]:
        """Search using DuckDuckGo API directly."""
        try:
            async with aiohttp.ClientSession() as session:
                # First, get the vqd token
                params = {
                    "q": query,
                    "format": "json",
                    "no_redirect": "1",
                    "no_html": "1",
                    "skip_disambig": "1"
                }
                
                async with session.get(
                    "https://api.duckduckgo.com/",
                    params=params
                ) as response:
                    data = await response.json()
                
                # Extract results (DuckDuckGo instant answers)
                results = []
                
                # Add abstract if available
                if data.get("Abstract"):
                    results.append(SearchResult(
                        title=data.get("Heading", query),
                        url=data.get("AbstractURL", ""),
                        snippet=data.get("Abstract", ""),
                        rank=1
                    ))
                
                # Add related topics
                for i, topic in enumerate(data.get("RelatedTopics", [])[:num_results-len(results)]):
                    if isinstance(topic, dict) and "Text" in topic:
                        results.append(SearchResult(
                            title=topic.get("Text", "").split(" - ")[0],
                            url=topic.get("FirstURL", ""),
                            snippet=topic.get("Text", ""),
                            rank=len(results) + 1
                        ))
                
                return results[:num_results]
                
        except Exception as e:
            raise ToolError(f"DuckDuckGo API search failed: {e}")
    
    async def _search_google(
        self,
        query: str,
        num_results: int,
        safe_search: bool
    ) -> List[SearchResult]:
        """Search using Google Custom Search API."""
        try:
            import os
            
            api_key = os.getenv("GOOGLE_API_KEY")
            search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            
            if not api_key or not search_engine_id:
                raise ToolError(
                    "Google search requires GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables"
                )
            
            async with aiohttp.ClientSession() as session:
                params = {
                    "key": api_key,
                    "cx": search_engine_id,
                    "q": query,
                    "num": num_results,
                    "safe": "active" if safe_search else "off"
                }
                
                async with session.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params=params
                ) as response:
                    data = await response.json()
                
                if "error" in data:
                    raise ToolError(f"Google API error: {data['error']['message']}")
                
                results = []
                for i, item in enumerate(data.get("items", [])):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        rank=i + 1
                    ))
                
                return results
                
        except Exception as e:
            raise ToolError(f"Google search failed: {e}")


class WebScrapeTool(BaseTool):
    """Tool for web scraping functionality."""
    
    def __init__(self, **kwargs):
        parameters = [
            ToolParameter(
                name="url",
                type="string",
                description="URL to scrape",
                required=True
            ),
            ToolParameter(
                name="selector",
                type="string",
                description="CSS selector to extract specific content",
                required=False,
                default=None
            ),
            ToolParameter(
                name="max_length",
                type="integer",
                description="Maximum length of extracted text",
                required=False,
                default=5000
            )
        ]
        
        super().__init__(
            name="web_scrape",
            description="Scrape content from web pages",
            parameters=parameters,
            **kwargs
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute web scraping."""
        url = kwargs["url"]
        selector = kwargs.get("selector")
        max_length = kwargs.get("max_length", 5000)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise ToolError(f"HTTP {response.status}: Failed to fetch {url}")
                    
                    html_content = await response.text()
            
            # Parse HTML content
            try:
                from bs4 import BeautifulSoup
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                if selector:
                    # Extract specific content using CSS selector
                    elements = soup.select(selector)
                    content = "\n".join([elem.get_text(strip=True) for elem in elements])
                else:
                    # Extract all text content
                    content = soup.get_text(separator='\n', strip=True)
                
                # Limit content length
                if len(content) > max_length:
                    content = content[:max_length] + "..."
                
                return ToolResult(
                    success=True,
                    result={
                        "url": url,
                        "content": content,
                        "length": len(content),
                        "title": soup.title.string if soup.title else ""
                    },
                    metadata={
                        "selector": selector,
                        "max_length": max_length
                    },
                    execution_time=0.0
                )
                
            except ImportError:
                raise ToolError("beautifulsoup4 not installed. Install with: pip install beautifulsoup4")
                
        except Exception as e:
            raise ToolError(f"Web scraping failed: {e}")
