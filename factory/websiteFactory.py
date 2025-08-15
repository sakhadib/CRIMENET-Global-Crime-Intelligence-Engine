from StrategyScraper.bbcNewsScraper import BBCNewsScraper
from StrategyScraper.aljajiraScraper import AlJazeeraScraper
from StrategyScraper.euroNewsScraper import EuroNewsScraper
from StrategyScraper.APNewsScraper import APNewsScraper
from StrategyScraper.VOAScraper import VOAScraper
from StrategyScraper.DWScraper import DWScraper

websites = [
    # {"name": "bbc", "scraper": BBCNewsScraper()},
    # {"name": "aljazeera", "scraper": AlJazeeraScraper()},
    # {"name": "euronews", "scraper": EuroNewsScraper()},
    # {"name": "apnews", "scraper": APNewsScraper()},
    # {"name": "voa", "scraper": VOAScraper()},
    {"name": "dw", "scraper": DWScraper()}
]   