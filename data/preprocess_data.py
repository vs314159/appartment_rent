import pandas as pd
import requests
import re
from constants import WALLS_TYPES


def extract_properties(row):
    # кількість кімнат вже є і повністю збігається
    row = re.sub('[0-9]+ кімната*и*', '', row)
    meterage, ap_info = row.split('м²')
    meterage = meterage.split('/')
    # для коректного розділення на поверхи і рік потрібно двічі відзеркалити рядок
    # на випадок, коли рік чи кількість поверху будику не вказані
    floor_year = [i[::-1] for i in re.findall('[0-9]{1,4}', ap_info[::-1])][::-1]
    # прибираю рік
    ap_info = re.sub('[0-9]{4}', '', ap_info)
    other = re.sub('[0-9]* з? [0-9]*', '', ap_info.split('поверх')[1]).strip()
    build_type = [re.sub(p, '', other) for p in WALLS_TYPES if p in other]
    wall_type = sum([re.findall(p, other) for p in WALLS_TYPES if p in other], [])
    return {
            'appartment_metrage': meterage[0],
            'kitchen_metrage': meterage[1] if len(meterage) > 1 else None,
            'bathroom_metrage': meterage[2] if len(meterage) > 2 else None,
            'floor': floor_year[0],
            'floor_all': floor_year[1] if len(floor_year) > 1 and len(floor_year[1]) <= 2 else None,
            'year_built': floor_year[-1] if len(floor_year) > 1 and len(floor_year[-1]) == 4 else None,
            'build_type': build_type[0] if build_type else None,
            'wall_type': wall_type[0] if wall_type else None,
            }


def extract_address(row):
    info_lst = row.split(', ')
    res = {'build_numb': None,
           'street': None,
           'district': None,
           'district2': None,
           'city': info_lst[-1],
           }
    for i in info_lst[:-1]:
        i = str(i)
        if i[0].isdigit():
            res['build_numb'] = i
        elif '.' in i:
            res['street'] = i
        elif i.endswith('ий'):
            res['district2'] = i
        else:
            res['district'] = i
    return res


def get_price_uah(curr_, date_):
    if curr_ == 'UAH':
        return 1
    url_ = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange'
    curr = '?valcode=' + curr_
    date = '&date=' + date_
    json = '&json'
    url = url_ + curr + date + json
    resp = requests.get(url)
    if resp.ok:
        data = resp.json()
        if isinstance(data, dict):
            return data['rate']
        elif isinstance(data, list):
            return data[0]['rate']
    else:
        print('request failed')


def preprocess_data(csv_file):
    df = pd.read_csv(csv_file, index_col=0)
    propert_df = pd.DataFrame.from_records(df['properties'].apply(extract_properties))
    df = pd.concat([df.drop('properties', axis=1), propert_df], axis=1)
    address = df.name_address.apply(extract_address).apply(pd.Series)
    # full_description вимагає окремої уваги, тому з ним попрацюю пізніше
    df.loc[:, 'date'] = pd.to_datetime(df.availabilityStarts_offers).dt.strftime('%Y%m%d')
    df.loc[:, 'convert_to_uah'] = df[['priceCurrency_offers', 'date']].T.apply(lambda x: get_price_uah(x[0], x[1])).T
    return pd.concat([df.drop(['name_address', 'date'], axis=1), address], axis=1)


def save_table(input_csv, output_csv):
    preprocess_data(input_csv).to_csv(output_csv)

