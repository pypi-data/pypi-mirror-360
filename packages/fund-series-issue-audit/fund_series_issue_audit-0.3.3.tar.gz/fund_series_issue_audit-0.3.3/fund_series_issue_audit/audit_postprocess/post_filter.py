from fund_insight_engine import get_fund_codes_discretionary
from fund_series_issue_audit.audit_result.result_utils import get_vp_of_row_in_df

def determine_different_holdings(vp, option_distinct_holdings=7):
    comp = vp.comparison
    contras = len(comp[comp['delta']=='-'])
    if contras >= option_distinct_holdings:
        return True
    else:
        return False

def filter_different_holdings_funds(df, option_distinct_holdings=7):
    df = df.copy()
    len_ref = len(df)
    for idx, row in df.iterrows():
        vp = get_vp_of_row_in_df(df, idx)
        df.at[idx, 'different_holdings'] = determine_different_holdings(vp, option_distinct_holdings=option_distinct_holdings)
    df = df[df['different_holdings']==False].drop(columns=['different_holdings'])
    len_filtered = len(df)
    print(f'🗑️ filter_different_holdings: {len_ref} -> {len_filtered}')
    return df.reset_index(drop=True)

def filter_discretionary_funds(df, date_ref=None):
    df = df.copy()
    len_ref = len(df)
    fund_codes_discretionary = get_fund_codes_discretionary(date_ref=date_ref)
    df = df[(~df['fund_code_i'].isin(fund_codes_discretionary)) & (~df['fund_code_j'].isin(fund_codes_discretionary))]
    len_filtered = len(df)
    print(f'🗑️ filter_discretionary: {len_ref} -> {len_filtered}')
    return df.reset_index(drop=True)

def determine_overlap_assets(vp, option_assets_overlap=0):
    assets_i = vp.pv_i.assets
    assets_j = vp.pv_j.assets
    distinct = assets_i.symmetric_difference(assets_j)
    if len(distinct) > option_assets_overlap:
        return True
    else:
        return False

def filter_heterogeneous_funds(df, option_assets_overlap=0):
    df = df.copy()
    len_ref = len(df)
    for idx, row in df.iterrows():
        vp = get_vp_of_row_in_df(df, idx)
        overlap = determine_overlap_assets(vp, option_assets_overlap=option_assets_overlap)
        if overlap:
            df.at[idx, 'heterogeneity'] = True
        else:
            df.at[idx, 'heterogeneity'] = False
    df = df[df['heterogeneity']==False].drop(columns=['heterogeneity'])
    len_filtered = len(df)
    print(f'🗑️ filter_heterogeneous: {len_ref} -> {len_filtered}')
    return df.reset_index(drop=True)