from service.scrapingService import ScrapingService
from service.logService import LogService
from service.crimeIdentifierService import CrimeIdentifierService
from service.csvService import CSVService
from factory.websiteFactory import websites


def main():
    print("CRIMENET - Global Crime Intelligence Engine")
    print("=" * 50)
    
    crimeIdentifierModelPath = 'model/NBCrime.pkl'
    
    scraping_service = ScrapingService(websites)
    data = scraping_service.scrape()
    
    print(f"Scraped {len(data)} headlines from various sources.")
    
    crime_identifier = CrimeIdentifierService(crimeIdentifierModelPath)
    crime_news = crime_identifier.filter_crime_headlines(data)
    
    print(f"Filtered {len(crime_news)} crime-related headlines.")

    csv_service = CSVService('data/crime_news.csv')
    csv_service.append_headlines(crime_news)
    
    print("Crime-related headlines saved to data.crime_news.csv")
    


if __name__ == "__main__":
    main()