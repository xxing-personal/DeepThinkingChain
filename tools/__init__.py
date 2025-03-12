"""
Tools package for DeepThinkingChain.

This package contains various tools used by the DeepThinkingChain agents.

This package contains the Tool base class and ToolManager for managing tools in the DeepThinkingChain project.

Note: For web scraping and Google search functionality, a ScrapingDog API key is recommended.
Set the SCRAPING_DOG_API_KEY environment variable to enable these features.
"""

from tools.tool import Tool
from tools.tool_manager import ToolManager

# Import financial data tools
try:
    from tools.financial_data_tool import (
        FinancialDataTool,
        CompanyProfileTool,
        FinancialRatiosTool,
        IncomeStatementTool
    )
except ImportError:
    pass

# Import web scraping tools
try:
    from tools.web_scraping_tool import (
        WebScrapingTool,
        AdvancedWebScrapingTool
    )
except ImportError:
    pass

# Import web search tools
try:
    from tools.web_search_tool import (
        WebSearchTool,
        GoogleSearchTool,
        DuckDuckGoSearchTool,
        NewsSearchTool
    )
except ImportError:
    pass

# Import code execution tools
try:
    from tools.code_execution_tool import CodeExecutionTool
except ImportError:
    pass

__all__ = [
    'Tool',
    'ToolManager',
    'FinancialDataTool',
    'CompanyProfileTool',
    'FinancialRatiosTool',
    'IncomeStatementTool',
    'WebScrapingTool',
    'AdvancedWebScrapingTool',
    'WebSearchTool',
    'GoogleSearchTool',
    'DuckDuckGoSearchTool',
    'NewsSearchTool',
    'CodeExecutionTool'
] 