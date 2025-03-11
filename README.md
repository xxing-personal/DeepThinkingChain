# DeepThinkingChain

A multi-agent system for conducting iterative deep research cycles for investment analysis.

## Overview

DeepThinkingChain is a lightweight multi-agent system designed to help investors systematically research stock opportunities. Each agent performs a clearly defined task—fetching data, analyzing results, planning subsequent actions, and summarizing findings—in an iterative "Deep Thinking Chain" loop.

## Workflow

```
[Coordinator] → [Tool Agent] → [Analysis Agent] → [Planning Agent] (repeat)
                            │
                            └──→ [Summarization Agent]
```

**Cycle steps:**
1. **Tool Call:** Fetches external financial and market data.
2. **Analysis:** Extracts key insights, identifies strengths, risks, and opportunities.
3. **Planning:** Determines if further iterations are needed or moves to summarization.
4. **Summarization:** Aggregates and summarizes key insights for final decision-making.

## Components

### Agents

- **ToolAgent**: Fetches financial data from external APIs (Financial Modeling Prep)
- **AnalysisAgent**: Analyzes financial data to extract insights and investment factors
- **PlanningAgent**: Decides whether to continue research or proceed to summarization
- **SummarizationAgent**: Compiles and synthesizes analyses into a comprehensive investment summary

### Prompts

The system uses a set of prompt templates and functions to generate prompts for the various agents:

- **initial_analysis_prompt**: Generates a prompt for the first analysis iteration, focusing on general financial performance
- **detailed_analysis_prompt**: Generates prompts for subsequent iterations with specific focus areas (competitive, growth, risk)
- **planning_prompt**: Generates a prompt for planning the next steps in the analysis process

## Usage

```python
from orchestrator import DeepThinkingChain

# Initialize the chain with a stock symbol
chain = DeepThinkingChain("NVDA")

# Run the analysis
chain.run()

# Results will be saved to results/NVDA_summary.md
```

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables:
   - Create a `.env` file with your API keys:
     ```
     FMP_API_KEY=your_financial_modeling_prep_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```
4. Run the orchestrator: `python orchestrator.py SYMBOL`

## Step-by-Step Example

Here's a complete example of how to analyze NVIDIA (NVDA) using DeepThinkingChain:

### Prerequisites

1. **Get API Keys**:
   - Sign up for a free API key at [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/)
   - Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)

2. **Environment Setup**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/DeepThinkingChain.git
   cd DeepThinkingChain
   
   # Create and activate a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create .env file with your API keys
   echo "FMP_API_KEY=your_financial_modeling_prep_api_key" > .env
   echo "OPENAI_API_KEY=your_openai_api_key" >> .env
   ```

### Running the Analysis

3. **Run the Analysis**:
   ```bash
   # Run the analysis with default settings (5 iterations)
   python orchestrator.py NVDA
   
   # Or specify a custom number of iterations
   python orchestrator.py NVDA 3
   ```

4. **Monitor the Progress**:
   - The system will display progress information for each iteration:
     ```
     🔍 Starting Deep Thinking Chain analysis for NVDA...
     
     📊 Iteration 1/3
     🔧 Tool Agent: Fetching data for NVDA with focus on financial_performance...
     🧠 Analysis Agent: Analyzing financial_performance data...
     📊 Analysis complete: positive sentiment with high confidence
     📈 Analysis progress: 33.3% complete
     📝 Planning Agent: Determining next steps...
     ```

5. **Review the Results**:
   ```bash
   # View the generated summary
   cat results/NVDA_summary.md
   ```

### Understanding the Output

The final summary in `results/NVDA_summary.md` includes:

- **Executive Summary**: Overall investment recommendation with key points
- **Company Overview**: Business model and market position
- **Financial Analysis**: Key metrics and financial health assessment
- **Growth Prospects**: Future growth opportunities and projections
- **Competitive Advantages**: Analysis of NVIDIA's moat and strengths
- **Risk Factors**: Potential challenges and threats
- **Valuation**: Fair value estimate and valuation metrics
- **Investment Recommendation**: Final recommendation with rationale

### Advanced Usage

You can also use the DeepThinkingChain programmatically in your Python code:

```python
from orchestrator import DeepThinkingChain

# Initialize with custom parameters
chain = DeepThinkingChain(
    symbol="NVDA",
    max_iterations=4  # Set custom number of iterations
)

# Run the analysis
summary_file = chain.run()

# Process the results
with open(summary_file, 'r') as f:
    summary = f.read()
    
print(f"Analysis complete! Summary saved to {summary_file}")
```

## Directory Structure

```
deep-thinking-chain/
├── orchestrator.py
├── memory/
│   └── [symbol]_memory.json
├── agents/
│   ├── __init__.py
│   ├── tool_agent.py
│   ├── analysis_agent.py
│   ├── planning_agent.py
│   └── summarization_agent.py
├── prompts/
│   └── analysis_prompts.py
└── results/
    └── <symbol>_summary.md
```

## License

MIT
