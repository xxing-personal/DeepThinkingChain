"""
Analysis Agent for the Deep Thinking Chain.

This module contains the AnalysisAgent class which is responsible for analyzing
financial data and extracting investment insights using the OpenAI API.
"""

import json
import os
import re
from typing import Dict, Any, Optional, List, Union
import time
from dotenv import load_dotenv

# Import the prompt manager and helper functions
from prompts.prompt_manager import PromptManager
from prompts.prompt_helper import (
    format_data_for_prompt,
    format_analyses_for_prompt
)

# Import the Model class
from model import Model

# Load environment variables
load_dotenv()

# Initialize the prompt manager
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "templates")
prompt_manager = PromptManager(TEMPLATES_DIR)

class AnalysisAgent:
    """Agent performing detailed analysis and extraction of insights from raw financial data."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        """Initialize the AnalysisAgent with model configuration.
        
        Args:
            model_name: The model to use for analysis. Defaults to "gpt-4o".
        """
        # Initialize the Model class
        self.model = Model(model=model_name)
        self.model_name = model_name
        
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
        # Format the data for the prompt
        formatted_data = format_data_for_prompt(data)
        
        # Set up the context and questions based on focus
        context = f"You are analyzing financial data for {symbol}. " + \
                 f"Focus on {focus if focus else 'general financial performance'}."
        
        questions = [
            "What are the key financial strengths and weaknesses?",
            "What is the overall investment sentiment (positive, neutral, negative)?",
            "What is the confidence level in this analysis (high, medium, low)?",
            "What are the most important factors for investors to consider?"
        ]
        
        if focus == "financial_performance":
            questions.append("How has the company performed financially in recent periods?")
            questions.append("What are the key financial ratios and what do they indicate?")
        elif focus == "competitive_analysis":
            questions.append("How does the company compare to its competitors?")
            questions.append("What competitive advantages or disadvantages does the company have?")
        elif focus == "growth_prospects":
            questions.append("What are the company's growth prospects?")
            questions.append("What factors could drive or hinder future growth?")
        elif focus == "risk_assessment":
            questions.append("What are the key risks facing the company?")
            questions.append("How might these risks impact investment returns?")
        
        # Format questions as a numbered list
        formatted_questions = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
        
        try:
            # Use the generic_analysis template
            template = prompt_manager.get_template("generic_analysis")
            if not template:
                raise ValueError("Generic analysis template not found")
            
            # Format the template with our values
            prompt = template.format(
                overall_goal=f"To provide a comprehensive {focus if focus else 'financial'} analysis of {symbol}",
                context=context,
                last_step_result=formatted_data,
                questions=formatted_questions
            )
            
            # Use the Model class to analyze the data
            response = self.model.generate(
                prompt=prompt,
                temperature=0.2,
                max_tokens=4000
            )
            
            # Parse the XML response
            try:
                # Extract the XML content
                import xml.etree.ElementTree as ET
                from prompts.prompt_template import xml_to_dict
                
                # Clean up the response to ensure it's valid XML
                xml_content = extract_xml_content(response)
                
                # Parse the XML response
                root = ET.fromstring(xml_content)
                result_dict = xml_to_dict(root)
                
                # Extract the analysis components
                thinking = result_dict.get("thinking", "")
                summary = result_dict.get("summary", "")
                qa_items = result_dict.get("QA", {}).get("QA_item", [])
                
                # If QA_item is not a list, make it a list
                if not isinstance(qa_items, list):
                    qa_items = [qa_items]
                
                # Extract answers to specific questions
                analysis_text = summary
                key_points = []
                sentiment = "neutral"
                confidence = "medium"
                
                for qa_item in qa_items:
                    question = qa_item.get("question", "").lower()
                    answer = qa_item.get("answer", "")
                    
                    # Extract key points
                    if "important factors" in question or "key financial" in question:
                        # Split the answer by sentences or bullet points
                        points = [p.strip() for p in answer.split('.') if p.strip()]
                        key_points.extend(points[:5])  # Take up to 5 points
                    
                    # Extract sentiment
                    if "sentiment" in question:
                        lower_answer = answer.lower()
                        if "positive" in lower_answer or "bullish" in lower_answer:
                            sentiment = "positive"
                        elif "negative" in lower_answer or "bearish" in lower_answer:
                            sentiment = "negative"
                    
                    # Extract confidence
                    if "confidence" in question:
                        lower_answer = answer.lower()
                        if "high" in lower_answer:
                            confidence = "high"
                        elif "low" in lower_answer:
                            confidence = "low"
                
                # If no key points were extracted, use the summary
                if not key_points:
                    # Split the summary by sentences
                    points = [p.strip() for p in summary.split('.') if p.strip()]
                    key_points = points[:5]  # Take up to 5 points
                
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
                
            except Exception as xml_error:
                print(f"Error parsing XML response: {str(xml_error)}")
                # Fall back to the original analysis method
                raise Exception(f"XML parsing failed: {str(xml_error)}")
            
        except Exception as e:
            print(f"Error during analysis with template: {str(e)}")
            
            # Fallback to the original implementation
            try:
                # Generate a simple prompt
                fallback_prompt = f"""
                # Financial Analysis Request for {symbol}
                
                Please analyze the following financial data and provide insights:
                
                {formatted_data}
                
                Focus on: {focus if focus else 'general financial performance'}
                
                Please provide:
                1. A detailed analysis
                2. Key points (5-7 bullet points)
                3. Overall sentiment (positive, neutral, negative)
                4. Confidence level (high, medium, low)
                """
                
                # Call OpenAI API directly
                response = self.model.generate(
                    prompt=fallback_prompt,
                    temperature=0.2,
                    max_tokens=4000
                )
                
                # Extract the analysis text
                analysis_text = response
                
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
        # Format the analyses for the prompt
        formatted_analyses = format_analyses_for_prompt(analyses)
        
        try:
            # Use the generic_analysis template for summarization
            template = prompt_manager.get_template("generic_analysis")
            if not template:
                raise ValueError("Generic analysis template not found")
            
            # Format the template with our values
            prompt = template.format(
                overall_goal=f"To provide a comprehensive investment recommendation for {symbol}",
                context=f"You are summarizing multiple analyses for {symbol} to create a final investment recommendation.",
                last_step_result=formatted_analyses,
                questions="1. What is the overall investment recommendation for this stock?\n" +
                         "2. What are the key strengths of this investment?\n" +
                         "3. What are the key risks of this investment?\n" +
                         "4. What is the long-term outlook for this stock?\n" +
                         "5. What factors should investors monitor going forward?"
            )
            
            # Use the Model class to generate the summary
            response = self.model.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=4000
            )
            
            # Try to extract the summary from the XML response
            try:
                import xml.etree.ElementTree as ET
                from prompts.prompt_template import xml_to_dict
                
                # Clean up the response to ensure it's valid XML
                xml_content = extract_xml_content(response)
                
                # Parse the XML response
                root = ET.fromstring(xml_content)
                result_dict = xml_to_dict(root)
                
                # Extract the summary and QA components
                summary = result_dict.get("summary", "")
                qa_items = result_dict.get("QA", {}).get("QA_item", [])
                
                # If QA_item is not a list, make it a list
                if not isinstance(qa_items, list):
                    qa_items = [qa_items]
                
                # Format the final summary in markdown
                final_summary = f"# Investment Summary for {symbol}\n\n"
                final_summary += f"## Executive Summary\n\n{summary}\n\n"
                
                # Add Q&A sections
                for qa_item in qa_items:
                    question = qa_item.get("question", "")
                    answer = qa_item.get("answer", "")
                    
                    # Format as markdown sections
                    section_title = question.strip("?").strip()
                    final_summary += f"## {section_title}\n\n{answer}\n\n"
                
                return final_summary
                
            except Exception as xml_error:
                print(f"Error parsing XML summary response: {str(xml_error)}")
                # Return the raw response if XML parsing fails
                return response
            
        except Exception as e:
            print(f"Error generating summary with template: {str(e)}")
            
            # Fallback to a simpler approach
            try:
                # Generate a simple prompt
                fallback_prompt = f"""
                # Investment Summary Request for {symbol}
                
                Please summarize the following analyses into a comprehensive investment recommendation:
                
                {formatted_analyses}
                
                Please provide:
                1. Executive Summary
                2. Key Strengths
                3. Key Risks
                4. Long-term Outlook
                5. Factors to Monitor
                
                Format your response in markdown with appropriate headings.
                """
                
                # Generate the summary
                summary = self.model.generate(
                    prompt=fallback_prompt,
                    temperature=0.3,
                    max_tokens=4000
                )
                
                return summary
                
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
