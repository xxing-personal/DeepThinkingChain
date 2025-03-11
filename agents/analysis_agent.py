"""
Analysis Agent for the Deep Thinking Chain.

This module contains the AnalysisAgent class which is responsible for analyzing
financial data and extracting investment insights using the OpenAI API.
"""

import json
import os
from typing import Dict, Any, Optional, List, Union
import time
from openai import OpenAI
from dotenv import load_dotenv

# Import prompt templates and functions
from prompts.analysis_prompts import (
    FINANCIAL_ANALYSIS_TEMPLATE,
    COMPETITIVE_ANALYSIS_TEMPLATE,
    GROWTH_ANALYSIS_TEMPLATE,
    RISK_ASSESSMENT_TEMPLATE,
    SUMMARY_TEMPLATE,
    initial_analysis_prompt,
    detailed_analysis_prompt,
    planning_prompt
)

# Load environment variables
load_dotenv()

class AnalysisAgent:
    """Agent performing detailed analysis and extraction of insights from raw financial data."""
    
    def __init__(self, model: str = "gpt-4o"):
        """Initialize the AnalysisAgent with OpenAI configuration.
        
        Args:
            model: The OpenAI model to use for analysis. Defaults to "gpt-4o".
        """
        # First check if API key is in environment, then fall back to .env file
        api_key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        # Check if API key is available
        if not api_key:
            print("Warning: OPENAI_API_KEY environment variable not found.")
            print("Please set your OpenAI API key as an environment variable.")
    
    def analyze(self, data: Dict[str, Any], focus: Optional[str] = None, symbol: str = "") -> Dict[str, Any]:
        """Analyzes financial data to identify key insights and investment factors.
        
        This method takes financial data (typically from the ToolAgent) and generates
        a structured analysis using the OpenAI API. The analysis focuses on different
        aspects of the investment opportunity based on the specified focus area.
        
        Args:
            data: Dictionary containing financial data to analyze
            focus: Optional focus area for the analysis. If None, a general financial
                  analysis will be performed. Valid values include:
                  - "financial_performance"
                  - "competitive_analysis"
                  - "growth_prospects"
                  - "risk_assessment"
            symbol: Stock symbol being analyzed (e.g., 'NVDA')
            
        Returns:
            Dict containing structured analysis results with the following keys:
            - "analysis_type": The type of analysis performed
            - "symbol": The stock symbol analyzed
            - "timestamp": When the analysis was performed
            - "insights": The detailed analysis text
            - "key_points": List of key points extracted from the analysis
            - "sentiment": Overall sentiment (positive, neutral, negative)
            - "confidence": Confidence level in the analysis (high, medium, low)
            
        Raises:
            Exception: If the OpenAI API call fails
        """
        # Generate the appropriate prompt based on focus
        if focus is None or focus == "financial_performance":
            prompt = initial_analysis_prompt(data, symbol)
        else:
            prompt = detailed_analysis_prompt(data, focus, symbol)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial analyst providing detailed investment analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            # Extract the analysis text
            analysis_text = response.choices[0].message.content
            
            # Process the analysis to extract key points and sentiment
            key_points = self._extract_key_points(analysis_text)
            sentiment_result = self._determine_sentiment(analysis_text)
            
            # Construct the result
            result = {
                "analysis_type": focus if focus else "general_financial",
                "symbol": symbol,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "insights": analysis_text,
                "key_points": key_points,
                "sentiment": sentiment_result["sentiment"],
                "confidence": sentiment_result["confidence"],
                "raw_data": data  # Include the original data for reference
            }
            
            return result
            
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            return {
                "analysis_type": focus if focus else "general_financial",
                "symbol": symbol,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "raw_data": data
            }
    
    def _extract_key_points(self, analysis_text: str) -> List[str]:
        """Extract key points from the analysis text.
        
        Args:
            analysis_text: The full analysis text
            
        Returns:
            List of key points extracted from the analysis
        """
        # Use OpenAI to extract key points
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract the 5-7 most important key points from this financial analysis. Return ONLY a JSON array of strings with no explanation."},
                    {"role": "user", "content": analysis_text}
                ],
                temperature=0.2,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            content = response.choices[0].message.content
            key_points = json.loads(content).get("key_points", [])
            
            # Ensure we have at least some key points
            if not key_points:
                # Fallback to simple extraction
                key_points = [line.strip() for line in analysis_text.split("\n") 
                             if line.strip().startswith("-") or line.strip().startswith("*")][:7]
            
            return key_points
        except Exception as e:
            print(f"Error extracting key points: {e}")
            # Fallback to simple extraction
            return [line.strip() for line in analysis_text.split("\n") 
                   if line.strip().startswith("-") or line.strip().startswith("*")][:7]
    
    def _determine_sentiment(self, analysis_text: str) -> Dict[str, str]:
        """Determine the overall sentiment and confidence level from the analysis.
        
        Args:
            analysis_text: The full analysis text
            
        Returns:
            Dict with sentiment and confidence keys
        """
        # Use OpenAI to determine sentiment
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Based on this financial analysis, determine the overall investment sentiment (positive, neutral, negative) and confidence level (high, medium, low). Return ONLY a JSON object with 'sentiment' and 'confidence' keys."},
                    {"role": "user", "content": analysis_text}
                ],
                temperature=0.2,
                max_tokens=100,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return {
                "sentiment": result.get("sentiment", "neutral"),
                "confidence": result.get("confidence", "medium")
            }
        except Exception as e:
            print(f"Error determining sentiment: {e}")
            return {"sentiment": "neutral", "confidence": "medium"}
    
    def summarize_analyses(self, analyses: List[Dict[str, Any]], symbol: str) -> str:
        """Generates a comprehensive final investment recommendation summary.
        
        Args:
            analyses: List of analysis results from previous iterations
            symbol: Stock symbol being analyzed
            
        Returns:
            A comprehensive investment recommendation summary
        """
        # Generate the planning prompt using the new function
        prompt = planning_prompt(analyses, symbol)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial advisor providing investment recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            # Return the summary text
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error during summarization: {str(e)}")
            return f"Error generating summary: {str(e)}"


if __name__ == "__main__":
    """Test the AnalysisAgent functionality."""
    import sys
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key as an environment variable.")
        sys.exit(1)
    
    # Sample data for testing
    sample_data = {
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
        }
    }
    
    # Initialize the agent
    agent = AnalysisAgent()
    
    # Test the analyze method
    print("\n" + "="*50)
    print("Testing AnalysisAgent with sample data...")
    print("="*50 + "\n")
    
    result = agent.analyze(sample_data, symbol="AAPL")
    
    print(f"Analysis Type: {result['analysis_type']}")
    print(f"Symbol: {result['symbol']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Confidence: {result['confidence']}")
    
    print("\nKey Points:")
    for i, point in enumerate(result['key_points'], 1):
        print(f"{i}. {point}")
    
    print("\nInsights Preview:")
    print(result['insights'][:500] + "...\n")
    
    print("="*50)
    print("AnalysisAgent test complete")
    print("="*50)
