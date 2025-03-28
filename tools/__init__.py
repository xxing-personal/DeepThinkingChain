"""
Tools package for DeepThinkingChain.

This package contains various tools used by the DeepThinkingChain agents.

This package contains the Tool base class and ToolManager for managing tools in the DeepThinkingChain project.

Note: For web scraping and Google search functionality, a ScrapingDog API key is recommended.
Set the SCRAPING_DOG_API_KEY environment variable to enable these features.
"""

import os
import sys

# Add parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .tool import Tool
from .tool_manager import ToolManager

# Import financial data tools
try:
    from .financial_data_tool import (
        FinancialDataTool,
        CompanyProfileTool,
        FinancialRatiosTool,
        IncomeStatementTool
    )
except ImportError:
    pass

# Import web scraping tools
try:
    from .web_scraping_tool import (
        WebScrapingTool,
        AdvancedWebScrapingTool
    )
except ImportError:
    pass

# Import web search tools
try:
    from .web_search_tool import (
        WebSearchTool,
        GoogleSearchTool,
        DuckDuckGoSearchTool,
        NewsSearchTool
    )
except ImportError:
    pass

# Import code execution tools
try:
    from .code_execution_tool import CodeExecutionTool
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