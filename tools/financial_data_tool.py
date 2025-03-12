"""
Financial Data Tool for DeepThinkingChain.

This module contains tools for fetching financial data from external APIs.
"""

import os
import requests
import numpy as np
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv

from tools.tool import Tool

# Load environment variables
load_dotenv()

class FinancialDataTool(Tool):
    """Consolidated tool for fetching various types of financial data."""
    
    name = "financial_data"
    description = "Fetches various types of financial data for a company."
    category = "financial_data"
    
    inputs = {
        "symbol": {
            "type": "str",
            "description": "The stock symbol to fetch data for (e.g., 'AAPL')",
            "required": True
        },
        "data_type": {
            "type": "str",
            "description": "Type of financial data to fetch (e.g., 'company_profile', 'income_statement', 'balance_sheet', etc.)",
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
    capabilities = "Retrieves various types of financial data from Financial Modeling Prep API."
    
    # Define valid data types and their descriptions
    DATA_TYPES = {
        "company_profile": "Basic company information including name, description, sector, industry, market cap, and current price",
        "financial_ratios": "Financial ratios data for deeper financial insights",
        "income_statement": "Income statement data for financial analysis",
        "balance_sheet": "Balance sheet data for financial analysis",
        "cash_flow": "Cash flow statement data for financial analysis",
        "peers": "Peer companies for a given stock symbol",
        "peer_ratios": "Financial ratios for a company and its peers",
        "market_share": "Market share data for a company (simulated)",
        "growth_estimates": "Growth estimates for a company",
        "analyst_recommendations": "Analyst recommendations for a company",
        "earnings_surprises": "Earnings surprises for a company",
        "sec_filings": "SEC filings for a company",
        "price_volatility": "Price volatility for a company",
        "financial_performance": "Comprehensive financial performance analysis for a company",
        "competitive_analysis": "Competitive analysis for a company",
        "growth_prospects": "Growth prospects analysis for a company",
        "risk_assessment": "Risk assessment for a company"
    }
    
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
    
    def get_company_profile(self, symbol: str) -> Dict[str, Any]:
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
    
    def get_financial_ratios(self, symbol: str, period: str = "annual", limit: int = 1) -> Dict[str, Any]:
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
    
    def get_income_statement(self, symbol: str, period: str = "annual", limit: int = 1) -> Dict[str, Any]:
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
    
    def get_balance_sheet(self, symbol: str, period: str = "annual", limit: int = 4) -> Dict[str, Any]:
        """
        Fetch balance sheet data for a given stock symbol.
        
        Args:
            symbol: The stock symbol to fetch data for
            period: The period to fetch data for ('annual' or 'quarter')
            limit: The number of periods to fetch
            
        Returns:
            Dict[str, Any]: Balance sheet data
        """
        endpoint = f"balance-sheet-statement/{symbol}"
        params = {"period": period, "limit": limit}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list):
            return {"symbol": symbol, "balance_sheet": response}
        return {"error": "No data found", "symbol": symbol}
    
    def get_cash_flow(self, symbol: str, period: str = "annual", limit: int = 4) -> Dict[str, Any]:
        """
        Fetch cash flow statement data for a given stock symbol.
        
        Args:
            symbol: The stock symbol to fetch data for
            period: The period to fetch data for ('annual' or 'quarter')
            limit: The number of periods to fetch
            
        Returns:
            Dict[str, Any]: Cash flow statement data
        """
        endpoint = f"cash-flow-statement/{symbol}"
        params = {"period": period, "limit": limit}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list):
            return {"symbol": symbol, "cash_flow": response}
        return {"error": "No data found", "symbol": symbol}
    
    def get_peers(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch peer companies for a given stock symbol.
        
        Args:
            symbol: The stock symbol to fetch peers for
            
        Returns:
            Dict[str, Any]: Peer companies data
        """
        endpoint = f"stock_peers"
        params = {"symbol": symbol}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list) and len(response) > 0:
            return {"symbol": symbol, "peers": response[0].get("peersList", [])}
        return {"error": "No data found", "symbol": symbol}
    
    def get_peer_ratios(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch financial ratios for a company and its peers.
        
        Args:
            symbol: The stock symbol to fetch data for
            
        Returns:
            Dict[str, Any]: Financial ratios for the company and its peers
        """
        # First get the peers
        peers_result = self.get_peers(symbol)
        
        if "error" in peers_result:
            return peers_result
        
        peers = peers_result.get("peers", [])
        
        # Limit to top 5 peers
        peers = peers[:5]
        
        # Add the original symbol
        symbols = [symbol] + peers
        
        # Fetch ratios for all symbols
        result = {"symbol": symbol, "peers": {}}
        
        for sym in symbols:
            ratios_result = self.get_financial_ratios(sym)
            if sym == symbol:
                result["ratios"] = ratios_result.get("ratios", {})
            else:
                result["peers"][sym] = ratios_result.get("ratios", {})
        
        return result
    
    def get_market_share(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch market share data for a given stock symbol (simulated).
        
        Args:
            symbol: The stock symbol to fetch data for
            
        Returns:
            Dict[str, Any]: Market share data
        """
        # Get company profile to determine industry
        profile = self.get_company_profile(symbol)
        
        if "error" in profile:
            return profile
        
        industry = profile.get("industry", "Unknown")
        
        # Get peers
        peers_result = self.get_peers(symbol)
        top_competitors = peers_result.get("peers", [])[:3]
        
        # This is simulated data - in a real implementation, this would come from a data source
        return {
            "symbol": symbol,
            "industry": industry,
            "market_share_percentage": 0.15,  # Simulated value
            "industry_rank": 3,  # Simulated value
            "top_competitors": top_competitors,
            "note": "This is simulated market share data for demonstration purposes."
        }
    
    def get_growth_estimates(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch growth estimates for a given stock symbol.
        
        Args:
            symbol: The stock symbol to fetch data for
            
        Returns:
            Dict[str, Any]: Growth estimates data
        """
        endpoint = f"analyst-estimates/{symbol}"
        params = {"period": "annual"}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list) and len(response) > 0:
            return {"symbol": symbol, "estimates": response}
        return {"error": "No data found", "symbol": symbol}
    
    def get_analyst_recommendations(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch analyst recommendations for a given stock symbol.
        
        Args:
            symbol: The stock symbol to fetch data for
            
        Returns:
            Dict[str, Any]: Analyst recommendations data
        """
        endpoint = f"analyst-stock-recommendations/{symbol}"
        response = self._make_request(endpoint)
        
        if isinstance(response, list):
            return {"symbol": symbol, "recommendations": response}
        return {"error": "No data found", "symbol": symbol}
    
    def get_earnings_surprises(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch earnings surprises for a given stock symbol.
        
        Args:
            symbol: The stock symbol to fetch data for
            
        Returns:
            Dict[str, Any]: Earnings surprises data
        """
        endpoint = f"earnings-surprises/{symbol}"
        response = self._make_request(endpoint)
        
        if isinstance(response, list):
            return {"symbol": symbol, "earnings_surprises": response}
        return {"error": "No data found", "symbol": symbol}
    
    def get_sec_filings(self, symbol: str, limit: int = 10) -> Dict[str, Any]:
        """
        Fetch SEC filings for a given stock symbol.
        
        Args:
            symbol: The stock symbol to fetch data for
            limit: The number of filings to fetch
            
        Returns:
            Dict[str, Any]: SEC filings data
        """
        endpoint = f"sec_filings/{symbol}"
        params = {"limit": limit}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list):
            return {"symbol": symbol, "filings": response}
        return {"error": "No data found", "symbol": symbol}
    
    def get_price_volatility(self, symbol: str) -> Dict[str, Any]:
        """
        Calculate price volatility for a given stock symbol.
        
        Args:
            symbol: The stock symbol to fetch data for
            
        Returns:
            Dict[str, Any]: Price volatility data
        """
        # Get historical price data
        endpoint = f"historical-price-full/{symbol}"
        params = {"timeseries": 365}  # Last year of data
        response = self._make_request(endpoint, params)
        
        if "historical" not in response:
            return {"error": "No historical data found", "symbol": symbol}
        
        # Calculate volatility (standard deviation of daily returns)
        historical_data = response["historical"]
        
        if len(historical_data) < 30:
            return {"error": "Insufficient historical data to calculate volatility", "symbol": symbol}
        
        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(historical_data)):
            today = historical_data[i]["close"]
            yesterday = historical_data[i-1]["close"]
            daily_return = (today - yesterday) / yesterday
            daily_returns.append(daily_return)
        
        # Calculate volatility (standard deviation of returns)
        volatility = np.std(daily_returns)
        annualized_volatility = volatility * np.sqrt(252)  # Annualize (252 trading days)
        
        return {
            "symbol": symbol,
            "daily_volatility": float(volatility),
            "annualized_volatility": float(annualized_volatility),
            "data_period": f"{historical_data[-1]['date']} to {historical_data[0]['date']}",
            "sample_size": len(historical_data)
        }
    
    def get_financial_performance(self, symbol: str) -> Dict[str, Any]:
        """
        Perform comprehensive financial performance analysis for a given stock symbol.
        
        Args:
            symbol: The stock symbol to analyze
            
        Returns:
            Dict[str, Any]: Comprehensive financial performance analysis
        """
        result = {"symbol": symbol}
        
        # Get company profile
        result["company_profile"] = self.get_company_profile(symbol)
        
        # Get financial ratios
        result["financial_ratios"] = self.get_financial_ratios(symbol)
        
        # Get income statement
        result["income_statement"] = self.get_income_statement(symbol, limit=2)
        
        # Get balance sheet
        result["balance_sheet"] = self.get_balance_sheet(symbol, limit=2)
        
        # Get cash flow
        result["cash_flow"] = self.get_cash_flow(symbol, limit=2)
        
        return result
    
    def get_competitive_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Perform competitive analysis for a given stock symbol.
        
        Args:
            symbol: The stock symbol to analyze
            
        Returns:
            Dict[str, Any]: Competitive analysis
        """
        result = {"symbol": symbol}
        
        # Get company profile
        result["company_profile"] = self.get_company_profile(symbol)
        
        # Get peers
        result["peers"] = self.get_peers(symbol)
        
        # Get peer ratios
        result["peer_ratios"] = self.get_peer_ratios(symbol)
        
        # Get market share
        result["market_share"] = self.get_market_share(symbol)
        
        return result
    
    def get_growth_prospects(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze growth prospects for a given stock symbol.
        
        Args:
            symbol: The stock symbol to analyze
            
        Returns:
            Dict[str, Any]: Growth prospects analysis
        """
        result = {"symbol": symbol}
        
        # Get company profile
        result["company_profile"] = self.get_company_profile(symbol)
        
        # Get growth estimates
        result["growth_estimates"] = self.get_growth_estimates(symbol)
        
        # Get analyst recommendations
        result["analyst_recommendations"] = self.get_analyst_recommendations(symbol)
        
        # Get earnings surprises
        result["earnings_surprises"] = self.get_earnings_surprises(symbol)
        
        return result
    
    def get_risk_assessment(self, symbol: str) -> Dict[str, Any]:
        """
        Perform risk assessment for a given stock symbol.
        
        Args:
            symbol: The stock symbol to analyze
            
        Returns:
            Dict[str, Any]: Risk assessment
        """
        result = {"symbol": symbol}
        
        # Get company profile
        result["company_profile"] = self.get_company_profile(symbol)
        
        # Get financial ratios
        result["financial_ratios"] = self.get_financial_ratios(symbol)
        
        # Get SEC filings
        result["sec_filings"] = self.get_sec_filings(symbol, limit=5)
        
        # Get price volatility
        result["price_volatility"] = self.get_price_volatility(symbol)
        
        return result
    
    def forward(self, symbol: str, data_type: str, period: str = "annual", limit: int = 4) -> Dict[str, Any]:
        """
        Fetch financial data for a given stock symbol based on the data type.
        
        Args:
            symbol: The stock symbol to fetch data for
            data_type: Type of financial data to fetch
            period: The period to fetch data for ('annual' or 'quarter')
            limit: The number of periods to fetch
            
        Returns:
            Dict[str, Any]: Financial data based on the requested type
        """
        # Check if data_type is valid
        if data_type not in self.DATA_TYPES:
            valid_types = ", ".join(self.DATA_TYPES.keys())
            return {
                "error": f"Invalid data_type: {data_type}. Valid types are: {valid_types}",
                "symbol": symbol
            }
        
        # Call the appropriate method based on data_type
        if data_type == "company_profile":
            return self.get_company_profile(symbol)
        elif data_type == "financial_ratios":
            return self.get_financial_ratios(symbol, period, limit)
        elif data_type == "income_statement":
            return self.get_income_statement(symbol, period, limit)
        elif data_type == "balance_sheet":
            return self.get_balance_sheet(symbol, period, limit)
        elif data_type == "cash_flow":
            return self.get_cash_flow(symbol, period, limit)
        elif data_type == "peers":
            return self.get_peers(symbol)
        elif data_type == "peer_ratios":
            return self.get_peer_ratios(symbol)
        elif data_type == "market_share":
            return self.get_market_share(symbol)
        elif data_type == "growth_estimates":
            return self.get_growth_estimates(symbol)
        elif data_type == "analyst_recommendations":
            return self.get_analyst_recommendations(symbol)
        elif data_type == "earnings_surprises":
            return self.get_earnings_surprises(symbol)
        elif data_type == "sec_filings":
            return self.get_sec_filings(symbol, limit)
        elif data_type == "price_volatility":
            return self.get_price_volatility(symbol)
        elif data_type == "financial_performance":
            return self.get_financial_performance(symbol)
        elif data_type == "competitive_analysis":
            return self.get_competitive_analysis(symbol)
        elif data_type == "growth_prospects":
            return self.get_growth_prospects(symbol)
        elif data_type == "risk_assessment":
            return self.get_risk_assessment(symbol)
        
        # This should never happen due to the check above, but just in case
        return {"error": f"Unhandled data_type: {data_type}", "symbol": symbol}


def main():
    """Example usage of the consolidated financial data tool."""
    from tools.tool_manager import ToolManager
    
    # Create a tool manager
    manager = ToolManager()
    
    # Add the consolidated financial data tool
    manager.add_tool(FinancialDataTool())
    
    # Set default tool for financial_data category
    manager.set_default_tool("financial_data", "financial_data")
    
    # Print available tools
    print(manager.get_tools_prompt())
    
    # Check if API key is set
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("FMP_API_KEY environment variable not set. Cannot run example.")
        return
    
    # Use the financial data tool
    financial_data_tool = manager.get_tool_by_name("financial_data")
    if financial_data_tool:
        # Get company profile
        result = financial_data_tool(symbol="AAPL", data_type="company_profile")
        print(f"\nCompany Profile for AAPL:")
        print(f"Name: {result.get('companyName')}")
        print(f"Industry: {result.get('industry')}")
        print(f"Market Cap: ${result.get('mktCap'):,}")
        print(f"Current Price: ${result.get('price')}")
        
        # Get income statement
        result = financial_data_tool(symbol="AAPL", data_type="income_statement", limit=1)
        print(f"\nIncome Statement for AAPL:")
        if "income_statement" in result and len(result["income_statement"]) > 0:
            income = result["income_statement"][0]
            print(f"Revenue: ${income.get('revenue'):,}")
            print(f"Net Income: ${income.get('netIncome'):,}")
            print(f"EPS: ${income.get('eps')}")


if __name__ == "__main__":
    main() 