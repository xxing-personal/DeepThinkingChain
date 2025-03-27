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
    """
    A wrapper for language model APIs in DeepThinkingChain.
    
    This class provides a unified interface for interacting with different
    language models, making it easy to switch between providers or models.
    """
    
    def __init__(self, model: str = "o3-mini"):
        """
        Initialize the model.
        
        Args:
            model: The model identifier to use (e.g., "gpt-4o", "claude-3-opus")
        """
        self.model_name = model
        
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
        
        logger.info(f"Initialized model wrapper with model: {model}")
        
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
            logger.info(f"Generating chat completion with model: {self.model_name}")
            logger.debug(f"Messages: {messages}")
            
            if LITELLM_AVAILABLE:
                response = completion(
                    model=self.model_name,
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
        
        # Get response - temperature handling is done in _chat_completion
        response = self._chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract content
        try:
            if LITELLM_AVAILABLE and isinstance(response, ModelResponse):
                return response.choices[0].message.content
            elif isinstance(response, dict) and "error" in response:
                return f"Error: {response['error']}"
            else:
                return "Failed to generate response"
        except Exception as e:
            logger.error(f"Error extracting response content: {str(e)}")
            return f"Error extracting response: {str(e)}"

    def generate_json(self, prompt: str,
                     system_prompt: Optional[str] = None,
                     temperature: float = 0.2,
                     max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate a response and parse it as JSON.
        
        Args:
            prompt: The text prompt
            system_prompt: Optional system prompt to set context
            temperature: Controls randomness (0.0 to 1.0), defaults to lower value for more consistent JSON
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dict or List: The parsed JSON response as a dictionary or list
        """
        # Start with a system prompt that encourages JSON output if none provided
        if system_prompt:
            json_system_prompt = f"{system_prompt} Return your response as valid JSON."
        else:
            json_system_prompt = "Return your response as valid JSON, with no additional text before or after."
            
        # Generate the response - temperature handling is done in _chat_completion and generate
        response_text = self.generate(
            prompt=prompt,
            system_prompt=json_system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Try to parse the response as JSON
        try:
            # First try a direct parse of the full response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON content
                pass
            
            # Look for brackets in the response
            array_start = response_text.find('[')
            array_end = response_text.rfind(']')
            object_start = response_text.find('{')
            object_end = response_text.rfind('}')
            
            # Determine if we have a valid JSON array or object
            if array_start != -1 and array_end != -1 and (object_start == -1 or array_start < object_start):
                # We have an array that starts before any object
                json_text = response_text[array_start:array_end+1]
                return json.loads(json_text)
            elif object_start != -1 and object_end != -1:
                # We have an object
                json_text = response_text[object_start:object_end+1]
                return json.loads(json_text)
            else:
                # No valid JSON markers found
                raise json.JSONDecodeError("No valid JSON found", response_text, 0)
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            logger.debug(f"Failed JSON response: {response_text}")
            # Return a dictionary with the error and original text
            return {
                "error": "Failed to parse JSON response",
                "original_text": response_text
            }

def main():
    """Test the Model class functionality with the O-series model."""
    
    # Create a Model instance with an O-series model
    model = Model(model="o3-mini")
    
    print("=== DeepThinkingChain Model Testing ===\n")
    
    # Test basic text generation
    print("1. Basic Text Generation Test")
    prompt = "Explain the concept of deep thinking in AI in three sentences."
    response = model.generate(prompt=prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}\n")
    
    # Test generation with system prompt
    print("2. Generation with System Prompt Test")
    system_prompt = "You are an expert in financial markets speaking to a novice investor."
    prompt = "What is dollar-cost averaging?"
    response = model.generate(prompt=prompt, system_prompt=system_prompt)
    print(f"System: {system_prompt}")
    print(f"Prompt: {prompt}")
    print(f"Response: {response}\n")
    
    # Test JSON generation
    print("3. JSON Generation Test")
    prompt = "List three technology stocks and their main products. Include keys for 'symbol', 'company_name', and 'main_products'."
    json_response = model.generate_json(prompt=prompt)
    print(f"Prompt: {prompt}")
    print(f"JSON Response: {json.dumps(json_response, indent=2)}")
    
    # Check if we got a valid JSON response (either dict or list without error)
    if (isinstance(json_response, dict) and not json_response.get("error")) or isinstance(json_response, list):
        print("✓ Successfully parsed JSON response")
    else:
        print("✗ Failed to parse JSON response")
    
    print("\n=== Testing Complete ===")


if __name__ == "__main__":
    main()
    