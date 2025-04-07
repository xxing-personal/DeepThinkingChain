#!/usr/bin/env python
"""
Run script for DeepThinkingChain.

This script demonstrates how to use the DeepThinkingChain for
multi-agent investment analysis on a specified stock symbol.
"""

import argparse
import sys
import time
from deepthinkingchain import DeepThinkingChain


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run DeepThinkingChain analysis for a stock symbol')
    
    parser.add_argument('symbol', 
                        type=str, 
                        help='Stock symbol to analyze (e.g., NVDA, AAPL)')
    
    parser.add_argument('-i', '--iterations', 
                        type=int, 
                        default=3,
                        help='Maximum number of analysis iterations (default: 3)')
    
    parser.add_argument('-q', '--quiet', 
                        action='store_true',
                        help='Run in quiet mode (no progress output)')
    
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    # Parse command line arguments
    args = parse_args()
    
    print(f"🔍 Starting DeepThinkingChain analysis for {args.symbol}")
    print(f"   Max iterations: {args.iterations}")
    print(f"   Verbose mode: {not args.quiet}")
    print("-" * 50)
    
    try:
        # Initialize the DeepThinkingChain
        start_time = time.time()
        chain = DeepThinkingChain(
            symbol=args.symbol,
            max_iterations=args.iterations
        )
        
        # Run the analysis
        results = chain.run(verbose=not args.quiet)
        
        # Display summary information
        print("\n" + "=" * 50)
        print(f"📊 Analysis Summary for {args.symbol}")
        print("=" * 50)
        print(f"Iterations completed: {results['iterations']}")
        print(f"Total time: {results['execution_time_seconds']:.2f} seconds")
        
        # Display recommendation if available
        if 'summary' in results and 'recommendation' in results['summary']:
            recommendation = results['summary']['recommendation']
            confidence = results['summary'].get('confidence', 'N/A')
            print(f"\nRecommendation: {recommendation.upper()} (Confidence: {confidence})")
        
        # Display key points if available
        if 'summary' in results and 'key_points' in results['summary']:
            print("\nKey Points:")
            for idx, point in enumerate(results['summary']['key_points'], 1):
                print(f"  {idx}. {point}")
                
        print(f"\nDetailed results saved to: results/{args.symbol}_analysis.json")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error running analysis: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main() 