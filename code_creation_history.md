### DeepThinkingChain Class Overview
* Initialization (__init__ method):
Takes a stock symbol and optional max_iterations parameter
Initializes all four agents (Tool, Analysis, Planning, Summarization)
Creates necessary directories (memory, results)
Sets up or loads memory for the analysis process
* Run Method:
Implements the iterative workflow described in the documentation
Follows the sequence: Tool Agent → Analysis Agent → Planning Agent
Continues iterations until either:
The Planning Agent determines analysis is complete
Maximum iterations are reached
Calls the Summarization Agent when analysis is complete
Saves the final summary to a markdown file in the results directory
* Helper Methods:
_save_memory(): Persists the analysis state to disk
* Main Execution Block:
Allows running the script directly with a stock symbol as a command-line argument
Prompts for a symbol if not provided via command line