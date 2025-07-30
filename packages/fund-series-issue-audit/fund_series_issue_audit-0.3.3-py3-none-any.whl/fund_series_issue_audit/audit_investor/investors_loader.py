from ..path_director import FILE_FOLDER
from ..pseudo_consts import MAPPING_FUND_NAMES
from shining_pebbles import load_xlsx_in_file_folder_by_regex, get_today, open_df_in_file_folder_by_regex, scan_files_including_regex
from canonical_transformer import get_inverse_mapping, map_df_to_csv, get_inverse_mapping, get_mapping_of_column_pairs
from string_date_controller import get_date_n_days_after

def get_inverse_mapping_fund_names():
    return get_inverse_mapping(MAPPING_FUND_NAMES)

def load_raw_investors(date_ref=None):
    file_folder = FILE_FOLDER['investor']
    regex = f'number_of_investors-at{date_ref.replace("-","")}.*.xlsx' if date_ref else f'number_of_investors.*.xlsx'
    df = load_xlsx_in_file_folder_by_regex(file_folder=file_folder, regex=regex)
    return df

def preprocess_df_investors(df):
    cols_in_row0 = list(df.iloc[0])
    df.columns = cols_in_row0
    df = df.drop(0, axis=0)
    cols_to_keep = ['펀드명', '개인', '법인']
    df = df[cols_to_keep]
    return df

def get_preprocessed_df_investors(date_ref=None):
    raw = load_raw_investors(date_ref=date_ref)
    df = preprocess_df_investors(raw)
    return df

def preprocess_level2_df_investors(df):
    inverse_mapping_fund_names = get_inverse_mapping_fund_names()
    df['fund_code'] = df['펀드명'].map(inverse_mapping_fund_names)
    df['fund_name'] = df['펀드명']
    df['num_of_individual'] = df['개인'].apply(lambda x: int(x) if x!='-' else 0)
    df['num_of_corporation'] = df['법인'].apply(lambda x: int(x) if x!='-' else 0)
    df['num_total'] = df['num_of_individual'] + df['num_of_corporation']
    cols_to_keep = ['fund_code', 'fund_name', 'num_of_individual', 'num_of_corporation', 'num_total']
    df = df[cols_to_keep]
    return df

def load_investors(date_ref=None):
    df = get_preprocessed_df_investors(date_ref=date_ref)
    df = preprocess_level2_df_investors(df)
    return df

def filter_fund_name(fund_name):
    return (
        fund_name
        .split(' Class')[0]
        .split(' 1종')[0]
        .split(' 2종')[0]
        .split(' 3종')[0]
        .split(' 제1종')[0]
        .split(' 제2종')[0]
        .replace(' ', '')
    )

def preprocess_df_number_of_investors(df):
    inverse_mapping_fund_names = get_inverse_mapping_fund_names()
    inverse_mapping_fund_names_2 = {k.replace(' ', ''): v for k,v in inverse_mapping_fund_names.items()}
    df['fund_name_representative'] = df['fund_name'].map(filter_fund_name)
    df['fund_code_representative'] = df['fund_name_representative'].map(inverse_mapping_fund_names_2)
    cols_to_keep = ['fund_code_representative', 'num_of_individual', 'num_total']
    return df[cols_to_keep].groupby('fund_code_representative').sum()

def save_preprocessed_df_number_of_investors(date_ref=None, option_save=True):
    df = load_investors(date_ref=date_ref)
    df = preprocess_df_number_of_investors(df)
    df.index.name = 'fund_code'
    if option_save:
        map_df_to_csv(df=df.reset_index(), file_folder=FILE_FOLDER['investor'], file_name=f'dataset-number_of_investors-at{get_today().replace("-","")}-save{get_today().replace("-","")}.csv')
    return df

def extract_infimum_date(date_ref=None, option_verbose=False):
    file_folder = FILE_FOLDER['investor']
    regex = 'dataset-number_of_investors-at'
    file_names = scan_files_including_regex(file_folder=file_folder, regex=regex)
    dates_existing = [file_name.split('-at')[1].split('-save')[0] for file_name in file_names]
    date_latest = sorted([date for date in dates_existing if date <= get_date_n_days_after(date_ref, 1).replace("-","")])[-1] if date_ref else sorted(dates_existing)[-1]
    if option_verbose:
        print(f'infimum date in investors database: {date_latest[:4]}-{date_latest[4:6]}-{date_latest[6:]}')
    return date_latest

def load_number_of_investors(date_ref=None, option_verbose=False):
    date_ref = extract_infimum_date(date_ref=date_ref, option_verbose=option_verbose)
    file_folder = FILE_FOLDER['investor']
    regex = f'dataset-number_of_investors-at{date_ref.replace("-","")}'
    df = open_df_in_file_folder_by_regex(file_folder=file_folder, regex=regex)
    return df

def get_mapping_indivs(date_ref=None, option_verbose=False):
    nums = load_number_of_investors(date_ref=date_ref, option_verbose=option_verbose).reset_index()
    return get_mapping_of_column_pairs(nums, key_col='fund_code', value_col='num_of_individual')

def get_mapping_totals(date_ref=None, option_verbose=False):
    nums = load_number_of_investors(date_ref=date_ref, option_verbose=option_verbose).reset_index()
    return get_mapping_of_column_pairs(nums, key_col='fund_code', value_col='num_total')
