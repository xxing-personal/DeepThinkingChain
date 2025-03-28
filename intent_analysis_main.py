#!/usr/bin/env python
"""
Main script to run the IntentAnalysisAgent with a specific query.

This script demonstrates how to initialize and run the IntentAnalysisAgent
with a given query and model.
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

def main():
    """Run the IntentAnalysisAgent with a specific query."""
    
    # The query to analyze
    query = "is NVDA a buy or sell"
    
    # The model to use
    model_name = "openai/o3-mini"
    
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
    print("\n=== Intent Analysis Results ===")
    print(formatted_result)
    
    # Print a human-readable response
    print("\n=== Human Readable Analysis ===")
    print(agent._format_response_to_str(result))
    
    return result

if __name__ == "__main__":
    main() 