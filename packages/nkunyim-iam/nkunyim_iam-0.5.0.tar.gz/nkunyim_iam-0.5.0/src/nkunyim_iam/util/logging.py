import csv
from datetime import datetime
import logging
from pathlib import Path

from django.conf import settings
from django.http import HttpRequest

from nkunyim_iam.util.client import HttpClient


LOG_TYPE_GEN = "GEN"
LOG_TYPE_API = "API"
LOG_TYPE_IAM = "IAM"

LOG_TYPE_KEY = "xantyp"
LOG_REQUEST_KEY = "xanreq"


class LoggingCommand:
    
    def __init__(self, req: HttpRequest) -> None:
        self.client = HttpClient(req=req, name=settings.LOGGING_SERVICE)
        super().__init__()
        
    def send(self, data: dict) -> None:
        self.client.post(path=f"/api/{str(data[LOG_TYPE_KEY]).lower()}_logs/", data=data)
        

class LoggingHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        date_str = datetime.now().strftime("%Y%m%d")
        self.file_path = Path(settings.TEXT_FILE_PATH) / f"{date_str}.csv"

    def emit(self, record: logging.LogRecord) -> None:
        try:
            data = record.__dict__.copy()

            if hasattr(record, LOG_REQUEST_KEY):
                xanreq: HttpRequest = getattr(record, LOG_REQUEST_KEY)
                LoggingCommand(req=xanreq).send(data=data)
            else:
                self._write_to_csv(data)

        except Exception:
            self.handleError(record)

    def _write_to_csv(self, data: dict) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        write_header = not self.file_path.exists() or self.file_path.stat().st_size == 0

        with self.file_path.open(mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())

            if write_header:
                writer.writeheader()

            writer.writerow(data)