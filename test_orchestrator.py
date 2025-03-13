#!/usr/bin/env python3
"""
Test script for the DeepThinkingChain orchestrator.

This script tests the integration of the updated AnalysisAgent with the orchestrator.
"""

import os
import sys
from typing import Dict, Any
import json
from unittest.mock import patch, MagicMock

# Import the DeepThinkingChain class
from orchestrator import DeepThinkingChain

# Import the agents for mocking
from agents.tool_agent import ToolAgent
from agents.analysis_agent import AnalysisAgent
from agents.planning_agent import PlanningAgent
from agents.summarization_agent import SummarizationAgent

# Import memory manager for mocking
from memory import MemoryManager

def mock_execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
    """Mock implementation of execute_tool method."""
    symbol = kwargs.get('symbol', 'TEST')
    
    # Return different mock data based on the tool name
    if tool_name == 'fetch_company_profile':
        return {
            "symbol": symbol,
            "companyName": f"Test Company ({symbol})",
            "industry": "Technology",
            "sector": "Information Technology",
            "description": f"This is a test description for {symbol}.",
            "mktCap": 1000000000,
            "price": 100.0
        }
    elif tool_name == 'fetch_financial_ratios':
        return {
            "peRatio": 20.5,
            "returnOnEquity": 0.15,
            "returnOnAssets": 0.1,
            "debtEquityRatio": 0.5
        }
    elif tool_name == 'fetch_income_statement':
        return {}
    elif tool_name == 'fetch_balance_sheet':
        return {}
    elif tool_name == 'fetch_cash_flow':
        return {}
    elif tool_name == 'fetch_peers':
        return ["COMP1", "COMP2"]
    elif tool_name == 'fetch_peer_ratios':
        return {}
    elif tool_name == 'fetch_market_share':
        return {}
    elif tool_name == 'fetch_growth_estimates':
        return {}
    elif tool_name == 'fetch_analyst_recommendations':
        return {}
    elif tool_name == 'fetch_earnings_surprises':
        return {}
    elif tool_name == 'fetch_sec_filings':
        return {}
    elif tool_name == 'fetch_price_volatility':
        return {}
    else:
        return {}

def mock_analyze(self, data, focus=None, symbol=""):
    """Mock implementation of analyze method."""
    return {
        "analysis_type": focus if focus else "general_financial",
        "symbol": symbol,
        "timestamp": "2023-06-01 10:00:00",
        "insights": f"This is a mock analysis for {symbol} focusing on {focus if focus else 'general financial performance'}.",
        "key_points": [
            f"Key point 1 for {symbol}",
            f"Key point 2 for {symbol}",
            f"Key point 3 for {symbol}"
        ],
        "sentiment": "positive",
        "confidence": "high"
    }

def mock_plan_next(self, analysis_result, iteration, max_iterations, completed_focus_areas, required_focus_areas):
    """Mock implementation of plan_next method."""
    # If we've done less than 2 iterations, continue with a new focus
    if iteration < 2:
        next_focus = "competitive_analysis" if "financial_performance" in completed_focus_areas else "financial_performance"
        return {
            "continue_analysis": True,
            "next_focus": next_focus,
            "reasoning": f"Mock reasoning: Moving to {next_focus} after iteration {iteration}."
        }
    else:
        # Otherwise, move to summarization
        return {
            "continue_analysis": False,
            "next_focus": None,
            "reasoning": "Mock reasoning: Analysis complete after 2 iterations."
        }

def mock_summarize(self, analyses, symbol):
    """Mock implementation of summarize method."""
    return f"""# Investment Summary for {symbol}

## Executive Summary
This is a mock investment summary for {symbol}.

## Analysis Overview
* Symbol: {symbol}
* Analyses: {len(analyses)}

## Key Points
* Mock key point 1
* Mock key point 2
* Mock key point 3

## Recommendation
Based on our mock analysis, we recommend a BUY for {symbol}.
"""

def test_orchestrator_initialization():
    """Test the initialization of the DeepThinkingChain class."""
    print("=== Testing DeepThinkingChain initialization ===")
    
    # Initialize the DeepThinkingChain
    chain = DeepThinkingChain("TEST", max_iterations=3)
    
    # Verify that the agents are initialized correctly
    assert isinstance(chain.tool_agent, ToolAgent), "ToolAgent not initialized correctly"
    assert isinstance(chain.analysis_agent, AnalysisAgent), "AnalysisAgent not initialized correctly"
    assert isinstance(chain.planning_agent, PlanningAgent), "PlanningAgent not initialized correctly"
    assert isinstance(chain.summarization_agent, SummarizationAgent), "SummarizationAgent not initialized correctly"
    
    # Verify that the memory manager is initialized correctly
    assert isinstance(chain.memory_manager, MemoryManager), "MemoryManager not initialized correctly"
    assert chain.memory_manager.symbol == "TEST", "Memory manager symbol not set correctly"
    
    print("✅ DeepThinkingChain initialization test passed")

def test_simplified_workflow():
    """Test a simplified version of the analysis workflow."""
    print("\n=== Testing simplified analysis workflow ===")
    
    # Create a results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Apply patches for the test
    with patch.object(ToolAgent, 'execute_tool', mock_execute_tool), \
         patch.object(AnalysisAgent, 'analyze', mock_analyze), \
         patch.object(PlanningAgent, 'plan_next', mock_plan_next), \
         patch.object(SummarizationAgent, 'summarize', mock_summarize):
        
        # Initialize the DeepThinkingChain with a test symbol
        chain = DeepThinkingChain("TEST", max_iterations=3)
        
        # Run the analysis with a maximum of 2 iterations
        chain.max_iterations = 2
        summary_file = chain.run()
        
        # Verify that the summary file was created
        assert os.path.exists(summary_file), f"Summary file {summary_file} not created"
        
        # Read the summary file
        with open(summary_file, 'r') as f:
            summary_content = f.read()
        
        # Verify that the summary contains the expected content
        assert "Investment Summary for TEST" in summary_content, "Summary does not contain the expected title"
        assert "Executive Summary" in summary_content, "Summary does not contain an executive summary"
        assert "Recommendation" in summary_content, "Summary does not contain a recommendation"
        
        print(f"✅ Simplified workflow test passed. Summary saved to {summary_file}")
        
        # Clean up the test file
        try:
            os.remove(summary_file)
            print(f"Cleaned up test file: {summary_file}")
        except:
            print(f"Could not clean up test file: {summary_file}")

if __name__ == "__main__":
    # Run the tests
    test_orchestrator_initialization()
    test_simplified_workflow()
    
    print("\n✅ All tests passed!") 