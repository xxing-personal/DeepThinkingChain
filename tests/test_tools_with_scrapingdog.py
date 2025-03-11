"""
Test script for our tools with ScrapingDog API integration.

This script tests the GoogleSearchTool and AdvancedWebScrapingTool from our tools package.
"""

import os
import sys
from tools.web_search_tool import GoogleSearchTool
from tools.web_scraping_tool import AdvancedWebScrapingTool

def test_google_search_tool():
    """Test GoogleSearchTool."""
    print("\n=== Testing GoogleSearchTool ===")
    
    # Create a Google search tool
    google_search = GoogleSearchTool()
    
    # Test the tool with a simple query
    query = "NVIDIA stock performance 2023"
    print(f"Searching Google for '{query}'...")
    
    try:
        results = google_search(query=query)
        if "Error" in results:
            print(f"Error in results: {results}")
            return False
        
        # Print a preview of the results
        print(f"\nResults preview (first 500 characters):")
        print(results[:500] + "...")
        
        print("\nGoogleSearchTool test completed successfully!")
        return True
    except Exception as e:
        print(f"Error using GoogleSearchTool: {str(e)}")
        return False

def test_advanced_web_scraping_tool():
    """Test AdvancedWebScrapingTool."""
    print("\n=== Testing AdvancedWebScrapingTool ===")
    
    # Create an advanced web scraping tool
    scraper = AdvancedWebScrapingTool()
    
    # Test the tool with a dynamic website
    url = "https://finance.yahoo.com/quote/NVDA"
    print(f"Scraping dynamic content from {url}...")
    
    try:
        content = scraper(url=url, dynamic=True, max_length=2000)
        if "Error" in content:
            print(f"Error in content: {content}")
            return False
        
        # Print a preview of the content
        print(f"\nContent preview (first 500 characters):")
        print(content[:500] + "...")
        
        print("\nAdvancedWebScrapingTool test completed successfully!")
        return True
    except Exception as e:
        print(f"Error using AdvancedWebScrapingTool: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("Testing Tools with ScrapingDog API Integration")
    print("============================================")
    
    # Check if API key is set in environment
    api_key = os.environ.get("SCRAPING_DOG_API_KEY") or os.environ.get("SCRAPINGDOG_API_KEY")
    if not api_key:
        print("Error: Neither SCRAPING_DOG_API_KEY nor SCRAPINGDOG_API_KEY environment variable is set.")
        print("Please set one of these environment variables.")
        sys.exit(1)
    
    print(f"Found ScrapingDog API key in environment variables (length: {len(api_key)} characters)")
    
    # Run tests
    search_success = test_google_search_tool()
    scraping_success = test_advanced_web_scraping_tool()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"GoogleSearchTool: {'✅ Passed' if search_success else '❌ Failed'}")
    print(f"AdvancedWebScrapingTool: {'✅ Passed' if scraping_success else '❌ Failed'}")
    
    if search_success and scraping_success:
        print("\nAll tests passed! Our tools are working correctly with ScrapingDog API.")
    else:
        print("\nSome tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 