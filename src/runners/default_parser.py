from abc import ABC, abstractmethod
from alive_progress import alive_bar
from db_client import insert_flat


class DefaultParser(ABC):

    @abstractmethod
    def get_parser_name(self):
        return 'unnamed parser'

    @abstractmethod
    def get_links(self, page_from=0, page_to=10) -> list:
        return []

    @abstractmethod
    def get_info_from_links(self, links: list, reference: str) -> list:
        return []

    @staticmethod
    def save(flats):
        with alive_bar(len(flats), title=f'[PostgreSQL] Загружаю в базу...') as bar:
            for count, flat in enumerate(flats, start=1):
                bar()
                try:
                    insert_flat(flat)
                except Exception as e:
                    print(f'[PostgreSQL] Запись №{count} не загружена, так как содержит ошибку. {flat.link}. '
                          f'Ошибка: {e}')
                    continue

    def get_started(self, page_from=1, page_to=2):
        print(f'Запуск парсера...')
        links = self.get_links(page_from=page_from, page_to=page_to)
        flats = self.get_info_from_links(links)
        self.save(flats)
        print(f'[PostgreSQL] Загружено {len(flats)} записей в базу данных. Хорошего дня!')