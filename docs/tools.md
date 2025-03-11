# Tools Package Documentation

## Overview

The Tools package provides a flexible and extensible framework for creating and managing tools in the DeepThinkingChain project. Tools are reusable components that perform specific tasks, such as fetching financial data, performing calculations, or processing information.

## Components

### Tool Base Class

The `Tool` class is the foundation of the tools system. It provides a common interface for all tools and includes features like:

- **Standardized Interface**: All tools follow the same pattern, making them easy to use and extend.
- **Self-Documentation**: Tools describe their inputs, outputs, and capabilities.
- **Function Conversion**: Convert existing functions to tools with minimal effort.
- **Input Validation**: Tools can validate their inputs to ensure correct usage.

### ToolManager

The `ToolManager` class manages a collection of tools and provides methods to:

- **Register Tools**: Add tools to the manager for later use.
- **Retrieve Tools**: Get tools by name or category.
- **Set Default Tools**: Define default tools for specific categories.
- **Generate Documentation**: Create formatted documentation for all available tools.
- **Load Tools Dynamically**: Discover and load tools from Python files in a directory.

### Financial Data Tools

The package includes several tools for fetching financial data from external APIs:

- **CompanyProfileTool**: Fetches basic company information.
- **FinancialRatiosTool**: Retrieves financial ratios data.
- **IncomeStatementTool**: Gets income statement data.

### Web Scraping Tools

The package includes tools for scraping web content:

- **WebScrapingTool**: Basic web scraping tool that fetches and converts HTML content to markdown.
- **AdvancedWebScrapingTool**: Enhanced scraping tool with support for JavaScript-rendered content.

### Web Search Tools

The package includes tools for searching the web:

- **GoogleSearchTool**: Searches the web using ScrapingDog's Google Search API, providing rich results including "People Also Asked" questions.
- **DuckDuckGoSearchTool**: Searches the web using DuckDuckGo's API (no API key required).
- **NewsSearchTool**: Searches for news articles using NewsAPI.

## Usage Examples

### Creating a Custom Tool

```python
from tools import Tool

class CalculatorTool(Tool):
    name = "calculator"
    description = "A simple calculator tool that performs basic arithmetic operations."
    inputs = {
        "operation": {
            "type": "str",
            "description": "The operation to perform (add, subtract, multiply, divide)",
            "required": True
        },
        "a": {
            "type": "float",
            "description": "First number",
            "required": True
        },
        "b": {
            "type": "float",
            "description": "Second number",
            "required": True
        }
    }
    output_type = "float"
    capabilities = "Can perform basic arithmetic operations."
    category = "math"
    
    def forward(self, operation: str, a: float, b: float) -> float:
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")

# Create and use the tool
calculator = CalculatorTool()
result = calculator(operation="add", a=5, b=3)
print(f"5 + 3 = {result}")  # Output: 5 + 3 = 8
```

### Creating a Tool from a Function

```python
from tools import Tool

def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert a temperature from Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5 / 9

# Create a tool from the function
converter_tool = Tool.from_function(
    fahrenheit_to_celsius,
    name="temperature_converter",
    description="Converts temperature from Fahrenheit to Celsius.",
    category="conversion",
    output_type="float"
)

# Use the tool
celsius = converter_tool(fahrenheit=98.6)
print(f"98.6°F = {celsius:.2f}°C")  # Output: 98.6°F = 37.00°C
```

### Using the ToolManager

```python
from tools import ToolManager
from tools.financial_data_tool import CompanyProfileTool

# Create a tool manager
manager = ToolManager()

# Add tools to the manager
manager.add_tool(CompanyProfileTool())

# Get a tool by name
company_profile_tool = manager.get_tool_by_name("company_profile")
if company_profile_tool:
    result = company_profile_tool(symbol="AAPL")
    print(f"Company: {result.get('companyName')}")
    print(f"Industry: {result.get('industry')}")

# Get tools by category
financial_tools = manager.get_tools_by_category("financial_data")
print(f"Financial tools: {list(financial_tools.keys())}")

# Generate documentation for all tools
documentation = manager.get_tools_prompt()
print(documentation)
```

### Using Web Scraping Tools

```python
from tools import WebScrapingTool

# Create a web scraping tool
scraper = WebScrapingTool()

# Scrape a webpage
url = "https://en.wikipedia.org/wiki/NVIDIA"
content = scraper(url=url, max_length=5000)
print(f"Content preview:\n{content[:500]}...")

# For JavaScript-rendered content
from tools import AdvancedWebScrapingTool

# Make sure to set the SCRAPING_DOG_API_KEY environment variable
advanced_scraper = AdvancedWebScrapingTool()
dynamic_content = advanced_scraper(url="https://finance.yahoo.com/quote/NVDA", dynamic=True)
```

### Using Web Search Tools

```python
from tools import DuckDuckGoSearchTool, GoogleSearchTool, NewsSearchTool

# Search with DuckDuckGo (no API key required)
duck_search = DuckDuckGoSearchTool()
results = duck_search(query="NVIDIA stock performance")
print(results)

# Search with Google via ScrapingDog
# Set SCRAPING_DOG_API_KEY environment variable
google_search = GoogleSearchTool()
results = google_search(query="NVIDIA financial results 2023")
print(results)

# Search for news (requires API key)
# Set NEWS_API_KEY environment variable
news_search = NewsSearchTool()
results = news_search(query="NVIDIA AI chips", days=30)
print(results)
```

## Extending the Tools Package

To add new tools to the system:

1. **Create a New Tool Class**: Subclass `Tool` and implement the `forward` method.
2. **Define Tool Metadata**: Set the `name`, `description`, `inputs`, `output_type`, `capabilities`, and `category` class attributes.
3. **Register with ToolManager**: Add the tool to a `ToolManager` instance.

You can also organize related tools into separate modules and use the `load_tools_from_directory` method to discover and load them automatically. 