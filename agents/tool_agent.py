import os
import requests
from typing import Dict, Any, Optional, List, Union
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
        
        try:
            response = requests.get(url, params=params)
            
            # Check if request was successful
            if response.status_code != 200:
                return {"error": f"API request failed with status code {response.status_code}"}
            
            # Parse response
            data = response.json()
            
            # Check if data is empty
            if not data:
                return {"error": "No data returned from API"}
            
            return data
        except Exception as e:
            return {"error": str(e)}
    
    def fetch_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Fetches basic company profile from financialmodelingprep API.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            Dict containing company profile data
        """
        endpoint = f"profile/{symbol}"
        response = self._make_request(endpoint)
        
        # The API returns a list with a single item
        if isinstance(response, list) and len(response) > 0:
            return response[0]
        elif "error" in response:
            return response
        else:
            return {"error": "Unexpected response format"}
    
    def fetch_financial_ratios(self, symbol: str) -> Dict[str, Any]:
        """Retrieves financial ratios data for deeper financial insights.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            Dict containing financial ratios
        """
        endpoint = f"ratios/{symbol}"
        response = self._make_request(endpoint)
        
        # The API returns a list of ratios for different periods
        if isinstance(response, list) and len(response) > 0:
            return response[0]  # Return the most recent period
        elif "error" in response:
            return response
        else:
            return {"error": "Unexpected response format"}
    
    def fetch_income_statement(self, symbol: str, limit: int = 4, period: str = "annual") -> List[Dict[str, Any]]:
        """Fetches income statement data for the company.
        
        Args:
            symbol: Stock symbol to fetch data for
            limit: Number of periods to fetch (default: 4)
            period: 'annual' or 'quarter' (default: 'annual')
            
        Returns:
            List of income statements for different periods
        """
        endpoint = f"income-statement/{symbol}"
        params = {"limit": limit, "period": period}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list):
            return response
        elif "error" in response:
            return [response]
        else:
            return [{"error": "Unexpected response format"}]
    
    def fetch_balance_sheet(self, symbol: str, limit: int = 4, period: str = "annual") -> List[Dict[str, Any]]:
        """Fetches balance sheet data for the company.
        
        Args:
            symbol: Stock symbol to fetch data for
            limit: Number of periods to fetch (default: 4)
            period: 'annual' or 'quarter' (default: 'annual')
            
        Returns:
            List of balance sheets for different periods
        """
        endpoint = f"balance-sheet-statement/{symbol}"
        params = {"limit": limit, "period": period}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list):
            return response
        elif "error" in response:
            return [response]
        else:
            return [{"error": "Unexpected response format"}]
    
    def fetch_cash_flow(self, symbol: str, limit: int = 4, period: str = "annual") -> List[Dict[str, Any]]:
        """Fetches cash flow statement data for the company.
        
        Args:
            symbol: Stock symbol to fetch data for
            limit: Number of periods to fetch (default: 4)
            period: 'annual' or 'quarter' (default: 'annual')
            
        Returns:
            List of cash flow statements for different periods
        """
        endpoint = f"cash-flow-statement/{symbol}"
        params = {"limit": limit, "period": period}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list):
            return response
        elif "error" in response:
            return [response]
        else:
            return [{"error": "Unexpected response format"}]
    
    def fetch_peers(self, symbol: str) -> List[str]:
        """Fetches peer companies for the given symbol.
        
        Args:
            symbol: Stock symbol to fetch peers for
            
        Returns:
            List of peer company symbols
        """
        endpoint = f"stock_peers"
        params = {"symbol": symbol}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list) and len(response) > 0:
            return response[0].get("peersList", [])
        elif "error" in response:
            return [response["error"]]
        else:
            return ["Error: Unexpected response format"]
    
    def fetch_peer_ratios(self, symbol: str) -> Dict[str, Any]:
        """Fetches financial ratios for the company and its peers.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            Dict containing financial ratios for the company and its peers
        """
        # First get the peers
        peers = self.fetch_peers(symbol)
        
        # If there was an error fetching peers
        if len(peers) == 1 and peers[0].startswith("Error"):
            return {"error": peers[0]}
        
        # Limit to top 5 peers
        peers = peers[:5]
        
        # Add the original symbol
        symbols = [symbol] + peers
        
        # Fetch ratios for all symbols
        result = {"symbol": symbol, "peers": {}}
        
        for sym in symbols:
            if sym == symbol:
                result["ratios"] = self.fetch_financial_ratios(sym)
            else:
                result["peers"][sym] = self.fetch_financial_ratios(sym)
        
        return result
    
    def fetch_market_share(self, symbol: str) -> Dict[str, Any]:
        """Fetches market share data for the company.
        
        Note: This is a simulated method as FMP doesn't provide direct market share data.
        In a real implementation, this would use a different data source or calculate
        market share based on revenue and industry size.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            Dict containing market share data
        """
        # Get company profile to determine industry
        profile = self.fetch_company_profile(symbol)
        
        if "error" in profile:
            return profile
        
        industry = profile.get("industry", "Unknown")
        
        # This is simulated data - in a real implementation, this would come from a data source
        return {
            "symbol": symbol,
            "industry": industry,
            "market_share_percentage": 0.15,  # Simulated value
            "industry_rank": 3,  # Simulated value
            "top_competitors": self.fetch_peers(symbol)[:3],
            "note": "This is simulated market share data for demonstration purposes."
        }
    
    def fetch_growth_estimates(self, symbol: str) -> Dict[str, Any]:
        """Fetches growth estimates for the company.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            Dict containing growth estimates
        """
        endpoint = f"analyst-estimates/{symbol}"
        params = {"period": "annual"}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list) and len(response) > 0:
            return {
                "symbol": symbol,
                "estimates": response
            }
        elif "error" in response:
            return response
        else:
            return {"error": "Unexpected response format"}
    
    def fetch_analyst_recommendations(self, symbol: str) -> Dict[str, Any]:
        """Fetches analyst recommendations for the company.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            Dict containing analyst recommendations
        """
        endpoint = f"analyst-stock-recommendations/{symbol}"
        response = self._make_request(endpoint)
        
        if isinstance(response, list):
            return {
                "symbol": symbol,
                "recommendations": response
            }
        elif "error" in response:
            return response
        else:
            return {"error": "Unexpected response format"}
    
    def fetch_earnings_surprises(self, symbol: str) -> Dict[str, Any]:
        """Fetches earnings surprises for the company.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            Dict containing earnings surprises
        """
        endpoint = f"earnings-surprises/{symbol}"
        response = self._make_request(endpoint)
        
        if isinstance(response, list):
            return {
                "symbol": symbol,
                "earnings_surprises": response
            }
        elif "error" in response:
            return response
        else:
            return {"error": "Unexpected response format"}
    
    def fetch_sec_filings(self, symbol: str, limit: int = 10) -> Dict[str, Any]:
        """Fetches SEC filings for the company.
        
        Args:
            symbol: Stock symbol to fetch data for
            limit: Number of filings to fetch (default: 10)
            
        Returns:
            Dict containing SEC filings
        """
        endpoint = f"sec_filings/{symbol}"
        params = {"limit": limit}
        response = self._make_request(endpoint, params)
        
        if isinstance(response, list):
            return {
                "symbol": symbol,
                "filings": response
            }
        elif "error" in response:
            return response
        else:
            return {"error": "Unexpected response format"}
    
    def fetch_price_volatility(self, symbol: str) -> Dict[str, Any]:
        """Fetches price volatility data for the company.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            Dict containing price volatility data
        """
        # Get historical price data
        endpoint = f"historical-price-full/{symbol}"
        params = {"timeseries": 365}  # Last year of data
        response = self._make_request(endpoint, params)
        
        if "historical" not in response:
            if "error" in response:
                return response
            else:
                return {"error": "Unexpected response format"}
        
        # Calculate volatility (standard deviation of daily returns)
        historical_data = response["historical"]
        
        if len(historical_data) < 30:
            return {"error": "Insufficient historical data to calculate volatility"}
        
        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(historical_data)):
            today = historical_data[i]["close"]
            yesterday = historical_data[i-1]["close"]
            daily_return = (today - yesterday) / yesterday
            daily_returns.append(daily_return)
        
        # Calculate volatility (standard deviation of returns)
        import numpy as np
        volatility = np.std(daily_returns)
        annualized_volatility = volatility * np.sqrt(252)  # Annualize (252 trading days)
        
        return {
            "symbol": symbol,
            "daily_volatility": float(volatility),
            "annualized_volatility": float(annualized_volatility),
            "data_period": f"{historical_data[-1]['date']} to {historical_data[0]['date']}",
            "sample_size": len(historical_data)
        }
    
    def fetch_data(self, symbol: str, focus: str) -> Dict[str, Any]:
        """Fetches financial data based on the current analysis focus.
        
        Args:
            symbol: Stock symbol to fetch data for
            focus: The focus area for the analysis
            
        Returns:
            Dict containing the requested financial data
        """
        # Add symbol to the result
        result = {"symbol": symbol}
        
        # Always include company profile
        result["company_profile"] = self.fetch_company_profile(symbol)
        
        # Fetch data based on focus
        if focus == "financial_performance":
            result["financial_ratios"] = self.fetch_financial_ratios(symbol)
            result["income_statement"] = self.fetch_income_statement(symbol, limit=2)
            result["balance_sheet"] = self.fetch_balance_sheet(symbol, limit=2)
            result["cash_flow"] = self.fetch_cash_flow(symbol, limit=2)
        
        elif focus == "competitive_analysis":
            result["peers"] = self.fetch_peers(symbol)
            result["peer_ratios"] = self.fetch_peer_ratios(symbol)
            result["market_share"] = self.fetch_market_share(symbol)
        
        elif focus == "growth_prospects":
            result["growth_estimates"] = self.fetch_growth_estimates(symbol)
            result["analyst_recommendations"] = self.fetch_analyst_recommendations(symbol)
            result["earnings_surprises"] = self.fetch_earnings_surprises(symbol)
        
        elif focus == "risk_assessment":
            result["financial_ratios"] = self.fetch_financial_ratios(symbol)
            result["sec_filings"] = self.fetch_sec_filings(symbol, limit=5)
            result["price_volatility"] = self.fetch_price_volatility(symbol)
        
        else:
            # Default: fetch basic financial data
            result["financial_ratios"] = self.fetch_financial_ratios(symbol)
        
        return result


if __name__ == "__main__":
    import sys
    
    # Get symbol from command line argument or use default
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    
    # Initialize the agent
    agent = ToolAgent()
    
    # Test company profile
    print(f"\nFetching company profile for {symbol}...")
    profile = agent.fetch_company_profile(symbol)
    print(json.dumps(profile, indent=2))
    
    # Test financial ratios
    print(f"\nFetching financial ratios for {symbol}...")
    ratios = agent.fetch_financial_ratios(symbol)
    print(json.dumps(ratios, indent=2))
    
    # Test data fetching with focus
    focus = sys.argv[2] if len(sys.argv) > 2 else "financial_performance"
    print(f"\nFetching data for {symbol} with focus on {focus}...")
    data = agent.fetch_data(symbol, focus)
    print(f"Data keys: {list(data.keys())}")
