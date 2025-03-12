#!/usr/bin/env python3
"""
Script to register all tools with the tool manager.
"""

from tools.tool_manager import ToolManager
from tools.financial_data_tool import FinancialDataTool
from tools.web_search_tool import (
    GoogleSearchTool,
    DuckDuckGoSearchTool,
)
from tools.web_scraping_tool import (
    WebScrapingTool,
    AdvancedWebScrapingTool
)
from tools.stock_valuation_tool import StockValuationTool

def register_tools():
    """Register all tools with the tool manager."""
    # Create a tool manager
    manager = ToolManager()
    
    # Add the consolidated financial data tool
    manager.add_tool(FinancialDataTool())
    
    # Add web search tools
    manager.add_tool(GoogleSearchTool())
    manager.add_tool(DuckDuckGoSearchTool())
    manager.add_tool(WebScrapingTool())
    manager.add_tool(AdvancedWebScrapingTool())
    
    # Add stock valuation tool
    manager.add_tool(StockValuationTool())
    
    # Set default tool for financial_data category
    manager.set_default_tool("financial_data", "financial_data")
    
    # Set default tool for web_search category
    manager.set_default_tool("web_search", "google_search")
    manager.set_default_tool("web_browser", "advanced_web_scraper")
    
    # Set default tool for financial_analysis category
    manager.set_default_tool("financial_analysis", "stock_valuation")
    
    return manager

if __name__ == "__main__":
    # Register tools
    manager = register_tools()
    
    # Print available tools
    print(manager.get_tools_prompt()) 