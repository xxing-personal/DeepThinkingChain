import json
import os
from typing import List, Dict, Any

# Import agents
from agents.tool_agent import ToolAgent
from agents.analysis_agent import AnalysisAgent
from agents.planning_agent import PlanningAgent
from agents.summarization_agent import SummarizationAgent

class DeepThinkingChain:
    """Orchestrates multi-agent investment analysis cycles for a given stock symbol."""

    def __init__(self, symbol: str, max_iterations: int = 5):
        """Initialize DeepThinkingChain with the target investment symbol.
        
        Args:
            symbol: The stock symbol to analyze (e.g., 'NVDA')
            max_iterations: Maximum number of analysis iterations to perform
        """
        self.symbol = symbol.upper()
        self.max_iterations = max_iterations
        self.iteration = 0
        self.analyses = []
        self.memory = {}
        
        # Initialize agents
        self.tool_agent = ToolAgent()
        self.analysis_agent = AnalysisAgent()
        self.planning_agent = PlanningAgent()
        self.summarization_agent = SummarizationAgent()
        
        # Create memory directory if it doesn't exist
        os.makedirs('memory', exist_ok=True)
        os.makedirs('results', exist_ok=True)
        
        # Initialize or load memory
        self.memory_file = f"memory/{self.symbol}_memory.json"
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = {
                "symbol": self.symbol,
                "iterations": [],
                "current_focus": "initial_overview"
            }
            self._save_memory()
    
    def _save_memory(self):
        """Save the current memory state to disk."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def run(self):
        """Runs the iterative deep thinking workflow, coordinating agents, and storing context.
        
        Returns:
            str: Path to the final summary file
        """
        print(f"🔍 Starting Deep Thinking Chain analysis for {self.symbol}...")
        
        continue_analysis = True
        while continue_analysis and self.iteration < self.max_iterations:
            self.iteration += 1
            print(f"\n📊 Iteration {self.iteration}/{self.max_iterations}")
            
            # Step 1: Tool Agent - Fetch data
            print(f"🔧 Tool Agent: Fetching data for {self.symbol}...")
            if self.iteration == 1:
                # First iteration: get company profile and basic financials
                data = {
                    "company_profile": self.tool_agent.fetch_company_profile(self.symbol),
                    "financial_ratios": self.tool_agent.fetch_financial_ratios(self.symbol)
                }
            else:
                # Subsequent iterations: get data based on planning agent's focus
                focus = self.memory.get("current_focus", "financial_performance")
                data = self.tool_agent.fetch_data(self.symbol, focus)
            
            # Step 2: Analysis Agent - Analyze data
            print("🧠 Analysis Agent: Analyzing data...")
            analysis_result = self.analysis_agent.analyze(data)
            self.analyses.append(analysis_result)
            
            # Store iteration results in memory
            iteration_memory = {
                "iteration": self.iteration,
                "focus": self.memory.get("current_focus"),
                "data": data,
                "analysis": analysis_result
            }
            self.memory["iterations"].append(iteration_memory)
            self._save_memory()
            
            # Step 3: Planning Agent - Determine next steps
            print("📝 Planning Agent: Determining next steps...")
            planning_result = self.planning_agent.plan_next(analysis_result)
            
            # Update memory with planning results
            self.memory["current_focus"] = planning_result.get("next_focus")
            self._save_memory()
            
            # Check if we should continue or move to summarization
            continue_analysis = planning_result.get("continue_analysis", False)
            
            if not continue_analysis:
                print("✅ Analysis complete. Moving to summarization...")
                break
        
        # Step 4: Summarization Agent - Generate final summary
        print("📋 Summarization Agent: Generating investment summary...")
        summary = self.summarization_agent.summarize(self.analyses)
        
        # Save summary to results directory
        summary_file = f"results/{self.symbol}_summary.md"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"🎉 Analysis complete! Summary saved to {summary_file}")
        return summary_file


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
    else:
        symbol = input("Enter stock symbol to analyze (e.g., NVDA): ")
    
    chain = DeepThinkingChain(symbol)
    summary_file = chain.run()
    
    print(f"\nTo view results: cat {summary_file}")
