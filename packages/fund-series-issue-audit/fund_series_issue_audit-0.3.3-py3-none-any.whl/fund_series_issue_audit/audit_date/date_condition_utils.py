import pandas as pd
from datetime import datetime
from ..pseudo_consts import MAPPING_INCEPTION_DATES, FUND_CODES_MAIN

def transform_mapping_datetime_inception_dates():
    filtered_inception_dates = {code: date_str for code, date_str in MAPPING_INCEPTION_DATES.items() 
                                if code in FUND_CODES_MAIN}
    data_datetime = {code: datetime.strptime(date_str, '%Y-%m-%d') for code, date_str in filtered_inception_dates.items()}
    
    return data_datetime

def generate_datetime_difference_matrix():
    data_datetime = transform_mapping_datetime_inception_dates()
    codes = list(data_datetime.keys())
    datetime_matrix = pd.DataFrame(index=codes, columns=codes)
    for row_code in codes:
        for col_code in codes:
            date_diff = abs((data_datetime[row_code] - data_datetime[col_code]).days)
            datetime_matrix.loc[row_code, col_code] = date_diff
    return datetime_matrix

MATRIX_DATE_DIFFERENCE = generate_datetime_difference_matrix()

def get_df_boolean(df, threshold=180):
    df_boolean = df <= threshold
    return df_boolean

def get_pairs_true_positions(df):
    return [(i, j) for i, j in df.stack()[df.stack() == True].index]

def remove_permutation_duplicates(pairs):
    return list({tuple(sorted(pair)) for pair in pairs})

def remove_self_pairs(pairs):
    return [pair for pair in pairs if pair[0] != pair[1]]

def get_valid_pairs(pairs):
    return remove_permutation_duplicates(remove_self_pairs(pairs))

def get_pairs_filtered_by_6_months_inception_condition(df=MATRIX_DATE_DIFFERENCE):
    df_boolean = get_df_boolean(df)
    pairs = get_pairs_true_positions(df_boolean)
    pairs = remove_self_pairs(pairs)
    return remove_permutation_duplicates(pairs)