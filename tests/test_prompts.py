"""
Test script for the prompt functions in prompts/analysis_prompts.py
"""

import json
from prompts.analysis_prompts import (
    initial_analysis_prompt,
    detailed_analysis_prompt,
    planning_prompt
)

def test_initial_analysis_prompt():
    """Test the initial_analysis_prompt function."""
    # Sample data for testing
    sample_data = {
        "symbol": "AAPL",
        "company_profile": {
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
    
    # Generate the prompt
    prompt = initial_analysis_prompt(sample_data)
    
    # Print the prompt for verification
    print("=== INITIAL ANALYSIS PROMPT ===")
    print(prompt)
    print("\n" + "="*50 + "\n")
    
    return prompt

def test_detailed_analysis_prompt():
    """Test the detailed_analysis_prompt function with different focus areas."""
    # Sample data for testing
    sample_data = {
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
        },
        "growth_rates": {
            "revenue_5yr_cagr": 0.12,
            "earnings_5yr_cagr": 0.15,
            "dividend_5yr_cagr": 0.08
        }
    }
    
    # Test with different focus areas
    focus_areas = ["competitive", "growth", "risk"]
    
    for focus in focus_areas:
        prompt = detailed_analysis_prompt(sample_data, focus)
        
        # Print the prompt for verification
        print(f"=== DETAILED ANALYSIS PROMPT ({focus.upper()}) ===")
        print(prompt)
        print("\n" + "="*50 + "\n")
    
    return prompt

def test_planning_prompt():
    """Test the planning_prompt function."""
    # Sample analyses for testing
    sample_analyses = [
        {
            "analysis_type": "Financial Performance",
            "symbol": "AAPL",
            "insights": "Apple shows strong financial performance with consistent revenue growth and high margins. The company has a robust balance sheet with significant cash reserves.",
            "key_points": [
                "Revenue growth of 12% year-over-year",
                "Gross margin of 43%, above industry average",
                "Strong cash position of $200B",
                "Consistent share repurchases and dividend growth"
            ],
            "sentiment": "Positive",
            "confidence": "High"
        },
        {
            "analysis_type": "Competitive Analysis",
            "symbol": "AAPL",
            "insights": "Apple maintains a strong competitive position in its core markets. The company's ecosystem and brand loyalty provide significant advantages over competitors.",
            "key_points": [
                "Leading market share in premium smartphones",
                "Strong ecosystem lock-in effects",
                "Brand value provides pricing power",
                "Facing increasing competition in services"
            ],
            "sentiment": "Positive",
            "confidence": "Medium"
        }
    ]
    
    # Generate the prompt
    prompt = planning_prompt(sample_analyses)
    
    # Print the prompt for verification
    print("=== PLANNING PROMPT ===")
    print(prompt)
    print("\n" + "="*50 + "\n")
    
    return prompt

if __name__ == "__main__":
    test_initial_analysis_prompt()
    test_detailed_analysis_prompt()
    test_planning_prompt() 