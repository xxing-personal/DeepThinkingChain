# DeepThinkingChain

A lightweight Python framework for building multi-agent systems that can collaborate to solve complex tasks.

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

## Getting Started

1.Install dependencies:

```bash
pip install -r requirements.txt
```

2.Run the orchestrator:

```bash
python orchestrator.py
```

## License

MIT
