import json
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import agents
from agents.tool_agent import ToolAgent
from agents.analysis_agent import AnalysisAgent
from agents.planning_agent import PlanningAgent
from agents.summarization_agent import SummarizationAgent

# Import prompt functions
from prompts.analysis_prompts import (
    initial_analysis_prompt,
    detailed_analysis_prompt,
    planning_prompt
)

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
        
        # Create necessary directories
        os.makedirs('memory', exist_ok=True)
        os.makedirs('results', exist_ok=True)
        
        # Initialize or load memory
        self.memory_file = f"memory/{self.symbol}_memory.json"
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    self.memory = json.load(f)
                print(f"📂 Loaded existing memory for {self.symbol}")
            except json.JSONDecodeError:
                print(f"⚠️ Error loading memory file. Creating new memory.")
                self._initialize_memory()
        else:
            self._initialize_memory()
    
    def _initialize_memory(self):
        """Initialize a new memory structure for the analysis process."""
        self.memory = {
            "symbol": self.symbol,
            "iterations": [],
            "current_focus": "financial_performance",
            "required_focus_areas": [
                "financial_performance",
                "competitive_analysis",
                "growth_prospects",
                "risk_assessment"
            ],
            "completed_focus_areas": [],
            "start_time": datetime.now().isoformat(),
            "completion_percentage": 0
        }
        self._save_memory()
        print(f"📝 Created new memory for {self.symbol}")
    
    def _save_memory(self):
        """Save the current memory state to disk."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving memory: {str(e)}")
    
    def _update_completion_percentage(self):
        """Update the analysis completion percentage based on iterations and focus areas."""
        required_areas = self.memory.get("required_focus_areas", [])
        completed_areas = self.memory.get("completed_focus_areas", [])
        
        # Base percentage on completed focus areas and iteration count
        if not required_areas:
            area_percentage = 0
        else:
            area_percentage = (len(completed_areas) / len(required_areas)) * 100
        
        # Factor in iteration count (each iteration contributes up to 20%)
        iteration_percentage = min(self.iteration / self.max_iterations * 20, 20)
        
        # Combine the two factors
        total_percentage = min(area_percentage * 0.8 + iteration_percentage, 100)
        
        self.memory["completion_percentage"] = round(total_percentage, 1)
        return self.memory["completion_percentage"]
    
    def run(self) -> str:
        """Runs the iterative deep thinking workflow, coordinating agents, and storing context.
        
        This method implements the full Deep Thinking Chain workflow:
        1. Tool Agent fetches financial data
        2. Analysis Agent analyzes the data
        3. Planning Agent determines next steps
        4. Loop continues until analysis is complete or max iterations reached
        5. Summarization Agent generates final investment summary
        
        Returns:
            str: Path to the final summary file
        """
        print(f"🔍 Starting Deep Thinking Chain analysis for {self.symbol}...")
        
        continue_analysis = True
        while continue_analysis and self.iteration < self.max_iterations:
            self.iteration += 1
            print(f"\n📊 Iteration {self.iteration}/{self.max_iterations}")
            
            # Step 1: Tool Agent - Fetch data based on current focus
            current_focus = self.memory.get("current_focus", "financial_performance")
            print(f"🔧 Tool Agent: Fetching data for {self.symbol} with focus on {current_focus}...")
            
            try:
                if self.iteration == 1 or current_focus == "financial_performance":
                    # First iteration or financial focus: get company profile and basic financials
                    data = {
                        "symbol": self.symbol,
                        "company_profile": self.tool_agent.fetch_company_profile(self.symbol),
                        "financial_ratios": self.tool_agent.fetch_financial_ratios(self.symbol),
                        "income_statement": self.tool_agent.fetch_income_statement(self.symbol, limit=2),
                        "balance_sheet": self.tool_agent.fetch_balance_sheet(self.symbol, limit=2),
                        "cash_flow": self.tool_agent.fetch_cash_flow(self.symbol, limit=2)
                    }
                elif current_focus == "competitive_analysis":
                    # Competitive analysis: get peer companies and comparison data
                    data = {
                        "symbol": self.symbol,
                        "company_profile": self.tool_agent.fetch_company_profile(self.symbol),
                        "peers": self.tool_agent.fetch_peers(self.symbol),
                        "peer_ratios": self.tool_agent.fetch_peer_ratios(self.symbol),
                        "market_share": self.tool_agent.fetch_market_share(self.symbol)
                    }
                elif current_focus == "growth_prospects":
                    # Growth analysis: get growth estimates and future projections
                    data = {
                        "symbol": self.symbol,
                        "company_profile": self.tool_agent.fetch_company_profile(self.symbol),
                        "growth_estimates": self.tool_agent.fetch_growth_estimates(self.symbol),
                        "analyst_recommendations": self.tool_agent.fetch_analyst_recommendations(self.symbol),
                        "earnings_surprises": self.tool_agent.fetch_earnings_surprises(self.symbol)
                    }
                elif current_focus == "risk_assessment":
                    # Risk assessment: get volatility, debt, and risk factors
                    data = {
                        "symbol": self.symbol,
                        "company_profile": self.tool_agent.fetch_company_profile(self.symbol),
                        "financial_ratios": self.tool_agent.fetch_financial_ratios(self.symbol),
                        "sec_filings": self.tool_agent.fetch_sec_filings(self.symbol, limit=5),
                        "price_volatility": self.tool_agent.fetch_price_volatility(self.symbol)
                    }
                else:
                    # Default: get data based on planning agent's focus
                    data = self.tool_agent.fetch_data(self.symbol, current_focus)
                
                # Check for errors in the data
                if any("error" in str(value) for key, value in data.items() if key != "symbol"):
                    print(f"⚠️ Warning: Some data could not be fetched. Continuing with available data.")
            
            except Exception as e:
                print(f"⚠️ Error fetching data: {str(e)}")
                data = {"symbol": self.symbol, "error": str(e)}
            
            # Step 2: Analysis Agent - Analyze data
            print(f"🧠 Analysis Agent: Analyzing {current_focus} data...")
            try:
                analysis_result = self.analysis_agent.analyze(data, focus=current_focus, symbol=self.symbol)
                
                # Add to analyses list
                self.analyses.append(analysis_result)
                
                # Add focus area to completed list if not already there
                if current_focus not in self.memory.get("completed_focus_areas", []):
                    self.memory.setdefault("completed_focus_areas", []).append(current_focus)
                
                # Print analysis summary
                print(f"📊 Analysis complete: {analysis_result.get('sentiment', 'N/A')} sentiment with {analysis_result.get('confidence', 'N/A')} confidence")
                print(f"🔑 Key points:")
                for point in analysis_result.get("key_points", [])[:3]:
                    print(f"  • {point}")
                if len(analysis_result.get("key_points", [])) > 3:
                    print(f"  • ... and {len(analysis_result.get('key_points', [])) - 3} more points")
            
            except Exception as e:
                print(f"⚠️ Error during analysis: {str(e)}")
                analysis_result = {
                    "analysis_type": current_focus,
                    "symbol": self.symbol,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "error": str(e),
                    "insights": f"Error during analysis: {str(e)}",
                    "key_points": ["Analysis failed due to an error"],
                    "sentiment": "neutral",
                    "confidence": "low"
                }
                self.analyses.append(analysis_result)
            
            # Store iteration results in memory
            iteration_memory = {
                "iteration": self.iteration,
                "focus": current_focus,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "data_keys": list(data.keys()),
                "analysis": analysis_result
            }
            self.memory["iterations"].append(iteration_memory)
            
            # Update completion percentage
            completion = self._update_completion_percentage()
            print(f"📈 Analysis progress: {completion}% complete")
            
            # Save memory after each iteration
            self._save_memory()
            
            # Step 3: Planning Agent - Determine next steps
            print("📝 Planning Agent: Determining next steps...")
            try:
                planning_result = self.planning_agent.plan_next(
                    analysis_result=analysis_result,
                    iteration=self.iteration,
                    max_iterations=self.max_iterations,
                    completed_focus_areas=self.memory.get("completed_focus_areas", []),
                    required_focus_areas=self.memory.get("required_focus_areas", [])
                )
                
                # Update memory with planning results
                self.memory["current_focus"] = planning_result.get("next_focus")
                self.memory["planning_reasoning"] = planning_result.get("reasoning")
                
                # Check if we should continue or move to summarization
                continue_analysis = planning_result.get("continue_analysis", False)
                
                # Print planning decision
                if continue_analysis:
                    print(f"🔄 Planning decision: Continue analysis with focus on {planning_result.get('next_focus')}")
                    print(f"💡 Reasoning: {planning_result.get('reasoning')}")
                else:
                    print("✅ Planning decision: Analysis complete. Moving to summarization...")
                    print(f"💡 Reasoning: {planning_result.get('reasoning')}")
            
            except Exception as e:
                print(f"⚠️ Error during planning: {str(e)}")
                # Default to continuing with a different focus area if possible
                completed_areas = self.memory.get("completed_focus_areas", [])
                required_areas = self.memory.get("required_focus_areas", [])
                
                # Find an uncompleted required area
                next_focus = None
                for area in required_areas:
                    if area not in completed_areas:
                        next_focus = area
                        break
                
                # If all required areas are completed or we've reached max iterations, stop
                if not next_focus or self.iteration >= self.max_iterations:
                    continue_analysis = False
                    print("✅ Moving to summarization due to planning error or completion...")
                else:
                    continue_analysis = True
                    self.memory["current_focus"] = next_focus
                    print(f"🔄 Continuing with focus on {next_focus} (default decision due to error)")
            
            # Save memory after planning
            self._save_memory()
        
        # Step 4: Summarization Agent - Generate final summary
        print("📋 Summarization Agent: Generating investment summary...")
        try:
            # Generate the summary
            summary = self.summarization_agent.summarize(self.analyses, symbol=self.symbol)
            
            # Save summary to results directory
            summary_file = f"results/{self.symbol}_summary.md"
            with open(summary_file, 'w') as f:
                f.write(summary)
            
            # Update memory with completion information
            self.memory["completion_time"] = datetime.now().isoformat()
            self.memory["completion_percentage"] = 100
            self.memory["summary_file"] = summary_file
            self._save_memory()
            
            print(f"🎉 Analysis complete! Summary saved to {summary_file}")
            return summary_file
        
        except Exception as e:
            print(f"⚠️ Error generating summary: {str(e)}")
            
            # Create a basic summary with available information
            basic_summary = f"# Investment Summary for {self.symbol}\n\n"
            basic_summary += f"## Analysis Overview\n\n"
            basic_summary += f"* Symbol: {self.symbol}\n"
            basic_summary += f"* Analysis Date: {datetime.now().strftime('%Y-%m-%d')}\n"
            basic_summary += f"* Iterations Completed: {self.iteration}\n\n"
            
            basic_summary += "## Analysis Results\n\n"
            for i, analysis in enumerate(self.analyses):
                basic_summary += f"### Analysis {i+1}: {analysis.get('analysis_type', 'Unknown')}\n\n"
                basic_summary += f"* Sentiment: {analysis.get('sentiment', 'N/A')}\n"
                basic_summary += f"* Confidence: {analysis.get('confidence', 'N/A')}\n\n"
                
                if "key_points" in analysis and analysis["key_points"]:
                    basic_summary += "Key Points:\n\n"
                    for point in analysis["key_points"]:
                        basic_summary += f"* {point}\n"
                    basic_summary += "\n"
            
            basic_summary += "\n## Error Information\n\n"
            basic_summary += f"An error occurred during the summarization process: {str(e)}\n"
            
            # Save basic summary
            summary_file = f"results/{self.symbol}_basic_summary.md"
            with open(summary_file, 'w') as f:
                f.write(basic_summary)
            
            print(f"⚠️ Error in summarization. Basic summary saved to {summary_file}")
            return summary_file


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
    else:
        symbol = input("Enter stock symbol to analyze (e.g., NVDA): ")
    
    # Optional: Allow specifying max iterations
    max_iterations = 5
    if len(sys.argv) > 2:
        try:
            max_iterations = int(sys.argv[2])
        except ValueError:
            print(f"Invalid max iterations value. Using default: {max_iterations}")
    
    # Run the analysis
    chain = DeepThinkingChain(symbol, max_iterations=max_iterations)
    summary_file = chain.run()
    
    print(f"\nTo view results: cat {summary_file}")
