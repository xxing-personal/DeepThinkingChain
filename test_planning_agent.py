"""
Test script for the PlanningAgent.

This script tests the PlanningAgent's ability to determine the next steps
in the investment analysis process based on current analysis results.
"""

import os
from dotenv import load_dotenv
from agents.planning_agent import PlanningAgent

# Load environment variables
load_dotenv()

def test_planning_agent():
    """Test the PlanningAgent with various scenarios."""
    # Initialize the agent
    agent = PlanningAgent()
    
    # Sample analysis results for testing
    financial_analysis = {
        "analysis_type": "financial_performance",
        "symbol": "AAPL",
        "timestamp": "2023-01-01 12:00:00",
        "insights": "Apple shows strong financial performance with robust cash flows and high margins. However, there are some concerns about future growth prospects that may require further research.",
        "key_points": [
            "Strong balance sheet with significant cash reserves",
            "High profit margins compared to industry peers",
            "Consistent revenue growth over the past 5 years",
            "Some uncertainty about future product innovation",
            "Potential market saturation in key product categories"
        ],
        "sentiment": "positive",
        "confidence": "medium"
    }
    
    competitive_analysis = {
        "analysis_type": "competitive_analysis",
        "symbol": "AAPL",
        "timestamp": "2023-01-01 13:00:00",
        "insights": "Apple maintains a strong competitive position in its core markets. The company's brand strength and ecosystem create significant barriers to entry. However, competition is intensifying in key product categories.",
        "key_points": [
            "Strong brand value and customer loyalty",
            "Integrated ecosystem creates switching costs",
            "Premium pricing strategy maintains margins",
            "Increasing competition in smartphone market",
            "Potential regulatory challenges to App Store model"
        ],
        "sentiment": "positive",
        "confidence": "high"
    }
    
    risk_analysis = {
        "analysis_type": "risk_assessment",
        "symbol": "AAPL",
        "timestamp": "2023-01-01 14:00:00",
        "insights": "While Apple faces several risks, its strong financial position and diversified product portfolio mitigate many concerns. Supply chain dependencies and regulatory scrutiny remain key challenges.",
        "key_points": [
            "Concentration risk in iPhone revenue",
            "Supply chain dependencies on China",
            "Regulatory scrutiny in multiple markets",
            "Strong cash position mitigates financial risks",
            "Product diversification reduces overall risk"
        ],
        "sentiment": "neutral",
        "confidence": "high"
    }
    
    # Test scenarios
    print("\n" + "="*50)
    print("Testing PlanningAgent with various scenarios")
    print("="*50)
    
    # Scenario 1: First iteration with financial analysis
    print("\nScenario 1: First iteration with financial analysis")
    result1 = agent.plan_next(financial_analysis, iteration=1)
    print(f"Decision: {'Continue' if result1['continue_analysis'] else 'Summarize'}")
    print(f"Next focus: {result1['next_focus']}")
    print(f"Reasoning: {result1['reasoning']}")
    print(f"Completion: {result1['completion_percentage']}%")
    
    # Scenario 2: Second iteration with financial and competitive analyses
    print("\nScenario 2: Second iteration with financial and competitive analyses")
    result2 = agent.plan_next(
        competitive_analysis, 
        iteration=2,
        previous_analyses=[financial_analysis]
    )
    print(f"Decision: {'Continue' if result2['continue_analysis'] else 'Summarize'}")
    print(f"Next focus: {result2['next_focus']}")
    print(f"Reasoning: {result2['reasoning']}")
    print(f"Completion: {result2['completion_percentage']}%")
    
    # Scenario 3: Third iteration with all required analyses
    print("\nScenario 3: Third iteration with all required analyses")
    result3 = agent.plan_next(
        risk_analysis, 
        iteration=3,
        previous_analyses=[financial_analysis, competitive_analysis]
    )
    print(f"Decision: {'Continue' if result3['continue_analysis'] else 'Summarize'}")
    print(f"Next focus: {result3['next_focus'] if result3['continue_analysis'] else 'None'}")
    print(f"Reasoning: {result3['reasoning']}")
    print(f"Completion: {result3['completion_percentage']}%")
    
    # Scenario 4: Low confidence analysis
    print("\nScenario 4: Low confidence analysis")
    low_confidence_analysis = financial_analysis.copy()
    low_confidence_analysis["confidence"] = "low"
    result4 = agent.plan_next(
        low_confidence_analysis, 
        iteration=3,
        previous_analyses=[competitive_analysis, risk_analysis]
    )
    print(f"Decision: {'Continue' if result4['continue_analysis'] else 'Summarize'}")
    print(f"Next focus: {result4['next_focus'] if result4['continue_analysis'] else 'None'}")
    print(f"Reasoning: {result4['reasoning']}")
    print(f"Completion: {result4['completion_percentage']}%")
    
    print("\n" + "="*50)
    print("PlanningAgent test complete")
    print("="*50)

if __name__ == "__main__":
    # Check if OpenAI API key is set (only needed for advanced focus determination)
    api_key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY environment variable not found.")
        print("Basic functionality will work, but advanced focus determination may fail.")
    
    # Run the tests
    test_planning_agent() 