import requests
from bs4 import BeautifulSoup
import json
import os
from constants import *
from data_to_csv import concat_save_csv_data
from preprocess_data import save_table
from fill_missing_data import fillna_district2


def add_full_description(data, full_descriptions):
    for i, item in enumerate(data):
        data[i]['full_description'] = full_descriptions[i].text


def add_subtitle(data, subtitles):
    for i, item in enumerate(data):
        data[i]['subtitle'] = subtitles[i].text


def add_properties(data, properties):
    for i, item in enumerate(data):
        data[i]['properties'] = properties[i].text


def request_data(url_base, pages_num):
    data = {}
    for i in range(1, pages_num + 1):
        url = url_base + f'?page={i}'
        resp = requests.get(url)
        # для коректного відображення кирилиці
        resp.encoding = resp.apparent_encoding
        if not resp.ok:
            print(f'Page #{i} didn`t load')
        if not i % 10:
            print(f'{i}/{pages_num}')
        soup = BeautifulSoup(resp.text, 'lxml')
        page_data = soup.find_all('script', type="application/ld+json")
        # тільки page_data[0] містить потрібну інформацію
        page_data_json = json.loads(page_data[0].text)["itemListElement"]
        # головна інформація, без '@type': 'ListItem', 'position': 1,
        page_data_json = list(map(lambda x: x['item'], page_data_json))
        # необрізаний опис квартири тут
        full_descriptions = soup.find_all('div', class_="realty-preview-description-wrapper")
        add_full_description(page_data_json, full_descriptions)
        # кількість кімнат, поверх, рік, тип будику
        properties = soup.find_all('div', class_="realty-preview-properties")
        add_properties(page_data_json, properties)
        # район
        subtitles = soup.find_all('div', class_="realty-preview-sub-title-wrapper")
        add_subtitle(page_data_json, subtitles)

        data[f'chunk{i}'] = page_data_json
    return data


def save_data(pages=PAGES_NUM):
    num_files = len(os.listdir(DATA_DIR))
    filename = f'{DATA_DIR}{num_files + 1}.json'
    data = request_data(URL_BASE, pages)
    with open(filename, "w") as outfile:
        json.dump(data, outfile)


def get_train_data(add_data=False, pages=PAGES_NUM):
    if add_data:
        save_data(pages)
        concat_save_csv_data(DATA_CSV)
    save_table(DATA_CSV, TRAIN_DATA_CSV)
    fillna_district2(TRAIN_DATA_CSV)


get_train_data()
