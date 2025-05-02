#!/usr/bin/env python3
"""
Script to run the DeepThinkingChain orchestrator.

This script provides a command-line interface to run the DeepThinkingChain
for analyzing queries using multi-agent orchestration.
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, Any

from deepthinkingchain.orchestrator import DeepThinkingChain

def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging configuration.
    
    Args:
        log_level: The logging level to use (default: INFO)
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def run_analysis(query: str, max_iterations: int = 30, session_id: str = None, verbose: bool = True) -> Dict[str, Any]:
    """Run the DeepThinkingChain analysis.
    
    Args:
        query: The query to analyze
        max_iterations: Maximum number of iterations to perform
        session_id: Optional session ID to use
        verbose: Whether to print progress messages
        
    Returns:
        Dict containing the analysis results
    """
    # Create and run the DeepThinkingChain
    chain = DeepThinkingChain(
        user_input=query,
        max_iterations=max_iterations,
        session_id=session_id
    )
    
    # Run the analysis
    results = chain.run(verbose=verbose)
    
    return results

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Run DeepThinkingChain analysis on a query."
    )
    
    parser.add_argument(
        "query",
        help="The query to analyze"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=30,
        help="Maximum number of iterations to perform (default: 30)"
    )
    
    parser.add_argument(
        "--session-id",
        help="Optional session ID to use"
    )
    
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Run in quiet mode (minimal output)"
    )
    
    parser.add_argument(
        "--output",
        help="Optional output file to save results (in addition to automatic saving)"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    
    try:
        # Run the analysis
        results = run_analysis(
            query=args.query,
            max_iterations=args.max_iterations,
            session_id=args.session_id,
            verbose=not args.quiet
        )
        
        # Print summary
        if not args.quiet:
            print("\nAnalysis Results:")
            print(f"Summary: {results['summary']}")
            print(f"\nNumber of iterations performed: {results['iterations']}")
            print(f"Execution time: {results['execution_time_seconds']:.2f} seconds")
        
        # Save to additional output file if specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
                if not args.quiet:
                    print(f"\nResults also saved to: {args.output}")
        
        return 0
        
    except Exception as e:
        logging.error(f"Error running analysis: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 