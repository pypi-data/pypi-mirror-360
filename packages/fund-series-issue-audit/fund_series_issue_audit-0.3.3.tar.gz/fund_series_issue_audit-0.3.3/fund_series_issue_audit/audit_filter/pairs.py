import pandas as pd
from itertools import combinations
from fund_insight_engine import get_fund_codes_main, get_mapping_fund_names_mongodb, get_fund_codes_discretionary


def get_pairs(date_ref=None, option_discretionary_exclude=False):
    fund_codes = get_fund_codes_main(date_ref=date_ref)
    if option_discretionary_exclude:
        fund_codes_discretionary = get_fund_codes_discretionary(date_ref=date_ref)
        fund_codes = set(fund_codes) - set(fund_codes_discretionary)
    pairs = list(combinations(fund_codes,2))
    return pairs

def get_df_pairs(date_ref=None):
    pairs = list(combinations(get_fund_codes_main(date_ref=date_ref),2))
    df = pd.DataFrame([{'fund_code_i': fund_code_i, 'fund_code_j': fund_code_j} for fund_code_i, fund_code_j in pairs])
    MAPPING_FUND_NAMES = get_mapping_fund_names_mongodb(date_ref=date_ref)
    df['fund_name_i'] = df['fund_code_i'].map(MAPPING_FUND_NAMES)
    df['fund_name_j'] = df['fund_code_j'].map(MAPPING_FUND_NAMES)
    return df
