"""
Test script for the SummarizationAgent.

This script tests the SummarizationAgent's ability to compile and synthesize
multiple analyses into a comprehensive investment summary.
"""

import os
from dotenv import load_dotenv
from agents.summarization_agent import SummarizationAgent

# Load environment variables
load_dotenv()

def test_summarization_agent():
    """Test the SummarizationAgent with sample analyses."""
    # Sample analyses for testing
    sample_analyses = [
        {
            "analysis_type": "financial_performance",
            "symbol": "NVDA",
            "timestamp": "2023-01-01 12:00:00",
            "insights": "NVIDIA shows exceptional financial performance with industry-leading margins and strong revenue growth. The company has successfully capitalized on the AI boom, with data center revenue growing significantly. Its balance sheet is solid with ample cash reserves.",
            "key_points": [
                "Industry-leading gross margins above 70%",
                "Strong revenue growth driven by AI and data center segments",
                "Solid balance sheet with significant cash reserves",
                "High R&D investment maintaining technological edge"
            ],
            "sentiment": "positive",
            "confidence": "high"
        },
        {
            "analysis_type": "competitive_analysis",
            "symbol": "NVDA",
            "timestamp": "2023-01-01 13:00:00",
            "insights": "NVIDIA maintains a dominant position in the GPU market, particularly for AI applications. The company's CUDA ecosystem and software stack create significant barriers to entry. Competition from AMD, Intel, and custom AI chips from cloud providers represents a growing challenge.",
            "key_points": [
                "Dominant market share in AI GPUs",
                "CUDA ecosystem creates strong moat",
                "Software stack adds significant value beyond hardware",
                "Growing competition from AMD, Intel, and custom AI chips",
                "Strong partnerships with major cloud providers"
            ],
            "sentiment": "positive",
            "confidence": "high"
        },
        {
            "analysis_type": "growth_prospects",
            "symbol": "NVDA",
            "timestamp": "2023-01-01 14:00:00",
            "insights": "NVIDIA's growth prospects remain strong, driven by expanding AI applications, data center growth, and emerging opportunities in automotive and edge computing. The company is well-positioned to benefit from the ongoing AI revolution across industries.",
            "key_points": [
                "Expanding AI applications across industries",
                "Growing data center market with increasing GPU adoption",
                "Emerging opportunities in automotive and edge computing",
                "Potential for further software revenue growth",
                "International expansion opportunities"
            ],
            "sentiment": "positive",
            "confidence": "medium"
        },
        {
            "analysis_type": "risk_assessment",
            "symbol": "NVDA",
            "timestamp": "2023-01-01 15:00:00",
            "insights": "While NVIDIA faces several risks, its strong market position and technological leadership mitigate many concerns. Key risks include cyclicality in demand, increasing competition, regulatory challenges related to acquisitions, and high valuation expectations.",
            "key_points": [
                "Cyclicality in semiconductor demand",
                "Increasing competition in AI chips",
                "Regulatory challenges for acquisitions",
                "High valuation creating elevated expectations",
                "Concentration risk in data center segment",
                "Geopolitical tensions affecting supply chain"
            ],
            "sentiment": "neutral",
            "confidence": "high"
        }
    ]
    
    # Initialize the agent
    agent = SummarizationAgent()
    
    # Test the summarize method
    print("\n" + "="*50)
    print("Testing SummarizationAgent with NVIDIA sample analyses...")
    print("="*50 + "\n")
    
    summary = agent.summarize(sample_analyses, "NVDA")
    
    # Save the summary to a file
    output_file = "results/NVDA_test_summary.md"
    os.makedirs("results", exist_ok=True)
    
    with open(output_file, "w") as f:
        f.write(summary)
    
    print(f"Summary generated and saved to {output_file}")
    print("\nSummary Preview:")
    print("-" * 50)
    print(summary[:500] + "..." if len(summary) > 500 else summary)
    print("-" * 50)
    
    # Test with empty analyses
    print("\nTesting with empty analyses...")
    empty_summary = agent.summarize([], "TEST")
    print("Empty Summary:")
    print(empty_summary)
    
    # Test with minimal analyses
    print("\nTesting with minimal analysis...")
    minimal_analysis = [{
        "analysis_type": "general_financial",
        "symbol": "TEST",
        "key_points": ["Test point 1", "Test point 2"]
    }]
    minimal_summary = agent.summarize(minimal_analysis, "TEST")
    print("Minimal Summary Preview:")
    print(minimal_summary[:200] + "..." if len(minimal_summary) > 200 else minimal_summary)
    
    print("\n" + "="*50)
    print("SummarizationAgent test complete")
    print("="*50)

if __name__ == "__main__":
    # Check if OpenAI API key is set
    api_key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key as an environment variable.")
        import sys
        sys.exit(1)
    
    # Run the tests
    test_summarization_agent() 