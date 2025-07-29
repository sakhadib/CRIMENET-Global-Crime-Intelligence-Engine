from service.scrapingService import ScrapingService
from service.crimeIdentifierService import CrimeIdentifierService
from service.csvService import CSVService
from factory.websiteFactory import websites

def test_new_format():
    print("Testing new CSV format with confidence scores...")
    
    # Test scraping
    scraping_service = ScrapingService(websites)
    data = scraping_service.scrape()
    print(f"Scraped {len(data)} headlines")
    
    # Check first few items have source
    print("\nFirst 3 headlines with source:")
    for i, item in enumerate(data[:3]):
        print(f"{i+1}. Source: {item.get('source', 'Missing')}")
        print(f"   Title: {item.get('title', 'Missing')[:60]}...")
        print()
    
    # Test crime identification with confidence
    crimeIdentifierModelPath = 'model/NBCrime.pkl'
    crime_identifier = CrimeIdentifierService(crimeIdentifierModelPath)
    crime_news = crime_identifier.filter_crime_headlines(data, confidence_threshold=0.75)
    
    print(f"Filtered {len(crime_news)} high-confidence crime headlines")
    
    # Check structure of filtered data
    if crime_news:
        print("\nFirst crime headline structure:")
        first_crime = crime_news[0]
        for key, value in first_crime.items():
            print(f"  {key}: {value}")
    
    # Test CSV saving
    csv_service = CSVService('data/test_crime_news.csv')
    csv_service.append_headlines(crime_news)
    
    print(f"\nSaved {len(crime_news)} headlines to test CSV file")

if __name__ == "__main__":
    test_new_format()
