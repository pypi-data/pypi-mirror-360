import logging
import threading
import time

from chayan import loader
from chayan.loader import Stock, CuratedStocks

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loader = CuratedStocks(refresh_delay_min=0.25)
    loader._logger.setLevel(logging.DEBUG)
    stocks = loader.load_curated_stocks()
    time.sleep(3)
    stocks = loader.load_curated_stocks()

    print('Sleeping for 65 sec ...')
    time.sleep(20)

    stocks = loader.load_curated_stocks()

    time.sleep(3)
    stocks = loader.load_curated_stocks()

    for s in stocks:
        print(s.display_info())
        print('-------\n')