import requests
from alive_progress import alive_bar
from bs4 import BeautifulSoup
from data.data import Flat
import re
from datetime import datetime
from data.db_client import insert_flat
from fake_useragent import UserAgent

ua = UserAgent()


def get_all_last_flats_links(page_from=0, page_to=1):
    headers = {'accept': '*/*', 'user-agent': ua.firefox}
    flat_links = []
    with alive_bar(page_to - page_from + 1, title='[REALT] Анализирую страницы...') as bar:
        while page_from <= page_to:
            bar()
            resp = requests.get(f'https://realt.by/sale/flats/?page={page_from}', headers=headers)
            html = BeautifulSoup(resp.content, 'html.parser')
            for a in html.find_all('a', href=True, class_='teaser-title'):
                flat_links.append(a['href'])
            page_from += 1
        ready_links = list(filter(lambda el: 'object' in el, flat_links))
        return ready_links


def enrich_links_to_flats(links, reference):
    flats = []
    with alive_bar(len(links), title='[REALT] Формирую ссылки...') as bar:
        for counter, link in enumerate(links, start=1):
            bar()
            resp = requests.get(link)
            html = BeautifulSoup(resp.content, 'html.parser')
            title = html.find('h1', class_='order-1 mb-0.5 md:-order-2 md:mb-4 block w-full lg:text-h1Lg '
                                           'text-h1 font-raleway font-bold flex items-center').text.strip()
            raw_price = html.find('h2', class_='w-full sm:w-auto sm:inline-block sm:mr-1.5 lg:text-h2Lg text-h2 '
                                               'font-raleway font-bold flex items-center')
            if raw_price is not None:
                price = int(re.sub('[^0-9]', '', raw_price.text.strip()))
            else:
                price = 0
            description = html.find('section', class_='bg-white flex flex-wrap md:p-6 my-4 '
                                                      'rounded-md').find('div', class_='w-full').text.strip()[:3000]
            try:
                date = datetime.strptime(html.find('span', class_='mr-1.5').text.strip(), '%d.%m.%Y')
            except Exception as e:
                date = datetime.now()
            space = html.find('ul', class_='w-full -my-1').text.split('Площадь общая')[1].split('Площадь жилая')[0].strip()
            city = html.find('a', class_='focus:outline-none sm:focus:shadow-10bottom transition-colors '
                                         'cursor-pointer inline md:inline-block mr-4 text-basic hover:text-info-500 '
                                         'active:text-info').text
            try:
                street = html.find_all('a', class_='focus:outline-none sm:focus:shadow-10bottom transition-colors '
                                                   'cursor-pointer inline md:inline-block mr-4 text-basic '
                                                   'hover:text-info-500 active:text-info')[1].text
            except Exception as e:
                street = 'Не указано в объявлении'
            try:
                area = html.find('a', class_='focus:outline-none sm:focus:shadow-10bottom transition-colors '
                                             'cursor-pointer inline md:inline-block !inline-block mr-4 text-basic '
                                             'hover:text-info-500 active:text-info').text
            except Exception as e:
                area = city
            try:
                year = ''
                raw_year = html.find('ul', class_='w-full -my-1').text.split('Год постройки')[1]
                for i in raw_year:
                    if len(year) < 4 and i.isdigit():
                        year += i
            except Exception as e:
                year = 0
            rooms = html.find('ul', class_='w-full -my-1').text.split('Количество комнат')[1].split('Раздельных комнат')[0].strip()
            phone_num = 'С реалта без selenium не достать номер телефона'
            flats.append(Flat(
                link=link,
                reference=reference,
                price=price,
                title=title,
                description=description,
                date=date,
                space=space,
                street=street,
                city=city,
                area=area,
                year=year,
                rooms=rooms,
                phone_num=phone_num
            ))
    return flats


def save_flats(flats):
    with alive_bar(len(flats), title='[REALT] Загружаю в базу...') as bar:
        for counter, flat in enumerate(flats, start=1):
            bar()
            insert_flat(flat)


def get_last_flats(page_from=0, page_to=1, reference='REALT'):
    print(f'Запуск парсера [{reference}]...')
    links = get_all_last_flats_links(page_from, page_to)
    flats = enrich_links_to_flats(links, reference=reference)
    save_flats(flats)
    print(f'[REALT] Загружено {len(flats)} записей в базу данных. Хорошего дня!')


get_last_flats(1,)
