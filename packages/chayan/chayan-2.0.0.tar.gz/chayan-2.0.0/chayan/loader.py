import csv
import os
import typing

from chayan.nifty_data import NiftyDataDownloader
import logging, sys

class Stock:
    def __init__(self, nse_symbol, isin, bse_id, name, sector, index=None):
        self.nse_symbol = nse_symbol
        self.isin = isin
        self.bse_id = bse_id
        self.name = name
        self.sector = sector
        self.index = index

    def __repr__(self):
        return (f"Stock(nse_symbol='{self.nse_symbol}', isin='{self.isin}', "
                f"name='{self.name}', sector='{self.sector}', index='{self.index}', "
                f"bse_id='{self.bse_id}')")

    def __eq__(self, other):
        return isinstance(other, Stock) and self.nse_symbol == other.nse_symbol

    def __lt__(self, other):
        return self.nse_symbol < other.nse_symbol

    def __hash__(self):
        return hash(self.nse_symbol)

    def display_info(self):
        return (f"Stock Information:\n"
                  f"Name: {self.name}\n"
                  f"NSE Symbol: {self.nse_symbol}\n"
                  f"ISIN: {self.isin}\n"
                  f"Sector: {self.sector}\n"
                  f"Index: {self.index}\n"
                  f"BSE ID: {self.bse_id}"
                  )


class CuratedStocks:

    def __init__(self):
        self.nifty_data_downloader = NiftyDataDownloader()
        self.curated_stocks = None

    def load_curated_stocks(self) -> typing.List[Stock]:
        self.nifty_data_downloader.download_content()

        # Return cached data if ready
        if self.curated_stocks is not None:
            return self.curated_stocks

        curated_stocks = set()
        # Iterate over all CSV files in the specified folder
        for filename in os.listdir(self.nifty_data_downloader.download_dir):
            index_name = filename.replace('ind_nifty', '').replace('list.csv', '').replace('_', '')
            if filename.endswith('.csv'):
                filepath = os.path.join(self.nifty_data_downloader.download_dir, filename)

                # Read the CSV file
                with open(filepath, 'r') as file:
                    reader = csv.DictReader(file)
                    # Process each row in the file
                    for row in reader:
                        curated_stocks.add(Stock(nse_symbol=row['Symbol'],
                                                 isin=row['ISIN Code'],
                                                 bse_id=None,
                                                 name=row['Company Name'],
                                                 sector=row['Industry'],
                                                 index=index_name))
        self.curated_stocks = sorted(curated_stocks)
        return self.curated_stocks

# if __name__ == "__main__":
#     logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(asctime)s] %(message)s')
#     for s in CuratedStocks().load_curated_stocks():
#         print(s)
