"""
Test script for the AnalysisAgent.

This script tests the AnalysisAgent's ability to analyze financial data
and generate investment insights using the OpenAI API.
"""

import os
import json
from dotenv import load_dotenv
from agents.analysis_agent import AnalysisAgent
from agents.tool_agent import ToolAgent

# Load environment variables
load_dotenv()

def test_with_sample_data():
    """Test the AnalysisAgent with sample data."""
    # Sample data for testing
    sample_data = {
        "company_profile": {
            "symbol": "AAPL",
            "companyName": "Apple Inc.",
            "industry": "Consumer Electronics",
            "sector": "Technology",
            "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
            "mktCap": 3000000000000,
            "price": 200.0
        },
        "financial_ratios": {
            "peRatio": 30.5,
            "returnOnEquity": 1.5,
            "returnOnAssets": 0.25,
            "debtEquityRatio": 1.8
        }
    }
    
    # Initialize the agent
    agent = AnalysisAgent()
    
    # Test the analyze method
    print("\n" + "="*50)
    print("Testing AnalysisAgent with sample data...")
    print("="*50 + "\n")
    
    result = agent.analyze(sample_data, symbol="AAPL")
    
    print(f"Analysis Type: {result['analysis_type']}")
    print(f"Symbol: {result['symbol']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Sentiment: {result.get('sentiment', 'N/A')}")
    print(f"Confidence: {result.get('confidence', 'N/A')}")
    
    if "error" in result:
        print(f"\nError: {result['error']}")
        return
    
    print("\nKey Points:")
    for i, point in enumerate(result.get('key_points', []), 1):
        print(f"{i}. {point}")
    
    print("\nInsights Preview:")
    insights = result.get('insights', '')
    print(insights[:500] + "..." if len(insights) > 500 else insights)
    
    print("\n" + "="*50)
    print("AnalysisAgent test with sample data complete")
    print("="*50)

def test_with_real_data(symbol="AAPL"):
    """Test the AnalysisAgent with real data from the ToolAgent."""
    print("\n" + "="*50)
    print(f"Testing AnalysisAgent with real data for {symbol}...")
    print("="*50 + "\n")
    
    # Check if FMP API key is set
    if not os.getenv("FMP_API_KEY"):
        print("Error: FMP_API_KEY environment variable not found.")
        return
    
    # Initialize the agents
    tool_agent = ToolAgent()
    analysis_agent = AnalysisAgent()
    
    # Fetch real data
    print(f"Fetching data for {symbol}...")
    data = {
        "company_profile": tool_agent.fetch_company_profile(symbol),
        "financial_ratios": tool_agent.fetch_financial_ratios(symbol)
    }
    
    # Check if data was fetched successfully
    if "error" in data["company_profile"] or "error" in data["financial_ratios"]:
        print("Error fetching data. Please check your API key and try again.")
        return
    
    print("Data fetched successfully.")
    
    # Analyze the data
    print("Analyzing data...")
    result = analysis_agent.analyze(data, symbol=symbol)
    
    if "error" in result:
        print(f"\nError during analysis: {result['error']}")
        return
    
    print(f"Analysis Type: {result['analysis_type']}")
    print(f"Symbol: {result['symbol']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Sentiment: {result.get('sentiment', 'N/A')}")
    print(f"Confidence: {result.get('confidence', 'N/A')}")
    
    print("\nKey Points:")
    for i, point in enumerate(result.get('key_points', []), 1):
        print(f"{i}. {point}")
    
    print("\nInsights Preview:")
    insights = result.get('insights', '')
    print(insights[:500] + "..." if len(insights) > 500 else insights)
    
    # Save the full analysis to a file
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/{symbol}_analysis.md"
    
    with open(output_file, "w") as f:
        f.write(f"# Investment Analysis for {symbol}\n\n")
        f.write(f"## {result['analysis_type'].replace('_', ' ').title()} Analysis\n\n")
        f.write(insights)
    
    print(f"\nFull analysis saved to {output_file}")
    
    print("\n" + "="*50)
    print("AnalysisAgent test with real data complete")
    print("="*50)

if __name__ == "__main__":
    import sys
    
    # Check if OpenAI API key is set
    api_key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("Error: OPENAI_API_KEY environment variable not set or using default value.")
        print("Please set your OpenAI API key in the .env file or environment.")
        sys.exit(1)
    
    # Determine which test to run
    if len(sys.argv) > 1:
        if sys.argv[1] == "sample":
            test_with_sample_data()
        else:
            # Assume the argument is a stock symbol
            test_with_real_data(sys.argv[1])
    else:
        # Run both tests with default symbol
        test_with_sample_data()
        test_with_real_data() 