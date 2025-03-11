"""
Planning Agent for the Deep Thinking Chain.

This module contains the PlanningAgent class which is responsible for determining
the next steps in the investment analysis process based on current analysis results.
"""

import os
import json
from typing import Dict, Any, List, Optional
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PlanningAgent:
    """Agent deciding next actions based on current analysis outcomes."""
    
    def __init__(self, model: str = "gpt-4o"):
        """Initialize the PlanningAgent with OpenAI configuration.
        
        Args:
            model: The OpenAI model to use for planning. Defaults to "gpt-4o".
        """
        # First check if API key is in environment, then fall back to .env file
        api_key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        # Check if API key is available
        if not api_key:
            print("Warning: OPENAI_API_KEY environment variable not found.")
            print("Please set your OpenAI API key as an environment variable.")
        
        # Define focus areas for research
        self.focus_areas = [
            "financial_performance",
            "competitive_analysis",
            "growth_prospects",
            "valuation",
            "risk_assessment"
        ]
        
        # Define criteria for completion
        self.completion_criteria = {
            "min_iterations": 3,
            "required_focus_areas": ["financial_performance", "risk_assessment"],
            "confidence_threshold": 0.7
        }
    
    def plan_next(self, analysis_result: Dict[str, Any], 
                  iteration: int = 1, 
                  max_iterations: int = 5,
                  completed_focus_areas: Optional[List[str]] = None,
                  required_focus_areas: Optional[List[str]] = None,
                  previous_analyses: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Determines the next iteration's actions or signals summarization.
        
        This method evaluates the current analysis results and decides whether to:
        1. Continue with another iteration of research, focusing on a specific area
        2. Move to the summarization phase if sufficient information has been gathered
        
        The decision is based on several factors:
        - Current iteration number and maximum allowed iterations
        - Coverage of key focus areas
        - Confidence level of existing analyses
        - Identified gaps or areas needing further investigation
        
        Args:
            analysis_result: The most recent analysis result from the AnalysisAgent
            iteration: Current iteration number (starting from 1)
            max_iterations: Maximum number of iterations allowed
            completed_focus_areas: List of focus areas that have been analyzed
            required_focus_areas: List of focus areas that must be covered
            previous_analyses: List of analysis results from previous iterations
                              (excluding the current one)
            
        Returns:
            Dict containing the planning decision with the following keys:
            - "continue_analysis": Boolean indicating whether to continue (True) or summarize (False)
            - "next_focus": The focus area for the next iteration (if continuing)
            - "reasoning": Explanation of the decision
            - "completion_percentage": Estimated percentage of research completion
            - "timestamp": When the planning decision was made
        """
        # Initialize previous_analyses if None
        if previous_analyses is None:
            previous_analyses = []
        
        # Combine current and previous analyses
        all_analyses = previous_analyses + [analysis_result]
        
        # Extract key information for decision making
        covered_focus_areas = [a.get("analysis_type") for a in all_analyses if "analysis_type" in a]
        current_focus = analysis_result.get("analysis_type", "general_financial")
        confidence = analysis_result.get("confidence", "medium")
        confidence_score = self._confidence_to_score(confidence)
        sentiment = analysis_result.get("sentiment", "neutral")
        
        # Check if we've covered the minimum required iterations
        min_iterations_met = iteration >= self.completion_criteria["min_iterations"]
        
        # Check if we've covered all required focus areas
        required_areas_covered = all(area in covered_focus_areas 
                                    for area in self.completion_criteria["required_focus_areas"])
        
        # Check if confidence is high enough
        confidence_met = confidence_score >= self.completion_criteria["confidence_threshold"]
        
        # Calculate completion percentage
        completion_percentage = self._calculate_completion_percentage(
            iteration, covered_focus_areas, confidence_score
        )
        
        # Determine if we should continue or summarize
        if not min_iterations_met or not required_areas_covered:
            # Continue analysis if minimum criteria not met
            continue_analysis = True
            reasoning = f"Continuing analysis because "
            
            if not min_iterations_met:
                reasoning += f"minimum iterations ({self.completion_criteria['min_iterations']}) not reached. "
            
            if not required_areas_covered:
                missing_areas = [area for area in self.completion_criteria["required_focus_areas"] 
                                if area not in covered_focus_areas]
                reasoning += f"required focus areas not covered: {', '.join(missing_areas)}. "
            
            # Determine next focus area
            next_focus = self._determine_next_focus(covered_focus_areas, analysis_result)
            
        elif self._should_explore_further(analysis_result, all_analyses):
            # Continue analysis if there are areas that need further exploration
            continue_analysis = True
            next_focus = self._determine_next_focus(covered_focus_areas, analysis_result)
            reasoning = f"Continuing analysis to explore {next_focus} based on current findings. "
            
        else:
            # Move to summarization
            continue_analysis = False
            next_focus = None
            reasoning = "Moving to summarization as sufficient information has been gathered. "
            
            if min_iterations_met:
                reasoning += f"Completed {iteration} iterations. "
            
            if required_areas_covered:
                reasoning += "All required focus areas have been covered. "
            
            if confidence_met:
                reasoning += f"Analysis confidence is sufficient ({confidence}). "
        
        # Construct the result
        result = {
            "continue_analysis": continue_analysis,
            "next_focus": next_focus,
            "reasoning": reasoning,
            "completion_percentage": completion_percentage,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "iteration": iteration,
            "covered_focus_areas": covered_focus_areas
        }
        
        return result
    
    def _confidence_to_score(self, confidence: str) -> float:
        """Convert confidence string to numerical score.
        
        Args:
            confidence: Confidence level string ("high", "medium", "low")
            
        Returns:
            Numerical score between 0 and 1
        """
        confidence_map = {
            "high": 0.9,
            "medium": 0.6,
            "low": 0.3
        }
        return confidence_map.get(confidence.lower(), 0.5)
    
    def _calculate_completion_percentage(self, 
                                        iteration: int, 
                                        covered_focus_areas: List[str],
                                        confidence_score: float) -> int:
        """Calculate the estimated completion percentage of the research.
        
        Args:
            iteration: Current iteration number
            covered_focus_areas: List of focus areas already covered
            confidence_score: Numerical confidence score
            
        Returns:
            Completion percentage (0-100)
        """
        # Base percentage on iterations (up to 30%)
        iteration_factor = min(iteration / self.completion_criteria["min_iterations"], 1.0) * 30
        
        # Focus areas coverage (up to 50%)
        required_areas = self.completion_criteria["required_focus_areas"]
        covered_required = sum(1 for area in required_areas if area in covered_focus_areas)
        focus_factor = (covered_required / len(required_areas)) * 50
        
        # Confidence factor (up to 20%)
        confidence_factor = confidence_score * 20
        
        # Calculate total and round to integer
        total = iteration_factor + focus_factor + confidence_factor
        return min(round(total), 100)
    
    def _determine_next_focus(self, 
                             covered_focus_areas: List[str],
                             analysis_result: Dict[str, Any]) -> str:
        """Determine the next focus area for research.
        
        Args:
            covered_focus_areas: List of focus areas already covered
            analysis_result: The most recent analysis result
            
        Returns:
            Next focus area to research
        """
        # First, prioritize required areas that haven't been covered
        for area in self.completion_criteria["required_focus_areas"]:
            if area not in covered_focus_areas:
                return area
        
        # Then, look for any focus area not yet covered
        for area in self.focus_areas:
            if area not in covered_focus_areas:
                return area
        
        # If all areas covered, use LLM to determine which area needs more depth
        try:
            # Create a prompt for the LLM
            prompt = self._create_next_focus_prompt(covered_focus_areas, analysis_result)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial research planner determining the next focus area for investment analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            # Extract the suggested focus area
            suggested_focus = response.choices[0].message.content.strip().lower()
            
            # Map the response to one of our focus areas
            for area in self.focus_areas:
                if area in suggested_focus:
                    return area
            
            # Default to financial_performance if no match
            return "financial_performance"
            
        except Exception as e:
            print(f"Error determining next focus: {str(e)}")
            # Default to a focus area with least coverage or financial_performance
            return "financial_performance"
    
    def _create_next_focus_prompt(self, 
                                 covered_focus_areas: List[str],
                                 analysis_result: Dict[str, Any]) -> str:
        """Create a prompt for determining the next focus area.
        
        Args:
            covered_focus_areas: List of focus areas already covered
            analysis_result: The most recent analysis result
            
        Returns:
            Prompt string for the LLM
        """
        key_points = analysis_result.get("key_points", [])
        key_points_text = "\n".join([f"- {point}" for point in key_points])
        
        prompt = f"""
Based on the current investment analysis for {analysis_result.get('symbol', 'the company')}, 
I need to determine which area requires further research.

We have already covered the following focus areas:
{', '.join(covered_focus_areas)}

The most recent analysis had the following key points:
{key_points_text}

The available focus areas are:
- financial_performance: Detailed analysis of financial statements, ratios, and trends
- competitive_analysis: Evaluation of market position, competitors, and industry dynamics
- growth_prospects: Assessment of growth opportunities, expansion potential, and future outlook
- valuation: Analysis of current valuation, fair value estimates, and valuation metrics
- risk_assessment: Identification and evaluation of key risks and challenges

Which ONE of these focus areas should be prioritized for the next research iteration?
Respond with just the focus area name.
"""
        return prompt
    
    def _should_explore_further(self, 
                               analysis_result: Dict[str, Any],
                               all_analyses: List[Dict[str, Any]]) -> bool:
        """Determine if further exploration is needed based on analysis results.
        
        Args:
            analysis_result: The most recent analysis result
            all_analyses: All analysis results so far
            
        Returns:
            Boolean indicating whether further exploration is needed
        """
        # Extract key information
        key_points = analysis_result.get("key_points", [])
        insights = analysis_result.get("insights", "")
        
        # Check for indicators of uncertainty or areas needing more research
        uncertainty_indicators = [
            "further research",
            "additional analysis",
            "more information",
            "unclear",
            "uncertain",
            "unknown",
            "limited data",
            "insufficient information"
        ]
        
        # Check if any uncertainty indicators are present in the insights or key points
        for indicator in uncertainty_indicators:
            if indicator in insights.lower():
                return True
            
            for point in key_points:
                if indicator in point.lower():
                    return True
        
        # If we've covered all focus areas and have high confidence, no need for further exploration
        if (len(all_analyses) >= len(self.focus_areas) and 
            analysis_result.get("confidence", "medium") == "high"):
            return False
        
        # Default to continuing if we're not sure
        return len(all_analyses) < 5  # Limit to 5 iterations maximum


if __name__ == "__main__":
    """Test the PlanningAgent functionality."""
    import sys
    
    # Check if OpenAI API key is set
    api_key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key as an environment variable.")
        sys.exit(1)
    
    # Sample analysis result for testing
    sample_analysis = {
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
    
    # Initialize the agent
    agent = PlanningAgent()
    
    # Test the plan_next method
    print("\n" + "="*50)
    print("Testing PlanningAgent with sample analysis...")
    print("="*50 + "\n")
    
    # Test with first iteration
    result = agent.plan_next(sample_analysis, iteration=1)
    
    print(f"Decision: {'Continue' if result['continue_analysis'] else 'Summarize'}")
    print(f"Next focus: {result['next_focus']}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"Completion: {result['completion_percentage']}%")
    
    # Test with later iteration and multiple analyses
    previous_analyses = [
        {
            "analysis_type": "financial_performance",
            "confidence": "high",
            "sentiment": "positive"
        },
        {
            "analysis_type": "competitive_analysis",
            "confidence": "medium",
            "sentiment": "neutral"
        },
        {
            "analysis_type": "risk_assessment",
            "confidence": "high",
            "sentiment": "neutral"
        }
    ]
    
    print("\nTesting with multiple previous analyses (iteration 4)...")
    result2 = agent.plan_next(
        sample_analysis, 
        iteration=4,
        previous_analyses=previous_analyses
    )
    
    print(f"Decision: {'Continue' if result2['continue_analysis'] else 'Summarize'}")
    print(f"Next focus: {result2['next_focus']}")
    print(f"Reasoning: {result2['reasoning']}")
    print(f"Completion: {result2['completion_percentage']}%")
    
    print("\n" + "="*50)
    print("PlanningAgent test complete")
    print("="*50)
