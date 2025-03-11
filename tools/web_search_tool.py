"""
Web Search Tools for DeepThinkingChain.

This module contains tools for searching the web.
"""

import os
import requests
import json
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import quote_plus

from tools.tool import Tool

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WebSearchTool(Tool):
    """Base class for web search tools."""
    
    category = "web_search"
    
    def __init__(self, max_results: int = 10):
        """
        Initialize the web search tool.
        
        Args:
            max_results: Maximum number of results to return
        """
        self.max_results = max_results
        super().__init__()


class GoogleSearchTool(WebSearchTool):
    """Tool for searching the web using ScrapingDog's Google Search API."""
    
    name = "google_search"
    description = "Performs a Google web search for your query and returns a string of the top search results."
    inputs = {
        "query": {
            "type": "str",
            "description": "The search query to perform",
            "required": True
        },
        "filter_year": {
            "type": "int",
            "description": "Optionally restrict results to a certain year",
            "required": False
        }
    }
    output_type = "str"
    capabilities = "Searches the web using ScrapingDog's Google Search API and returns relevant results."
    
    def __init__(self, max_results: int = 10):
        """
        Initialize the Google search tool.
        
        Args:
            max_results: Maximum number of results to return
        """
        # Check both environment variable names
        self.api_key = os.environ.get("SCRAPING_DOG_API_KEY") or os.environ.get("SCRAPINGDOG_API_KEY") or os.getenv("SCRAPING_DOG_API_KEY") or os.getenv("SCRAPINGDOG_API_KEY")
        
        if not self.api_key:
            logger.warning("Neither SCRAPING_DOG_API_KEY nor SCRAPINGDOG_API_KEY environment variable is set. Google search will be limited.")
        
        super().__init__(max_results=max_results)
    
    def forward(self, query: str, filter_year: Optional[int] = None) -> str:
        """
        Perform a Google search using ScrapingDog API.
        
        Args:
            query: The search query to perform
            filter_year: Optionally restrict results to a certain year
            
        Returns:
            str: The search results as a formatted string
        """
        if not self.api_key:
            return "Error: ScrapingDog API key not set. Please set either SCRAPING_DOG_API_KEY or SCRAPINGDOG_API_KEY environment variable."
        
        try:
            # Construct the search query
            search_query = query
            if filter_year:
                search_query += f" {filter_year}"
            
            # Construct the API URL for ScrapingDog's Google search
            url = "https://api.scrapingdog.com/google/"
            params = {
                "api_key": self.api_key,
                "query": search_query,
                "results": min(self.max_results, 10),  # Limit to 10 results per request
                "country": "us",
                "page": 0
            }
            
            # Make the request
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Check if there are search results
            if "organic_results" not in data or len(data["organic_results"]) == 0:
                year_filter_message = f" with filter year={filter_year}" if filter_year is not None else ""
                return f"No results found for '{query}'{year_filter_message}. Try with a more general query, or remove the year filter."
            
            # Format the results
            results = []
            
            # Add "People Also Asked" section if available
            if "peopleAlsoAskedFor" in data and data["peopleAlsoAskedFor"]:
                results.append("## People Also Asked")
                for question in data["peopleAlsoAskedFor"]:
                    results.append(f"### {question.get('question', 'Question')}")
                    results.append(f"[{question.get('title', 'No title')}]({question.get('link', '#')})")
                    if question.get("answers"):
                        results.append(question["answers"])
                    results.append("")  # Add an empty line for readability
            
            # Add organic results
            results.append("## Search Results")
            for i, item in enumerate(data["organic_results"], 1):
                title = item.get("title", "No title")
                link = item.get("link", "No link")
                snippet = item.get("snippet", "No description")
                displayed_link = item.get("displayed_link", "")
                
                results.append(f"{i}. {title}")
                results.append(f"   URL: {link}")
                results.append(f"   Site: {displayed_link}")
                results.append(f"   Description: {snippet}")
                results.append("")  # Add an empty line for readability
            
            # Join the results
            return "\n".join(results)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error performing Google search: {str(e)}")
            return f"Error performing Google search: {str(e)}"
        except Exception as e:
            logger.error(f"Error processing Google search results: {str(e)}")
            return f"Error processing Google search results: {str(e)}"


class DuckDuckGoSearchTool(WebSearchTool):
    """Tool for searching the web using DuckDuckGo."""
    
    name = "duckduckgo_search"
    description = "Performs a DuckDuckGo web search based on your query and returns the top search results."
    inputs = {
        "query": {
            "type": "str",
            "description": "The search query to perform",
            "required": True
        }
    }
    output_type = "str"
    capabilities = "Searches the web using DuckDuckGo and returns relevant results."
    
    def __init__(self, max_results: int = 10):
        """
        Initialize the DuckDuckGo search tool.
        
        Args:
            max_results: Maximum number of results to return
        """
        super().__init__(max_results=max_results)
    
    def forward(self, query: str) -> str:
        """
        Perform a DuckDuckGo search.
        
        Args:
            query: The search query to perform
            
        Returns:
            str: The search results as a formatted string
        """
        try:
            # DuckDuckGo doesn't have an official API, so we'll use their search JSON endpoint
            url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json"
            
            # Make the request
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Format the results
            results = []
            
            # Add abstract if available
            if data.get("Abstract"):
                results.append(f"Abstract: {data['Abstract']}\n")
            
            # Add related topics
            if data.get("RelatedTopics"):
                count = 0
                for i, topic in enumerate(data["RelatedTopics"], 1):
                    if count >= self.max_results:
                        break
                    
                    if "Text" in topic and "FirstURL" in topic:
                        text = topic["Text"]
                        url = topic["FirstURL"]
                        results.append(f"{i}. {text}\n   URL: {url}\n")
                        count += 1
            
            if not results:
                return f"No results found for query: {query}"
            
            # Join the results
            return "\n".join(results)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error performing DuckDuckGo search: {str(e)}")
            return f"Error performing DuckDuckGo search: {str(e)}"
        except Exception as e:
            logger.error(f"Error processing DuckDuckGo search results: {str(e)}")
            return f"Error processing DuckDuckGo search results: {str(e)}"


class NewsSearchTool(WebSearchTool):
    """Tool for searching news articles."""
    
    name = "news_search"
    description = "Searches for news articles related to your query."
    inputs = {
        "query": {
            "type": "str",
            "description": "The search query to perform",
            "required": True
        },
        "days": {
            "type": "int",
            "description": "Number of days to look back for news",
            "required": False
        }
    }
    output_type = "str"
    capabilities = "Searches for recent news articles using the NewsAPI."
    
    def __init__(self, max_results: int = 10):
        """
        Initialize the news search tool.
        
        Args:
            max_results: Maximum number of results to return
        """
        self.api_key = os.getenv("NEWS_API_KEY")
        
        if not self.api_key:
            logger.warning("NEWS_API_KEY environment variable not set. News search will be limited.")
        
        super().__init__(max_results=max_results)
    
    def forward(self, query: str, days: int = 7) -> str:
        """
        Search for news articles.
        
        Args:
            query: The search query to perform
            days: Number of days to look back for news
            
        Returns:
            str: The search results as a formatted string
        """
        if not self.api_key:
            return "Error: News API key not set. Please set the NEWS_API_KEY environment variable."
        
        try:
            # Construct the API URL
            url = "https://newsapi.org/v2/everything"
            
            # Calculate the date range
            from datetime import datetime, timedelta
            to_date = datetime.now().strftime("%Y-%m-%d")
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            params = {
                "apiKey": self.api_key,
                "q": query,
                "from": from_date,
                "to": to_date,
                "language": "en",
                "sortBy": "relevancy",
                "pageSize": self.max_results
            }
            
            # Make the request
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Check if there are search results
            if data.get("status") != "ok" or "articles" not in data:
                return f"No news results found for query: {query}"
            
            # Format the results
            results = []
            for i, article in enumerate(data["articles"], 1):
                title = article.get("title", "No title")
                source = article.get("source", {}).get("name", "Unknown source")
                url = article.get("url", "No URL")
                published_at = article.get("publishedAt", "Unknown date")
                description = article.get("description", "No description")
                
                results.append(f"{i}. {title} ({source})\n   Published: {published_at}\n   URL: {url}\n   Description: {description}\n")
            
            # Join the results
            return "\n".join(results)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error performing news search: {str(e)}")
            return f"Error performing news search: {str(e)}"
        except Exception as e:
            logger.error(f"Error processing news search results: {str(e)}")
            return f"Error processing news search results: {str(e)}"


def main():
    """Example usage of the web search tools."""
    # Create a Google search tool
    google_search = GoogleSearchTool()
    
    # Test the tool with a simple query
    query = "NVIDIA stock performance 2023"
    print(f"Searching Google for '{query}'...")
    if os.getenv("SCRAPING_DOG_API_KEY"):
        results = google_search(query=query)
        print(results)
    else:
        print("SCRAPING_DOG_API_KEY not set. Skipping Google search test.")
    
    # Create a DuckDuckGo search tool
    duckduckgo_search = DuckDuckGoSearchTool()
    
    # Test the tool with a simple query
    print(f"\nSearching DuckDuckGo for '{query}'...")
    results = duckduckgo_search(query=query)
    print(results)
    
    # Create a news search tool
    news_search = NewsSearchTool()
    
    # Test the tool with a simple query
    print(f"\nSearching news for '{query}'...")
    if os.getenv("NEWS_API_KEY"):
        results = news_search(query=query, days=30)
        print(results)
    else:
        print("NEWS_API_KEY not set. Skipping news search test.")


if __name__ == "__main__":
    main() 