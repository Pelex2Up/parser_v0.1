import schedule
import time
from constants import USED_PARSERS
import threading
from datetime import datetime
import sentry_sdk
from archivator import archive_old_flats

sentry_sdk.init(
    dsn="https://031227e66b7f4f4f8e2e5b18f7ce31d7@o4504887248355328.ingest.sentry.io/4504890026229760",
    traces_sample_rate=1.0
)

PARSE_EVERY_MINUTES = 2


def parse_all():
    print(f'Парсер стартовал: {datetime.now()}')
    for parser in USED_PARSERS:
        thread = threading.Thread(target=parser.get_started)
        thread.start()


schedule.every(PARSE_EVERY_MINUTES).minutes.do(parse_all)
schedule.every().day.at("01:00").do(archive_old_flats)

while True:
    schedule.run_pending()
    time.sleep(1)
