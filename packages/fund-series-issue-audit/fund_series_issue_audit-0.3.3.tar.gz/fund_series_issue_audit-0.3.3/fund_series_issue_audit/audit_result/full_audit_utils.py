import pandas as pd
from itertools import combinations
from tqdm import tqdm
from canonical_transformer import map_df_to_csv_including_korean
from shining_pebbles import open_df_in_file_folder_by_regex, get_today
from fund_insight_engine import get_fund_codes_main, get_mapping_fund_names_mongodb, get_mapping_fund_inception_dates_mongodb
from fund_series_issue_audit.audit_portfolio import PortfolioVector, VectorPair
from ..path_director import FILE_FOLDER

def get_data_of_pair(i, j, date_ref=None):
    pv_i = PortfolioVector(fund_code=i, date_ref=date_ref)
    pv_j = PortfolioVector(fund_code=j, date_ref=date_ref)
    vp = VectorPair(pv_i, pv_j)
    data = {'fund_code_i': i, 'fund_code_j': j, 'inner_product': vp.inner_product}
    return data

def generate_full_audit(date_ref=None, option_save=True):
    FUND_CODES_MAIN = get_fund_codes_main(date_ref=date_ref)
    PAIRS = list(combinations(FUND_CODES_MAIN, 2))
    data = [get_data_of_pair(i,j, date_ref=date_ref) for i, j in tqdm(PAIRS)]
    df = pd.DataFrame(data)
    df['fund_name_i'] = df['fund_code_i'].map(get_mapping_fund_names_mongodb(date_ref=date_ref))
    df['fund_name_j'] = df['fund_code_j'].map(get_mapping_fund_names_mongodb(date_ref=date_ref))
    df['inception_date_i'] = df['fund_code_i'].map(get_mapping_fund_inception_dates_mongodb(date_ref=date_ref))
    df['inception_date_j'] = df['fund_code_j'].map(get_mapping_fund_inception_dates_mongodb(date_ref=date_ref))
    df['inner_product'] = df['inner_product'].apply(lambda x: round(x, 4))
    df = df.sort_values(by='inner_product', ascending=False)
    COLS_ORDERED = ['fund_code_i', 'fund_code_j', 'fund_name_i', 'fund_name_j', 'inception_date_i', 'inception_date_j', 'inner_product']
    df = df[COLS_ORDERED]
    df = df.reset_index(drop=True)
    if option_save:
        map_df_to_csv_including_korean(df=df, file_folder=FILE_FOLDER['result'], file_name=f'dataset-full_audit-at{date_ref.replace("-","")}-save{get_today().replace("-","")}.csv', include_index=True)
    return df

def load_full_audit(date_ref=None, option_threshold=None):
    regex = f'dataset-full_audit-at{date_ref.replace("-", "")}' if date_ref else 'dataset-full_audit-at'
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['result'], regex=regex)
    if option_threshold:
        df = df[df['inner_product'] >= option_threshold]
    return df
