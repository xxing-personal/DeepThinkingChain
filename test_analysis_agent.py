"""
Test script for the AnalysisAgent with the new template system.
"""

import os
import json
from dotenv import load_dotenv
from agents.analysis_agent import AnalysisAgent

# Load environment variables
load_dotenv()

def main():
    """Test the AnalysisAgent functionality."""
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key as an environment variable.")
        return
    
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
    print("Initializing AnalysisAgent...")
    agent = AnalysisAgent()
    
    # Test the analyze method
    print("\n" + "="*50)
    print("Testing AnalysisAgent with sample data...")
    print("="*50 + "\n")
    
    try:
        result = agent.analyze(sample_data, symbol="AAPL")
        
        print(f"Analysis Type: {result['analysis_type']}")
        print(f"Symbol: {result['symbol']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confidence: {result['confidence']}")
        
        print("\nKey Points:")
        for i, point in enumerate(result['key_points'], 1):
            print(f"{i}. {point}")
        
        print("\nInsights Preview:")
        print(result['insights'][:500] + "...\n")
        
        # Test the summarize_analyses method
        print("\n" + "="*50)
        print("Testing summarize_analyses method...")
        print("="*50 + "\n")
        
        # Create a list of analyses for summarization
        analyses = [result]
        
        summary = agent.summarize_analyses(analyses, symbol="AAPL")
        
        print("Summary Preview:")
        print(summary[:500] + "...\n")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
    
    print("="*50)
    print("AnalysisAgent test complete")
    print("="*50)

if __name__ == "__main__":
    main() 