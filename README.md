# DeepThinkingChain

A lightweight Python framework for building multi-agent systems that can collaborate to solve complex tasks, specifically tailored for evaluating investment opportunities.

## Project Structure

DeepThinkingChain/
├── orchestrator.py       # Main orchestration logic for agent coordination
├── agents/               # Individual agent implementations
│   ├── __init__.py
│   ├── tool_agent.py     # Agent for tool usage and execution
│   ├── analysis_agent.py # Agent for data analysis
│   ├── planning_agent.py # Agent for task planning and decomposition
│   └── summarization_agent.py # Agent for summarizing results
├── prompts/              # Prompt templates for agents
│   └── analysis_prompts.py
└── results/              # Directory for storing execution results

## Setup Instructions

1. Create and activate a virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
   - Get a free API key from [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/)
   - Create a `.env` file in the project root
   - Add your API key: `FMP_API_KEY=your_api_key_here`

## Usage

### Testing the Tool Agent

To test the ToolAgent's data fetching capabilities:

```bash
python agents/tool_agent.py [SYMBOL]
```

Where `[SYMBOL]` is an optional stock symbol (defaults to AAPL if not provided).

### Running the Full Analysis

To run a complete investment analysis:

```bash
python orchestrator.py [SYMBOL]
```

Where `[SYMBOL]` is the stock symbol you want to analyze (e.g., NVDA, AAPL, MSFT).

## License

MIT
