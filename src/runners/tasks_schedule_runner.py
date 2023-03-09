import schedule
import time
from constants import USED_PARSERS
import threading
from datetime import datetime

PARSE_EVERY_MINUTES = 5


def parse_all():
    print(f'Парсер стартовал: {datetime.now()}')
    for parser in USED_PARSERS:
        thread = threading.Thread(target=parser.get_started)
        thread.start()


schedule.every(PARSE_EVERY_MINUTES).minutes.do(parse_all)


while True:
    schedule.run_pending()
    time.sleep(1)
