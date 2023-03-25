import time

import schedule
from db_client import get_all_flats, DBNAME, USER, PASSWORD, HOST
import psycopg2
from datetime import datetime
from sentry_sdk import capture_message, push_scope


def archive_old_flats(flats=get_all_flats()):
    for flat in flats:
        flat_date = flat[6].replace(tzinfo=None)
        delta_days = (datetime.now() - flat_date).days
        if not flat[16] and delta_days > 10:
            with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
                with conn.cursor() as cur:
                    cur.execute("""UPDATE flats SET is_archive=true WHERE id=%s""", (flat[0], ))
            print(f"id: {flat[0]}. Успешно архивировано")
    with push_scope() as scope:
        scope.set_extra('debug', False)
        capture_message('Архивирование устаревших записей завершено успешно.', 'info')


# archive_old_flats()
schedule.every().day.at("01:00").do(archive_old_flats)

while True:
    schedule.run_pending()
    time.sleep(60)