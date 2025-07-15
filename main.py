from StrategyScraper.bbcNewsScraper import BBCNewsScraper
from typing import Dict, Any, List, Union


# def main():
#     """Main function to test BBC News scraping functionality."""
    
#     # Initialize the BBC scraper
#     bbc_scraper = BBCNewsScraper()
    
#     print("CRIMENET - Global Crime Intelligence Engine")
#     print("=" * 50)
#     print("Testing BBC News Scraper...")
#     print()
    
#     # Scrape the home page
#     data = bbc_scraper.ScrapeHome()
    
#     # Handle the response based on its type
#     if isinstance(data, str):
#         # Error occurred
#         print(f"Error occurred: {data}")
#     elif isinstance(data, list):
#         # Success - we have a list of headlines
#         print(f"Successfully scraped {len(data)} headlines from BBC:")
#         print("-" * 50)
        
#         for i, item in enumerate(data, 1):
#             print(f"{i}. Title: {item['title']}")
#             print(f"   Link: {item['link']}")
#             print()
            
#         # Show summary
#         print("-" * 50)
#         print(f"Total headlines found: {len(data)}")
#     else:
#         print("Unexpected response type received.")


def main():
    bbc_scraper = BBCNewsScraper()
    print("CRIMENET - Global Crime Intelligence Engine")
    print("Testing BBC News Scraper... full text scraping")
    
    print("=" * 50)
    
    url = "https://www.bbc.com/news/articles/cx2jjnky5leo"
    full_text = bbc_scraper.ScrapeFullText(url)
    print("Full text scraping result:")
    print(full_text)

if __name__ == "__main__":
    main()