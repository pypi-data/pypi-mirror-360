from fund_series_issue_audit.audit_investor import get_mapping_indivs, get_mapping_totals

def filter_investors(df_pairs, date_ref=None, option_concise=True):
    df = df_pairs.copy()
    MAPPING_INDIVS = get_mapping_indivs(date_ref=date_ref, option_verbose=True)
    MAPPING_TOTALS = get_mapping_totals(date_ref=date_ref)
    df['indivs_i'] = df['fund_code_i'].map(MAPPING_INDIVS)
    df['totals_i'] = df['fund_code_i'].map(MAPPING_TOTALS)
    df['indivs_j'] = df['fund_code_j'].map(MAPPING_INDIVS)
    df['totals_j'] = df['fund_code_j'].map(MAPPING_TOTALS)
    df['indivs'] = df['indivs_i']+df['indivs_j']
    df['totals'] = df['totals_i']+df['totals_j']
    if option_concise:
        df = df.drop(columns=['indivs_i', 'totals_i', 'indivs_j', 'totals_j'])
    return df