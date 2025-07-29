import datetime
import logging
import os
import shutil
import time

import fcntl
import requests


class NiftyDataDownloader:

    def __init__(self, download_dir: str = "chayan_downloads"):
        self.__logger = logging.getLogger(self.__module__ + '.' + self.__class__.__name__)
        self.download_dir = download_dir


    def reset_download_dir(self):
        """
        Safely resets the NIFTY data download directory.

        Locking Logic:
        - This method ensures that only one process modifies the download directory at a time.
        - It uses a file-based advisory lock (`fcntl.flock`) on a `.dirlock` file located in the download directory.
        - If another process holds the lock, this process will block and wait until the lock is released.
        - The lock is automatically released when the file is closed (at the end of the `with` block) or if the
          process is forcefully terminated (`kill -9`).

        Behavior:
        - Checks if a file named with today’s date (in format `%Y-%m-%d`) exists in the directory.
        - If the file exists, the method does nothing and returns.
        - If the file does not exist, all other files and subdirectories (except the lock file) in the directory are deleted.

        Notes:
        - Designed to be safe with multiple trusted processes on the same machine.
        - Locking is local and advisory — all cooperating processes must use the same lock mechanism.
        """

        os.makedirs(self.download_dir, exist_ok=True)

        lock_path = os.path.join(self.download_dir, ".dirlock")
        pid = os.getpid()
        start_time = time.time()

        self.__logger.info(f"[{datetime.datetime.now()}] PID {pid} attempting to acquire lock...")

        with open(lock_path, "w") as lock_file:
            fcntl.flock(lock_file, fcntl.LOCK_EX)  # Will block if another process has the lock

            elapsed = time.time() - start_time
            self.__logger.info(f"[{datetime.datetime.now()}] PID {pid} acquired lock after {elapsed:.2f} seconds.")

            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            file_path = os.path.join(self.download_dir, today_str)

            if os.path.exists(file_path):
                print(f"[{datetime.datetime.now()}] PID {pid} found today's file ({today_str}) — nothing to do.")
                return False

            self.__logger.info(f"[{datetime.datetime.now()}] PID {pid} clearing download directory...")

            # Delete all contents except the lock file
            for fname in os.listdir(self.download_dir):
                if fname == ".dirlock":
                    continue
                fpath = os.path.join(self.download_dir, fname)
                try:
                    if os.path.isfile(fpath) or os.path.islink(fpath):
                        os.unlink(fpath)
                    elif os.path.isdir(fpath):
                        shutil.rmtree(fpath)
                except Exception as e:
                    self.__logger.error(f"[{datetime.datetime.now()}] PID {pid} failed to delete {fpath}: {e}")

            self.__logger.info(f"[{datetime.datetime.now()}] PID {pid} finished cleanup and will release lock.")
            return True


    def download_content(self, failed_file='failed.txt') -> None:
        if not self.reset_download_dir():
            return

        urls = []

        # NSE Indices to fetch. All stocks in the following indices will be fetched and returned. (around 300)
        names = [
            '100',
            'midcap100',
            'smallcap100',
            'auto',
            'bank',
            'fmcg',
            'it',
            'media',
            'metal',
            'pharma',
            'realty',
            'consumerdurables',
            'oilgas',
            'pse',
            'indiadefence_'
        ]

        for n in names:
            urls.append(f"https://nsearchives.nseindia.com/content/indices/ind_nifty{n}list.csv")

        HEADERS = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1"
        }
        # Create the output directory if it does not exist
        os.makedirs(self.download_dir, exist_ok=True)

        # Open the failed file in write mode
        with open(failed_file, 'w') as failed:
            for url in urls:
                try:
                    self.__logger.info('Processing: ' + url)
                    response = requests.get(url, headers=HEADERS)
                    response.raise_for_status()  # Raise an HTTPError for bad responses

                    # Extract the filename from the URL
                    filename = os.path.join(self.download_dir, url.split('/')[-1])

                    # Save the content to a file
                    with open(filename, 'wb') as file:
                        file.write(response.content)
                    self.__logger.info(f"Downloaded {url} to {filename}")

                except requests.RequestException as e:
                    # Write the failed URL to the failed file
                    failed.write(url + '\n')
                    self.__logger.info(f"Failed to download {url}: {e}")

        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(self.download_dir, today_str)

        with open(file_path, 'w') as f:
            f.write('')  # create empty file

