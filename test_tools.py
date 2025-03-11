"""
Test script for the Tool and ToolManager classes.

This script demonstrates how to use the Tool and ToolManager classes in the DeepThinkingChain project.
It includes tests for tool creation, tool management, and financial data tools.
"""

import os
import dotenv
from tools import Tool, ToolManager
from tools.financial_data_tool import CompanyProfileTool, FinancialRatiosTool, IncomeStatementTool

# Load environment variables
dotenv.load_dotenv()

def test_tool_creation():
    """Test creating a custom tool."""
    print("\n=== Testing Tool Creation ===")
    
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
        capabilities = "Can perform basic arithmetic operations: addition, subtraction, multiplication, and division."
        category = "math"
        
        def forward(self, operation: str, a: float, b: float) -> float:
            """
            Perform a basic arithmetic operation.
            
            Args:
                operation: The operation to perform (add, subtract, multiply, divide)
                a: First number
                b: Second number
                
            Returns:
                float: The result of the operation
            """
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
    
    # Create a calculator tool
    calculator = CalculatorTool()
    
    # Test the calculator tool
    print("Testing calculator tool:")
    operations = [
        ("add", 5, 3),
        ("subtract", 10, 4),
        ("multiply", 6, 7),
        ("divide", 15, 3)
    ]
    
    for op, a, b in operations:
        result = calculator(operation=op, a=a, b=b)
        print(f"  {a} {op} {b} = {result}")

def test_tool_from_function():
    """Test creating a tool from a function."""
    print("\n=== Testing Tool from Function ===")
    
    def fahrenheit_to_celsius(fahrenheit: float) -> float:
        """
        Convert a temperature from Fahrenheit to Celsius.
        
        Args:
            fahrenheit: Temperature in Fahrenheit
            
        Returns:
            float: Temperature in Celsius
        """
        return (fahrenheit - 32) * 5 / 9
    
    # Create a tool from the function
    converter_tool = Tool.from_function(
        fahrenheit_to_celsius,
        name="temperature_converter",
        description="Converts temperature from Fahrenheit to Celsius.",
        category="conversion",
        output_type="float"
    )
    
    # Test the converter tool
    fahrenheit = 98.6
    celsius = converter_tool(fahrenheit=fahrenheit)
    print(f"Testing temperature converter tool:")
    print(f"  {fahrenheit}°F = {celsius:.2f}°C")

def test_tool_manager():
    """Test the ToolManager class."""
    print("\n=== Testing ToolManager ===")
    
    # Create a tool manager
    manager = ToolManager()
    
    # Create a calculator tool
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
        capabilities = "Can perform basic arithmetic operations: addition, subtraction, multiplication, and division."
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
    
    # Create a temperature converter tool
    def fahrenheit_to_celsius(fahrenheit: float) -> float:
        return (fahrenheit - 32) * 5 / 9
    
    converter_tool = Tool.from_function(
        fahrenheit_to_celsius,
        name="temperature_converter",
        description="Converts temperature from Fahrenheit to Celsius.",
        category="conversion",
        output_type="float"
    )
    
    # Add tools to the manager
    manager.add_tool(CalculatorTool())
    manager.add_tool(converter_tool)
    
    # Add financial data tools
    manager.add_tool(CompanyProfileTool())
    manager.add_tool(FinancialRatiosTool())
    manager.add_tool(IncomeStatementTool())
    
    # Try to import and add web scraping tools
    try:
        from tools.web_scraping_tool import WebScrapingTool, AdvancedWebScrapingTool
        manager.add_tool(WebScrapingTool())
        manager.add_tool(AdvancedWebScrapingTool())
    except ImportError:
        print("Web scraping tools not available.")
    
    # Try to import and add web search tools
    try:
        from tools.web_search_tool import GoogleSearchTool, DuckDuckGoSearchTool, NewsSearchTool
        manager.add_tool(GoogleSearchTool())
        manager.add_tool(DuckDuckGoSearchTool())
        manager.add_tool(NewsSearchTool())
    except ImportError:
        print("Web search tools not available.")
    
    # Set default tools for categories
    manager.set_default_tool("math", "calculator")
    manager.set_default_tool("conversion", "temperature_converter")
    manager.set_default_tool("financial_data", "company_profile")
    
    # Print available tools
    print("Available tools:")
    for name in manager.get_tool_names():
        print(f"  - {name}")
    
    # Print available categories
    print("\nAvailable categories:")
    for category in manager.get_categories():
        print(f"  - {category}")
    
    # Print default tools
    print("\nDefault tools:")
    for category in manager.get_categories():
        default_tool = manager.get_default_tool(category)
        if default_tool:
            print(f"  - {category}: {default_tool.name}")
        else:
            print(f"  - {category}: None")

def test_financial_data_tools():
    """Test the financial data tools."""
    print("\n=== Testing Financial Data Tools ===")
    
    # Check if API key is set
    if not os.getenv("FMP_API_KEY"):
        print("FMP_API_KEY environment variable not set. Skipping financial data tools test.")
        return
    
    # Create financial data tools
    company_profile_tool = CompanyProfileTool()
    financial_ratios_tool = FinancialRatiosTool()
    
    # Test company profile tool
    print("Testing company profile tool:")
    try:
        result = company_profile_tool(symbol="AAPL")
        print(f"  Company: {result.get('profile', {}).get('companyName', 'N/A')}")
        print(f"  Industry: {result.get('profile', {}).get('industry', 'N/A')}")
        print(f"  Market Cap: {result.get('profile', {}).get('mktCap', 'N/A')}")
    except Exception as e:
        print(f"  Error: {str(e)}")
    
    # Test financial ratios tool
    print("\nTesting financial ratios tool:")
    try:
        result = financial_ratios_tool(symbol="AAPL", period="annual", limit=1)
        if isinstance(result, dict) and "ratios" in result and result["ratios"]:
            ratios = result["ratios"][0]
            print(f"  PE Ratio: {ratios.get('peRatio', 'N/A')}")
            print(f"  ROE: {ratios.get('returnOnEquity', 'N/A')}")
            print(f"  Debt to Equity: {ratios.get('debtToEquity', 'N/A')}")
        else:
            print("  No financial ratios data available.")
    except Exception as e:
        print(f"  Error: {str(e)}")

def test_web_scraping_tools():
    """Test the web scraping tools."""
    print("\n=== Testing Web Scraping Tools ===")
    
    try:
        from tools.web_scraping_tool import WebScrapingTool
        
        # Create a web scraping tool
        scraper = WebScrapingTool()
        
        # Test the tool with a simple website
        url = "https://en.wikipedia.org/wiki/NVIDIA"
        print(f"Scraping {url}...")
        try:
            content = scraper(url=url, max_length=1000)
            print(f"Content preview (first 200 chars):\n{content[:200]}...")
        except Exception as e:
            print(f"Error: {str(e)}")
    except ImportError:
        print("Web scraping tools not available.")

def test_web_search_tools():
    """Test the web search tools."""
    print("\n=== Testing Web Search Tools ===")
    
    try:
        # Test DuckDuckGo search
        from tools.web_search_tool import DuckDuckGoSearchTool
        
        duckduckgo_search = DuckDuckGoSearchTool()
        query = "NVIDIA stock performance"
        print(f"Searching DuckDuckGo for '{query}'...")
        try:
            results = duckduckgo_search(query=query)
            print(f"Results preview (first 200 chars):\n{results[:200]}...")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        # Test Google search with ScrapingDog
        from tools.web_search_tool import GoogleSearchTool
        
        if os.getenv("SCRAPING_DOG_API_KEY"):
            google_search = GoogleSearchTool()
            print(f"\nSearching Google (via ScrapingDog) for '{query}'...")
            try:
                results = google_search(query=query)
                print(f"Results preview (first 200 chars):\n{results[:200]}...")
            except Exception as e:
                print(f"Error: {str(e)}")
        else:
            print("\nSCRAPING_DOG_API_KEY not set. Skipping Google search test.")
        
        # Test News search
        from tools.web_search_tool import NewsSearchTool
        
        if os.getenv("NEWS_API_KEY"):
            news_search = NewsSearchTool()
            print(f"\nSearching news for '{query}'...")
            try:
                results = news_search(query=query, days=30)
                print(f"Results preview (first 200 chars):\n{results[:200]}...")
            except Exception as e:
                print(f"Error: {str(e)}")
        else:
            print("\nNEWS_API_KEY not set. Skipping news search test.")
            
    except ImportError:
        print("Web search tools not available.")

def main():
    """Run all tests."""
    # Load environment variables
    dotenv.load_dotenv()
    
    # Run tests
    test_tool_creation()
    test_tool_from_function()
    test_tool_manager()
    test_financial_data_tools()
    test_web_scraping_tools()
    test_web_search_tools()

if __name__ == "__main__":
    main() 