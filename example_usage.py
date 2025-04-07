#!/usr/bin/env python
"""
Example Usage of DeepThinkingChain.

This example demonstrates how to use the DeepThinkingChain in a Python script.
"""

from deepthinkingchain import DeepThinkingChain


def analyze_stock(symbol: str, max_iterations: int = 3) -> None:
    """
    Analyze a stock using the DeepThinkingChain.
    
    Args:
        symbol: The stock symbol to analyze (e.g., 'AAPL')
        max_iterations: Maximum number of analysis iterations
    """
    print(f"Analyzing {symbol}...")
    
    # Initialize the chain
    chain = DeepThinkingChain(
        symbol=symbol,
        max_iterations=max_iterations
    )
    
    # Run the analysis
    results = chain.run(verbose=True)
    
    # Access and use the results programmatically
    summary = results['summary']
    
    print("\nAnalysis Results:")
    print(f"Recommendation: {summary.get('recommendation', 'N/A')}")
    print(f"Confidence: {summary.get('confidence', 'N/A')}")
    
    # You can access all analyses performed
    print(f"\nNumber of analyses performed: {len(results['analyses'])}")
    
    # The full results are available for further processing
    return results


if __name__ == "__main__":
    # Example: Analyze Apple stock with 2 iterations
    results = analyze_stock("AAPL", max_iterations=2)
    
    # Example: You could analyze multiple stocks
    # stocks = ["AAPL", "MSFT", "GOOG", "AMZN"]
    # for stock in stocks:
    #     analyze_stock(stock) 