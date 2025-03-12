#!/usr/bin/env python3
"""
Test script for the ToolAgent to test web search tools.
"""

import json
import os
from agents.tool_agent import ToolAgent

def print_section(title):
    """Print a section title with formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def main():
    """Main function to test the ToolAgent with web search tools."""
    # Initialize the tool agent
    print_section("Initializing Tool Agent")
    agent = ToolAgent()
    
    # Display available tools
    print_section("Available Tools")
    print(agent.get_tools_prompt())
    
    # Test DuckDuckGo search
    print_section("DuckDuckGo Search")
    query = "NVIDIA AI technology 2023"
    print(f"Searching for: '{query}'")
    result = agent.execute_tool("duckduckgo_search", query=query)
    print(result)
    
    # Test Google search if API key is available
    if os.getenv("SCRAPING_DOG_API_KEY") or os.getenv("SCRAPINGDOG_API_KEY"):
        print_section("Google Search")
        query = "NVIDIA stock performance 2023"
        print(f"Searching for: '{query}'")
        result = agent.execute_tool("google_search", query=query)
        print(result)
    else:
        print_section("Google Search")
        print("Skipping Google search test because SCRAPING_DOG_API_KEY is not set.")
    
    # Test News search if API key is available
    if os.getenv("NEWS_API_KEY"):
        print_section("News Search")
        query = "NVIDIA AI chips"
        print(f"Searching for news about: '{query}'")
        result = agent.execute_tool("news_search", query=query, days=30)
        print(result)
    else:
        print_section("News Search")
        print("Skipping News search test because NEWS_API_KEY is not set.")
    
    # Test stock search
    print_section("Stock Search")
    query = "NVIDIA"
    print(f"Searching for stock: '{query}'")
    result = agent.execute_tool("stock_search", query=query)
    
    # Print only the first 3 results to keep output manageable
    if isinstance(result, dict) and "results" in result and isinstance(result["results"], list):
        limited_results = result.copy()
        limited_results["results"] = result["results"][:3]
        print(json.dumps(limited_results, indent=2))
    else:
        print(json.dumps(result, indent=2))
    
    # Test stock browse
    print_section("Stock Browse")
    category = "industry"
    value = "Semiconductors"
    print(f"Browsing stocks in {category}: '{value}'")
    result = agent.execute_tool("stock_browse", category=category, value=value, limit=3)
    print(json.dumps(result, indent=2))
    
    # Test market news
    print_section("Market News")
    symbol = "NVDA"
    print(f"Getting news for: '{symbol}'")
    result = agent.execute_tool("market_news", symbol=symbol, limit=3)
    
    # Print only the first 3 news items to keep output manageable
    if isinstance(result, dict) and "news" in result and isinstance(result["news"], list):
        limited_results = result.copy()
        limited_results["news"] = result["news"][:3]
        print(json.dumps(limited_results, indent=2))
    else:
        print(json.dumps(result, indent=2))
    
    print_section("Test Complete")
    print("The tool agent successfully tested web search and browse tools.")

if __name__ == "__main__":
    main() 