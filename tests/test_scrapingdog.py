"""
Test script for ScrapingDog API integration.

This script tests both the Google search and web scraping functionality using ScrapingDog API.

Usage:
    python test_scrapingdog.py [API_KEY]
"""

import os
import sys
import requests
import json
from urllib.parse import quote_plus

def test_google_search(api_key):
    """Test Google search using ScrapingDog API directly."""
    print("\n=== Testing Google Search via ScrapingDog ===")
    
    # Test query
    query = "NVIDIA stock performance 2023"
    print(f"Searching Google for '{query}'...")
    
    # Construct the API URL for ScrapingDog's Google search
    url = "https://api.scrapingdog.com/google/"
    params = {
        "api_key": api_key,
        "query": query,
        "results": 5,  # Limit to 5 results
        "country": "us",
        "page": 0
    }
    
    try:
        # Make the request
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Check if there are search results
        if "organic_results" not in data or len(data["organic_results"]) == 0:
            print("No results found.")
            return False
        
        # Print the results
        print(f"\nFound {len(data['organic_results'])} results:")
        for i, item in enumerate(data["organic_results"][:3], 1):  # Show first 3 results
            title = item.get("title", "No title")
            link = item.get("link", "No link")
            print(f"{i}. {title}")
            print(f"   URL: {link}")
            print()
        
        print("Google search test completed successfully!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error performing Google search: {str(e)}")
        return False
    except Exception as e:
        print(f"Error processing Google search results: {str(e)}")
        return False

def test_web_scraping(api_key):
    """Test web scraping using ScrapingDog API directly."""
    print("\n=== Testing Web Scraping via ScrapingDog ===")
    
    # Test URL
    url = "https://finance.yahoo.com/quote/NVDA"
    print(f"Scraping content from {url}...")
    
    # Construct the API URL for ScrapingDog's scraping service
    api_url = "https://api.scrapingdog.com/scrape"
    params = {
        "api_key": api_key,
        "url": url,
        "dynamic": "true"  # Enable JavaScript rendering
    }
    
    try:
        # Make the request
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        
        # Check if the response is valid HTML
        content = response.text
        if len(content) < 100:
            print(f"Error: Response too short ({len(content)} characters)")
            return False
        
        # Print a preview of the content
        print(f"\nContent preview (first 300 characters):")
        print(content[:300].replace('\n', ' ').replace('\r', '') + "...")
        
        # Check if we got some expected content
        if "NVIDIA" in content or "NVDA" in content:
            print("\nFound expected content in the response!")
        else:
            print("\nWarning: Expected content not found in the response.")
        
        print("Web scraping test completed successfully!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error scraping webpage: {str(e)}")
        return False
    except Exception as e:
        print(f"Error processing scraped content: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("ScrapingDog API Integration Tests")
    print("================================")
    
    # Get API key from environment or command line
    api_key = os.environ.get("SCRAPING_DOG_API_KEY") or os.environ.get("SCRAPINGDOG_API_KEY")
    
    # Check if API key is provided as command-line argument
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        print("Using API key from command-line argument")
    
    if not api_key:
        print("Error: Neither SCRAPING_DOG_API_KEY nor SCRAPINGDOG_API_KEY environment variable is set, and no API key provided as argument.")
        print("Please set one of these environment variables or provide the API key as an argument:")
        print(f"  python {sys.argv[0]} YOUR_API_KEY")
        sys.exit(1)
    
    print(f"Using ScrapingDog API key (length: {len(api_key)} characters)")
    
    # Run tests
    search_success = test_google_search(api_key)
    scraping_success = test_web_scraping(api_key)
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Google Search: {'✅ Passed' if search_success else '❌ Failed'}")
    print(f"Web Scraping: {'✅ Passed' if scraping_success else '❌ Failed'}")
    
    if search_success and scraping_success:
        print("\nAll tests passed! ScrapingDog API integration is working correctly.")
    else:
        print("\nSome tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 