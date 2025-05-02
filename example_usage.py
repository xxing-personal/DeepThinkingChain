#!/usr/bin/env python
"""
Example Usage of DeepThinkingChain.

This example demonstrates how to use the DeepThinkingChain in a Python script.
"""

from deepthinkingchain import DeepThinkingChain


def analyze_query(query: str, max_iterations: int = 3) -> None:
    """
    Analyze a query using the DeepThinkingChain.
    
    Args:
        query: The query to analyze (e.g., 'Analyze AAPL stock performance')
        max_iterations: Maximum number of analysis iterations
    """
    print(f"Analyzing query: {query}")
    
    # Initialize the chain
    chain = DeepThinkingChain(
        user_input=query,
        max_iterations=max_iterations
    )
    
    # Run the analysis
    results = chain.run(verbose=True)
    
    # Access and use the results programmatically
    summary = results['summary']
    
    print("\nAnalysis Results:")
    print(f"Summary: {summary}")
    
    # You can access all analyses performed
    print(f"\nNumber of iterations performed: {results['iterations']}")
    print(f"Execution time: {results['execution_time_seconds']:.2f} seconds")
    
    # The full results are available for further processing
    return results


if __name__ == "__main__":
    # Example: Analyze Apple stock with 2 iterations
    query = "Analyze Apple (AAPL) stock performance and provide investment recommendations"
    results = analyze_query(query, max_iterations=2)
    
    # Example: You could analyze multiple queries
    # queries = [
    #     "Analyze Microsoft (MSFT) stock performance",
    #     "Analyze Google (GOOGL) stock performance",
    #     "Analyze Amazon (AMZN) stock performance"
    # ]
    # for query in queries:
    #     analyze_query(query) 