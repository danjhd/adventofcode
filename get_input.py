#!/usr/bin/env python3
""" This script downloads a specified advent of code input file.
    It defaults to the current day/year but parameters can be used to define a specific day or year (or both). """

import argparse
import logging
import os
import sqlite3
from datetime import date

import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')

def get_cookies_firefox():
    """ Get the advent of code cookies from Firefox """
    profiles_dir = os.path.join(os.path.expanduser('~'), 'AppData/Roaming/Mozilla/Firefox/Profiles')
    db_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(profiles_dir) for f in filenames if f == 'cookies.sqlite']
    for db_file in db_files:
        logging.info('Reading sqlite db from: %s...', db_file)
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()
        try:
            rows = cursor.execute('SELECT name, value FROM moz_cookies WHERE host = ".adventofcode.com"').fetchall()
            logging.info('Cookies found...')
            return rows
        except sqlite3.OperationalError:
            logging.warning('Cookies not found...')
    return []

def download_input(year: int, day: int):
    """ download the input file """
    cookies = get_cookies_firefox()
    if not cookies:
        logging.warning('No Cookies found. Will attempt request without cookies...')
    headers = {'Cookie': '; '.join([f'{c[0]}={c[1]}' for c in cookies])}
    req = requests.get(f'https://adventofcode.com/{year}/day/{day}/input', headers=headers, timeout=30)
    if req.status_code != 200:
        logging.error('Unable to download input... %s', req.content.decode('utf-8'))
        return
    input_file = f'./{year}/day{day:02}/input'
    os.makedirs(os.path.dirname(input_file), exist_ok=True)
    logging.info('Writing file to: %s...', input_file)
    open(input_file, 'wb').write(req.content)
    return input_file

def main(params):
    """ Download the inout for a specific day of advent of code """
    download_input(params.year, params.day)

if __name__ == '__main__':
    today = date.today()
    parser = argparse.ArgumentParser(description='This script downloads the puzzle input for Advent of Code.')
    parser.add_argument('-y', '--year', default=today.year, help='defaults to current year')
    parser.add_argument('-d', '--day', default=today.day, help='defaults to current day')
    args = parser.parse_args()
    main(args)
