import csv
from datetime import datetime
import logging
import os

from django.conf import settings
from django.http import HttpRequest

from nkunyim_iam.util.client import HttpClient


LOG_TYPE_GEN = "GEN"
LOG_TYPE_API = "API"
LOG_TYPE_IAM = "IAM"


class LoggingCommand:
    
    def __init__(self, req: HttpRequest) -> None:
        self.client = HttpClient(req=req, name=settings.LOGGING_SERVICE)
        super().__init__()
        
    def send(self, data: dict) -> None:
        self.client.post(path=f"/api/{str(data['xantyp']).lower()}_logs/", data=data)
        

class LoggingHandler(logging.Handler):
    
    def __init__(self) -> None:
        super().__init__()
        
        path = datetime.now().strftime("%Y%m%d")
        self.file_path = f"{settings.TEXT_FILE_PATH}/{path}.csv"


    def emit(self, record):
        try:
            data_dict = record.__dict__.copy()
            if hasattr(record, 'xanreq'):
                xanreq: HttpRequest = record.xanreq
                command = LoggingCommand(req=xanreq)
                command.send(data=data_dict)
            else:
                file_exists = os.path.isfile(self.file_path)
                write_header = not file_exists or os.path.getsize(self.file_path) == 0

                with open(self.file_path, mode='a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=data_dict.keys())

                    if write_header:
                        writer.writeheader()

                    writer.writerow(data_dict)

        except Exception:
            self.handleError(record)
            
