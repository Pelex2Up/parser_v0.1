import traceback
import requests
from alive_progress import alive_bar
from bs4 import BeautifulSoup
from data import Flat
import re
from datetime import datetime
from fake_useragent import UserAgent
from default_parser import DefaultParser


class RealtParser(DefaultParser):

    def get_parser_name(self):
        return 'REALT'

    def get_links(self, page_from=0, page_to=1):
        reference = self.get_parser_name()
        ua = UserAgent()
        headers = {'accept': '*/*', 'user-agent': ua.firefox}
        flat_links = []
        with alive_bar(page_to - page_from + 1, title=f'[{reference}] Анализирую страницы...') as bar:
            while page_from <= page_to:
                bar()
                resp = requests.get(f'https://realt.by/sale/flats/?page={page_from}', headers=headers)
                html = BeautifulSoup(resp.content, 'html.parser')
                for a in html.find_all('a', href=True, class_='teaser-title'):
                    flat_links.append(a['href'])
                page_from += 1
            ready_links = list(filter(lambda el: 'object' in el, flat_links))
            return ready_links

    def get_info_from_links(self, links, reference=None):
        reference = self.get_parser_name()
        ua = UserAgent()
        headers = {'accept': '*/*', 'user-agent': ua.firefox}
        flats = []
        with alive_bar(len(links), title=f'[{reference}] Формирую ссылки...') as bar:
            for counter, link in enumerate(links, start=1):
                bar()
                resp = requests.get(link, headers=headers)
                html = BeautifulSoup(resp.content, 'html.parser')
                title = html.find('h1', class_='order-1').text.strip()
                raw_price = html.find('h2', class_='w-full sm:w-auto sm:inline-block sm:mr-1.5 lg:text-h2Lg text-h2 '
                                                   'font-raleway font-bold flex items-center')
                if raw_price is not None:
                    price = int(re.sub('[^0-9]', '', raw_price.text.strip()))
                else:
                    price = 0
                try:
                    images = set()
                    image_divs = html.find_all("div", {"class": "swiper-slide"})
                    for img_div in image_divs:
                        for img in list(filter(lambda el: el is not None and (el[:4] == 'http' and 'user' in el),
                                               map(lambda el2: el2['src'], img_div.findAll("img")))):
                            images.add(img)
                    images = list(images)
                except Exception as e:
                    traceback.print_exc()
                    images = []
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
                    phone_num=phone_num,
                    images=images
                ))
        return flats
