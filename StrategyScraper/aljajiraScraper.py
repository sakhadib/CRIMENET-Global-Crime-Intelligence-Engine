import requests
from bs4 import BeautifulSoup, Tag
from typing import List, Union, Dict
from .scraper import NewsScraper

class AlJazeeraScraper(NewsScraper):
    def __init__(self, base_url="https://www.aljazeera.com"):
        self.base_url = base_url
        
    def ScrapeHome(self) -> Union[List[Dict[str, str]], str]:
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            articles = []
            
            # Try multiple selectors as Al Jazeera might use different structures
            selectors = [
                'a.u-clickable-card__link',
                'a[href*="/news/"]',
                'h3 a, h2 a, h1 a',
                'article a'
            ]
            
            links = []
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    break
            
            if not links:
                return "No articles found with any of the selectors"

            for link in links:
                if isinstance(link, Tag):
                    # Try multiple ways to extract title
                    title = self._extract_title(link)
                    
                    # Skip if no valid title found
                    if not title or title == "No title found" or len(title.strip()) < 5:
                        continue

                    href_attr = link.get('href')

                    if title and href_attr:
                        href = str(href_attr).strip()
                        
                        # Convert relative URLs to absolute URLs
                        if href.startswith('/'):
                            href = self.base_url + href
                        elif not href.startswith('http'):
                            href = self.base_url + '/' + href

                        # Avoid duplicates
                        if not any(article['link'] == href for article in articles):
                            articles.append({
                                'title': title.strip(),
                                'link': href
                            })
            
            return articles if articles else "No valid articles found"
            
        except requests.RequestException as e:
            return f"Request error: {str(e)}"
        except Exception as e:
            return f"Parsing error: {str(e)}"
    
    def _extract_title(self, link_element: Tag) -> str:
        """Helper method to extract title from various HTML structures"""
        
        # Method 1: Direct span inside link
        title_element = link_element.find('span')
        if title_element and isinstance(title_element, Tag):
            title = title_element.get_text(strip=True)
            if title and len(title) > 5:
                return title
        
        # Method 2: Heading tags with span inside
        heading_element = link_element.find(['h3', 'h2', 'h1'])
        if heading_element and isinstance(heading_element, Tag):
            title_element = heading_element.find('span')
            if title_element and isinstance(title_element, Tag):
                title = title_element.get_text(strip=True)
                if title and len(title) > 5:
                    return title
            
            # Direct text from heading
            title = heading_element.get_text(strip=True)
            if title and len(title) > 5:
                return title
        
        # Method 3: Direct text from link
        title = link_element.get_text(strip=True)
        if title and len(title) > 5:
            return title
        
        # Method 4: Try to find title attribute
        title_attr = link_element.get('title')
        if title_attr and isinstance(title_attr, str) and len(title_attr.strip()) > 5:
            return title_attr.strip()
        
        # Method 5: Look for specific Al Jazeera classes
        title_classes = [
            'gc__title', 
            'article-title', 
            'featured-article__title',
            'latest-news__title'
        ]
        
        for class_name in title_classes:
            title_element = link_element.find(class_=class_name)
            if title_element:
                title = title_element.get_text(strip=True)
                if title and len(title) > 5:
                    return title
        
        return "No title found"
    
    def ScrapeFullText(self, url: str) -> str:
        """
        Scrapes a full article's text from the given URL.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different selectors for Al Jazeera article content
            content_selectors = [
                'div.wysiwyg',
                'div.article-body',
                'div.post-content',
                'div[data-article-body]',
                '.gc__content p',
                'article p'
            ]
            
            for selector in content_selectors:
                content_elements = soup.select(selector)
                if content_elements:
                    if selector.endswith(' p'):
                        # Multiple paragraphs
                        paragraphs = [elem.get_text(strip=True) for elem in content_elements if elem.get_text(strip=True)]
                        if paragraphs:
                            return "\n\n".join(paragraphs)
                    else:
                        # Single content container
                        content = content_elements[0].get_text(strip=True)
                        if content and len(content) > 100:  # Ensure we have substantial content
                            return content
            
            return "Error: No article content found"
            
        except requests.RequestException as e:
            return f"Error: Unable to fetch the article. {str(e)}"
        except Exception as e:
            return f"Error: Failed to parse article content. {str(e)}"
    
    def ScrapeSpecial(self, url: str) -> Union[List[str], str]:
        """
        Scrapes special content from a specific Al Jazeera URL.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract special content like quotes, highlights, etc.
            special_content = []
            
            # Look for quotes
            quotes = soup.find_all(['blockquote', '.quote', '.highlight'])
            for quote in quotes:
                if isinstance(quote, Tag):
                    text = quote.get_text(strip=True)
                    if text and len(text) > 10:
                        special_content.append(text)
            
            # Look for highlighted text
            highlights = soup.find_all(['strong', 'em', '.highlight', '.emphasis'])
            for highlight in highlights:
                if isinstance(highlight, Tag):
                    text = highlight.get_text(strip=True)
                    if text and len(text) > 10 and text not in special_content:
                        special_content.append(text)
            
            return special_content if special_content else "No special content found"
            
        except requests.RequestException as e:
            return f"Error: Unable to fetch the page. {str(e)}"
        except Exception as e:
            return f"Error: Failed to parse special content. {str(e)}"
