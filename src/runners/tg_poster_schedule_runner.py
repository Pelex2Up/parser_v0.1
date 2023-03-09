import schedule
import time
from constants import USED_PARSERS
import db_client
import tg_poster
from datetime import datetime

PARSE_EVERY_MINUTES = 1


def do_post_in_telegram():
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


schedule.every(PARSE_EVERY_MINUTES).minutes.do(do_post_in_telegram)


while True:
    schedule.run_pending()
    time.sleep(1)
