import pandas as pd
import os

class CSVService:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def create_with_headers(self):
        """
        Creates a new CSV file with headers if it doesn't exist.
        """
        if not os.path.exists(self.file_path):
            df = pd.DataFrame(columns=['source', 'title', 'url', 'confidence_score'])
            df.to_csv(self.file_path, index=False)

    def append_headlines(self, headlines: list[dict]):
        """
        Appends a list of headlines to the CSV file.

        :param headlines: List of dictionaries with 'source', 'title', 'url', and 'confidence_score'.
        """
        # Create file with headers if it doesn't exist
        file_exists = os.path.exists(self.file_path)
        
        df = pd.DataFrame(headlines, columns=['source', 'title', 'url', 'confidence_score'])
        df.to_csv(self.file_path, mode='a', header=not file_exists, index=False)