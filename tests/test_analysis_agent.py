"""
Test script for the AnalysisAgent with the new prompt functions.
"""

import os
from dotenv import load_dotenv
from agents.analysis_agent import AnalysisAgent

# Load environment variables
load_dotenv()

def test_analysis_agent():
    """Test the AnalysisAgent with the new prompt functions."""
    # Check if OpenAI API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key to run this test.")
        return
    
    # Initialize the agent
    agent = AnalysisAgent()
    
    # Sample data for testing
    sample_data = {
        "company_profile": {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
            "market_cap": 2800000000000,
            "price": 175.50
        },
        "financial_ratios": {
            "pe_ratio": 28.5,
            "price_to_sales": 7.2,
            "debt_to_equity": 1.5,
            "current_ratio": 1.2,
            "gross_margin": 0.43,
            "operating_margin": 0.30,
            "net_margin": 0.25
        }
    }
    
    # Test initial analysis
    print("Testing initial analysis...")
    result = agent.analyze(sample_data, symbol="AAPL")
    
    # Print the results
    print(f"Analysis Type: {result['analysis_type']}")
    print(f"Symbol: {result['symbol']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Confidence: {result['confidence']}")
    print("\nKey Points:")
    for point in result["key_points"]:
        print(f"- {point}")
    
    print("\nInsights Preview:")
    print(result["insights"][:500] + "...")
    
    # Test detailed analysis with a specific focus
    print("\n\nTesting detailed analysis (competitive)...")
    sample_data_competitive = {
        "symbol": "AAPL",
        "competitors": [
            {"symbol": "MSFT", "name": "Microsoft Corporation", "market_cap": 2500000000000},
            {"symbol": "GOOG", "name": "Alphabet Inc.", "market_cap": 1800000000000},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "market_cap": 1600000000000}
        ],
        "market_share": {
            "smartphones": 0.18,
            "tablets": 0.32,
            "wearables": 0.35
        }
    }
    
    result = agent.analyze(sample_data_competitive, focus="competitive_analysis", symbol="AAPL")
    
    # Print the results
    print(f"Analysis Type: {result['analysis_type']}")
    print(f"Symbol: {result['symbol']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Confidence: {result['confidence']}")
    print("\nKey Points:")
    for point in result["key_points"]:
        print(f"- {point}")
    
    print("\nInsights Preview:")
    print(result["insights"][:500] + "...")
    
    # Test planning with multiple analyses
    print("\n\nTesting planning with multiple analyses...")
    analyses = [
        {
            "analysis_type": "general_financial",
            "symbol": "AAPL",
            "insights": "Apple shows strong financial performance with consistent revenue growth and high margins. The company has a robust balance sheet with significant cash reserves.",
            "key_points": [
                "Revenue growth of 12% year-over-year",
                "Gross margin of 43%, above industry average",
                "Strong cash position of $200B",
                "Consistent share repurchases and dividend growth"
            ],
            "sentiment": "positive",
            "confidence": "high"
        },
        {
            "analysis_type": "competitive_analysis",
            "symbol": "AAPL",
            "insights": "Apple maintains a strong competitive position in its core markets. The company's ecosystem and brand loyalty provide significant advantages over competitors.",
            "key_points": [
                "Leading market share in premium smartphones",
                "Strong ecosystem lock-in effects",
                "Brand value provides pricing power",
                "Facing increasing competition in services"
            ],
            "sentiment": "positive",
            "confidence": "medium"
        }
    ]
    
    summary = agent.summarize_analyses(analyses, symbol="AAPL")
    
    # Print the summary
    print("\nSummary Preview:")
    print(summary[:500] + "...")

if __name__ == "__main__":
    test_analysis_agent() 