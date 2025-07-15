import requests
from bs4 import BeautifulSoup, Tag
from typing import List, Union, Dict
from .scraper import NewsScraper

class BBCNewsScraper(NewsScraper):
    
    def __init__(self, base_url="https://www.bbc.com"):
        self.base_url = base_url
    
    def ScrapeHome(self) -> Union[List[Dict[str, str]], str]:
        """
        Scrapes the home page of BBC and returns the headlines with their links.
        Returns a list of dictionaries with 'title' and 'link' keys.
        """
        response = requests.get(self.base_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            headlines = []
            
            # Find all anchor tags with data-testid="internal-link"
            internal_links = soup.find_all('a', attrs={'data-testid': 'internal-link'})
            
            for link in internal_links:
                # Ensure link is a Tag object
                if isinstance(link, Tag):
                    # Look for h2 with data-testid="card-headline" within this link
                    headline_element = link.find('h2', attrs={'data-testid': 'card-headline'})
                    
                    if headline_element and isinstance(headline_element, Tag):
                        title = headline_element.get_text(strip=True)
                        href_attr = link.get('href')
                        
                        # Make sure we have both title and link
                        if title and href_attr:
                            href = str(href_attr)  # Convert to string
                            
                            # Convert relative URLs to absolute URLs
                            if href.startswith('/'):
                                href = self.base_url + href
                            elif not href.startswith('http'):
                                href = self.base_url + '/' + href
                            
                            headlines.append({
                                'title': title,
                                'link': href
                            })
            
            return headlines
        else:
            return f"Error: Unable to fetch the home page. Status code {response.status_code}"
    
    def ScrapeFullText(self, url: str) -> str:
        """
        Scrapes a full article's text from the given URL.
        Looks for div elements with data-component="text-block" and extracts all p tags within them.
        """
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all div elements with data-component="text-block"
            text_blocks = soup.find_all('div', attrs={'data-component': 'text-block'})
            
            if text_blocks:
                full_text_parts = []
                
                for block in text_blocks:
                    if isinstance(block, Tag):
                        # Find all p tags within this text block
                        paragraphs = block.find_all('p')
                        
                        for para in paragraphs:
                            if isinstance(para, Tag):
                                text = para.get_text(strip=True)
                                if text:  # Only add non-empty paragraphs
                                    full_text_parts.append(text)
                
                if full_text_parts:
                    return "\n\n".join(full_text_parts)
                else:
                    return "Error: No text content found in the article"
            else:
                return "Error: No text blocks found in the article"
        else:
            return f"Error: Unable to fetch the article. Status code {response.status_code}"
    
    def ScrapeSpecial(self, url: str) -> Union[List[str], str]:
        """
        Scrapes special content from a specific BBC URL.
        """
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            special_content = soup.find_all('p')  # Example for scraping paragraphs
            return [para.get_text(strip=True) for para in special_content if para.get_text(strip=True)]
        else:
            return f"Error: Unable to fetch the special content. Status code {response.status_code}"
