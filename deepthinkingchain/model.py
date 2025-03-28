"""
Model class for the Deep Thinking Chain.

This module contains the Model class which is responsible for generating
text using large language models.
"""

import logging
import os
import re
from typing import List, Dict, Any, Optional, Union
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import LiteLLM for multi-provider support
try:
    import litellm
    from litellm import ModelResponse, completion
    # Configure LiteLLM to drop unsupported parameters
    litellm.drop_params = True
    LITELLM_AVAILABLE = True
except ImportError:
    logger.warning("LiteLLM package not available. Install with 'pip install litellm'")
    LITELLM_AVAILABLE = False


class Model:
    """Wrapper for language model interactions."""
    
    def __init__(self, model: Optional[str] = "openai/o3-mini", **kwargs):
        """Initialize a Model instance.
        
        Args:
            model: Model identifier (provider/model_name)
            **kwargs: Additional arguments to pass to the underlying model
        """
        self.model_id = model
        self.config = kwargs
        logger.info(f"Initialized Model with {model}")
        
        if not LITELLM_AVAILABLE:
            logger.warning("LiteLLM not available. Some functionality may be limited.")
            
        # Check for API keys in environment
        if os.environ.get("OPENAI_API_KEY"):
            logger.info(f"Found OpenAI API key in environment variables")
        if os.environ.get("ANTHROPIC_API_KEY"):
            logger.info(f"Found Anthropic API key in environment variables")
        
        # Track reasoning capabilities
        self.reasoning_model = model in [
            "gpt-4", "gpt-4-turbo", "gpt-4o", 
            "claude-3-opus", "claude-3-sonnet",
            "gemini-pro", "gemini-1.5-pro"
        ]
        
        # Track if this is an O-series model (which only supports temperature=1.0)
        self.o_series_model = model.startswith("o3-") or model.startswith("o1-")
        
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
        # Force temperature=1.0 for O-series models and reasoning models
        if self.o_series_model or self.reasoning_model:
            temperature = 1.0
            
        try:
            logger.info(f"Generating chat completion with model: {self.model_id}")
            logger.debug(f"Messages: {messages}")
            
            if LITELLM_AVAILABLE:
                response = completion(
                    model=self.model_id,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response
            else:
                logger.error("LiteLLM not available")
                return {"error": "LiteLLM not available. Install with 'pip install litellm'"}
        except Exception as e:
            logger.error(f"Error generating chat completion: {str(e)}")
            return {"error": str(e)}

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text based on the prompt.
        
        Args:
            prompt: The prompt to generate text from
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            Generated text as a string
        """
        logger.info(f"Generating text with model {self.model_id}")
        
        # This is a stub implementation
        return f"This is a stub response from {self.model_id} for prompt: {prompt[:50]}..."
    
    def generate_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a JSON response based on the prompt.
        
        Args:
            prompt: The prompt to generate a response from
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            Generated response as a dictionary
        """
        logger.info(f"Generating JSON with model {self.model_id}")
        
        # This is a stub implementation
        try:
            return {
                "result": "success",
                "model": self.model_id,
                "response": f"Stub response from {self.model_id}",
                "prompt_length": len(prompt)
            }
        except Exception as e:
            logger.error(f"Error generating JSON: {str(e)}")
            return {"error": str(e)}


def main():
    """Simple test function for Model class."""
    model = Model("gemini-pro")
    
    # Test 1: Basic generation
    response = model.generate("What is the capital of France?")
    print(f"Test 1 - Basic question:\n{response}\n")
    
    # Test 2: JSON generation
    response = model.generate_json("List three countries and their capitals.")
    print(f"Test 2 - JSON response:\n{json.dumps(response, indent=2)}\n")
    
    # Test 3: System prompt
    response = model.generate(
        "What should I wear today?",
        system_prompt="You are a professional fashion advisor. Give practical advice."
    )
    print(f"Test 3 - Fashion advice:\n{response}")


if __name__ == "__main__":
    main() 