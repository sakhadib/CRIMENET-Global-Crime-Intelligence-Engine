import requests
from bs4 import BeautifulSoup, Tag
from typing import List, Union, Dict
from .scraper import NewsScraper

class DWScraper(NewsScraper):
    def __init__(self, base_url="https://www.dw.com"):
        self.base_url = base_url
        
    def ScrapeHome(self) -> Union[List[Dict[str, str]], str]:
        try:
            response = requests.get(f"{self.base_url}/en", timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            articles = []
            
            # DW-specific selectors based on the HTML structure shown
            selectors = [
                'a[href*="/en/"]',  # DW English articles
                'article a',
                'h1 a, h2 a, h3 a, h4 a',  # Headlines with links
                '.teaser a',  # Teaser links
                '.story a',   # Story links
                'div[class*="teaser"] a',  # Teaser containers
                'div[class*="story"] a',   # Story containers
                '.news-item a',
                '.article-link a'
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
                    # Extract title using DW-specific methods
                    title = self._extract_title(link)
                    
                    # Skip if no valid title found
                    if not title or title == "No title found" or len(title.strip()) < 10:
                        continue

                    href_attr = link.get('href')

                    if title and href_attr:
                        href = str(href_attr).strip()
                        
                        # Convert relative URLs to absolute URLs
                        if href.startswith('/'):
                            href = self.base_url + href
                        elif not href.startswith('http'):
                            href = self.base_url + '/' + href

                        # Filter for actual DW news articles
                        if self._is_valid_dw_article(href):
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
    
    def _is_valid_dw_article(self, href: str) -> bool:
        """Check if the URL is a valid DW article"""
        if not href or 'dw.com' not in href:
            return False
            
        # Exclude non-article pages
        excluded_patterns = [
            '/service/',
            '/aboutdw/',
            '/contact/',
            '/privacy/',
            '/imprint/',
            '/newsletter/',
            '/search/',
            'javascript:',
            'mailto:',
            '#',
            '.jpg',
            '.png',
            '.gif',
            '.pdf'
        ]
        
        for pattern in excluded_patterns:
            if pattern in href.lower():
                return False
                
        # Include typical article patterns
        article_patterns = [
            '/en/',
            '/a-'
        ]
        
        return any(pattern in href for pattern in article_patterns)
    
    def _extract_title(self, link_element: Tag) -> str:
        """Helper method to extract title from DW HTML structures"""
        
        # Method 1: Direct text content of the link
        direct_text = link_element.get_text(strip=True)
        if direct_text and len(direct_text) > 10:
            # Filter out common navigation text
            excluded_texts = ['more', 'read more', 'continue reading', 'watch video', 'listen', 'share']
            if not any(excluded.lower() in direct_text.lower() for excluded in excluded_texts):
                return direct_text
        
        # Method 2: Title attribute
        title_attr = link_element.get('title')
        if title_attr and isinstance(title_attr, str) and len(title_attr.strip()) > 10:
            return title_attr.strip()
        
        # Method 3: Look in parent elements for title
        parent = link_element.parent
        if parent:
            # Check parent for heading tags
            for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if parent.name == heading_tag:
                    title_text = parent.get_text(strip=True)
                    if title_text and len(title_text) > 10:
                        return title_text
                        
                # Check for heading tags within parent
                heading = parent.find(heading_tag)
                if heading:
                    title_text = heading.get_text(strip=True)
                    if title_text and len(title_text) > 10:
                        return title_text
        
        # Method 4: Look for DW-specific classes
        title_classes = [
            'teaser-title',
            'story-title', 
            'article-title',
            'headline',
            'title',
            'teaser-text',
            'story-text'
        ]
        
        # Check in the link element itself
        for class_name in title_classes:
            title_element = link_element.find(class_=class_name)
            if title_element:
                title = title_element.get_text(strip=True)
                if title and len(title) > 10:
                    return title
        
        # Check in parent/ancestor elements
        current_element = link_element.parent
        depth = 0
        while current_element and depth < 3:  # Don't go too deep
            for class_name in title_classes:
                title_element = current_element.find(class_=class_name)
                if title_element:
                    title = title_element.get_text(strip=True)
                    if title and len(title) > 10:
                        return title
            current_element = current_element.parent
            depth += 1
        
        # Method 5: Look for alt text in images
        img = link_element.find('img')
        if img:
            alt_text = img.get('alt')
            if alt_text and len(alt_text.strip()) > 10:
                return alt_text.strip()
        
        return "No title found"
    
    def ScrapeFullText(self, url: str) -> str:
        """
        Scrapes a full article's text from the given DW URL.
        """
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # DW-specific content selectors
            content_selectors = [
                'div[class*="longText"]',  # DW main content
                'div[class*="articleText"]',
                'div[class*="content"]',
                'article div[class*="text"]',
                '.article-content',
                '.story-content',
                '.longText p',
                'article p',
                '.text p',
                'main p'
            ]
            
            for selector in content_selectors:
                content_elements = soup.select(selector)
                if content_elements:
                    if selector.endswith(' p'):
                        # Multiple paragraphs
                        paragraphs = []
                        for elem in content_elements:
                            text = elem.get_text(strip=True)
                            if text and len(text) > 30:  # Filter out very short paragraphs
                                # Skip common DW footer text
                                if not any(skip_text in text.lower() for skip_text in 
                                         ['dw recommends', 'more on this topic', 'watch video', 'related subjects']):
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
                                    if text and len(text) > 30:
                                        # Skip DW-specific elements
                                        if not any(skip_text in text.lower() for skip_text in 
                                                 ['dw recommends', 'copyright', 'related:', 'watch:', 'listen:']):
                                            paragraph_texts.append(text)
                                if paragraph_texts:
                                    return "\n\n".join(paragraph_texts)
                            
                            # Fallback to all text in container
                            content = content_elem.get_text(strip=True)
                            if content and len(content) > 200:
                                return content
            
            return "Error: No article content found"
            
        except requests.RequestException as e:
            return f"Error: Unable to fetch the article. {str(e)}"
        except Exception as e:
            return f"Error: Failed to parse article content. {str(e)}"
    
    def ScrapeSpecial(self, url: str) -> Union[List[str], str]:
        """
        Scrapes special content from a specific DW URL (quotes, highlights, etc.).
        """
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            special_content = []
            
            # Look for quotes and highlighted content
            quote_selectors = [
                'blockquote',
                '.quote',
                '.highlight',
                '.pullquote',
                '.fact-box',
                'em',
                'strong'
            ]
            
            for selector in quote_selectors:
                elements = soup.select(selector)
                for element in elements:
                    if isinstance(element, Tag):
                        text = element.get_text(strip=True)
                        if text and len(text) > 20 and text not in special_content:
                            # Avoid adding navigation or common elements
                            excluded_phrases = [
                                'dw recommends', 'watch video', 'listen to audio', 
                                'more on this topic', 'related subjects', 'share',
                                'facebook', 'twitter', 'whatsapp', 'telegram'
                            ]
                            if not any(phrase in text.lower() for phrase in excluded_phrases):
                                special_content.append(text)
            
            # Look for DW-specific highlighted content
            dw_highlight_selectors = [
                '.factbox',
                '.infobox',
                '.teaser-text',
                '.summary',
                '.intro',
                '.lead'
            ]
            
            for selector in dw_highlight_selectors:
                elements = soup.select(selector)
                for element in elements:
                    if isinstance(element, Tag):
                        text = element.get_text(strip=True)
                        if text and len(text) > 20 and text not in special_content:
                            special_content.append(text)
            
            # Remove duplicates while preserving order
            unique_content = []
            for item in special_content:
                if item not in unique_content and len(item) > 20:
                    unique_content.append(item)
            
            return unique_content if unique_content else "No special content found"
            
        except requests.RequestException as e:
            return f"Error: Unable to fetch the page. {str(e)}"
        except Exception as e:
            return f"Error: Failed to parse special content. {str(e)}"

    def ScrapeByCategory(self, category: str) -> Union[List[Dict[str, str]], str]:
        """
        Scrapes articles from a specific DW category.
        Common DW categories: world, germany, business, science, environment, culture, sports
        """
        try:
            category_url = f"{self.base_url}/en/{category.lower()}"
            response = requests.get(category_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            articles = []
            
            # Use the same selectors as ScrapeHome but on category page
            selectors = [
                'a[href*="/en/"]',
                'article a',
                'h1 a, h2 a, h3 a, h4 a',
                '.teaser a',
                'div[class*="teaser"] a'
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
                        if title and title != "No title found" and len(title.strip()) > 10:
                            href = str(href).strip()
                            
                            if href.startswith('/'):
                                href = self.base_url + href
                            elif not href.startswith('http'):
                                href = self.base_url + '/' + href
                            
                            if self._is_valid_dw_article(href):
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
    
    def ScrapeByRegion(self, region: str) -> Union[List[Dict[str, str]], str]:
        """
        Scrapes articles from a specific DW regional section.
        Common DW regions: africa, asia, europe, americas
        """
        try:
            region_url = f"{self.base_url}/en/{region.lower()}"
            response = requests.get(region_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            articles = []
            
            # Regional page selectors
            selectors = [
                'a[href*="/en/"]',
                '.region-teaser a',
                'article a',
                'h2 a, h3 a',
                '.story a'
            ]
            
            links = []
            for selector in selectors:
                found_links = soup.select(selector)
                if found_links:
                    links.extend(found_links)
            
            seen_hrefs = set()
            for link in links:
                if isinstance(link, Tag):
                    href = link.get('href')
                    if href and href not in seen_hrefs:
                        seen_hrefs.add(href)
                        
                        title = self._extract_title(link)
                        if title and title != "No title found" and len(title.strip()) > 10:
                            href = str(href).strip()
                            
                            if href.startswith('/'):
                                href = self.base_url + href
                            elif not href.startswith('http'):
                                href = self.base_url + '/' + href
                            
                            if self._is_valid_dw_article(href):
                                articles.append({
                                    'title': title.strip(),
                                    'link': href,
                                    'region': region
                                })
            
            return articles if articles else f"No articles found for {region} region"
            
        except requests.RequestException as e:
            return f"Request error for region {region}: {str(e)}"
        except Exception as e:
            return f"Parsing error for region {region}: {str(e)}"