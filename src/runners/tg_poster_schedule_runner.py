import schedule
import time
from constants import USED_PARSERS
import db_client
import tg_poster
from datetime import datetime
import sentry_sdk

sentry_sdk.init(
    dsn="https://031227e66b7f4f4f8e2e5b18f7ce31d7@o4504887248355328.ingest.sentry.io/4504890026229760",
    traces_sample_rate=1.0
)

POST_EVERY_MINUTES = 10


def do_post_in_telegram() -> None:
    print(f'Телеграм оповещения стартовали: {datetime.now()}')
    parser_names = list(map(lambda el: el.get_parser_name(), USED_PARSERS))
    posts = db_client.get_all_not_posted_flats(parser_names)
    for post in posts:
        post_message = f'<b>Цена:</b> {post[2]} BYN\n'
        post_message += f'<b>Описание:</b> {post[4]}\n\n'
        post_message += f"<b>Ссылка: </b> <a href='{post[0]}'>Источник</a>\n\n"
        # post_message += '\n'.join(list(map(lambda el: el, post[6].split(',')[:6])))
        tg_poster.send_tg_post(post_message)
        time.sleep(5)
    db_client.update_is_posted_state(list(map(lambda el: el[7], posts)))


schedule.every(POST_EVERY_MINUTES).minutes.do(do_post_in_telegram)


while True:
    schedule.run_pending()
    time.sleep(1)
