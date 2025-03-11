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
