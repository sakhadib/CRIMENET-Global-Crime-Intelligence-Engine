import pandas as pd

class CSVService:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def append_headlines(self, headlines: list[dict]):
        """
        Appends a list of headlines to the CSV file.

        :param headlines: List of dictionaries with 'title' and 'link'.
        """
        df = pd.DataFrame(headlines, columns=['title', 'link'])
        df.to_csv(self.file_path, mode='a', header=False, index=False)