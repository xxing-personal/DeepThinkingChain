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

# Import the Model class
from model import Model

# Load environment variables
load_dotenv()

class AnalysisAgent:
    """Agent performing detailed analysis and extraction of insights from raw financial data."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        """Initialize the AnalysisAgent with model configuration.
        
        Args:
            model_name: The model to use for analysis. Defaults to "gpt-4o".
        """
        # Initialize the Model class
        self.model = Model(model=model_name)
        
        # For backward compatibility, also initialize OpenAI client
        api_key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        
        # Check if API key is available
        if not api_key:
            print("Warning: OPENAI_API_KEY environment variable not found.")
            print("Please set your OpenAI API key as an environment variable.")
    
    def analyze(self, data: Dict[str, Any], focus: Optional[str] = None, symbol: str = "") -> Dict[str, Any]:
        """Analyzes financial data to identify key insights and investment factors.
        
        This method takes financial data (typically from the ToolAgent) and generates
        a structured analysis using the Model class. The analysis focuses on different
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
            Exception: If the model API call fails
        """
        # Generate the appropriate prompt based on focus
        if focus is None or focus == "financial_performance":
            prompt = initial_analysis_prompt(data, symbol)
        else:
            prompt = detailed_analysis_prompt(data, focus, symbol)
        
        try:
            # Use the Model class to analyze the data
            analysis_result = self.model.analyze_financial_data(
                data=data,
                focus=focus,
                symbol=symbol
            )
            
            # Extract the analysis text
            analysis_text = analysis_result["analysis"]
            
            # Process the analysis to extract key points and sentiment
            key_points = analysis_result["key_points"]
            sentiment = analysis_result["sentiment"]
            confidence = analysis_result["confidence"]
            
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
            
            # Fallback to the original OpenAI implementation if Model class fails
            try:
                # Call OpenAI API directly
                response = self.client.chat.completions.create(
                    model=self.model_name,
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
            except Exception as inner_e:
                print(f"Fallback analysis also failed: {str(inner_e)}")
                return {
                    "analysis_type": focus if focus else "general_financial",
                    "symbol": symbol,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "error": f"{str(e)} -> {str(inner_e)}",
                    "raw_data": data
                }
    
    def _extract_key_points(self, analysis_text: str) -> List[str]:
        """Extract key points from the analysis text.
        
        Args:
            analysis_text: The full analysis text
            
        Returns:
            List of key points extracted from the analysis
        """
        try:
            # Use the Model class to extract key points
            result = self.model.analyze_text(analysis_text, focus="key_points")
            
            # Try to parse the result
            if "parsed_result" in result and "key_points" in result["parsed_result"]:
                return result["parsed_result"]["key_points"]
            
            # If the above fails, try to parse the raw analysis text as JSON
            try:
                content = result["analysis"]
                key_points = json.loads(content).get("key_points", [])
                return key_points
            except (json.JSONDecodeError, KeyError):
                # Fallback to the model's built-in key point extraction
                return self.model._extract_key_points(analysis_text)
                
        except Exception as e:
            print(f"Error extracting key points: {str(e)}")
            
            # Fallback to direct OpenAI call if Model class fails
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
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
                
                return key_points
            except Exception as inner_e:
                print(f"Fallback key point extraction also failed: {str(inner_e)}")
                
                # Simple extraction based on bullet points or numbered lists
                lines = analysis_text.split('\n')
                key_points = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('•') or line.startswith('-') or line.startswith('*') or \
                       (line.startswith(tuple('1234567890')) and '. ' in line[:5]):
                        point = line.lstrip('•-*1234567890. ')
                        if point:
                            key_points.append(point)
                
                # If no bullet points found, use the first few sentences
                if not key_points:
                    sentences = analysis_text.split('.')[:3]
                    key_points = [s.strip() + '.' for s in sentences if len(s.strip()) > 20]
                
                return key_points

    def _determine_sentiment(self, analysis_text: str) -> Dict[str, str]:
        """Determine the overall sentiment and confidence level from the analysis text.
        
        Args:
            analysis_text: The full analysis text
            
        Returns:
            Dict with 'sentiment' and 'confidence' keys
        """
        try:
            # Use the Model class to determine sentiment
            result = self.model.analyze_text(analysis_text, focus="sentiment")
            
            # Try to parse the result
            if "parsed_result" in result and "sentiment" in result["parsed_result"]:
                return {
                    "sentiment": result["parsed_result"]["sentiment"],
                    "confidence": result["parsed_result"]["confidence"]
                }
            
            # If the above fails, try to parse the raw analysis text as JSON
            try:
                content = result["analysis"]
                sentiment_data = json.loads(content)
                return {
                    "sentiment": sentiment_data.get("sentiment", "neutral"),
                    "confidence": sentiment_data.get("confidence", "medium")
                }
            except (json.JSONDecodeError, KeyError):
                # Fallback to the model's built-in sentiment detection
                return self.model._determine_sentiment(analysis_text)
                
        except Exception as e:
            print(f"Error determining sentiment: {str(e)}")
            
            # Fallback to direct OpenAI call if Model class fails
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
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
            except Exception as inner_e:
                print(f"Fallback sentiment determination also failed: {str(inner_e)}")
                
                # Simple rule-based sentiment analysis
                lower_text = analysis_text.lower()
                
                # Determine sentiment
                sentiment = "neutral"
                if any(word in lower_text for word in ["bullish", "positive", "strong buy", "recommend buy"]):
                    sentiment = "positive"
                elif any(word in lower_text for word in ["bearish", "negative", "sell", "avoid"]):
                    sentiment = "negative"
                
                # Determine confidence
                confidence = "medium"
                if any(word in lower_text for word in ["high confidence", "strongly", "certainly", "definitely"]):
                    confidence = "high"
                elif any(word in lower_text for word in ["low confidence", "uncertain", "unclear", "might", "may"]):
                    confidence = "low"
                
                return {
                    "sentiment": sentiment,
                    "confidence": confidence
                }
    
    def summarize_analyses(self, analyses: List[Dict[str, Any]], symbol: str) -> str:
        """Summarize multiple analyses into a comprehensive investment recommendation.
        
        Args:
            analyses: List of analysis results from previous iterations
            symbol: Stock symbol being analyzed
            
        Returns:
            str: A comprehensive investment summary in markdown format
        """
        # Prepare the prompt with all analyses
        analyses_text = ""
        for i, analysis in enumerate(analyses, 1):
            focus = analysis.get("focus", analysis.get("analysis_type", "general"))
            insights = analysis.get("insights", analysis.get("analysis", ""))
            sentiment = analysis.get("sentiment", "neutral")
            confidence = analysis.get("confidence", "medium")
            
            analyses_text += f"\n\n## Analysis {i}: {focus.replace('_', ' ').title()}\n"
            analyses_text += f"Sentiment: {sentiment}, Confidence: {confidence}\n\n"
            analyses_text += insights[:2000]  # Limit length to avoid token limits
            analyses_text += "\n\n---"
        
        # Create the prompt
        prompt = f"""
        # Investment Summary for {symbol}
        
        Based on the following analyses, create a comprehensive investment summary for {symbol}.
        
        {analyses_text}
        
        Please provide a well-structured investment summary in markdown format with the following sections:
        
        1. Executive Summary (brief overview and recommendation)
        2. Company Overview (business model, market position)
        3. Financial Analysis (key metrics, financial health)
        4. Growth Prospects (future growth opportunities)
        5. Competitive Advantages (moat, strengths)
        6. Risk Factors (challenges, threats)
        7. Valuation (fair value estimate, valuation metrics)
        8. Investment Recommendation (final recommendation with rationale)
        
        Include specific data points from the analyses to support your conclusions.
        """
        
        try:
            # Use the Model class to generate the summary
            system_prompt = "You are a professional investment analyst creating comprehensive stock analyses. Your summaries are well-structured, data-driven, and balanced, considering both bullish and bearish arguments."
            
            summary = self.model.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=4000
            )
            
            return summary
            
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            
            # Fallback to direct OpenAI call if Model class fails
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a financial advisor providing investment recommendations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=4000
                )
                
                # Return the summary text
                return response.choices[0].message.content
                
            except Exception as inner_e:
                print(f"Fallback summary generation also failed: {str(inner_e)}")
                
                # Generate a basic summary if all else fails
                return f"""
                # Investment Summary for {symbol}
                
                ## Executive Summary
                
                Due to technical issues, a comprehensive analysis could not be generated. 
                Based on the available data, {symbol} appears to be a {analyses[-1].get('sentiment', 'neutral')} investment opportunity.
                
                ## Analysis Summary
                
                {', '.join([a.get('key_points', ['No key points available'])[0] for a in analyses[:3]])}
                
                *This is a limited summary due to technical issues.*
                """


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
