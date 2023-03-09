from alive_progress import alive_bar
from bs4 import BeautifulSoup
import requests
import re
import datetime
from data import Flat
from fake_useragent import UserAgent
from default_parser import DefaultParser


class DomovitaParser(DefaultParser):

    def get_parser_name(self):
        return 'DOMOVITA'

    def get_links(self, page_from=0, page_to=10):
        reference = self.get_parser_name()
        ua = UserAgent()
        headers = {'accept': '*/*', 'user-agent': ua.firefox}
        flat_links = []
        url = 'https://domovita.by/minsk/flats/sale?page='
        with alive_bar(page_to - page_from + 1, title=f'[{reference}] Анализирую страницы...') as bar:
            while page_from <= page_to:
                bar()
                response = requests.get(f'{url + str(page_from)}', headers=headers)
                html = BeautifulSoup(response.content, 'html.parser')
                for i in html.find_all('a', href=True, class_='found_item p-0 clearfix d_flex OFlatsSale'):
                    flat_links.append(i['href'])
                page_from += 1
        return flat_links

    def get_info_from_links(self, links, reference=None):
        reference = self.get_parser_name()
        ua = UserAgent()
        headers = {'accept': '*/*', 'user-agent': ua.firefox}
        flats = []
        with alive_bar(len(links), title=f'[{reference}] Формирую ссылки...') as bar:
            for count, link in enumerate(links, start=1):
                bar()
                response = requests.get(link, headers=headers)
                html = BeautifulSoup(response.content, 'html.parser')
                title = html.find('div', class_='object-head__name').text.strip()
                try:
                    images = set()
                    for i in html.find('div', class_='col-md-9 left_colmn sm-mb-20').find_all('li'):
                        for img in list(filter(lambda el: el is not None and ('http' in el.attrs['data-src']), i)):
                            images.add(img.attrs['data-src'])
                    images = list(images)
                except Exception as e:
                    images = []
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
                    phone_num=phone_num,
                    images=images
                ))
        return flats
