import requests
from bs4 import BeautifulSoup, Tag
from typing import List, Union, Dict
from .scraper import NewsScraper

class VOAScraper(NewsScraper):
    def __init__(self, base_url="https://www.voanews.com"):
        self.base_url = base_url
        
    def ScrapeHome(self) -> Union[List[Dict[str, str]], str]:
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            articles = []
            
            # VOA-specific selectors based on the HTML structure shown
            selectors = [
                'div.media-block a',  # Main article links
                'div.media-block-wrap a',
                'h2 a, h3 a, h4 a',  # Heading links
                'div.col-xs-12 a',  # Column content links
                'div.container a[href*="/a/"]',  # VOA article URLs typically contain /a/
                'a[href*="/a/"]',  # Generic VOA article pattern
                'article a'
            ]
            
            links = []
            for selector in selectors:
                found_links = soup.select(selector)
                if found_links:
                    links.extend(found_links)
                    
            # Remove duplicates while preserving order
            seen_hrefs = set()
            unique_links = []
            for link in links:
                href = link.get('href')
                if href and href not in seen_hrefs:
                    seen_hrefs.add(href)
                    unique_links.append(link)
            
            if not unique_links:
                return "No articles found with any of the selectors"

            for link in unique_links:
                if isinstance(link, Tag):
                    # Extract title using VOA-specific methods
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

                        # Filter for actual news articles (VOA uses /a/ pattern)
                        if '/a/' in href or 'voanews.com' in href:
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
        """Helper method to extract title from VOA HTML structures"""
        
        # Method 1: Check if link itself contains the title text
        direct_text = link_element.get_text(strip=True)
        if direct_text and len(direct_text) > 5 and not direct_text.lower().startswith(('read more', 'more', 'continue')):
            return direct_text
        
        # Method 2: Look for title in parent or sibling elements
        parent = link_element.parent
        if parent:
            # Check for title in parent heading tags
            for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                heading = parent.find(heading_tag)
                if heading:
                    title_text = heading.get_text(strip=True)
                    if title_text and len(title_text) > 5:
                        return title_text
        
        # Method 3: Look for VOA-specific title classes
        title_classes = [
            'section-head',
            'media-block-wrap',
            'category-mb',
            'wg-hlight',
            'story-title'
        ]
        
        for class_name in title_classes:
            # Check in the link itself
            title_element = link_element.find(class_=class_name)
            if title_element:
                title = title_element.get_text(strip=True)
                if title and len(title) > 5:
                    return title
            
            # Check in parent element
            if link_element.parent:
                title_element = link_element.parent.find(class_=class_name)
                if title_element:
                    title = title_element.get_text(strip=True)
                    if title and len(title) > 5:
                        return title
        
        # Method 4: Check title attribute
        title_attr = link_element.get('title')
        if title_attr and isinstance(title_attr, str) and len(title_attr.strip()) > 5:
            return title_attr.strip()
        
        # Method 5: Look in nearby text content
        if link_element.parent:
            parent_text = link_element.parent.get_text(strip=True)
            # Remove the link text to get surrounding context
            if direct_text:
                parent_text = parent_text.replace(direct_text, '').strip()
            if parent_text and len(parent_text) > 5:
                # Take first meaningful sentence
                sentences = parent_text.split('.')
                if sentences and len(sentences[0].strip()) > 5:
                    return sentences[0].strip()
        
        return "No title found"
    
    def ScrapeFullText(self, url: str) -> str:
        """
        Scrapes a full article's text from the given VOA URL.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # VOA-specific content selectors
            content_selectors = [
                'div.wsw',  # Main content wrapper
                'div.article-content',
                'div.content',
                'div.story-content',
                'div.entry-content',
                'div.post-content',
                'article div.content',
                'main p',  # Paragraphs in main content
                '.wsw p'   # Paragraphs in wsw container
            ]
            
            for selector in content_selectors:
                content_elements = soup.select(selector)
                if content_elements:
                    if selector.endswith(' p'):
                        # Multiple paragraphs
                        paragraphs = []
                        for elem in content_elements:
                            text = elem.get_text(strip=True)
                            if text and len(text) > 20:  # Filter out very short paragraphs
                                paragraphs.append(text)
                        if paragraphs:
                            return "\n\n".join(paragraphs)
                    else:
                        # Single content container
                        for content_elem in content_elements:
                            # Extract all paragraph text from within the container
                            paragraphs = content_elem.find_all('p')
                            if paragraphs:
                                paragraph_texts = []
                                for p in paragraphs:
                                    text = p.get_text(strip=True)
                                    if text and len(text) > 20:
                                        paragraph_texts.append(text)
                                if paragraph_texts:
                                    return "\n\n".join(paragraph_texts)
                            
                            # Fallback to all text in container
                            content = content_elem.get_text(strip=True)
                            if content and len(content) > 100:
                                return content
            
            return "Error: No article content found"
            
        except requests.RequestException as e:
            return f"Error: Unable to fetch the article. {str(e)}"
        except Exception as e:
            return f"Error: Failed to parse article content. {str(e)}"
    
    def ScrapeSpecial(self, url: str) -> Union[List[str], str]:
        """
        Scrapes special content from a specific VOA URL (quotes, highlights, etc.).
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            special_content = []
            
            # Look for quotes and highlighted content
            quote_selectors = [
                'blockquote',
                '.quote',
                '.highlight',
                '.pullquote',
                'em',
                'strong'
            ]
            
            for selector in quote_selectors:
                elements = soup.select(selector)
                for element in elements:
                    if isinstance(element, Tag):
                        text = element.get_text(strip=True)
                        if text and len(text) > 10 and text not in special_content:
                            # Avoid adding very common words or short phrases
                            if not any(common in text.lower() for common in ['read more', 'click here', 'share', 'tweet']):
                                special_content.append(text)
            
            # Look for VOA-specific highlighted content
            voa_highlight_selectors = [
                '.wg-hlight',
                '.category-mb',
                '.section-head'
            ]
            
            for selector in voa_highlight_selectors:
                elements = soup.select(selector)
                for element in elements:
                    if isinstance(element, Tag):
                        text = element.get_text(strip=True)
                        if text and len(text) > 10 and text not in special_content:
                            special_content.append(text)
            
            # Remove duplicates while preserving order
            unique_content = []
            for item in special_content:
                if item not in unique_content:
                    unique_content.append(item)
            
            return unique_content if unique_content else "No special content found"
            
        except requests.RequestException as e:
            return f"Error: Unable to fetch the page. {str(e)}"
        except Exception as e:
            return f"Error: Failed to parse special content. {str(e)}"

    def ScrapeByCategory(self, category: str) -> Union[List[Dict[str, str]], str]:
        """
        Scrapes articles from a specific VOA category.
        Common VOA categories: world, usa, africa, asia, europe, middle-east, americas
        """
        try:
            category_url = f"{self.base_url}/{category.lower()}"
            response = requests.get(category_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            articles = []
            
            # Use the same selectors as ScrapeHome but on category page
            selectors = [
                'div.media-block a',
                'div.media-block-wrap a',
                'h2 a, h3 a, h4 a',
                'a[href*="/a/"]'
            ]
            
            links = []
            for selector in selectors:
                found_links = soup.select(selector)
                if found_links:
                    links.extend(found_links)
            
            # Process links same as in ScrapeHome
            seen_hrefs = set()
            for link in links:
                if isinstance(link, Tag):
                    href = link.get('href')
                    if href and href not in seen_hrefs:
                        seen_hrefs.add(href)
                        
                        title = self._extract_title(link)
                        if title and title != "No title found" and len(title.strip()) > 5:
                            href = str(href).strip()
                            
                            if href.startswith('/'):
                                href = self.base_url + href
                            elif not href.startswith('http'):
                                href = self.base_url + '/' + href
                            
                            if '/a/' in href or 'voanews.com' in href:
                                articles.append({
                                    'title': title.strip(),
                                    'link': href,
                                    'category': category
                                })
            
            return articles if articles else f"No articles found in {category} category"
            
        except requests.RequestException as e:
            return f"Request error for category {category}: {str(e)}"
        except Exception as e:
            return f"Parsing error for category {category}: {str(e)}"