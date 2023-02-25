import realt_parser as realt
import domovita_parser as domovita
from threading import Thread


if __name__ == '__main__':
    th1 = Thread(target=domovita.get_started, args=(1, 3))
    th2 = Thread(target=realt.get_last_flats, args=(1,))
    th1.start()
    th2.start()
