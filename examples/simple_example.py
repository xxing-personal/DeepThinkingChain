"""
Simple example demonstrating DeepThinkingChain usage.

This script shows how to initialize and use the DeepThinkingChain package.
"""

import os
from dotenv import load_dotenv
from deepthinkingchain import DeepThinkingChain, Model

# Load environment variables (API keys, etc.)
load_dotenv()

def main():
    # Check if API keys are available
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️ Warning: No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file.")
    
    # Initialize a language model (defaults to OpenAI)
    model = Model(model="gpt-4")
    
    # Simple test of the model
    response = model.generate(
        prompt="What are the key factors to consider when evaluating a tech company's financials?",
        system_prompt="You are a financial analyst specializing in technology companies."
    )
    
    print("\n=== Model Test Response ===")
    print(response)
    print("\n==========================")
    
    # Initialize the Deep Thinking Chain for a specific stock symbol
    # Note: This requires API keys and functioning agent implementations
    try:
        print("\nInitializing DeepThinkingChain for NVDA...")
        chain = DeepThinkingChain(symbol="NVDA", max_iterations=3)
        
        # This would normally start the full analysis
        # Commented out since it requires all components to be implemented
        # summary_file = chain.run()
        # print(f"Analysis complete. Summary saved to {summary_file}")
        
        print("Chain initialized successfully.")
        print("To run a full analysis, uncomment the chain.run() line in the code.")
        
    except Exception as e:
        print(f"Error initializing DeepThinkingChain: {str(e)}")
        print("This is expected if you don't have all agent implementations yet.")

if __name__ == "__main__":
    main() 