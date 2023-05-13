import pandas as pd
import os
from constants import DATA_DIR


def get_df(file_):
    df = pd.read_json(file_)

    item_df = df.stack().reset_index(drop=True).to_frame()[0].apply(pd.Series)

    item_df = pd.concat([item_df, item_df.address.apply(pd.Series).add_suffix('_address')], axis=1)
    item_df = pd.concat([item_df, item_df['@type'].apply(pd.Series).add_prefix('type')], axis=1)

    item_df = pd.concat([item_df, item_df.offers.apply(pd.Series).add_suffix('_offers')], axis=1)
    item_df = pd.concat([item_df, item_df.geo.apply(pd.Series).add_suffix('_geo')], axis=1)

    item_df = item_df.drop(
        ['@type', 'address', 'offers', 'geo',
         '0_geo', '@type_geo', 'availability_offers'], axis=1)
    return item_df


def concat_save_csv_data(csv_file):
    raw_data_files = os.listdir(DATA_DIR)
    dataframes = []
    for file_ in raw_data_files:
        dataframes.append(get_df(DATA_DIR + file_))
    # outer - на всяк випадок, якщо з'явиться непередбачувана колонка
    # оголошення можуть повторюватися, оскільки на етапі збору не перевіряю
    # чи є вже це оголошення в даних
    df_all = pd.concat(dataframes, axis=0, join='outer', ignore_index=True).drop_duplicates(ignore_index=True)
    unique_ind = df_all['url'].drop_duplicates().index
    df_all = df_all.iloc[unique_ind].reset_index(drop=True)
    df_all.to_csv(csv_file)
