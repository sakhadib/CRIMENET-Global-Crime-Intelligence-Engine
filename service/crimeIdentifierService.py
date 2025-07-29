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

    def classify_with_confidence(self, title: str, confidence_threshold: float = 0.75):
        """
        Classify a headline using the trained model with confidence threshold.
        
        :param title: The headline to classify.
        :param confidence_threshold: Minimum confidence score required for crime classification.
        :return: tuple (is_crime: bool, confidence_score: float)
        """
        # Preprocess the title
        processed_title = self.preprocess(title)
        
        # Since the model is a pipeline that includes the vectorizer,
        # we pass the raw text directly to the model
        prediction_proba = self.model.predict_proba([processed_title])
        
        # Get the probability for crime class (class 1)
        crime_probability = prediction_proba[0][1] if len(prediction_proba[0]) > 1 else 0.0
        
        # Only classify as crime if confidence is above threshold
        is_crime = crime_probability > confidence_threshold
        
        classification = "crime-related" if is_crime else "non-crime"
        confidence_str = f"(confidence: {crime_probability:.3f})"
        self.logger.log(f"Classified headline as {classification} {confidence_str}: '{title}'")
        
        return is_crime, crime_probability

    def classify(self, title: str, confidence_threshold: float = 0.75):
        """
        Classify a headline using the trained model with confidence threshold.
        
        :param title: The headline to classify.
        :param confidence_threshold: Minimum confidence score required for crime classification.
        :return: 1 if crime-related with high confidence, 0 otherwise.
        """
        is_crime, _ = self.classify_with_confidence(title, confidence_threshold)
        return 1 if is_crime else 0

    def filter_crime_headlines(self, headlines_dict: list, confidence_threshold: float = 0.75):
        """
        Filters the headlines to return only crime-related news with high confidence.
        
        :param headlines_dict: List of dictionaries with {'title': <headline>, 'link': <URL>, 'source': <source>}
        :param confidence_threshold: Minimum confidence score required for crime classification.
        :return: List of dictionaries with only high-confidence crime-related headlines including confidence scores.
        """
        self.logger.log(f"Starting crime headline filtering process for {len(headlines_dict)} headlines with confidence threshold {confidence_threshold}")
        
        crime_news = []
        skipped_count = 0
        
        # Loop through each headline and classify it
        for data in headlines_dict:
            title = data.get('title')
            link = data.get('link')
            source = data.get('source', 'Unknown')
            
            # Skip if title or link is missing
            if not title or not link:
                skipped_count += 1
                continue
            
            # Classify the headline with confidence threshold
            is_crime, confidence_score = self.classify_with_confidence(title, confidence_threshold)
            
            if is_crime:  # Only include high-confidence crime headlines
                crime_news.append({
                    'source': source,
                    'title': title,
                    'url': link,
                    'confidence_score': round(confidence_score, 3)
                })
        
        self.logger.log(f"Crime filtering completed: {len(crime_news)} high-confidence crime headlines found, {skipped_count} headlines skipped due to missing data")
        
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
