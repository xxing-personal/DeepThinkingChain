import os
import requests
from typing import Dict, Any, Optional
import json
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class ToolAgent:
    """Agent responsible for fetching external financial data."""
    
    def __init__(self):
        """Initialize the ToolAgent with API configuration.
        
        The API key should be set as an environment variable FMP_API_KEY.
        """
        self.api_key = os.getenv("FMP_API_KEY")
        if not self.api_key:
            print("Warning: FMP_API_KEY environment variable not found.")
            print("Please set your Financial Modeling Prep API key as an environment variable.")
            print("You can get a free API key at https://financialmodelingprep.com/developer/docs/")
        
        self.base_url = "https://financialmodelingprep.com/api/v3"
        
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the Financial Modeling Prep API.
        
        Args:
            endpoint: API endpoint to call
            params: Additional query parameters
            
        Returns:
            Dict containing the API response
            
        Raises:
            Exception: If the API request fails
        """
        if params is None:
            params = {}
        
        # Add API key to parameters
        params["apikey"] = self.api_key
        
        # Make the request
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        
        # Check if request was successful
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
        
        # Parse and return the response
        return response.json()
    
    def fetch_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Fetches basic company profile from financialmodelingprep API.
        
        Args:
            symbol: Stock symbol (e.g., 'NVDA')
            
        Returns:
            Dict containing company profile information including:
            - Company name, description, sector, industry
            - Market capitalization, current price
            - Basic financial metrics
        """
        try:
            endpoint = f"profile/{symbol}"
            result = self._make_request(endpoint)
            
            # The API returns a list with a single item
            if result and isinstance(result, list) and len(result) > 0:
                return result[0]
            return {}
        except Exception as e:
            print(f"Error fetching company profile for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def fetch_financial_ratios(self, symbol: str) -> Dict[str, Any]:
        """Retrieves financial ratios data for deeper financial insights.
        
        Args:
            symbol: Stock symbol (e.g., 'NVDA')
            
        Returns:
            Dict containing key financial ratios including:
            - Profitability ratios (ROE, ROA, profit margins)
            - Liquidity ratios (current ratio, quick ratio)
            - Solvency ratios (debt-to-equity, interest coverage)
            - Valuation ratios (P/E, P/B, EV/EBITDA)
        """
        try:
            endpoint = f"ratios/{symbol}"
            result = self._make_request(endpoint)
            
            # The API returns a list of ratios by period
            if result and isinstance(result, list) and len(result) > 0:
                # Return the most recent period's ratios
                return result[0]
            return {}
        except Exception as e:
            print(f"Error fetching financial ratios for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def fetch_data(self, symbol: str, focus: str) -> Dict[str, Any]:
        """Fetches specific financial data based on the current analysis focus.
        
        Args:
            symbol: Stock symbol (e.g., 'NVDA')
            focus: The current analysis focus area (e.g., 'financial_performance', 
                  'competitive_analysis', 'growth_prospects', etc.)
            
        Returns:
            Dict containing the requested financial data
        """
        data = {}
        
        # Fetch different data based on the focus area
        if focus == "financial_performance":
            data["income_statement"] = self._fetch_income_statement(symbol)
            data["balance_sheet"] = self._fetch_balance_sheet(symbol)
            data["cash_flow"] = self._fetch_cash_flow(symbol)
            
        elif focus == "competitive_analysis":
            data["peers"] = self._fetch_peers(symbol)
            # Get sector performance for comparison
            if data.get("peers"):
                sector_data = {}
                for peer in data["peers"][:3]:  # Limit to top 3 peers
                    sector_data[peer] = self.fetch_company_profile(peer)
                data["peer_profiles"] = sector_data
                
        elif focus == "growth_prospects":
            data["growth_estimates"] = self._fetch_growth_estimates(symbol)
            data["analyst_recommendations"] = self._fetch_analyst_recommendations(symbol)
            
        elif focus == "valuation":
            data["key_metrics"] = self._fetch_key_metrics(symbol)
            data["dcf"] = self._fetch_dcf_valuation(symbol)
            
        elif focus == "risk_assessment":
            data["sec_filings"] = self._fetch_sec_filings(symbol)
            
        else:
            # Default: fetch general company information
            data["company_profile"] = self.fetch_company_profile(symbol)
            data["financial_ratios"] = self.fetch_financial_ratios(symbol)
            
        return data
    
    def _fetch_income_statement(self, symbol: str) -> Dict[str, Any]:
        """Fetches income statement data."""
        try:
            endpoint = f"income-statement/{symbol}"
            params = {"limit": 4}  # Last 4 periods
            return self._make_request(endpoint, params)
        except Exception as e:
            print(f"Error fetching income statement for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def _fetch_balance_sheet(self, symbol: str) -> Dict[str, Any]:
        """Fetches balance sheet data."""
        try:
            endpoint = f"balance-sheet-statement/{symbol}"
            params = {"limit": 4}  # Last 4 periods
            return self._make_request(endpoint, params)
        except Exception as e:
            print(f"Error fetching balance sheet for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def _fetch_cash_flow(self, symbol: str) -> Dict[str, Any]:
        """Fetches cash flow statement data."""
        try:
            endpoint = f"cash-flow-statement/{symbol}"
            params = {"limit": 4}  # Last 4 periods
            return self._make_request(endpoint, params)
        except Exception as e:
            print(f"Error fetching cash flow statement for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def _fetch_peers(self, symbol: str) -> list:
        """Fetches company peers/competitors."""
        try:
            endpoint = f"stock_peers"
            params = {"symbol": symbol}
            result = self._make_request(endpoint, params)
            if result and isinstance(result, list) and len(result) > 0:
                return result[0].get("peersList", [])
            return []
        except Exception as e:
            print(f"Error fetching peers for {symbol}: {str(e)}")
            return []
    
    def _fetch_growth_estimates(self, symbol: str) -> Dict[str, Any]:
        """Fetches growth estimates."""
        try:
            endpoint = f"analyst-estimates/{symbol}"
            params = {"period": "annual"}
            return self._make_request(endpoint, params)
        except Exception as e:
            print(f"Error fetching growth estimates for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def _fetch_analyst_recommendations(self, symbol: str) -> Dict[str, Any]:
        """Fetches analyst recommendations."""
        try:
            endpoint = f"analyst-stock-recommendations/{symbol}"
            return self._make_request(endpoint)
        except Exception as e:
            print(f"Error fetching analyst recommendations for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def _fetch_key_metrics(self, symbol: str) -> Dict[str, Any]:
        """Fetches key metrics."""
        try:
            endpoint = f"key-metrics/{symbol}"
            params = {"limit": 4}  # Last 4 periods
            return self._make_request(endpoint, params)
        except Exception as e:
            print(f"Error fetching key metrics for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def _fetch_dcf_valuation(self, symbol: str) -> Dict[str, Any]:
        """Fetches discounted cash flow valuation."""
        try:
            endpoint = f"discounted-cash-flow/{symbol}"
            return self._make_request(endpoint)
        except Exception as e:
            print(f"Error fetching DCF valuation for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def _fetch_sec_filings(self, symbol: str) -> Dict[str, Any]:
        """Fetches recent SEC filings."""
        try:
            endpoint = f"sec_filings/{symbol}"
            params = {"limit": 10}  # Last 10 filings
            return self._make_request(endpoint, params)
        except Exception as e:
            print(f"Error fetching SEC filings for {symbol}: {str(e)}")
            return {"error": str(e)}
