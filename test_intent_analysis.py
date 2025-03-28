#!/usr/bin/env python
"""
Test script for the IntentAnalysisAgent with multiple queries.

This script tests the IntentAnalysisAgent with various queries to evaluate its
intent analysis capabilities.
"""

import os
import sys
import logging
from dotenv import load_dotenv
import json

# Set up the Python path to include the DeepThinkingChain package directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables (for API keys)
load_dotenv()

# Import IntentAnalysisAgent directly
from agents import IntentAnalysisAgent

def test_intent_analysis(query, model_name="openai/o3-mini"):
    """Run the IntentAnalysisAgent with a specific query.
    
    Args:
        query: The query to analyze
        model_name: The model to use for analysis
        
    Returns:
        The analysis results
    """
    # Create the agent
    logger.info(f"Initializing IntentAnalysisAgent with model {model_name}")
    agent = IntentAnalysisAgent(
        prompt_template_name="intent_analysis",
        model_name=model_name
    )
    
    # Run the agent with the query
    logger.info(f"Running IntentAnalysisAgent with query: {query}")
    result = agent.analyze_intent(query)
    
    # Format and print the results
    formatted_result = json.dumps(result, indent=2)
    print(f"\n=== Intent Analysis for: '{query}' ===")
    print(formatted_result)
    
    # Print a human-readable response
    print("\n=== Human Readable Analysis ===")
    print(agent._format_response_to_str(result))
    
    return result

def main():
    """Test the IntentAnalysisAgent with multiple queries."""
    
    # Define a list of test cases
    test_cases = [
        "Is NVDA a buy or sell?",
        "What are the growth prospects for Tesla over the next 5 years?",
        "Compare Apple, Microsoft, and Google as long-term investments",
        "Should I invest in cryptocurrency right now?",
        "What impact will rising interest rates have on the banking sector?"
    ]
    
    # Run tests for each case
    for query in test_cases:
        test_intent_analysis(query)
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main() 