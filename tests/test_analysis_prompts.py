#!/usr/bin/env python3
"""
Test script for the analysis_prompts module.

This script tests the functionality of the analysis_prompts module
with the new prompt template system.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the prompts package
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompts import analysis_prompts

def test_initial_analysis_prompt():
    """Test the initial_analysis_prompt function."""
    print("=== Testing initial_analysis_prompt ===")
    
    # Sample data for testing
    data = {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "market_cap": "$2.5T",
        "current_price": "$150.25",
        "financial_metrics": {
            "revenue_growth": "15%",
            "profit_margin": "25%",
            "debt_to_equity": "1.2",
            "return_on_equity": "85%"
        },
        "competitors": ["MSFT", "GOOG", "AMZN"]
    }
    
    # Generate the prompt
    prompt = analysis_prompts.initial_analysis_prompt(data)
    
    # Print the prompt
    print("\nGenerated Prompt:")
    print("-" * 80)
    print(prompt)
    print("-" * 80)
    
    # Verify that the prompt contains key elements
    assert "Apple Inc." in prompt or "AAPL" in prompt, "Company name or symbol not in prompt"
    assert "financial" in prompt.lower(), "Financial analysis focus not in prompt"
    assert "revenue_growth: 15%" in prompt, "Financial metric not in prompt"
    
    print("✅ initial_analysis_prompt test passed")

def test_detailed_analysis_prompt():
    """Test the detailed_analysis_prompt function with different focus areas."""
    print("\n=== Testing detailed_analysis_prompt ===")
    
    # Sample data for testing
    data = {
        "symbol": "NVDA",
        "company_name": "NVIDIA Corporation",
        "sector": "Technology",
        "industry": "Semiconductors",
        "market_cap": "$1.2T",
        "current_price": "$450.75",
        "financial_metrics": {
            "revenue_growth": "35%",
            "profit_margin": "40%",
            "debt_to_equity": "0.5",
            "return_on_equity": "45%"
        },
        "competitors": ["AMD", "INTC", "TSM"]
    }
    
    # Test each focus area
    focus_areas = ["competitive", "growth", "risk"]
    
    for focus in focus_areas:
        print(f"\nTesting focus area: {focus}")
        
        # Generate the prompt
        prompt = analysis_prompts.detailed_analysis_prompt(data, focus)
        
        # Print a snippet of the prompt
        print(f"\nGenerated Prompt (first 300 chars):")
        print("-" * 80)
        print(prompt[:300] + "...")
        print("-" * 80)
        
        # Verify that the prompt contains key elements
        assert "NVDA" in prompt or "NVIDIA" in prompt, "Company name or symbol not in prompt"
        assert focus.lower() in prompt.lower(), f"{focus} focus not in prompt"
        
        print(f"✅ detailed_analysis_prompt test passed for {focus} focus")

def test_planning_prompt():
    """Test the planning_prompt function."""
    print("\n=== Testing planning_prompt ===")
    
    # Sample analyses for testing
    analyses = [
        {
            "symbol": "TSLA",
            "analysis_type": "financial_performance",
            "insights": "Tesla shows strong revenue growth but faces margin pressure.",
            "key_points": [
                "Revenue grew 30% YoY",
                "Margins declined 2% due to price cuts",
                "Strong cash position with $20B on hand"
            ],
            "sentiment": "positive",
            "confidence": "high"
        },
        {
            "symbol": "TSLA",
            "analysis_type": "competitive_analysis",
            "insights": "Tesla maintains EV market leadership but faces increasing competition.",
            "key_points": [
                "Market share of 65% in US EV market",
                "Chinese competitors gaining ground in Asia",
                "Legacy automakers ramping up EV production"
            ],
            "sentiment": "neutral",
            "confidence": "medium"
        }
    ]
    
    # Generate the prompt
    prompt = analysis_prompts.planning_prompt(analyses)
    
    # Print a snippet of the prompt
    print("\nGenerated Prompt (first 300 chars):")
    print("-" * 80)
    print(prompt[:300] + "...")
    print("-" * 80)
    
    # Verify that the prompt contains key elements
    assert "TSLA" in prompt, "Symbol not in prompt"
    assert "research coordinator" in prompt.lower(), "Role description not in prompt"
    assert "financial_performance" in prompt, "Analysis type not in prompt"
    assert "competitive_analysis" in prompt, "Analysis type not in prompt"
    
    print("✅ planning_prompt test passed")

def test_summary_prompt():
    """Test the summary_prompt function."""
    print("\n=== Testing summary_prompt ===")
    
    # Sample analyses for testing
    analyses = [
        {
            "symbol": "AMZN",
            "analysis_type": "financial_performance",
            "insights": "Amazon shows strong revenue growth and improving profitability.",
            "key_points": [
                "Revenue grew 20% YoY",
                "AWS continues to be the profit engine",
                "Retail margins improving"
            ],
            "sentiment": "positive",
            "confidence": "high"
        },
        {
            "symbol": "AMZN",
            "analysis_type": "growth_prospects",
            "insights": "Amazon has multiple growth vectors across e-commerce, cloud, and new initiatives.",
            "key_points": [
                "International e-commerce expansion ongoing",
                "AWS expected to grow 25%+ annually",
                "Healthcare and advertising represent new growth areas"
            ],
            "sentiment": "positive",
            "confidence": "high"
        },
        {
            "symbol": "AMZN",
            "analysis_type": "risk_assessment",
            "insights": "Amazon faces regulatory, competitive, and margin risks.",
            "key_points": [
                "Antitrust scrutiny in US and EU",
                "Increasing competition in cloud from Microsoft and Google",
                "Labor cost pressures in fulfillment centers"
            ],
            "sentiment": "neutral",
            "confidence": "medium"
        }
    ]
    
    # Generate the prompt
    prompt = analysis_prompts.summary_prompt(analyses)
    
    # Print a snippet of the prompt
    print("\nGenerated Prompt (first 300 chars):")
    print("-" * 80)
    print(prompt[:300] + "...")
    print("-" * 80)
    
    # Verify that the prompt contains key elements
    assert "AMZN" in prompt, "Symbol not in prompt"
    assert "financial advisor" in prompt.lower(), "Role description not in prompt"
    assert "investment recommendation" in prompt.lower(), "Task description not in prompt"
    
    print("✅ summary_prompt test passed")

def test_get_template_by_focus():
    """Test the get_template_by_focus function for backward compatibility."""
    print("\n=== Testing get_template_by_focus ===")
    
    # Test each focus area
    focus_areas = ["financial", "competitive", "growth", "risk"]
    
    for focus in focus_areas:
        template = analysis_prompts.get_template_by_focus(focus)
        
        # Print the first 100 characters of the template
        print(f"\nTemplate for {focus} focus (first 100 chars):")
        print("-" * 80)
        print(template[:100] + "...")
        print("-" * 80)
        
        # Verify that the template contains key elements
        assert "financial analyst" in template.lower(), "Role description not in template"
        assert focus.lower() in template.lower() or (focus == "financial" and "investment opportunity" in template.lower()), f"{focus} focus not in template"
        
        print(f"✅ get_template_by_focus test passed for {focus} focus")

if __name__ == "__main__":
    # Run all tests
    test_initial_analysis_prompt()
    test_detailed_analysis_prompt()
    test_planning_prompt()
    test_summary_prompt()
    test_get_template_by_focus()
    
    print("\n✅ All tests passed!") 