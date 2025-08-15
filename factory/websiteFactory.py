from StrategyScraper.bbcNewsScraper import BBCNewsScraper
from StrategyScraper.aljajiraScraper import AlJazeeraScraper
from StrategyScraper.yahooNewsScraper import YahooNewsScraper
from StrategyScraper.googleNewsScraper import GoogleNewsScraper
from StrategyScraper.newYorkTimesScraper import NewYorkTimesScraper
from StrategyScraper.euroNewsScraper import EuroNewsScraper
from StrategyScraper.APNewsScraper import APNewsScraper
from StrategyScraper.VOAScraper import VOAScraper
from StrategyScraper.DWScraper import DWScraper

websites = [
    # {"name": "bbc", "scraper": BBCNewsScraper()},
    # {"name": "aljazeera", "scraper": AlJazeeraScraper()},
    # {"name": "yahoonews", "scraper": YahooNewsScraper()},
    # {"name": "googlenews", "scraper": GoogleNewsScraper()},
    {"name": "newyorktimes", "scraper": NewYorkTimesScraper()}
]   