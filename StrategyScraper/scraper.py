from abc import ABC, abstractmethod

class NewsScraper(ABC):
    
    @abstractmethod
    def ScrapeHome(self):
        """
        Scrape and return the home page of the news website.
        """
        pass
    
    @abstractmethod
    def ScrapeFullText(self):
        """
        Scrape and return the full text of a specific news article.
        """
        pass
    
    @abstractmethod
    def ScrapeSpecial(self, url):
        """
        Scrape and return special content from the provided URL.
        
        :param url: The URL of the page to scrape.
        """
        pass
