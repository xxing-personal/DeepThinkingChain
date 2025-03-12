#!/usr/bin/env python3
"""
Test script for the ToolAgent to test the consolidated financial data tool.
"""

import json
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agents.tool_agent import ToolAgent

def print_section(title):
    """Print a section title with formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def main():
    """Main function to test the ToolAgent with the consolidated financial data tool."""
    # Initialize the tool agent
    print_section("Initializing Tool Agent")
    agent = ToolAgent()
    
    # Display available tools
    print_section("Available Tools")
    print(agent.get_tools_prompt())
    
    # Test company profile
    print_section("Company Profile")
    symbol = "NVDA"
    print(f"Getting company profile for: '{symbol}'")
    result = agent.execute_tool("financial_data", symbol=symbol, data_type="company_profile")
    print(json.dumps(result, indent=2))
    
    # Test income statement
    print_section("Income Statement")
    print(f"Getting income statement for: '{symbol}'")
    result = agent.execute_tool("financial_data", symbol=symbol, data_type="income_statement", limit=1)
    
    # Print only the first income statement to keep output manageable
    if isinstance(result, dict) and "income_statement" in result and isinstance(result["income_statement"], list):
        limited_results = result.copy()
        limited_results["income_statement"] = result["income_statement"][:1]
        print(json.dumps(limited_results, indent=2))
    else:
        print(json.dumps(result, indent=2))
    
    # Test balance sheet
    print_section("Balance Sheet")
    print(f"Getting balance sheet for: '{symbol}'")
    result = agent.execute_tool("financial_data", symbol=symbol, data_type="balance_sheet", limit=1)
    
    # Print only the first balance sheet to keep output manageable
    if isinstance(result, dict) and "balance_sheet" in result and isinstance(result["balance_sheet"], list):
        limited_results = result.copy()
        limited_results["balance_sheet"] = result["balance_sheet"][:1]
        print(json.dumps(limited_results, indent=2))
    else:
        print(json.dumps(result, indent=2))
    
    # Test cash flow
    print_section("Cash Flow")
    print(f"Getting cash flow for: '{symbol}'")
    result = agent.execute_tool("financial_data", symbol=symbol, data_type="cash_flow", limit=1)
    
    # Print only the first cash flow to keep output manageable
    if isinstance(result, dict) and "cash_flow" in result and isinstance(result["cash_flow"], list):
        limited_results = result.copy()
        limited_results["cash_flow"] = result["cash_flow"][:1]
        print(json.dumps(limited_results, indent=2))
    else:
        print(json.dumps(result, indent=2))
    
    # Test financial ratios
    print_section("Financial Ratios")
    print(f"Getting financial ratios for: '{symbol}'")
    result = agent.execute_tool("financial_data", symbol=symbol, data_type="financial_ratios", limit=1)
    
    # Print only the first set of ratios to keep output manageable
    if isinstance(result, dict) and "ratios" in result and isinstance(result["ratios"], list):
        limited_results = result.copy()
        limited_results["ratios"] = result["ratios"][:1]
        print(json.dumps(limited_results, indent=2))
    else:
        print(json.dumps(result, indent=2))
    
    # Test peers
    print_section("Peers")
    print(f"Getting peers for: '{symbol}'")
    result = agent.execute_tool("financial_data", symbol=symbol, data_type="peers")
    print(json.dumps(result, indent=2))
    
    # Test financial performance (comprehensive analysis)
    print_section("Financial Performance")
    print(f"Getting financial performance for: '{symbol}'")
    result = agent.execute_tool("financial_data", symbol=symbol, data_type="financial_performance")
    
    # Print a summary of the financial performance to keep output manageable
    if isinstance(result, dict):
        summary = {
            "symbol": result.get("symbol"),
            "company_name": result.get("company_profile", {}).get("companyName"),
            "industry": result.get("company_profile", {}).get("industry"),
            "market_cap": result.get("company_profile", {}).get("mktCap"),
            "current_price": result.get("company_profile", {}).get("price"),
            "has_income_statement": "income_statement" in result and len(result["income_statement"].get("income_statement", [])) > 0,
            "has_balance_sheet": "balance_sheet" in result and len(result["balance_sheet"].get("balance_sheet", [])) > 0,
            "has_cash_flow": "cash_flow" in result and len(result["cash_flow"].get("cash_flow", [])) > 0,
            "has_financial_ratios": "financial_ratios" in result and len(result["financial_ratios"].get("ratios", [])) > 0
        }
        print(json.dumps(summary, indent=2))
    else:
        print(json.dumps(result, indent=2))
    
    print_section("Test Complete")
    print("The tool agent successfully tested the consolidated financial data tool.")

if __name__ == "__main__":
    main() 