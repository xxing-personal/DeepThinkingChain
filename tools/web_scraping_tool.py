"""
Web Scraping Tools for DeepThinkingChain.

This module contains tools for scraping web content.
"""

import os
import requests
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlparse
import logging

from tools.tool import Tool

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def truncate_content(content: str, max_length: int = 10000) -> str:
    """
    Truncate content to a maximum length.
    
    Args:
        content: The content to truncate
        max_length: Maximum length of the content
        
    Returns:
        str: Truncated content
    """
    if len(content) > max_length:
        return content[:max_length] + f"\n\n[Content truncated to {max_length} characters. Original length: {len(content)} characters]"
    return content


class WebScrapingTool(Tool):
    """Tool for scraping web content."""
    
    name = "web_scraper"
    description = "Visits a webpage at the given URL and reads its content as a markdown string. You can use this to browse webpages."
    inputs = {
        "url": {
            "type": "str",
            "description": "The URL of the webpage to visit",
            "required": True
        },
        "max_length": {
            "type": "int",
            "description": "Maximum length of the content to return",
            "required": False
        }
    }
    output_type = "str"
    capabilities = "Retrieves and converts web content to markdown format."
    category = "web_scraping"
    
    def __init__(self):
        """Initialize the web scraping tool."""
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        self.converter.ignore_images = False
        self.converter.ignore_tables = False
        self.converter.body_width = 0  # No wrapping
        super().__init__()
    
    def forward(self, url: str, max_length: int = 10000) -> str:
        """
        Scrape content from a webpage.
        
        Args:
            url: The URL of the webpage to scrape
            max_length: Maximum length of the content to return
            
        Returns:
            str: The scraped content as markdown
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return f"Error: Invalid URL format: {url}"
            
            # Add user agent to avoid being blocked
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # Fetch the webpage
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Convert to markdown
            markdown = self.converter.handle(str(soup))
            
            # Truncate if necessary
            return truncate_content(markdown, max_length)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return f"Error fetching URL: {str(e)}"
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return f"Error processing URL: {str(e)}"


class AdvancedWebScrapingTool(Tool):
    """Tool for scraping JavaScript-rendered web content."""
    
    name = "advanced_web_scraper"
    description = "Visits a webpage at the given URL and reads its content as a markdown string, with support for JavaScript-rendered content."
    inputs = {
        "url": {
            "type": "str",
            "description": "The URL of the webpage to visit",
            "required": True
        },
        "dynamic": {
            "type": "bool",
            "description": "Whether to render JavaScript (set to true for dynamic websites)",
            "required": False
        },
        "max_length": {
            "type": "int",
            "description": "Maximum length of the content to return",
            "required": False
        }
    }
    output_type = "str"
    capabilities = "Retrieves and converts web content to markdown format, with support for JavaScript-rendered content."
    category = "web_scraping"
    
    def __init__(self):
        """Initialize the advanced web scraping tool."""
        # Check both environment variable names
        self.api_key = os.environ.get("SCRAPING_DOG_API_KEY") or os.environ.get("SCRAPINGDOG_API_KEY") or os.getenv("SCRAPING_DOG_API_KEY") or os.getenv("SCRAPINGDOG_API_KEY")
        if not self.api_key:
            logger.warning("Neither SCRAPING_DOG_API_KEY nor SCRAPINGDOG_API_KEY environment variable is set. Advanced web scraping will be limited.")
        
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        self.converter.ignore_images = False
        self.converter.ignore_tables = False
        self.converter.body_width = 0  # No wrapping
        super().__init__()
    
    def forward(self, url: str, dynamic: bool = False, max_length: int = 10000) -> str:
        """
        Scrape content from a webpage, with support for JavaScript-rendered content.
        
        Args:
            url: The URL of the webpage to scrape
            dynamic: Whether to render JavaScript
            max_length: Maximum length of the content to return
            
        Returns:
            str: The scraped content as markdown
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return f"Error: Invalid URL format: {url}"
            
            if dynamic and self.api_key:
                # Use ScrapingDog API for JavaScript-rendered content
                api_url = "https://api.scrapingdog.com/scrape"
                params = {
                    "api_key": self.api_key,
                    "url": url,
                    "dynamic": "true" if dynamic else "false"
                }
                
                response = requests.get(api_url, params=params, timeout=30)
                response.raise_for_status()
                
                if response.status_code == 200:
                    html_content = response.text
                else:
                    return f"Error: ScrapingDog API returned status code {response.status_code}"
            else:
                # Fall back to regular requests if dynamic is False or API key is not set
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                html_content = response.text
            
            # Parse the HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Convert to markdown
            markdown = self.converter.handle(str(soup))
            
            # Truncate if necessary
            return truncate_content(markdown, max_length)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return f"Error fetching URL: {str(e)}"
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return f"Error processing URL: {str(e)}"


def main():
    """Example usage of the web scraping tools."""
    # Create a web scraping tool
    scraper = WebScrapingTool()
    
    # Test the tool with a simple website
    url = "https://en.wikipedia.org/wiki/NVIDIA"
    print(f"Scraping {url}...")
    content = scraper(url=url, max_length=2000)
    print(f"Content preview (first 500 chars):\n{content[:500]}...")
    
    # Create an advanced web scraping tool
    advanced_scraper = AdvancedWebScrapingTool()
    
    # Check if API key is set
    if os.getenv("SCRAPING_DOG_API_KEY"):
        # Test the tool with a dynamic website
        url = "https://finance.yahoo.com/quote/NVDA"
        print(f"\nScraping dynamic content from {url}...")
        content = advanced_scraper(url=url, dynamic=True, max_length=2000)
        print(f"Content preview (first 500 chars):\n{content[:500]}...")
    else:
        print("\nSCRAPING_DOG_API_KEY not set. Skipping advanced scraping test.")


if __name__ == "__main__":
    main() 