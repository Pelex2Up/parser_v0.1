from alive_progress import alive_bar
from bs4 import BeautifulSoup
import requests
import re
import datetime
from data import Flat
from data.db_client import insert_flat
from fake_useragent import UserAgent

ua = UserAgent()


def get_links(page_from=0, page_to=10):
    headers = {'accept': '*/*', 'user-agent': ua.firefox}
    flat_links = []
    url = 'https://domovita.by/minsk/flats/sale?page='
    with alive_bar(page_to - page_from + 1, title='[DOMOVITA] Анализирую страницы...') as bar:
        while page_from <= page_to:
            bar()
            response = requests.get(f'{url + str(page_from)}', headers=headers)
            html = BeautifulSoup(response.content, 'html.parser')
            for i in html.find_all('a', href=True, class_='found_item p-0 clearfix d_flex OFlatsSale'):
                flat_links.append(i['href'])
            page_from += 1
    return flat_links


def get_info_from_links(links, reference):
    flats = []
    with alive_bar(len(links), title='[DOMOVITA] Формирую ссылки...') as bar:
        for count, link in enumerate(links, start=1):
            bar()
            response = requests.get(link)
            html = BeautifulSoup(response.content, 'html.parser')
            title = html.find('div', class_='object-head__name').text.strip()
            raw_price = html.find('div', class_='dropdown-pricechange_price-block')
            if raw_price is not None:
                price = int(re.sub('[^0-9]', '', raw_price.text.split('р.')[0].strip()))
            else:
                price = 0
            try:
                description = html.find('div', id='object-description').text.strip()[:3000]
            except Exception as e:
                description = 'Описание отсутствует в объявлении'
            try:
                upd_date = html.find('span', class_='publication-info__item publication-info__update-date').text.strip()
                upd_date = upd_date.split(' ')
                date = datetime.datetime.strptime(upd_date[-1], '%d.%m.%Y')
            except Exception as e:
                pub_date = html.find('span', class_='publication-info__item publication-info__publication-date').text.strip()
                pub_date = pub_date.split(' ')
                date = datetime.datetime.strptime(pub_date[-1], '%d.%m.%Y')
            space = html.find_all('div', class_='object-info__params')[1].text.split('Общая площадь')[1].strip().split('\n')[0]
            city = html.find('span', id='city').text.strip()
            street = html.find('div', 'object-info__params').text.split('Адрес')[1].strip().split('\n')[0].strip()
            try:
                area = html.find('div', 'object-info__params').text.split('Район')[1].strip().split('\n')[0].strip()
            except Exception as e:
                area = "Район не отмечен в объявлении"
            try:
                year = ''
                raw_year = html.find_all('div', 'object-info__params')[0].text.split('Год постройки')[1].split('\n\n')[1]
                for i in raw_year:
                    if i.isdigit():
                        year += i
            except Exception as e:
                year = 0
            rooms = html.find_all('div', 'object-info__params')[1].text.split('Комнат')[1].split('\n')[1].strip()
            phone_num = html.find('a', class_='owner-info__phone').text.strip()
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


def save(flats):
    with alive_bar(len(flats), title='[DOMOVITA] Загружаю в базу...') as bar:
        for count, flat in enumerate(flats, start=1):
            bar()
            try:
                insert_flat(flat)
            except Exception as e:
                print(f'[DOMOVITA] Запись №{count} не загружена, так как содержит ошибку. {flat.link}. '
                      f'Ошибка: {e}')
                continue


def get_started(page_from=1, page_to=1, reference='DOMOVITA'):
    print(f'Запуск парсера [{reference}]...')
    links = get_links(page_from=page_from, page_to=page_to)
    flats = get_info_from_links(links, reference=reference)
    save(flats)
    print(f'[{reference}] Загружено {len(flats)} записей в базу данных. Хорошего дня!')


get_started(1, 5)