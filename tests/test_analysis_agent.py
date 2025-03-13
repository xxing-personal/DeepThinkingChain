#!/usr/bin/env python3
"""
Test script for the AnalysisAgent class.

This script tests the functionality of the AnalysisAgent with the new prompt template system.
"""

import os
import sys
from pathlib import Path
import json

# Add the parent directory to the path so we can import the agents package
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.analysis_agent import AnalysisAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_analyze_method():
    """Test the analyze method with different focus areas."""
    print("=== Testing AnalysisAgent.analyze method ===")
    
    # Sample data for testing
    data = {
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
        },
        "competitors": ["MSFT", "GOOG", "AMZN"],
        "growth_metrics": {
            "revenue_growth": "15%",
            "earnings_growth": "20%",
            "user_growth": "10%"
        },
        "risk_factors": [
            "Supply chain disruptions",
            "Regulatory challenges",
            "Intense competition"
        ]
    }
    
    # Initialize the agent
    agent = AnalysisAgent()
    
    # Test with different focus areas
    focus_areas = [None, "competitive", "growth", "risk"]
    
    for focus in focus_areas:
        focus_name = focus if focus else "financial_performance"
        print(f"\nTesting analyze method with focus: {focus_name}")
        
        # Call the analyze method
        result = agent.analyze(data, focus=focus, symbol="AAPL")
        
        # Print the result summary
        print(f"Analysis Type: {result['analysis_type']}")
        print(f"Symbol: {result['symbol']}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confidence: {result['confidence']}")
        
        print("\nKey Points:")
        for i, point in enumerate(result['key_points'][:3], 1):  # Show only first 3 points
            print(f"{i}. {point}")
        
        print("\nInsights Preview:")
        print(result['insights'][:200] + "...\n")
        
        # Verify that the result contains the expected keys
        assert "analysis_type" in result, "Missing analysis_type in result"
        assert "symbol" in result, "Missing symbol in result"
        assert "timestamp" in result, "Missing timestamp in result"
        assert "insights" in result, "Missing insights in result"
        assert "key_points" in result, "Missing key_points in result"
        assert "sentiment" in result, "Missing sentiment in result"
        assert "confidence" in result, "Missing confidence in result"
        
        print(f"✅ analyze test passed for {focus_name} focus")

def test_summarize_analyses():
    """Test the summarize_analyses method."""
    print("\n=== Testing AnalysisAgent.summarize_analyses method ===")
    
    # Sample analyses for testing
    analyses = [
        {
            "analysis_type": "general_financial",
            "symbol": "AAPL",
            "timestamp": "2023-06-01 10:00:00",
            "insights": "Apple shows strong financial performance with high margins and consistent revenue growth.",
            "key_points": [
                "Revenue grew 15% YoY",
                "Profit margins at 25%",
                "Strong cash position with $200B"
            ],
            "sentiment": "positive",
            "confidence": "high"
        },
        {
            "analysis_type": "competitive",
            "symbol": "AAPL",
            "timestamp": "2023-06-02 10:00:00",
            "insights": "Apple maintains strong competitive position in premium devices with high brand loyalty.",
            "key_points": [
                "Market leader in premium smartphones",
                "Ecosystem creates high switching costs",
                "Services revenue growing faster than hardware"
            ],
            "sentiment": "positive",
            "confidence": "high"
        },
        {
            "analysis_type": "growth",
            "symbol": "AAPL",
            "timestamp": "2023-06-03 10:00:00",
            "insights": "Apple has multiple growth vectors including services, wearables, and potential new product categories.",
            "key_points": [
                "Services growing at 20% annually",
                "Wearables segment showing strong momentum",
                "Potential entry into AR/VR market"
            ],
            "sentiment": "positive",
            "confidence": "medium"
        },
        {
            "analysis_type": "risk",
            "symbol": "AAPL",
            "timestamp": "2023-06-04 10:00:00",
            "insights": "Apple faces regulatory risks, supply chain challenges, and increasing competition in key markets.",
            "key_points": [
                "Antitrust scrutiny in App Store business",
                "Supply chain concentration in China",
                "Slowing innovation cycle in smartphones"
            ],
            "sentiment": "neutral",
            "confidence": "medium"
        }
    ]
    
    # Initialize the agent
    agent = AnalysisAgent()
    
    # Call the summarize_analyses method
    print("Generating investment summary...")
    summary = agent.summarize_analyses(analyses, symbol="AAPL")
    
    # Print a preview of the summary
    print("\nSummary Preview:")
    print("-" * 80)
    print(summary[:500] + "...\n")
    print("-" * 80)
    
    # Verify that the summary contains key sections or their alternatives
    expected_sections = [
        ["Investment Summary", "Investment Thesis", "Executive Summary"],  # Any of these is acceptable
        ["Company Overview", "Business Overview"],
        ["Financial Analysis", "Financial Performance"],
        ["Growth Prospects", "Growth Outlook"],
        ["Competitive Advantages", "Competitive Position"],
        ["Risk Factors", "Risks and Challenges"],
        ["Valuation", "Valuation Assessment"],
        ["Investment Recommendation", "Recommendation"]
    ]
    
    for section_alternatives in expected_sections:
        section_found = any(alt in summary for alt in section_alternatives)
        assert section_found, f"Missing section {section_alternatives[0]} or its alternatives in summary"
    
    print("✅ summarize_analyses test passed")

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key as an environment variable.")
        sys.exit(1)
    
    # Run the tests
    test_analyze_method()
    test_summarize_analyses()
    
    print("\n✅ All tests passed!") 