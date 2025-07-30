from shining_pebbles import get_yesterday, get_today, open_df_in_file_folder_by_regex
from canonical_transformer import map_df_to_csv_including_korean
from ..audit_result import save_results_of_fund_series_issue
from ..audit_investor import get_mapping_indivs, get_mapping_totals
from ..path_director import FILE_FOLDER
from .result_utils import get_comparison_of_row_in_df

def save_automated_series_issue_audit(date_ref=None, option_save=True, option_threshold=0.8):
    date_ref = date_ref if date_ref else get_yesterday()
    audit = save_results_of_fund_series_issue(date_ref=date_ref)
    MAPPING_INDIVS = get_mapping_indivs(date_ref=date_ref)
    MAPPING_TOTALS = get_mapping_totals(date_ref=date_ref)
    audit['indivs_i'] = audit['fund_code_i'].map(MAPPING_INDIVS)
    audit['totals_i'] = audit['fund_code_i'].map(MAPPING_TOTALS)
    audit['indivs_j'] = audit['fund_code_j'].map(MAPPING_INDIVS)
    audit['totals_j'] = audit['fund_code_j'].map(MAPPING_TOTALS)
    audit['indivs'] = audit['indivs_i']+audit['indivs_j']
    audit['totals'] = audit['totals_i']+audit['totals_j']
    if option_threshold:
        audit = audit[audit['inner_product']>=option_threshold]
    final_result = audit.sort_values(by='totals', ascending=False)
    COLS_TO_KEEP = ['fund_code_i', 'fund_code_j', 'inner_product', 'fund_name_i',
       'fund_name_j', 'inception_date_i', 'inception_date_j', 'asset_validity', 'indivs_i', 'totals_i', 'indivs_j',
       'totals_j', 'indivs', 'totals']
    final_result = final_result[COLS_TO_KEEP]
    if option_save:
        map_df_to_csv_including_korean(df=final_result, file_folder=FILE_FOLDER['result'], file_name=f'dataset-result_automated_series_issue_audit-at{date_ref.replace("-","")}-save{get_today().replace("-","")}.csv')
    return final_result

def load_automated_series_issue_audit_result(date_ref=None, option_threshold=0.8):
    regex = f'dataset-result_automated_series_issue_audit-at{date_ref.replace("-", "")}' if date_ref else 'dataset-result_automated_series_issue_audit-at'
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['result'], regex=regex)
    df = df.reset_index()
    if option_threshold:
        df = df[df['inner_product']>=option_threshold]
    return df

def show_comparison(index, date_ref=None):
    df = load_automated_series_issue_audit_result(date_ref=date_ref)
    comparison = get_comparison_of_row_in_df(df, index, date_ref=date_ref)
    return comparison