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

# Import prompt templates
from prompts.analysis_prompts import (
    FINANCIAL_ANALYSIS_TEMPLATE,
    COMPETITIVE_ANALYSIS_TEMPLATE,
    GROWTH_ANALYSIS_TEMPLATE,
    RISK_ASSESSMENT_TEMPLATE,
    SUMMARY_TEMPLATE
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
        # Determine which template to use based on focus
        template = self._select_template(focus)
        
        # Format the data for the prompt
        formatted_data = self._format_data(data)
        
        # Create the prompt
        prompt = template.format(symbol=symbol, data=formatted_data)
        
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
            sentiment, confidence = self._determine_sentiment(analysis_text)
            
            # Construct the result
            result = {
                "analysis_type": focus if focus else "general_financial",
                "symbol": symbol,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "insights": analysis_text,
                "key_points": key_points,
                "sentiment": sentiment,
                "confidence": confidence,
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
    
    def _select_template(self, focus: Optional[str]) -> str:
        """Select the appropriate template based on the focus area.
        
        Args:
            focus: The focus area for the analysis
            
        Returns:
            The template string to use
        """
        if focus == "competitive_analysis":
            return COMPETITIVE_ANALYSIS_TEMPLATE
        elif focus == "growth_prospects":
            return GROWTH_ANALYSIS_TEMPLATE
        elif focus == "risk_assessment":
            return RISK_ASSESSMENT_TEMPLATE
        else:
            # Default to general financial analysis
            return FINANCIAL_ANALYSIS_TEMPLATE
    
    def _format_data(self, data: Dict[str, Any]) -> str:
        """Format the data for inclusion in the prompt.
        
        Args:
            data: The data to format
            
        Returns:
            A formatted string representation of the data
        """
        # For large data structures, we need to be selective about what we include
        # to avoid exceeding token limits
        formatted_parts = []
        
        for key, value in data.items():
            if isinstance(value, dict) and "error" in value:
                # Skip data with errors
                continue
                
            # Format based on data type
            if key == "company_profile":
                formatted_parts.append(f"COMPANY PROFILE:\n{json.dumps(value, indent=2)}")
            elif key == "financial_ratios":
                formatted_parts.append(f"FINANCIAL RATIOS:\n{json.dumps(value, indent=2)}")
            elif key == "income_statement":
                # For large datasets, include only the most recent periods
                if isinstance(value, list) and len(value) > 0:
                    recent_data = value[:2]  # Most recent 2 periods
                    formatted_parts.append(f"RECENT INCOME STATEMENTS:\n{json.dumps(recent_data, indent=2)}")
            elif key == "balance_sheet":
                if isinstance(value, list) and len(value) > 0:
                    recent_data = value[:2]  # Most recent 2 periods
                    formatted_parts.append(f"RECENT BALANCE SHEETS:\n{json.dumps(recent_data, indent=2)}")
            elif key == "cash_flow":
                if isinstance(value, list) and len(value) > 0:
                    recent_data = value[:2]  # Most recent 2 periods
                    formatted_parts.append(f"RECENT CASH FLOW STATEMENTS:\n{json.dumps(recent_data, indent=2)}")
            elif key == "peers":
                formatted_parts.append(f"PEER COMPANIES:\n{json.dumps(value, indent=2)}")
            elif key == "peer_profiles":
                formatted_parts.append(f"PEER PROFILES:\n{json.dumps(value, indent=2)}")
            elif key == "growth_estimates":
                formatted_parts.append(f"GROWTH ESTIMATES:\n{json.dumps(value, indent=2)}")
            elif key == "analyst_recommendations":
                formatted_parts.append(f"ANALYST RECOMMENDATIONS:\n{json.dumps(value, indent=2)}")
            elif key == "key_metrics":
                if isinstance(value, list) and len(value) > 0:
                    recent_data = value[:2]  # Most recent 2 periods
                    formatted_parts.append(f"KEY METRICS:\n{json.dumps(recent_data, indent=2)}")
            elif key == "dcf":
                formatted_parts.append(f"DCF VALUATION:\n{json.dumps(value, indent=2)}")
            elif key == "sec_filings":
                if isinstance(value, list) and len(value) > 0:
                    recent_data = value[:5]  # Most recent 5 filings
                    formatted_parts.append(f"RECENT SEC FILINGS:\n{json.dumps(recent_data, indent=2)}")
            else:
                # For other data types, include a summary
                formatted_parts.append(f"{key.upper()}:\n{str(value)[:500]}...")
        
        return "\n\n".join(formatted_parts)
    
    def _extract_key_points(self, analysis_text: str) -> List[str]:
        """Extract key points from the analysis text.
        
        Args:
            analysis_text: The full analysis text
            
        Returns:
            List of key points extracted from the analysis
        """
        # In a more sophisticated implementation, we could use another LLM call
        # to extract key points. For now, we'll use a simple heuristic approach.
        
        key_points = []
        
        # Split by newlines and look for bullet points or numbered items
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            # Check for bullet points, numbered lists, or lines starting with "Key"
            if (line.startswith('-') or 
                line.startswith('•') or 
                (line.startswith(tuple('123456789')) and '. ' in line[:5]) or
                line.lower().startswith('key')):
                
                # Clean up the line
                clean_line = line
                if line.startswith('-') or line.startswith('•'):
                    clean_line = line[1:].strip()
                elif line.startswith(tuple('123456789')) and '. ' in line[:5]:
                    clean_line = line[line.find('.')+1:].strip()
                
                if clean_line and len(clean_line) > 10:  # Avoid very short points
                    key_points.append(clean_line)
        
        # If we couldn't find any key points with the above method,
        # just take the first few sentences
        if not key_points:
            sentences = analysis_text.split('.')
            key_points = [s.strip() + '.' for s in sentences[:5] if len(s.strip()) > 20]
        
        # Limit to top 10 key points
        return key_points[:10]
    
    def _determine_sentiment(self, analysis_text: str) -> tuple:
        """Determine the overall sentiment and confidence from the analysis text.
        
        Args:
            analysis_text: The full analysis text
            
        Returns:
            Tuple of (sentiment, confidence) where:
            - sentiment is one of "positive", "neutral", or "negative"
            - confidence is one of "high", "medium", or "low"
        """
        # In a more sophisticated implementation, we could use another LLM call
        # or a sentiment analysis model. For now, we'll use a simple keyword approach.
        
        # Positive keywords
        positive_words = [
            'growth', 'strong', 'opportunity', 'upside', 'outperform',
            'buy', 'attractive', 'undervalued', 'recommend', 'positive',
            'advantage', 'moat', 'leader', 'innovative', 'profitable'
        ]
        
        # Negative keywords
        negative_words = [
            'risk', 'challenge', 'threat', 'decline', 'underperform',
            'sell', 'overvalued', 'avoid', 'negative', 'weak',
            'competition', 'pressure', 'concern', 'debt', 'uncertain'
        ]
        
        # Count occurrences
        positive_count = sum(analysis_text.lower().count(word) for word in positive_words)
        negative_count = sum(analysis_text.lower().count(word) for word in negative_words)
        
        # Determine sentiment
        if positive_count > negative_count * 1.5:
            sentiment = "positive"
        elif negative_count > positive_count * 1.5:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Determine confidence based on the difference
        total_count = positive_count + negative_count
        if total_count == 0:
            confidence = "low"
        else:
            difference = abs(positive_count - negative_count) / total_count
            if difference > 0.5:
                confidence = "high"
            elif difference > 0.2:
                confidence = "medium"
            else:
                confidence = "low"
        
        return sentiment, confidence
    
    def summarize_analyses(self, analyses: List[Dict[str, Any]], symbol: str) -> str:
        """Generates a comprehensive final investment recommendation summary.
        
        Args:
            analyses: List of analysis results from previous iterations
            symbol: Stock symbol being analyzed
            
        Returns:
            A comprehensive investment recommendation summary
        """
        # Format the analyses for the prompt
        formatted_analyses = json.dumps([
            {
                "analysis_type": a.get("analysis_type", "unknown"),
                "insights": a.get("insights", ""),
                "key_points": a.get("key_points", []),
                "sentiment": a.get("sentiment", "neutral")
            }
            for a in analyses
        ], indent=2)
        
        # Create the prompt using the summary template
        prompt = SUMMARY_TEMPLATE.format(symbol=symbol, analyses=formatted_analyses)
        
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
