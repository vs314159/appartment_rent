import pandas as pd


def fillna_district2(train_data):
    df = pd.read_csv(train_data, index_col=0)
    d_df = df[['district', 'district2']].drop_duplicates().dropna()
    # деякі мікрорайони відносять до 2-3 районів, тому для однозначності
    # лишаю лише перший в списку
    district_dict = d_df.groupby(['district'])['district2'].apply(list).apply(lambda x: x[0])
    df.loc[df['district2'].isna(), 'district2'] = df.loc[df['district2'].isna(), 'district2'].map(district_dict)
    df.to_csv(train_data)
