import pandas as pd
from tqdm import tqdm
from shining_pebbles import get_today, get_yesterday, get_date_n_days_ago,open_df_in_file_folder_by_regex
from canonical_transformer import map_dataframe_to_csv_including_korean
from fund_insight_engine import get_mapping_fund_inception_dates_mongodb, get_mapping_fund_names_mongodb
from ..audit_portfolio import PortfolioVector, VectorPair
from ..audit_date import get_pairs_filtered_by_6_months_inception_condition
from ..asset_condition_utils import get_asset_vector_string
from ..path_director import FILE_FOLDER
from fund_series_issue_audit.audit_filter import get_filtered_pairs

def get_inner_products_of_fund_series_issue(date_ref=None):
    data = []
    pairs = get_pairs_filtered_by_6_months_inception_condition()
    for i, j in tqdm(pairs):
        pv_i = PortfolioVector(fund_code=i, date_ref=date_ref)
        pv_j = PortfolioVector(fund_code=j, date_ref=date_ref)
        vp = VectorPair(pv_i, pv_j)
        dct = {'fund_code_i': i, 'fund_code_j': j, 'inner_product': vp.inner_product}
        data.append(dct)
    return data

def save_results_of_fund_series_issue(option_save=True, option_asset_validity=True, date_ref=None):
    date_ref = date_ref if date_ref else get_yesterday()
    inner_products = get_inner_products_of_fund_series_issue(date_ref=date_ref)
    results = pd.DataFrame(inner_products).sort_values(by='inner_product', ascending=False)
    results = results[results['inner_product']<1.0]
    MAPPING_FUND_NAMES = get_mapping_fund_names_mongodb(date_ref=date_ref)
    MAPPING_INCEPTION_DATES = get_mapping_fund_inception_dates_mongodb(date_ref=date_ref)
    results['fund_name_i'] = results['fund_code_i'].map(MAPPING_FUND_NAMES)
    results['fund_name_j'] = results['fund_code_j'].map(MAPPING_FUND_NAMES)
    results['inception_date_i'] = results['fund_code_i'].map(MAPPING_INCEPTION_DATES)
    results['inception_date_j'] = results['fund_code_j'].map(MAPPING_INCEPTION_DATES)
    results['asset_vector_i'] = results['fund_code_i'].apply(lambda x: get_asset_vector_string(fund_code=x))
    results['asset_vector_j'] = results['fund_code_j'].apply(lambda x: get_asset_vector_string(fund_code=x))
    results['asset_validity'] = results['asset_vector_i'] == results['asset_vector_j']
    results['asset_validity'] = results['asset_validity'].apply(lambda x: True if x else False)
    results['inner_product'] = results['inner_product'].apply(lambda x: round(x, 4))
    if option_asset_validity:
        results = results[results['asset_validity']==True].reset_index(drop=True)
    if option_save:
        map_dataframe_to_csv_including_korean(results.reset_index(), file_folder=FILE_FOLDER['result'], file_name=f'dataset-series_issue-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.csv')
    return results

def load_result_series_issue_audit(date_ref=None, option_threshold=True):
    regex = f'dataset-series_issue-at{date_ref.replace("-", "")}' if date_ref else 'dataset-series_issue-at'
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['result'], regex=regex)
    if option_threshold:
        df = df[df['inner_product']>=0.8]
    return df

def extract_pair_fund_codes_of_row_in_df(df, index_row):
    srs = df.iloc[index_row]
    pair = srs['fund_code_i'], srs['fund_code_j']
    return pair
    
def get_vp_of_row_in_df(df, index_row, date_ref=None):
    date_ref = date_ref if date_ref else get_date_n_days_ago(get_yesterday(),1)
    pair_codes = extract_pair_fund_codes_of_row_in_df(df, index_row)
    pv_i = PortfolioVector(fund_code=pair_codes[0], date_ref=date_ref)
    pv_j = PortfolioVector(fund_code=pair_codes[1], date_ref=date_ref)
    vp = VectorPair(pv_i=pv_i, pv_j=pv_j)
    return vp

def get_comparison_of_row_in_df(df, index_row, date_ref=None):
    date_ref = date_ref if date_ref else get_date_n_days_ago(get_yesterday(),1)
    vp = get_vp_of_row_in_df(df, index_row, date_ref=date_ref)
    comparison = vp.comparison
    print(f'Calculated inner product <pv_i|pv_j> == {vp.inner_product}')
    return comparison

def append_inner_products_in_df(df, date_ref=None, option_round=4):
    df = df.copy()
    for idx, row in tqdm(df.iterrows()):
        pv_i = PortfolioVector(fund_code=row['fund_code_i'], date_ref=date_ref)
        pv_j = PortfolioVector(fund_code=row['fund_code_j'], date_ref=date_ref)
        vp = VectorPair(pv_i=pv_i, pv_j=pv_j)
        df.at[idx, 'inner_product'] = round(vp.inner_product, option_round)
    return df

def get_df_filtered_series_issue_audit(date_ref=None, option_round=4, option_concise=False, option_save=True):
    date_ref = date_ref if date_ref else get_yesterday()
    df = get_filtered_pairs(date_ref=date_ref, option_concise=option_concise).copy()
    df = append_inner_products_in_df(df, date_ref=date_ref, option_round=option_round)
    df = df.sort_values(by='inner_product', ascending=False).reset_index(drop=True)
    if option_save:
        map_dataframe_to_csv_including_korean(df.reset_index(drop=True), file_folder=FILE_FOLDER['result'], file_name=f'dataset-series_issue_audit-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.csv')
    return df

def load_series_issue_audit_result(date_ref=None, option_threshold=0.8, option_concise=False):
    regex = f'dataset-series_issue_audit-at{date_ref.replace("-", "")}' if date_ref else 'dataset-series_issue_audit-at'
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['result'], regex=regex)
    df = df.reset_index()
    if option_threshold:
        df = df[df['inner_product']>=option_threshold]
    if option_concise:
        df['fund_i'] = df.apply(lambda row: f"{row['fund_name_i']} ({row['fund_code_i']})", axis=1)
        df['fund_j'] = df.apply(lambda row: f"{row['fund_name_j']} ({row['fund_code_j']})", axis=1)
        df = df.drop(columns=['fund_code_i', 'fund_code_j', 'fund_name_i', 'fund_name_j', 'inception_date_i', 'inception_date_j', 'indivs_i', 'indivs_j', 'totals_i', 'totals_j'])
        COLS_ORDERED = ['fund_i', 'fund_j', 'inner_product', 'delta_days', 'indivs', 'totals']
        df = df[COLS_ORDERED]
    return df

def save_postprocess_result(df, date_ref=None):
    date_ref = date_ref if date_ref else get_yesterday()
    map_dataframe_to_csv_including_korean(df.reset_index(drop=True), file_folder=FILE_FOLDER['result'], file_name=f'dataset-filtered_series_issue_audit-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.csv')