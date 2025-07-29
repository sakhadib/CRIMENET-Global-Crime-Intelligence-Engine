from StrategyScraper.bbcNewsScraper import BBCNewsScraper
from StrategyScraper.aljajiraScraper import AlJazeeraScraper

websites = [
    {"name": "bbc", "scraper": BBCNewsScraper()},
    {"name": "aljazeera", "scraper": AlJazeeraScraper()},
]   