"""
Test script for the Model class in DeepThinkingChain.

This script demonstrates how to use the Model class for various tasks:
1. Basic text generation
2. Financial data analysis
3. Text analysis (sentiment, key points)
4. Using different models and providers
"""

import json
import os
from dotenv import load_dotenv
from model import Model

# Load environment variables
load_dotenv()

def test_basic_generation():
    """Test basic text generation with the Model class."""
    print("\n=== Testing Basic Text Generation ===")
    
    # Create a Model instance with default settings (gpt-4o)
    model = Model()
    
    # Generate text with a simple prompt
    prompt = "What are the key factors to consider when analyzing a technology stock?"
    system_prompt = "You are a financial advisor specializing in technology stocks."
    
    print(f"Prompt: {prompt}")
    print(f"System Prompt: {system_prompt}")
    print("\nGenerating response...")
    
    response = model.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.7
    )
    
    print("\nResponse:")
    print(response)

def test_financial_analysis():
    """Test financial data analysis with the Model class."""
    print("\n=== Testing Financial Data Analysis ===")
    
    # Create a Model instance
    model = Model(model="gpt-3.5-turbo")  # Using a faster model for testing
    
    # Sample financial data
    sample_data = {
        "company_profile": {
            "name": "Example Tech Inc.",
            "symbol": "EXMP",
            "sector": "Technology",
            "industry": "Software",
            "market_cap": 500000000,
            "price": 45.67,
            "description": "Example Tech Inc. develops cloud-based software solutions for small businesses."
        },
        "financial_ratios": {
            "pe_ratio": 25.4,
            "price_to_sales": 8.2,
            "debt_to_equity": 0.5,
            "current_ratio": 2.1,
            "profit_margin": 0.15,
            "return_on_equity": 0.18,
            "return_on_assets": 0.12
        },
        "income_statement": {
            "revenue": 120000000,
            "gross_profit": 80000000,
            "operating_income": 30000000,
            "net_income": 18000000,
            "eps": 1.8
        }
    }
    
    print(f"Analyzing financial data for: {sample_data['company_profile']['name']} ({sample_data['company_profile']['symbol']})")
    print("Focus: financial_performance")
    print("\nGenerating analysis...")
    
    # Analyze the financial data
    analysis_result = model.analyze_financial_data(
        data=sample_data,
        focus="financial_performance",
        symbol=sample_data['company_profile']['symbol']
    )
    
    # Print the results
    print(f"\nSentiment: {analysis_result['sentiment']} (Confidence: {analysis_result['confidence']})")
    print("\nKey Points:")
    for point in analysis_result['key_points']:
        print(f"- {point}")
    
    print("\nAnalysis Preview:")
    print(analysis_result['analysis'][:500] + "...\n")

def test_text_analysis():
    """Test text analysis with the Model class."""
    print("\n=== Testing Text Analysis ===")
    
    # Create a Model instance
    model = Model()
    
    # Sample text to analyze
    text_to_analyze = """
    Example Tech Inc. shows strong financial performance with a healthy profit margin of 15% and a current ratio of 2.1, 
    indicating good liquidity. The PE ratio of 25.4 is reasonable for a technology company, though the price-to-sales 
    ratio of 8.2 suggests the stock may be somewhat expensive relative to its revenue. The debt-to-equity ratio of 0.5 
    is manageable and indicates a conservative capital structure. Overall, this appears to be a financially sound company 
    with good growth potential in the software sector. However, investors should be cautious about the high price-to-sales 
    ratio, which could indicate overvaluation if growth slows down.
    """
    
    print("Analyzing text for sentiment...")
    sentiment_result = model.analyze_text(text_to_analyze, focus="sentiment")
    print(f"Sentiment Analysis Result: {sentiment_result['analysis']}")
    
    print("\nAnalyzing text for key points...")
    key_points_result = model.analyze_text(text_to_analyze, focus="key_points")
    print(f"Key Points Analysis Result: {key_points_result['analysis']}")

def test_different_models():
    """Test using different models with the Model class."""
    print("\n=== Testing Different Models ===")
    
    # Test with different models if available
    models_to_test = [
        {"name": "gpt-3.5-turbo", "provider": "openai"},
        {"name": "gpt-4o", "provider": "openai"},
    ]
    
    # Add LiteLLM models if available
    if os.environ.get("ANTHROPIC_API_KEY"):
        models_to_test.append({"name": "claude-3-sonnet", "provider": "anthropic", "use_litellm": True})
    
    prompt = "Explain the concept of intrinsic value in investing in one paragraph."
    
    for model_config in models_to_test:
        try:
            print(f"\nTesting model: {model_config['name']} (Provider: {model_config['provider']})")
            
            # Create a Model instance with the specified configuration
            model = Model(
                model=model_config["name"],
                provider=model_config["provider"],
                use_litellm=model_config.get("use_litellm", False)
            )
            
            # Generate text
            response = model.generate(prompt=prompt, temperature=0.7)
            
            print(f"Response from {model_config['name']}:")
            print(response)
            
        except Exception as e:
            print(f"Error testing {model_config['name']}: {str(e)}")

def main():
    """Run all tests."""
    print("=== Model Class Test Script ===")
    
    # Run the tests
    test_basic_generation()
    test_financial_analysis()
    test_text_analysis()
    test_different_models()
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    main() 