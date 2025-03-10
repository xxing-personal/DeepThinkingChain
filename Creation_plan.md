# Deep Thinking Chain for Investment Analysis

## 🎯 Purpose
The purpose of this project is to build a lightweight multi-agent system to conduct iterative deep research cycles, specifically tailored for evaluating investment opportunities (e.g., analyzing a stock like NVDA). The system orchestrates tool-calls, analysis, planning, and summarization iteratively to produce comprehensive investment insights.

---

## 📌 Overview
This lightweight multi-agent system helps investors systematically research stock opportunities. Each agent performs a clearly defined task—fetching data, analyzing results, planning subsequent actions, and summarizing findings—in an iterative "Deep Thinking Chain" loop.

---

## 🔄 Workflow

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

---

## 🔄 Workflow Example

```
[Coordinator] → Initiates query for stock (e.g., NVDA)
    ├── ToolAgent fetches initial financial data
    ├── Analysis Agent extracts insights (moat, CapEx, risks)
    ├── Planning Agent decides next steps (further analysis needed?)
    └── Loop repeats as needed → Final Summarization Agent synthesizes insights
```

---

## 📂 Folder Structure
```
deep-thinking-chain-investment/
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

---

## 📚 Key Function Docstrings

### orchestrator.py
```python
class DeepThinkingChain:
    """Orchestrates multi-agent investment analysis cycles for a given stock symbol."""

    def __init__(self, symbol: str):
        """Initialize DeepThinkingChain with the target investment symbol."""

    def run(self):
        """Runs the iterative deep thinking workflow, coordinating agents, and storing context."""
```

### agents/tool_agent.py
```python
class ToolAgent:
    """Agent responsible for fetching external financial data."""

    def fetch_company_profile(self, symbol: str) -> dict:
        """Fetches basic company profile from financialmodelingprep API."""

    def fetch_financial_ratios(self, symbol: str) -> dict:
        """Retrieves financial ratios data for deeper financial insights."""
```

### agents/analysis_agent.py
```python
class AnalysisAgent:
    """Agent performing detailed analysis and extraction of insights from raw financial data."""

    def analyze(self, data: dict) -> dict:
        """Analyzes financial data to identify key insights and investment factors like moat, CapEx, and risks."""
```

### agents/planning_agent.py
```python
class PlanningAgent:
    """Agent deciding next actions based on current analysis outcomes."""

    def plan_next(self, analysis_result: dict) -> dict:
        """Determines the next iteration's actions or signals summarization."""
```

### agents/summarization_agent.py
```python
class SummarizationAgent:
    """Agent that compiles and synthesizes the entire research process into an actionable summary."""

    def summarize(self, analyses: list[dict]) -> str:
        """Generates a comprehensive final investment recommendation summary."""
```

---

This context ensures clarity, ease of development, and straightforward maintainability as you build your MVP.

