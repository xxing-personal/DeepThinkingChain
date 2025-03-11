"""
Summarization Agent for the Deep Thinking Chain.

This module contains the SummarizationAgent class which is responsible for
compiling and synthesizing multiple analyses into a comprehensive investment summary.
"""

import os
import json
from typing import Dict, Any, List, Optional
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SummarizationAgent:
    """Agent that compiles and synthesizes the entire research process into an actionable summary."""
    
    def __init__(self, model: str = "gpt-4o"):
        """Initialize the SummarizationAgent with OpenAI configuration.
        
        Args:
            model: The OpenAI model to use for summarization. Defaults to "gpt-4o".
        """
        # First check if API key is in environment, then fall back to .env file
        api_key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        # Check if API key is available
        if not api_key:
            print("Warning: OPENAI_API_KEY environment variable not found.")
            print("Please set your OpenAI API key as an environment variable.")
    
    def summarize(self, analyses: List[Dict[str, Any]], symbol: str) -> str:
        """Generates a comprehensive final investment recommendation summary.
        
        This method takes all the analyses performed during the research process
        and synthesizes them into a cohesive, well-structured investment summary
        in Markdown format.
        
        Args:
            analyses: List of analysis results from all iterations
            symbol: Stock symbol being analyzed (e.g., 'NVDA')
            
        Returns:
            A comprehensive Markdown-formatted investment summary
        """
        if not analyses:
            return f"# Investment Summary for {symbol}\n\nNo analyses were provided to summarize."
        
        try:
            # Prepare the analyses for summarization
            formatted_analyses = self._format_analyses(analyses)
            
            # Create the prompt for the OpenAI API
            prompt = self._create_summary_prompt(formatted_analyses, symbol)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial advisor creating comprehensive investment summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            # Extract the summary text
            summary_text = response.choices[0].message.content
            
            # Add metadata and formatting
            final_summary = self._format_final_summary(summary_text, symbol, analyses)
            
            return final_summary
            
        except Exception as e:
            print(f"Error during summarization: {str(e)}")
            return self._create_error_summary(symbol, str(e), analyses)
    
    def _format_analyses(self, analyses: List[Dict[str, Any]]) -> str:
        """Format the analyses for inclusion in the prompt.
        
        Args:
            analyses: List of analysis results
            
        Returns:
            Formatted string representation of the analyses
        """
        formatted_parts = []
        
        for i, analysis in enumerate(analyses, 1):
            analysis_type = analysis.get("analysis_type", "unknown")
            timestamp = analysis.get("timestamp", "unknown time")
            sentiment = analysis.get("sentiment", "neutral")
            confidence = analysis.get("confidence", "medium")
            
            # Format the analysis header
            header = f"## Analysis {i}: {analysis_type.replace('_', ' ').title()}"
            formatted_parts.append(header)
            
            # Add metadata
            metadata = f"- **Timestamp:** {timestamp}\n- **Sentiment:** {sentiment}\n- **Confidence:** {confidence}"
            formatted_parts.append(metadata)
            
            # Add key points if available
            key_points = analysis.get("key_points", [])
            if key_points:
                points_text = "### Key Points:\n" + "\n".join([f"- {point}" for point in key_points])
                formatted_parts.append(points_text)
            
            # Add insights if available
            insights = analysis.get("insights", "")
            if insights:
                insights_text = "### Insights:\n" + insights
                formatted_parts.append(insights_text)
            
            # Add separator
            formatted_parts.append("-" * 40)
        
        return "\n\n".join(formatted_parts)
    
    def _create_summary_prompt(self, formatted_analyses: str, symbol: str) -> str:
        """Create a prompt for generating the investment summary.
        
        Args:
            formatted_analyses: Formatted string of all analyses
            symbol: Stock symbol being analyzed
            
        Returns:
            Prompt string for the OpenAI API
        """
        prompt = f"""
You are a financial advisor tasked with creating a comprehensive investment summary for {symbol}.
Based on the following analyses, create a well-structured investment recommendation in Markdown format.

The summary should include:

1. **Executive Summary**
   - Overall investment recommendation (Buy/Hold/Sell)
   - Key investment thesis in 2-3 sentences
   - Target price range or expected return (if available)

2. **Company Overview**
   - Brief description of the company and its business model
   - Key products/services and revenue streams
   - Market position and competitive landscape

3. **Financial Analysis**
   - Key financial metrics and trends
   - Balance sheet strength and cash flow analysis
   - Profitability and efficiency metrics

4. **Growth Prospects**
   - Historical growth rates and future projections
   - Growth drivers and opportunities
   - Potential catalysts for future performance

5. **Competitive Advantages**
   - Moat analysis (brand, network effects, switching costs, etc.)
   - Differentiation factors
   - Sustainability of competitive advantages

6. **Risk Factors**
   - Key risks to the investment thesis
   - Mitigating factors
   - Risk-reward assessment

7. **Valuation**
   - Current valuation metrics compared to historical averages and peers
   - Fair value estimate and methodology
   - Upside/downside scenarios

8. **Investment Recommendation**
   - Clear recommendation with rationale
   - Time horizon for the investment
   - Key metrics to monitor

Use proper Markdown formatting with headers, bullet points, and emphasis where appropriate.
Be balanced in your assessment, acknowledging both bullish and bearish arguments.
Base your recommendation strictly on the information provided in the analyses.

ANALYSES:

{formatted_analyses}
"""
        return prompt
    
    def _format_final_summary(self, summary_text: str, symbol: str, analyses: List[Dict[str, Any]]) -> str:
        """Format the final summary with metadata and additional information.
        
        Args:
            summary_text: The raw summary text from the OpenAI API
            symbol: Stock symbol being analyzed
            analyses: List of analysis results
            
        Returns:
            Formatted final summary
        """
        # Extract analysis types and timestamps
        analysis_types = [a.get("analysis_type", "unknown") for a in analyses]
        timestamps = [a.get("timestamp", "unknown") for a in analyses]
        
        # Create metadata section
        metadata = f"""
---
Symbol: {symbol}
Analyses Performed: {len(analyses)}
Analysis Types: {', '.join(analysis_type.replace('_', ' ').title() for analysis_type in set(analysis_types))}
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}
---

"""
        
        # Add a title if not present
        if not summary_text.strip().startswith("# "):
            title = f"# Investment Summary for {symbol}\n\n"
        else:
            title = ""
        
        # Combine all parts
        final_summary = title + metadata + summary_text
        
        return final_summary
    
    def _create_error_summary(self, symbol: str, error_message: str, analyses: List[Dict[str, Any]]) -> str:
        """Create a basic summary in case of an error.
        
        Args:
            symbol: Stock symbol being analyzed
            error_message: Error message
            analyses: List of analysis results
            
        Returns:
            Basic summary with available information
        """
        # Create title and error message
        summary = f"# Investment Summary for {symbol}\n\n"
        summary += f"**Note:** An error occurred during summarization: {error_message}\n\n"
        summary += "Below is a basic summary of the available analyses:\n\n"
        
        # Add a summary of each analysis
        for i, analysis in enumerate(analyses, 1):
            analysis_type = analysis.get("analysis_type", "unknown").replace('_', ' ').title()
            sentiment = analysis.get("sentiment", "neutral")
            confidence = analysis.get("confidence", "medium")
            
            summary += f"## Analysis {i}: {analysis_type}\n\n"
            summary += f"- **Sentiment:** {sentiment}\n"
            summary += f"- **Confidence:** {confidence}\n\n"
            
            # Add key points if available
            key_points = analysis.get("key_points", [])
            if key_points:
                summary += "### Key Points:\n\n"
                for point in key_points:
                    summary += f"- {point}\n"
                summary += "\n"
        
        return summary


if __name__ == "__main__":
    """Test the SummarizationAgent functionality."""
    import sys
    
    # Check if OpenAI API key is set
    api_key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key as an environment variable.")
        sys.exit(1)
    
    # Sample analyses for testing
    sample_analyses = [
        {
            "analysis_type": "financial_performance",
            "symbol": "AAPL",
            "timestamp": "2023-01-01 12:00:00",
            "insights": "Apple shows strong financial performance with robust cash flows and high margins. The company has consistently grown revenue and earnings over the past 5 years. Its balance sheet remains strong with significant cash reserves.",
            "key_points": [
                "Strong balance sheet with significant cash reserves",
                "High profit margins compared to industry peers",
                "Consistent revenue growth over the past 5 years"
            ],
            "sentiment": "positive",
            "confidence": "high"
        },
        {
            "analysis_type": "competitive_analysis",
            "symbol": "AAPL",
            "timestamp": "2023-01-01 13:00:00",
            "insights": "Apple maintains a strong competitive position in its core markets. The company's brand strength and ecosystem create significant barriers to entry. However, competition is intensifying in key product categories.",
            "key_points": [
                "Strong brand value and customer loyalty",
                "Integrated ecosystem creates switching costs",
                "Premium pricing strategy maintains margins",
                "Increasing competition in smartphone market"
            ],
            "sentiment": "positive",
            "confidence": "medium"
        },
        {
            "analysis_type": "risk_assessment",
            "symbol": "AAPL",
            "timestamp": "2023-01-01 14:00:00",
            "insights": "While Apple faces several risks, its strong financial position and diversified product portfolio mitigate many concerns. Supply chain dependencies and regulatory scrutiny remain key challenges.",
            "key_points": [
                "Concentration risk in iPhone revenue",
                "Supply chain dependencies on China",
                "Regulatory scrutiny in multiple markets",
                "Strong cash position mitigates financial risks"
            ],
            "sentiment": "neutral",
            "confidence": "high"
        }
    ]
    
    # Initialize the agent
    agent = SummarizationAgent()
    
    # Test the summarize method
    print("\n" + "="*50)
    print("Testing SummarizationAgent with sample analyses...")
    print("="*50 + "\n")
    
    summary = agent.summarize(sample_analyses, "AAPL")
    
    # Save the summary to a file
    output_file = "results/AAPL_test_summary.md"
    os.makedirs("results", exist_ok=True)
    
    with open(output_file, "w") as f:
        f.write(summary)
    
    print(f"Summary generated and saved to {output_file}")
    print("\nSummary Preview:")
    print("-" * 50)
    print(summary[:500] + "..." if len(summary) > 500 else summary)
    print("-" * 50)
    
    print("\n" + "="*50)
    print("SummarizationAgent test complete")
    print("="*50)
