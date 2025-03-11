"""
Financial Data Tool for DeepThinkingChain.

This module contains tools for fetching financial data from external APIs.
"""

import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from tools.tool import Tool

# Load environment variables
load_dotenv()

class FinancialDataTool(Tool):
    """Base class for financial data tools."""
    
    category = "financial_data"
    
    def __init__(self):
        """Initialize the financial data tool."""
        self.api_key = os.getenv("FMP_API_KEY")
        if not self.api_key:
            print("Warning: FMP_API_KEY environment variable not set.")
        super().__init__()
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the Financial Modeling Prep API.
        
        Args:
            endpoint: The API endpoint to request
            params: Additional parameters for the request
            
        Returns:
            Dict[str, Any]: The JSON response from the API
        """
        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/{endpoint}"
        
        # Add API key to parameters
        if params is None:
            params = {}
        params["apikey"] = self.api_key
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return {"error": str(e)}


class CompanyProfileTool(FinancialDataTool):
    """Tool for fetching company profile data."""
    
    name = "company_profile"
    description = "Fetches basic company information including name, description, sector, industry, market cap, and current price."
    inputs = {
        "symbol": {
            "type": "str",
            "description": "The stock symbol to fetch data for (e.g., 'AAPL')",
            "required": True
        }
    }
    output_type = "dict"
    capabilities = "Retrieves company profile information from Financial Modeling Prep API."
    
    def forward(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch company profile data for a given stock symbol.
        
        Args:
            symbol: The stock symbol to fetch data for
            
        Returns:
            Dict[str, Any]: Company profile data
        """
        endpoint = f"profile/{symbol}"
        response = self._make_request(endpoint)
        
        if isinstance(response, list) and len(response) > 0:
            return response[0]
        return {"error": "No data found", "symbol": symbol}


class FinancialRatiosTool(FinancialDataTool):
    """Tool for fetching financial ratios data."""
    
    name = "financial_ratios"
    description = "Retrieves financial ratios data for deeper financial insights."
    inputs = {
        "symbol": {
            "type": "str",
            "description": "The stock symbol to fetch data for (e.g., 'AAPL')",
            "required": True
        },
        "period": {
            "type": "str",
            "description": "The period to fetch data for ('annual' or 'quarter')",
            "required": False
        },
        "limit": {
            "type": "int",
            "description": "The number of periods to fetch",
            "required": False
        }
    }
    output_type = "dict"
    capabilities = "Retrieves financial ratios from Financial Modeling Prep API."
    
    def forward(self, symbol: str, period: str = "annual", limit: int = 1) -> Dict[str, Any]:
        """
        Fetch financial ratios data for a given stock symbol.
        
        Args:
            symbol: The stock symbol to fetch data for
            period: The period to fetch data for ('annual' or 'quarter')
            limit: The number of periods to fetch
            
        Returns:
            Dict[str, Any]: Financial ratios data
        """
        endpoint = f"ratios/{symbol}"
        params = {"period": period, "limit": limit}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list) and len(response) > 0:
            return {"symbol": symbol, "ratios": response}
        return {"error": "No data found", "symbol": symbol}


class IncomeStatementTool(FinancialDataTool):
    """Tool for fetching income statement data."""
    
    name = "income_statement"
    description = "Retrieves income statement data for financial analysis."
    inputs = {
        "symbol": {
            "type": "str",
            "description": "The stock symbol to fetch data for (e.g., 'AAPL')",
            "required": True
        },
        "period": {
            "type": "str",
            "description": "The period to fetch data for ('annual' or 'quarter')",
            "required": False
        },
        "limit": {
            "type": "int",
            "description": "The number of periods to fetch",
            "required": False
        }
    }
    output_type = "dict"
    capabilities = "Retrieves income statement data from Financial Modeling Prep API."
    
    def forward(self, symbol: str, period: str = "annual", limit: int = 1) -> Dict[str, Any]:
        """
        Fetch income statement data for a given stock symbol.
        
        Args:
            symbol: The stock symbol to fetch data for
            period: The period to fetch data for ('annual' or 'quarter')
            limit: The number of periods to fetch
            
        Returns:
            Dict[str, Any]: Income statement data
        """
        endpoint = f"income-statement/{symbol}"
        params = {"period": period, "limit": limit}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list) and len(response) > 0:
            return {"symbol": symbol, "income_statement": response}
        return {"error": "No data found", "symbol": symbol}


def main():
    """Example usage of the financial data tools."""
    from tools.tool_manager import ToolManager
    
    # Create a tool manager
    manager = ToolManager()
    
    # Add financial data tools
    manager.add_tool(CompanyProfileTool())
    manager.add_tool(FinancialRatiosTool())
    manager.add_tool(IncomeStatementTool())
    
    # Set default tool for financial_data category
    manager.set_default_tool("financial_data", "company_profile")
    
    # Print available tools
    print(manager.get_tools_prompt())
    
    # Check if API key is set
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("FMP_API_KEY environment variable not set. Cannot run example.")
        return
    
    # Use the company profile tool
    company_profile_tool = manager.get_tool_by_name("company_profile")
    if company_profile_tool:
        result = company_profile_tool(symbol="AAPL")
        print(f"\nCompany Profile for AAPL:")
        print(f"Name: {result.get('companyName')}")
        print(f"Industry: {result.get('industry')}")
        print(f"Market Cap: ${result.get('mktCap'):,}")
        print(f"Current Price: ${result.get('price')}")


if __name__ == "__main__":
    main() 