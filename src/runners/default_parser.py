from abc import ABC, abstractmethod
from alive_progress import alive_bar
from db_client import insert_flat, insert_batch
from data import Flat
from sentry_sdk import capture_exception, capture_message, push_scope


class DefaultParser(ABC):

    @abstractmethod
    def get_parser_name(self) -> str:
        return 'unnamed parser'

    @abstractmethod
    def get_links(self, page_from=0, page_to=10) -> list[str]:
        return []

    @abstractmethod
    def get_info_from_links(self, links: list, reference: str) -> list[Flat]:
        return []

    @staticmethod
    def save(flats: list, mode: str) -> None:
        count_bad_push = 0
        if mode == 'batch':
            flats_list = []
            with alive_bar(len(flats), title=f'[PostgreSQL] Загружаю в базу...') as bar:
                for flat in flats:
                    flats_list.append(tuple([flat.link, flat.reference, flat.price, flat.title, flat.description, flat.date,
                                      flat.space, flat.city, flat.street, flat.area, int(flat.year), int(flat.rooms),
                                      flat.phone_num, ','.join(flat.images)]))
                    bar()
                insert_batch(flats_list)
        elif mode == 'default':
            with alive_bar(len(flats), title=f'[PostgreSQL] Загружаю в базу...') as bar:
                for count, flat in enumerate(flats, start=1):
                    bar()
                    with push_scope() as scope:
                        scope.set_extra('debug', False)
                        try:
                            insert_flat(flat)
                        except Exception as e:
                            capture_exception(e)
                            count_bad_push += 1
                            # print(f'[PostgreSQL] Запись №{count} не загружена, так как содержит ошибку. {flat.link}. '
                            #       f'Ошибка: {e}')
                            continue
        with push_scope() as scope:
            scope.set_extra('debug', False)
            capture_message(f'Обработано: {len(flats)} записей, загружено в базу данных: {len(flats) - count_bad_push}.'
                            f' Ошибок: {count_bad_push}. Хорошего дня!', 'info')
        print(f'[PostgreSQL] Обработано: {len(flats)} записей, загружено в базу данных: {len(flats) - count_bad_push}. '
              f'Ошибок: {count_bad_push}. Хорошего дня!')

    def get_started(self, page_from=2, page_to=4) -> None:
        print(f'Запуск парсера...')
        links = self.get_links(page_from=page_from, page_to=page_to)
        flats = self.get_info_from_links(links)
        self.save(flats, mode='default')
