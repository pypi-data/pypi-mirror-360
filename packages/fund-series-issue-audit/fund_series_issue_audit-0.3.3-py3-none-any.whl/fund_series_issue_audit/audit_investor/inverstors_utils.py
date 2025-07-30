import re
from pathlib import Path
from typing import List, Optional
import unicodedata
import pandas as pd
from pathlib import Path
from shining_pebbles import get_today


def list_files_including_regex(folder_path: str, regex: Optional[str] = None) -> List[str]:
    """
    List filenames in a folder with optional regex filtering.
    
    Args:
        folder_path: Path to the folder
        regex: Optional regex pattern to filter filenames (supports Korean)
    
    Returns:
        List of matching filenames
    """
    try:
        folder = Path(folder_path)
        
        if not folder.exists():
            raise FileNotFoundError(f"Folder does not exist: {folder_path}")
        
        all_files = [f.name for f in folder.iterdir() if f.is_file()]
        
        if not regex:
            return all_files
        
        # For Korean compatibility, use string contains with normalization
        # instead of regex which has issues with NFD Korean characters
        filtered_files = []
        search_nfc = unicodedata.normalize('NFC', regex)
        search_nfd = unicodedata.normalize('NFD', regex)
        
        for filename in all_files:
            file_nfc = unicodedata.normalize('NFC', filename)
            file_nfd = unicodedata.normalize('NFD', filename)
            
            # Try both string contains and regex matching
            contains_match = (search_nfc in file_nfc or 
                            search_nfc in file_nfd or 
                            search_nfd in file_nfc or 
                            search_nfd in file_nfd)
            
            # Also try regex on normalized strings for advanced patterns
            regex_match = False
            try:
                pattern = re.compile(search_nfc, re.IGNORECASE | re.UNICODE)
                regex_match = (pattern.search(file_nfc) or pattern.search(file_nfd))
            except re.error:
                pass
            
            if contains_match or regex_match:
                filtered_files.append(filename)
        
        return filtered_files
        
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def debug_korean_search(folder_path: str, search_term: str):
    """Debug function to check Korean character encoding issues."""
    import unicodedata
    
    folder = Path(folder_path)
    
    print(f"Searching for: '{search_term}'")
    print(f"Search term bytes: {search_term.encode('utf-8')}")
    print(f"Search term NFC: '{unicodedata.normalize('NFC', search_term)}'")
    print(f"Search term NFD: '{unicodedata.normalize('NFD', search_term)}'")
    print()
    
    for f in folder.iterdir():
        if f.is_file() and '펀드' in f.name:  # Only show Korean files
            filename = f.name
            filename_nfc = unicodedata.normalize('NFC', filename)
            filename_nfd = unicodedata.normalize('NFD', filename)
            search_nfc = unicodedata.normalize('NFC', search_term)
            search_nfd = unicodedata.normalize('NFD', search_term)
            
            print(f"File: '{filename}'")
            print(f"  Original bytes: {filename.encode('utf-8')}")
            print(f"  NFC form: '{filename_nfc}' -> {filename_nfc.encode('utf-8')}")
            print(f"  NFD form: '{filename_nfd}' -> {filename_nfd.encode('utf-8')}")
            print()
            print("  Match tests:")
            print(f"    search_nfc in filename: {search_nfc in filename}")
            print(f"    search_nfd in filename: {search_nfd in filename}")
            print(f"    search_nfc in filename_nfc: {search_nfc in filename_nfc}")
            print(f"    search_nfc in filename_nfd: {search_nfc in filename_nfd}")
            print(f"    search_nfd in filename_nfc: {search_nfd in filename_nfc}")
            print(f"    search_nfd in filename_nfd: {search_nfd in filename_nfd}")
            print()


def load_xlsx(file_path: str, sheet_name=0) -> pd.DataFrame:
    print(f'loading: {file_path.split("/")[-1]}')
    path = Path(file_path)
    df = pd.read_excel(path, sheet_name=sheet_name)
    return df

def preprocess_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    columns = list(df.iloc[0])
    df.columns = columns
    df = df.iloc[1:]
    return df

def extract_date_ref_in_xlsx(file_path: str) -> str:
    df = load_xlsx(file_path)
    df = preprocess_column_names(df)
    date_ref = df['기준일자'].unique()[0]
    return date_ref

def convert_date_as_dashed(date_ref_with_slash: str) -> str:
    return date_ref_with_slash.replace('/', '-')

def get_file_name_format(file_path: str) -> str:
    date_ref_with_slash = extract_date_ref_in_xlsx(file_path)
    date_ref_dashed = convert_date_as_dashed(date_ref_with_slash)
    file_name_format = f'xlsx-number_of_investors-at{date_ref_dashed.replace("-", "")}-save{get_today().replace("-", "")}.xlsx'
    return file_name_format

from pathlib import Path

def rename_file_name_of_investors(file_name_old, file_name_new):
    """Rename file from old name to new name."""
    try:
        old_path = Path(file_name_old)
        new_path = Path(file_name_new)
        
        if not old_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {old_path}")
        
        new_path.parent.mkdir(parents=True, exist_ok=True)
        old_path.rename(new_path)
        
        return True
        
    except Exception as e:
        print(f"Error renaming file: {e}")
        return False
