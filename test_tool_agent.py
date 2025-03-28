#!/usr/bin/env python3
"""
Test script for the ToolAgent.

This script demonstrates how to use the ToolAgent to load and execute a specific tool.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the project directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the ToolAgent
from agents.tool_agent import ToolAgent

# Load environment variables
load_dotenv()

def main():
    """Run the ToolAgent with a specific tool."""
    
    # First, let's show all available tools using the default ToolAgent (loads all tools)
    print("=== Available Tools ===")
    all_tools_agent = ToolAgent()
    print(all_tools_agent.get_tools_prompt())
    print("\n")
    
    # Now, let's use the ToolAgent with a specific tool - for example, the financial data tool
    tool_name = "financial_data"
    
    # Parameters for the financial data tool
    tool_params = {
        "symbol": "AAPL",
        "data_type": "company_profile"
    }
    
    print(f"=== Running ToolAgent with specific tool: {tool_name} ===")
    print(f"Parameters: {json.dumps(tool_params, indent=2)}")
    
    # Create the ToolAgent with the specific tool
    agent = ToolAgent(tools_name=tool_name, tools_params=tool_params)
    
    # Make sure the tool was loaded successfully
    if tool_name in agent.list_tools():
        # Execute the tool
        result = agent.execute_tool()
        
        # Print the result
        print("\n=== Tool Execution Result ===")
        print(agent._format_response_to_str(result))
    else:
        print(f"Error: Tool '{tool_name}' could not be loaded.")
        
    # Let's try another tool, the Google search tool
    tool_name = "google_search"
    
    # Parameters for the Google search tool
    # Note: Based on the GoogleSearchTool class, it accepts 'query' and optional 'filter_year'
    tool_params = {
        "query": "Apple Inc. latest financial performance",
        "filter_year": 2023  # This is optional
    }
    
    print(f"\n\n=== Running ToolAgent with specific tool: {tool_name} ===")
    print(f"Parameters: {json.dumps(tool_params, indent=2)}")
    
    # Create the ToolAgent with the specific tool
    agent = ToolAgent(tools_name=tool_name, tools_params=tool_params)
    
    # Make sure the tool was loaded successfully
    if tool_name in agent.list_tools():
        # Execute the tool
        result = agent.execute_tool()
        
        # Print the result
        print("\n=== Tool Execution Result ===")
        print(agent._format_response_to_str(result))
    else:
        print(f"Error: Tool '{tool_name}' could not be loaded.")
    
    # Let's try the DuckDuckGo search tool
    tool_name = "duckduckgo_search"
    
    # Parameters for the DuckDuckGo search tool
    tool_params = {
        "query": "Apple Inc. latest financial performance"
    }
    
    print(f"\n\n=== Running ToolAgent with specific tool: {tool_name} ===")
    print(f"Parameters: {json.dumps(tool_params, indent=2)}")
    
    # Create the ToolAgent with the specific tool
    agent = ToolAgent(tools_name=tool_name, tools_params=tool_params)
    
    # Make sure the tool was loaded successfully
    if tool_name in agent.list_tools():
        # Execute the tool
        result = agent.execute_tool()
        
        # Print the result
        print("\n=== Tool Execution Result ===")
        print(agent._format_response_to_str(result))
    else:
        print(f"Error: Tool '{tool_name}' could not be loaded.")

if __name__ == "__main__":
    main() 