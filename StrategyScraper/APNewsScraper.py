import requests
from datetime import datetime
import time
from .scraper import NewsScraper

class APNewsScraper(NewsScraper):
    """
    Associated Press News Scraper
    Scrapes news articles directly from AP News website (no RSS)
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://apnews.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    def ScrapeHome(self):
        """
        Main scraping method for AP News homepage
        """
        try:
            print("Starting AP News scraping from website...")
            
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            articles = self._parse_homepage(response.text)
            
            if articles:
                print(f"AP News scraping completed: {len(articles)} articles found")
            else:
                print("AP News scraping completed: No articles found")
                
            return articles
            
        except Exception as e:
            print(f"Error in AP News scraping: {e}")
            return []
    
    def _parse_homepage(self, html_content):
        """
        Parse AP News homepage HTML to extract articles
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            articles = []
            processed_urls = set()
            
            # Look for article containers based on the screenshot
            # AP News uses various selectors for article links
            selectors_to_try = [
                'a[href*="/article/"]',  # Direct article links
                '.PageList-items a',      # Page list items
                '.PagePromo-title a',     # Promo title links  
                '.Link',                  # General link class
                'h2 a',                   # Headlines in h2 tags
                'h3 a',                   # Headlines in h3 tags
                '.bsp-custom-headline a', # Custom headlines
            ]
            
            for selector in selectors_to_try:
                links = soup.select(selector)
                
                for link in links:
                    try:
                        href = link.get('href', '')
                        title = link.get_text().strip()
                        
                        # Filter for actual article URLs
                        if not href or href in processed_urls:
                            continue
                            
                        # Build full URL
                        if href.startswith('/'):
                            full_url = self.base_url + href
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue
                            
                        # Only process AP News articles
                        if 'apnews.com' not in full_url or '/article/' not in full_url:
                            continue
                            
                        # Validate title
                        if not title or len(title) < 10 or len(title) > 200:
                            continue
                            
                        processed_urls.add(href)
                        
                        # Try to get description from nearby elements
                        description = ""
                        parent = link.parent
                        if parent:
                            # Look for description in sibling or parent elements
                            desc_elem = parent.find('p') or parent.find('.PagePromo-description')
                            if desc_elem:
                                description = desc_elem.get_text().strip()[:300]
                        
                        article = {
                            'title': title,
                            'link': full_url,
                            'description': description,
                            'pub_date': '',  # Will be empty for homepage scraping
                            'source': 'AP News',
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        articles.append(article)
                        
                        # Limit articles to prevent overwhelming
                        if len(articles) >= 30:
                            break
                            
                    except Exception as e:
                        continue
                
                if len(articles) >= 20:  # Stop if we have enough articles
                    break
            
            # Remove duplicates based on title
            seen_titles = set()
            unique_articles = []
            for article in articles:
                title_lower = article['title'].lower()
                if title_lower not in seen_titles:
                    seen_titles.add(title_lower)
                    unique_articles.append(article)
            
            print(f"Successfully scraped {len(unique_articles)} unique articles from AP News")
            return unique_articles
            
        except ImportError:
            print("BeautifulSoup not installed. Install with: pip install beautifulsoup4")
            return []
        except Exception as e:
            print(f"Error parsing AP News homepage: {e}")
            return []
    
    def ScrapeRSSOnly(self):
        """
        AP News doesn't have RSS - redirect to main scraping
        """
        print("AP News doesn't provide RSS feeds - using website scraping")
        return self.ScrapeHome()
    
    def ScrapeCategory(self, category="general"):
        """
        Scrape articles from specific AP News category pages
        """
        try:
            # AP News category URLs
            category_urls = {
                "politics": f"{self.base_url}/politics",
                "sports": f"{self.base_url}/sports", 
                "entertainment": f"{self.base_url}/entertainment",
                "health": f"{self.base_url}/health",
                "science": f"{self.base_url}/science",
                "technology": f"{self.base_url}/technology",
                "business": f"{self.base_url}/business",
                "world": f"{self.base_url}/world-news",
                "us": f"{self.base_url}/us-news",
                "general": self.base_url
            }
            
            category_url = category_urls.get(category.lower(), self.base_url)
            
            print(f"Fetching AP News {category} category from: {category_url}")
            
            response = requests.get(category_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            articles = self._parse_homepage(response.text)
            
            # Add category to each article
            for article in articles:
                article['category'] = category
            
            print(f"Successfully scraped {len(articles)} articles from AP News {category} category")
            return articles
            
        except Exception as e:
            print(f"Error scraping AP News {category} category: {e}")
            return []
    
    def ScrapeFullText(self, url):
        """
        Scrape full text content from an AP News article URL
        """
        try:
            print(f"Scraping full text from: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # AP News article content selectors
            content_selectors = [
                '[data-key="article"] p',  # Main article paragraphs
                '.Article p',              # Article class paragraphs
                '.RichTextStoryBody p',    # Rich text body
                'div[role="main"] p',      # Main content area
                '.story-body p'            # Story body paragraphs
            ]
            
            full_text = ""
            
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    text_parts = []
                    for p in paragraphs:
                        text = p.get_text().strip()
                        if text and len(text) > 20:  # Filter out very short paragraphs
                            text_parts.append(text)
                    
                    if text_parts:
                        full_text = '\n\n'.join(text_parts)
                        break
            
            if full_text:
                print(f"Successfully extracted {len(full_text)} characters of text")
                return full_text
            else:
                print("No article text content found")
                return ""
                
        except ImportError:
            print("BeautifulSoup not installed. Install with: pip install beautifulsoup4")
            return ""
        except requests.RequestException as e:
            print(f"Network error fetching full text: {e}")
            return ""
        except Exception as e:
            print(f"Error scraping full text: {e}")
            return ""
    
    def ScrapeSpecial(self, special_type="breaking"):
        """
        Scrape special content from AP News (breaking news, trending, etc.)
        """
        try:
            print(f"Scraping special content: {special_type}")
            
            # For breaking news, check the main page and look for breaking indicators
            if special_type.lower() == "breaking":
                articles = self.ScrapeHome()
                
                # Filter for articles that might be breaking news
                # Look for keywords in titles or check recency
                breaking_articles = []
                breaking_keywords = ['breaking', 'urgent', 'developing', 'live', 'update', 'latest']
                
                for article in articles[:15]:  # Check first 15 articles
                    title_lower = article['title'].lower()
                    if any(keyword in title_lower for keyword in breaking_keywords):
                        article['special_type'] = 'breaking'
                        breaking_articles.append(article)
                
                # If no breaking keywords found, return recent articles
                if not breaking_articles:
                    for article in articles[:10]:
                        article['special_type'] = 'breaking'
                        breaking_articles.append(article)
                
                print(f"Found {len(breaking_articles)} breaking news articles")
                return breaking_articles
            
            # For trending, return top articles from main feed
            elif special_type.lower() == "trending":
                articles = self.ScrapeHome()
                trending = articles[:15]  # Top 15 articles
                for article in trending:
                    article['special_type'] = 'trending'
                
                print(f"Found {len(trending)} trending articles")
                return trending
            
            # For other special types, return general articles
            else:
                articles = self.ScrapeHome()
                for article in articles:
                    article['special_type'] = special_type
                
                print(f"Found {len(articles)} articles for special type: {special_type}")
                return articles
                
        except Exception as e:
            print(f"Error scraping special content: {e}")
            return []