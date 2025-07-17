import os
from datetime import datetime

class LogService:
    def __init__(self):
        self.logs = []
        self.log_file = 'log'
        # Check if log file exists, create if not
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                pass

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp} - {message}]"
        self.logs.append(log_entry)
        # Append log message to file
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')

    def get_logs(self):
        return self.logs
