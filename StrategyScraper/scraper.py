from abc import ABC, abstractmethod
from typing import List, Union, Dict

class NewsScraper(ABC):
    
    @abstractmethod
    def ScrapeHome(self) -> Union[List[Dict[str, str]], str]:
        """
        Scrape and return the home page of the news website.
        Returns a list of dictionaries with 'title' and 'link' keys, or error string.
        """
        pass
    
    @abstractmethod
    def ScrapeFullText(self) -> str:
        """
        Scrape and return the full text of a specific news article.
        """
        pass
    
    @abstractmethod
    def ScrapeSpecial(self, url: str) -> Union[List[str], str]:
        """
        Scrape and return special content from the provided URL.
        
        :param url: The URL of the page to scrape.
        """
        pass
