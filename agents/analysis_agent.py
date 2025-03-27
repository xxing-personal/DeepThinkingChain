"""
Analysis Agent for the Deep Thinking Chain.

This module contains the AnalysisAgent class which is responsible for analyzing
financial data and extracting investment insights.
"""

import json
import os
import time
import logging
import re
from typing import Dict, Any, Optional, List, Union

# Import the base Agent class
from .agent_base import Agent

# Import helper functions
from ..prompts.prompt_helper import format_data_for_prompt
from ..memory import MemoryManager
from ..model import Model
from ..constants import AgentType

# Set up logging
logger = logging.getLogger(__name__)

class AnalysisAgent(Agent):
    """Agent performing detailed analysis and extraction of insights from raw financial data."""
    
    def __init__(self, prompt_template_name: str = "generic_analysis", 
                 memory_manager: Optional[Union[str, MemoryManager]] = None, 
                 model_name: str = "gpt-3.5-turbo"):
        """Initialize the AnalysisAgent with model configuration.
        
        Args:
            prompt_template_name: The template to use for analysis. Defaults to "generic_analysis".
            memory_manager: Optional memory manager for saving agent results
            model_name: The model to use for analysis. Defaults to "gpt-3.5-turbo".
        """
        # Initialize the base Agent class
        super().__init__(prompt_template_name=prompt_template_name, 
                         memory_manager=memory_manager, 
                         model_name=model_name)
        
        # Set the agent type
        self.agent_type = AgentType.ANALYSIS
        
        # Update metadata
        self.metadata.update({
            "agent_type": self.agent_type
        })
        
        # Initialize model for generating text
        self.model = Model(model=model_name)
    
    def _run(self, last_step_result: Union[str, Dict[str, Any], None] = None) -> Dict[str, Any]:
        """Run the analysis agent to analyze financial data and extract insights.
        
        Args:
            last_step_result: Data from the last step to be analyzed, either as formatted string or dict
            
        Returns:
            A dictionary containing the analysis results
        """
        try:
            # Process the template using additional parameters from last step result
            additional_params = {}
            if last_step_result is not None:
                if isinstance(last_step_result, dict):
                    additional_params["last_step_result"] = format_data_for_prompt(last_step_result)
                else:
                    additional_params["last_step_result"] = str(last_step_result)
            else:
                additional_params["last_step_result"] = "No previous results available."
                
            # Process the template
            prompt = self.process_template(**additional_params)
            
            # Use the Model class to analyze the data
            response = self.model.generate(
                prompt=prompt,
                temperature=0.2,
                max_tokens=4000
            )
            
            # Parse the response
            return self._parse_response(response)
                
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            
            # Return an error result
            return {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "status": "failed"
            }
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the response from the language model.
        
        Args:
            response: The response from the language model
            
        Returns:
            A dictionary containing the parsed results
        """
        try:
            # First, try to extract JSON using regex
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            
            if json_match:
                json_str = json_match.group(1)
                try:
                    # Try to parse the JSON string
                    result_dict = json.loads(json_str)
                except json.JSONDecodeError:
                    # If it still fails, fall back to the template's extraction method
                    result_dict = self.template.extract_output_to_dict(response)
            else:
                # No JSON code block found, use the template's extraction method
                result_dict = self.template.extract_output_to_dict(response)
            
            # Extract the analysis components from the result dictionary
            result_content = result_dict.get("result", {})
            thinking = result_content.get("thinking", "")
            summary = result_content.get("summary", "")
            qa_items = result_content.get("QA", [])
            
            # If QA is not a list, make it a list
            if not isinstance(qa_items, list):
                qa_items = [qa_items] if qa_items else []
            
            # Process key insights
            key_points = self._extract_key_points(summary) if summary else []
            sentiment_info = self._determine_sentiment(summary) if summary else {"sentiment": "neutral", "confidence": "medium"}
            
            # If we have a pending question in memory and QA items, update the memory
            if hasattr(self, 'memory_manager') and self.memory_manager and hasattr(self.memory_manager, 'questions') and self.memory_manager.questions and qa_items:
                for qa_item in qa_items:
                    if isinstance(qa_item, dict):
                        question_text = qa_item.get("question", "")
                        answer_text = qa_item.get("answer", "")
                        
                        # Find matching question in memory
                        for q in self.memory_manager.questions:
                            if q.text.lower() == question_text.lower() and q.status == "pending":
                                # Update the question with the answer
                                q.add_answer(answer_text)
                                break
            
            # Construct the result
            result = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "thinking": thinking,
                "summary": summary,
                "insights": summary,  # For backward compatibility
                "key_points": key_points,
                "sentiment": sentiment_info["sentiment"],
                "confidence": sentiment_info["confidence"],
                "qa_items": qa_items
            }
            
            # Add metadata about this analysis if we have a memory manager
            if hasattr(self, 'memory_manager') and self.memory_manager:
                result["memory_id"] = self.memory_manager.memory_id
                result["iteration"] = self.memory_manager.memory.get("iteration_counter", 0) + 1
                
                # Update the overall summary in memory
                if summary:
                    self.memory_manager.memory["summary"] = summary
            
            return result
            
        except Exception as parsing_error:
            logger.error(f"Error parsing analysis response: {str(parsing_error)}")
            
            # Simple fallback in case of parsing error
            fallback_result = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "thinking": "Error parsing structured output",
                "summary": response[:500],  # Use first part of response as summary
                "insights": response[:500],
                "key_points": self._extract_key_points(response),
                "sentiment": "neutral",
                "confidence": "low",
                "qa_items": [],
                "raw_response": response
            }
            
            return fallback_result
            
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from analysis text.
        
        Args:
            text: The analysis text to extract key points from
            
        Returns:
            List of key points
        """
        try:
            if not text:
                return ["No text provided for analysis"]
                
            key_points = []
            
            # Check for bullet points
            if "•" in text or "*" in text or "-" in text:
                # Split by bullet points
                for line in text.split('\n'):
                    line = line.strip()
                    if line.startswith('•') or line.startswith('*') or line.startswith('-'):
                        # Clean up the point
                        point = line.lstrip('•*- ').strip()
                        if point and len(point) > 10:  # Ensure it's substantive
                            key_points.append(point)
            
            # If no bullet points found, split by sentences
            if not key_points:
                sentences = [s.strip() for s in text.split('.') if s.strip()]
                for sentence in sentences:
                    if len(sentence) > 15 and not sentence.startswith('#') and not sentence.startswith('*'):
                        key_points.append(sentence)
            
            # Limit to 5 most important points
            return key_points[:5]
            
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            # Return a safe default value
            return [text[:100] + "..."] if text else ["No key points could be extracted"]
            
    def _determine_sentiment(self, text: str) -> Dict[str, str]:
        """Determine the sentiment and confidence of an analysis text.
        
        Args:
            text: The analysis text to determine sentiment for
            
        Returns:
            Dict with sentiment and confidence
        """
        try:
            if not text:
                return {"sentiment": "neutral", "confidence": "low"}
            
            # Default values
            sentiment = "neutral"
            confidence = "medium"
            
            # Check for positive signals
            positive_words = ["positive", "bullish", "strong", "growth", "increase", "improved", 
                            "opportunity", "outperform", "upside", "buy", "recommend"]
            # Check for negative signals
            negative_words = ["negative", "bearish", "weak", "decline", "decrease", "deteriorated", 
                            "challenge", "underperform", "downside", "sell", "avoid"]
            
            # Convert to lowercase for case-insensitive matching
            text_lower = text.lower()
            
            # Count sentiment signals
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            # Determine overall sentiment
            if positive_count > negative_count:
                sentiment = "positive"
            elif negative_count > positive_count:
                sentiment = "negative"
            
            # Determine confidence
            signal_strength = positive_count + negative_count
            if signal_strength > 5:
                confidence = "high"
            elif signal_strength < 2:
                confidence = "low"
            
            return {"sentiment": sentiment, "confidence": confidence}
            
        except Exception as e:
            logger.error(f"Error determining sentiment: {str(e)}")
            return {"sentiment": "neutral", "confidence": "medium"}
            
            
  