"""
Model wrapper for language model interactions in DeepThinkingChain.

This module provides a unified interface for interacting with language models,
making it easy to switch between different models or providers.
"""

import logging
import os
from typing import List, Dict, Any, Optional, Union
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI package not available. Install with 'pip install openai'")
    OPENAI_AVAILABLE = False

# Try to import LiteLLM for multi-provider support
try:
    import litellm
    from litellm import ModelResponse, completion
    LITELLM_AVAILABLE = True
except ImportError:
    logger.warning("LiteLLM package not available. Install with 'pip install litellm'")
    LITELLM_AVAILABLE = False


class Model:
    """
    A wrapper for language model APIs in DeepThinkingChain.
    
    This class provides a unified interface for interacting with different
    language models, making it easy to switch between providers or models.
    """
    
    def __init__(self, model: str = "gpt-4o", provider: str = "openai", use_litellm: bool = False):
        """
        Initialize the model.
        
        Args:
            model: The model identifier to use (e.g., "gpt-4o", "claude-3-opus")
            provider: The provider to use (e.g., "openai", "anthropic")
            use_litellm: Whether to use LiteLLM for multi-provider support
        """
        self.model_name = model
        self.provider = provider
        self.use_litellm = use_litellm and LITELLM_AVAILABLE
        
        # Set up the client based on the provider and availability
        if self.use_litellm:
            logger.info(f"Using LiteLLM with model: {model}")
            # LiteLLM will handle the API key
        elif provider == "openai" and OPENAI_AVAILABLE:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=api_key)
            logger.info(f"Initialized OpenAI client with model: {model}")
        else:
            logger.warning(f"Provider {provider} not supported or required packages not installed")
            
        # Track reasoning capabilities
        self.reasoning_model = model in [
            "gpt-4", "gpt-4-turbo", "gpt-4o", 
            "claude-3-opus", "claude-3-sonnet",
            "gemini-pro", "gemini-1.5-pro"
        ]
        self.reasoning_effort = "medium"
        
    def set_reasoning_effort(self, reasoning_effort: str = "medium") -> None:
        """
        Set the reasoning effort level for the model.
        
        Args:
            reasoning_effort: The level of reasoning effort ("low", "medium", "high")
        """
        if reasoning_effort not in ["low", "medium", "high"]:
            logger.warning(f"Invalid reasoning effort: {reasoning_effort}. Using 'medium'.")
            reasoning_effort = "medium"
        self.reasoning_effort = reasoning_effort
        logger.info(f"Set reasoning effort to: {reasoning_effort}")

    def _chat_completion(self, messages: List[Dict[str, str]], 
                         temperature: float = 0.7,
                         max_tokens: Optional[int] = None) -> Union[Dict[str, Any], Any]:
        """
        Generate a chat completion using the specified model.
        
        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The response from the language model
        """
        try:
            logger.info(f"Generating chat completion with model: {self.model_name}")
            logger.debug(f"Messages: {messages}")
            
            if self.use_litellm:
                response = completion(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response
            elif self.provider == "openai" and OPENAI_AVAILABLE:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response
            else:
                logger.error("No valid model client available")
                return {"error": "No valid model client available"}
        except Exception as e:
            logger.error(f"Error generating chat completion: {str(e)}")
            return {"error": str(e)}

    def generate(self, prompt: str, 
                 system_prompt: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: Optional[int] = None) -> str:
        """
        Generate text based on a prompt.
        
        Args:
            prompt: The text prompt
            system_prompt: Optional system prompt to set context
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            str: The generated text
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        # Add user prompt
        messages.append({"role": "user", "content": prompt})
        
        # Get response
        response = self._chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract content based on provider
        try:
            if self.use_litellm:
                return response.choices[0].message.content
            elif self.provider == "openai" and OPENAI_AVAILABLE:
                return response.choices[0].message.content
            elif isinstance(response, dict) and "error" in response:
                return f"Error: {response['error']}"
            else:
                return "Failed to generate response"
        except Exception as e:
            logger.error(f"Error extracting response content: {str(e)}")
            return f"Error extracting response: {str(e)}"

    def analyze_text(self, text: str, focus: str = "general") -> Dict[str, Any]:
        """
        Analyze text for different purposes like extracting key points or determining sentiment.
        
        Args:
            text: The text to analyze
            focus: The focus of the analysis (e.g., "key_points", "sentiment", "planning_summary")
            
        Returns:
            Dict containing analysis results
        """
        system_prompt = ""
        prompt = ""
        temperature = 0.3
        use_json = False
        
        # Configure the analysis based on the focus
        if focus == "key_points":
            system_prompt = "Extract the 5-7 most important key points from this financial analysis. Return ONLY a JSON array of strings with no explanation."
            prompt = f"Extract key points from the following text:\n\n{text}"
            use_json = True
        elif focus == "sentiment":
            system_prompt = "Based on this financial analysis, determine the overall investment sentiment (positive, neutral, negative) and confidence level (high, medium, low). Return ONLY a JSON object with 'sentiment' and 'confidence' keys."
            prompt = f"Determine the sentiment and confidence from the following text:\n\n{text}"
            use_json = True
        elif focus == "planning_summary":
            system_prompt = "You are a financial advisor providing investment recommendations."
            prompt = text  # The text is already a prompt in this case
        else:
            system_prompt = "Analyze the following text and provide insights."
            prompt = f"Analyze the following text:\n\n{text}"
        
        # Generate the analysis
        analysis_text = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        
        # Process the result based on the focus
        if use_json:
            try:
                # Try to parse as JSON
                result = json.loads(analysis_text)
                return {
                    "analysis": analysis_text,
                    "parsed_result": result,
                    "focus": focus,
                    "timestamp": time.time()
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw text
                logger.warning(f"Failed to parse JSON response: {analysis_text}")
                return {
                    "analysis": analysis_text,
                    "error": "Failed to parse JSON response",
                    "focus": focus,
                    "timestamp": time.time()
                }
        else:
            # Return the raw text for non-JSON responses
            return {
                "analysis": analysis_text,
                "focus": focus,
                "timestamp": time.time()
            }

    def analyze_financial_data(self, data: Dict[str, Any], 
                              focus: Optional[str] = None,
                              symbol: str = "") -> Dict[str, Any]:
        """
        Analyze financial data for investment insights.
        
        Args:
            data: Financial data to analyze
            focus: Focus area for analysis (e.g., "financial_performance", "competitive_analysis")
            symbol: Stock symbol being analyzed
            
        Returns:
            Dict containing analysis results, key points, and sentiment
        """
        # Determine the appropriate system prompt based on focus
        if focus == "financial_performance":
            system_prompt = "You are a financial analyst specializing in fundamental analysis."
        elif focus == "competitive_analysis":
            system_prompt = "You are a market analyst specializing in competitive positioning."
        elif focus == "growth_prospects":
            system_prompt = "You are a growth analyst specializing in future projections."
        elif focus == "risk_assessment":
            system_prompt = "You are a risk analyst specializing in identifying potential threats."
        else:
            system_prompt = "You are an investment analyst providing comprehensive financial analysis."
        
        # Format the data for the prompt
        data_str = json.dumps(data, indent=2)
        
        # Create the prompt
        prompt = f"""
        Analyze the following financial data for {symbol}:
        
        {data_str}
        
        Focus on {focus if focus else 'overall financial performance'}.
        
        Provide:
        1. A detailed analysis
        2. Key points (bullet points)
        3. Overall sentiment (bullish, neutral, or bearish)
        4. Confidence level (high, medium, or low)
        """
        
        # Generate the analysis
        analysis_text = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3  # Lower temperature for more consistent analysis
        )
        
        # Extract key points and sentiment
        key_points = self._extract_key_points(analysis_text)
        sentiment = self._determine_sentiment(analysis_text)
        
        # Return the results
        return {
            "analysis": analysis_text,
            "key_points": key_points,
            "sentiment": sentiment["sentiment"],
            "confidence": sentiment["confidence"],
            "focus": focus if focus else "general",
            "symbol": symbol,
            "timestamp": time.time()
        }
    
    def _extract_key_points(self, analysis_text: str) -> List[str]:
        """
        Extract key points from analysis text.
        
        Args:
            analysis_text: The full analysis text
            
        Returns:
            List of key points
        """
        # Simple extraction based on bullet points or numbered lists
        lines = analysis_text.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            # Check for bullet points or numbered lists
            if line.startswith('•') or line.startswith('-') or line.startswith('*') or \
               (line.startswith(tuple('1234567890')) and '. ' in line[:5]):
                # Clean up the point
                point = line.lstrip('•-*1234567890. ')
                if point:
                    key_points.append(point)
        
        # If no bullet points found, try to extract using a model
        if not key_points and len(analysis_text) > 100:
            try:
                prompt = f"""
                Extract the 3-5 most important key points from this financial analysis:
                
                {analysis_text}
                
                Format each point as a separate line starting with a dash.
                """
                
                key_points_text = self.generate(
                    prompt=prompt,
                    system_prompt="You extract key points from financial analyses concisely.",
                    temperature=0.3
                )
                
                # Process the generated key points
                for line in key_points_text.split('\n'):
                    line = line.strip()
                    if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                        point = line.lstrip('-•* ')
                        if point:
                            key_points.append(point)
            except Exception as e:
                logger.error(f"Error extracting key points: {str(e)}")
                # Fallback: use the first few sentences
                sentences = analysis_text.split('.')[:3]
                key_points = [s.strip() + '.' for s in sentences if len(s.strip()) > 20]
        
        return key_points
    
    def _determine_sentiment(self, analysis_text: str) -> Dict[str, str]:
        """
        Determine the sentiment and confidence from analysis text.
        
        Args:
            analysis_text: The full analysis text
            
        Returns:
            Dict with sentiment and confidence
        """
        # Look for explicit sentiment statements
        lower_text = analysis_text.lower()
        
        # Check for explicit sentiment indicators
        sentiment = "neutral"  # Default
        if "bullish" in lower_text or "positive" in lower_text or "strong buy" in lower_text:
            sentiment = "bullish"
        elif "bearish" in lower_text or "negative" in lower_text or "sell" in lower_text:
            sentiment = "bearish"
        
        # Check for explicit confidence indicators
        confidence = "medium"  # Default
        if "high confidence" in lower_text or "strongly" in lower_text:
            confidence = "high"
        elif "low confidence" in lower_text or "uncertain" in lower_text:
            confidence = "low"
        
        return {
            "sentiment": sentiment,
            "confidence": confidence
        }


def main():
    """Test the Model class with a simple example."""
    # Create a Model instance
    model = Model(model="gpt-3.5-turbo")
    
    # Test basic generation
    response = model.generate(
        prompt="What are the key factors to consider when analyzing a technology stock?",
        system_prompt="You are a financial advisor specializing in technology stocks."
    )
    
    print("=== Basic Generation Test ===")
    print(response)
    print("\n")
    
    # Test financial data analysis
    sample_data = {
        "company_profile": {
            "name": "Example Tech Inc.",
            "sector": "Technology",
            "industry": "Software",
            "market_cap": 500000000,
            "price": 45.67
        },
        "financial_ratios": {
            "pe_ratio": 25.4,
            "price_to_sales": 8.2,
            "debt_to_equity": 0.5,
            "current_ratio": 2.1,
            "profit_margin": 0.15
        }
    }
    
    analysis_result = model.analyze_financial_data(
        data=sample_data,
        focus="financial_performance",
        symbol="EXMP"
    )
    
    print("=== Financial Analysis Test ===")
    print(f"Analysis for: {analysis_result['symbol']}")
    print(f"Focus: {analysis_result['focus']}")
    print(f"Sentiment: {analysis_result['sentiment']} (Confidence: {analysis_result['confidence']})")
    print("\nKey Points:")
    for point in analysis_result['key_points']:
        print(f"- {point}")
    print("\nFull Analysis:")
    print(analysis_result['analysis'])
    
    # Test text analysis
    print("\n=== Text Analysis Test ===")
    text_to_analyze = """
    Example Tech Inc. shows strong financial performance with a healthy profit margin of 15% and a current ratio of 2.1, 
    indicating good liquidity. The PE ratio of 25.4 is reasonable for a technology company, though the price-to-sales 
    ratio of 8.2 suggests the stock may be somewhat expensive relative to its revenue. The debt-to-equity ratio of 0.5 
    is manageable and indicates a conservative capital structure. Overall, this appears to be a financially sound company 
    with good growth potential in the software sector.
    """
    
    sentiment_result = model.analyze_text(text_to_analyze, focus="sentiment")
    print(f"Sentiment Analysis: {sentiment_result['analysis']}")
    
    key_points_result = model.analyze_text(text_to_analyze, focus="key_points")
    print(f"Key Points Analysis: {key_points_result['analysis']}")


if __name__ == "__main__":
    main() 