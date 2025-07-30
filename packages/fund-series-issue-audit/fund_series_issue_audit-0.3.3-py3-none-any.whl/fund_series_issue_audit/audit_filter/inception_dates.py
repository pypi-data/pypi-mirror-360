import pandas as pd
from fund_insight_engine import get_mapping_fund_inception_dates_mongodb

def filter_6_months(df_pairs, date_ref=None, option_concise=False):
    df = df_pairs.copy()
    MAPPING_ICEPTION_DATES = get_mapping_fund_inception_dates_mongodb(date_ref=date_ref)
    df['inception_date_i'] = df['fund_code_i'].map(MAPPING_ICEPTION_DATES)
    df['inception_date_j'] = df['fund_code_j'].map(MAPPING_ICEPTION_DATES)
    df['delta_days'] = abs((pd.to_datetime(df['inception_date_i']) - pd.to_datetime(df['inception_date_j'])).dt.days)
    df = df.sort_values(by='delta_days').reset_index(drop=True)
    DAYS_6_MONTHS = 185
    df = df[df['delta_days']<=DAYS_6_MONTHS]
    if option_concise:
        df = df.drop(columns=['inception_date_i', 'inception_date_j'])
    return df