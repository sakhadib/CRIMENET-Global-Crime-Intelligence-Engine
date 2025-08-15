import requests
from bs4 import BeautifulSoup, Tag
import xml.etree.ElementTree as ET
from typing import List, Union, Dict
from .scraper import NewsScraper

class EuroNewsScraper(NewsScraper):
    def __init__(self, base_url="https://www.euronews.com", rss_url="https://www.euronews.com/rss"):
        self.base_url = base_url
        self.rss_url = rss_url
        
    def ScrapeHome(self) -> Union[List[Dict[str, str]], str]:
        try:
            # First try RSS feed (more reliable)
            articles = self._scrape_from_rss()
            if articles and articles != "No articles found in RSS feed":
                return articles
            
            # Fallback to HTML scraping if RSS fails
            return self._scrape_from_html()
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _scrape_from_rss(self) -> Union[List[Dict[str, str]], str]:
        """Scrape articles from RSS feed"""
        try:
            response = requests.get(self.rss_url, timeout=10)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            articles = []
            
            # Find all item elements in the RSS feed
            for item in root.findall('.//item'):
                title_elem = item.find('title')
                link_elem = item.find('link')
                description_elem = item.find('description')
                pub_date_elem = item.find('pubDate')
                
                if title_elem is not None and link_elem is not None:
                    title = title_elem.text.strip() if title_elem.text else ""
                    link = link_elem.text.strip() if link_elem.text else ""
                    description = description_elem.text.strip() if description_elem is not None and description_elem.text else ""
                    pub_date = pub_date_elem.text.strip() if pub_date_elem is not None and pub_date_elem.text else ""
                    
                    if title and link and len(title) > 5:
                        article_data = {
                            'title': title,
                            'link': link
                        }
                        
                        # Add optional fields if available
                        if description:
                            article_data['description'] = description
                        if pub_date:
                            article_data['pub_date'] = pub_date
                            
                        articles.append(article_data)
            
            return articles if articles else "No articles found in RSS feed"
            
        except requests.RequestException as e:
            return f"RSS request error: {str(e)}"
        except ET.ParseError as e:
            return f"RSS parsing error: {str(e)}"
        except Exception as e:
            return f"RSS error: {str(e)}"
    
    def _scrape_from_html(self) -> Union[List[Dict[str, str]], str]:
        """Fallback HTML scraping method"""
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            articles = []
            
            # Based on the Euronews HTML structure from the screenshot
            selectors = [
                'a.c-article-item',
                'a[href*="/news/"]',
                'article a',
                '.o-block-listing__item a',
                '.c-article-item__link',
                'h3 a, h2 a, h1 a'
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
            return f"HTML request error: {str(e)}"
        except Exception as e:
            return f"HTML parsing error: {str(e)}"
    
    def _extract_title(self, link_element: Tag) -> str:
        """Helper method to extract title from various Euronews HTML structures"""
        
        # Method 1: Look for specific Euronews title classes
        title_classes = [
            'c-article-item__title',
            'o-block-listing__title',
            'article-title',
            'm-object__title',
            'c-story-title'
        ]
        
        for class_name in title_classes:
            title_element = link_element.find(class_=class_name)
            if title_element:
                title = title_element.get_text(strip=True)
                if title and len(title) > 5:
                    return title
        
        # Method 2: Look for span with title text
        span_element = link_element.find('span')
        if span_element and isinstance(span_element, Tag):
            title = span_element.get_text(strip=True)
            if title and len(title) > 5:
                return title
        
        # Method 3: Heading tags with text
        heading_element = link_element.find(['h3', 'h2', 'h1', 'h4'])
        if heading_element and isinstance(heading_element, Tag):
            # Check for span inside heading first
            span_in_heading = heading_element.find('span')
            if span_in_heading and isinstance(span_in_heading, Tag):
                title = span_in_heading.get_text(strip=True)
                if title and len(title) > 5:
                    return title
            
            # Direct text from heading
            title = heading_element.get_text(strip=True)
            if title and len(title) > 5:
                return title
        
        # Method 4: Direct text from link
        title = link_element.get_text(strip=True)
        if title and len(title) > 5:
            return title
        
        # Method 5: Try title attribute
        title_attr = link_element.get('title')
        if title_attr and isinstance(title_attr, str) and len(title_attr.strip()) > 5:
            return title_attr.strip()
        
        # Method 6: Look for paragraph with title text
        p_element = link_element.find('p')
        if p_element and isinstance(p_element, Tag):
            title = p_element.get_text(strip=True)
            if title and len(title) > 5:
                return title
        
        return "No title found"
    
    def ScrapeFullText(self, url: str) -> str:
        """
        Scrapes a full article's text from the given Euronews URL.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different selectors for Euronews article content
            content_selectors = [
                'div.c-article-content',
                'div.article-body',
                'div.c-article-text',
                '.o-article-text p',
                '.c-article-story p',
                'article .content p',
                '.post-content p',
                '[data-article-body] p',
                '.c-article-body p'
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
            
            # Fallback: try to get all paragraphs from main content area
            main_content = soup.find('main') or soup.find('article')
            if main_content:
                paragraphs = main_content.find_all('p')
                if paragraphs:
                    text_content = []
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 20:  # Filter out very short paragraphs
                            text_content.append(text)
                    if text_content:
                        return "\n\n".join(text_content)
            
            return "Error: No article content found"
            
        except requests.RequestException as e:
            return f"Error: Unable to fetch the article. {str(e)}"
        except Exception as e:
            return f"Error: Failed to parse article content. {str(e)}"
    
    def ScrapeSpecial(self, url: str) -> Union[List[str], str]:
        """
        Scrapes special content from a specific Euronews URL.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract special content like quotes, highlights, etc.
            special_content = []
            
            # Look for quotes and blockquotes
            quotes = soup.find_all(['blockquote', '.quote', '.c-quote', '.o-quote'])
            for quote in quotes:
                if isinstance(quote, Tag):
                    text = quote.get_text(strip=True)
                    if text and len(text) > 10:
                        special_content.append(f"Quote: {text}")
            
            # Look for highlighted text
            highlights = soup.find_all(['strong', 'em', '.highlight', '.emphasis', '.c-highlight'])
            for highlight in highlights:
                if isinstance(highlight, Tag):
                    text = highlight.get_text(strip=True)
                    if text and len(text) > 10 and text not in [s.replace("Quote: ", "") for s in special_content]:
                        special_content.append(f"Highlight: {text}")
            
            # Look for Euronews specific elements like key points or summaries
            key_elements = soup.find_all(['.c-key-points', '.c-summary', '.o-summary'])
            for element in key_elements:
                if isinstance(element, Tag):
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:
                        special_content.append(f"Key Point: {text}")
            
            # Look for live blog updates if it's a live article
            live_updates = soup.find_all(['.c-live-update', '.live-update', '.o-live-post'])
            for update in live_updates:
                if isinstance(update, Tag):
                    text = update.get_text(strip=True)
                    if text and len(text) > 10:
                        special_content.append(f"Live Update: {text}")
            
            return special_content if special_content else "No special content found"
            
        except requests.RequestException as e:
            return f"Error: Unable to fetch the page. {str(e)}"
        except Exception as e:
            return f"Error: Failed to parse special content. {str(e)}"
    
    def ScrapeRSSOnly(self) -> Union[List[Dict[str, str]], str]:
        """
        Method to exclusively use RSS feed (more reliable)
        """
        return self._scrape_from_rss()