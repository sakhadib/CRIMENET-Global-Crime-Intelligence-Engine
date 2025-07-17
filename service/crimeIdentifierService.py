import joblib
import pandas as pd
from .logService import LogService

class CrimeIdentifierService:
    def __init__(self, model_path: str):
        """
        Initializes the CrimeIdentifierService class.

        :param model_path: The path to the saved Naive Bayes model (.pkl file).
        """
        # Initialize logging service
        self.logger = LogService()
        
        # Load the pre-trained Naive Bayes model (pipeline)
        self.logger.log(f"Loading crime identification model from: {model_path}")
        self.model = joblib.load(model_path)
        self.logger.log("Crime identification model loaded successfully")

    def preprocess(self, text):
        """
        Preprocesses the input text before classification.
        
        :param text: The input text to preprocess.
        :return: Preprocessed text ready for model prediction.
        """
        return text  # Assuming you don't have any further preprocessing for simplicity.

    def classify(self, title: str):
        """
        Classify a headline using the trained model.
        
        :param title: The headline to classify.
        :return: 1 if crime-related, 0 otherwise.
        """
        # Preprocess the title
        processed_title = self.preprocess(title)
        
        # Since the model is a pipeline that includes the vectorizer,
        # we pass the raw text directly to the model
        prediction = self.model.predict([processed_title])
        
        result = prediction[0]
        classification = "crime-related" if result == 1 else "non-crime"
        self.logger.log(f"Classified headline as {classification}: '{title[:50]}{'...' if len(title) > 50 else ''}'")
        
        return result  # Return 0 or 1

    def filter_crime_headlines(self, headlines_dict: list):
        """
        Filters the headlines to return only crime-related news.
        
        :param headlines_dict: List of dictionaries with {'title': <headline>, 'link': <URL>}
        :return: List of dictionaries with only crime-related headlines and their links.
        """
        self.logger.log(f"Starting crime headline filtering process for {len(headlines_dict)} headlines")
        
        crime_news = []
        skipped_count = 0
        
        # Loop through each headline and classify it
        for data in headlines_dict:
            title = data.get('title')
            link = data.get('link')
            
            # Skip if title or link is missing
            if not title or not link:
                skipped_count += 1
                continue
            
            # Classify the headline
            if self.classify(title) == 1:  # 1 is crime-related
                crime_news.append(data)
        
        self.logger.log(f"Crime filtering completed: {len(crime_news)} crime headlines found, {skipped_count} headlines skipped due to missing data")
        
        return crime_news


# Usage Example:

# if __name__ == "__main__":
#     # Path to your trained model file
#     model_path = 'naive_bayes_model.pkl'
    
#     # Initialize the CrimeIdentifier with the model path
#     crime_identifier = CrimeIdentifier(model_path)
    
#     # Example scraped data (dict of title and link)
#     scraped_data = [
#         {"title": "Police arrest man for armed robbery", "link": "https://example.com/1"},
#         {"title": "Local community garden opens new section", "link": "https://example.com/2"},
#         {"title": "Crime wave hits downtown", "link": "https://example.com/3"},
#         {"title": "New school program for children", "link": "https://example.com/4"}
#     ]
    
#     # Filter out the crime-related headlines
#     filtered_data = crime_identifier.filter_crime_headlines(scraped_data)
    
#     # Print the filtered crime-related headlines and their links
#     print(filtered_data)
