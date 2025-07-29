from .logService import LogService


class ScrapingService:
    def __init__(self, websites):
        self.websites = websites
        self.log_service = LogService()
        self.data = []

    def scrape(self):
        self.log_service.log("Starting scraping process")
        
        for website in self.websites:
            website_name = website.get("name", "Unknown")
            scraper = website.get("scraper")
            
            if scraper:
                self.log_service.log(f"Starting to scrape {website_name}")
                try:
                    data = scraper.ScrapeHome()
                    
                    # Handle both success (list) and error (string) cases
                    if isinstance(data, list):
                        # Add source information to each headline
                        for item in data:
                            if isinstance(item, dict):
                                item['source'] = website_name
                        
                        self.data.extend(data)
                        self.log_service.log(f"Successfully scraped {len(data)} headlines from {website_name}")
                    elif isinstance(data, str):
                        # Error case
                        self.log_service.log(f"Error scraping {website_name}: {data}")
                    else:
                        self.log_service.log(f"Unexpected response type from {website_name}: {type(data)}")
                        
                except Exception as e:
                    self.log_service.log(f"Exception occurred while scraping {website_name}: {str(e)}")
            else:
                self.log_service.log(f"No scraper found for {website_name}")

        self.log_service.log(f"Scraping completed. Total headlines collected: {len(self.data)}")
        return self.data
