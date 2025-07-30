from fund_series_issue_audit import PortfolioVector
from fund_insight_engine.s3_retriever import get_mapping_fund_names_of_division_01
from fund_insight_engine import get_mapping_fund_names
from shining_pebbles import get_yesterday, get_today, get_date_n_days_ago
from tqdm import tqdm
import pandas as pd

def fetch_portfolio_listed(fund_code, date_ref=None):
    date_ref = date_ref if date_ref else get_yesterday()
    pv = PortfolioVector(fund_code=fund_code, date_ref=date_ref)
    raw = pv.get_raw_portfolio()
    df = raw[raw['종목정보: 자산분류'].str.contains('거래소상장_주식|코스닥상장_주식')]
    COLS_TO_KEEP = ['종목', '종목명', '원화 보유정보: 수량','원화 보유정보: 평가액', '원화 보유정보: 취득액', '원화 보유정보: 평가손익']
    df = df[COLS_TO_KEEP]
    return df

def fetch_portfolio_division_01(date_ref=None):
    date_ref = date_ref if date_ref else get_yesterday()
    dfs = []
    mapping_division_01 = get_mapping_fund_names_of_division_01()
    for fund_code, fund_name in tqdm(mapping_division_01.items()):
        print(fund_code, fund_name)
        try:
            df = fetch_portfolio_listed(fund_code=fund_code, date_ref=date_ref)
            dfs.append(df)
        except Exception as e:
            print(f'PortfolioVector error: {e}')
    portfolio_division_01 = pd.concat(dfs, axis=0)
    portfolio_division_01 = portfolio_division_01.groupby('종목').agg({'종목명': 'first', '원화 보유정보: 수량': 'sum', '원화 보유정보: 평가액': 'sum', '원화 보유정보: 취득액': 'sum', '원화 보유정보: 평가손익': 'sum'})
    portfolio_division_01['손익률'] = (portfolio_division_01['원화 보유정보: 평가액'] / portfolio_division_01['원화 보유정보: 취득액'] -1) * 100
    return portfolio_division_01
def search_equity_info_including_keyword(df, keyword):
    return df[df['종목명'].str.contains(keyword)]

def get_specific_equity_info_in_funds(keyword, date_ref=None, option_concise=True):
    date_ref = date_ref if date_ref else get_yesterday()
    mapping_names = get_mapping_fund_names()
    dfs = []
    for fund_code, fund_name in mapping_names.items(): 
        try:
            pv = PortfolioVector(fund_code=fund_code, date_ref=date_ref)
            raw = pv.get_raw_portfolio()
            raw['펀드코드'] = fund_code
            raw['펀드명'] = fund_name
            columns = ['펀드코드', '펀드명'] + [col for col in raw.columns if col not in ['펀드코드', '펀드명']]
            raw = raw[columns].set_index('펀드코드')
            df = search_equity_info_including_keyword(df=raw, keyword=keyword)
            if not df.empty:
                dfs.append(df)
        except Exception as e:
            pass
            # print(e)
    result = pd.concat(dfs, axis=0)
    if option_concise:
        COLS_TO_KEEP = ['펀드명', '종목', '종목명', '원화 보유정보: 수량','원화 보유정보: 평가액', '원화 보유정보: 취득액', '원화 보유정보: 평가손익', '원화 보유정보: 손익률']
        result = result[COLS_TO_KEEP]
    return result

def get_df_delta_shares_between_dates(keyword, date_i, date_f):
    today = get_specific_equity_info_in_funds(keyword=keyword, date_ref=date_f)
    yesterday = get_specific_equity_info_in_funds(keyword=keyword, date_ref=date_i)
    COLS_TO_MERGE = ['펀드명', '종목명', '원화 보유정보: 수량']
    COLS_TOBE_MERGED = ['원화 보유정보: 수량']
    df_delta = today[COLS_TO_MERGE].merge(yesterday[COLS_TOBE_MERGED], how='outer', left_index=True, right_index=True, suffixes=(f'({date_f})', f'({date_i})'))
    df_delta['수량변화'] = df_delta.iloc[:, -2] - df_delta.iloc[:, -1]
    print(f'inputs: keyword={keyword}, dates=({date_i}, {date_f})')
    return df_delta

def show_delta_shares(keyword, date_ref=None):
    date_f = date_ref if date_ref else get_yesterday()
    date_i = get_date_n_days_ago(date_f, 1)
    df_delta = get_df_delta_shares_between_dates(keyword, date_i, date_f)
    return df_delta