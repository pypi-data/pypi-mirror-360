from financial_dataset_preprocessor import get_preprocessed_funds_by_fund_class, get_preprocessed_funds_main
from .general_utils import get_fund_codes_from_df, get_mapping_fund_names_filtered_by_fund_codes
from functools import partial
from typing import Callable, Optional, List, Dict


def get_fund_codes_by_fund_class(fund_class: str, date_ref: Optional[str] = None) -> List[str]:
    df = get_preprocessed_funds_by_fund_class(fund_class=fund_class, date_ref=date_ref)
    return get_fund_codes_from_df(df)

def get_mapping_fund_names_by_fund_class(fund_class: str, date_ref: Optional[str] = None) -> Dict[str, str]:
    fund_codes = get_fund_codes_by_fund_class(fund_class=fund_class, date_ref=date_ref)
    return get_mapping_fund_names_filtered_by_fund_codes(fund_codes=fund_codes, date_ref=date_ref)

MAPPING_FUND_CLASSES = {
   'mother': '운용펀드',
   'general': '일반',
   'class': '클래스펀드',
   'nonclassified': '-'
}

def create_fund_class_getter(fund_class_key: str) -> Callable[[Optional[str]], List[str]]:
    return partial(get_fund_codes_by_fund_class, fund_class=MAPPING_FUND_CLASSES[fund_class_key])

def create_fund_name_mapping_getter(fund_class_key: str) -> Callable[[Optional[str]], Dict[str, str]]:
    return partial(get_mapping_fund_names_by_fund_class, fund_class=MAPPING_FUND_CLASSES[fund_class_key])

get_fund_codes_mother = create_fund_class_getter('mother')
get_mapping_fund_names_mother = create_fund_name_mapping_getter('mother')

get_fund_codes_nonclassified = create_fund_class_getter('nonclassified')
get_mapping_fund_names_nonclassified = create_fund_name_mapping_getter('nonclassified')

get_fund_codes_general = create_fund_class_getter('general')
get_mapping_fund_names_general = create_fund_name_mapping_getter('general')

get_fund_codes_class = create_fund_class_getter('class')
get_mapping_fund_names_class = create_fund_name_mapping_getter('class')

def get_fund_codes_main(date_ref: Optional[str] = None) -> List[str]:
    df = get_preprocessed_funds_main(date_ref=date_ref)
    return get_fund_codes_from_df(df)

def get_mapping_fund_names_main(date_ref: Optional[str] = None) -> Dict[str, str]:
    fund_codes = get_fund_codes_main(date_ref=date_ref)
    return get_mapping_fund_names_filtered_by_fund_codes(fund_codes=fund_codes, date_ref=date_ref)

def get_mapping_by_fund_class(keyword_class: str, date_ref: Optional[str] = None) -> Dict[str, str]:
    mapping = {
        '운용펀드': get_mapping_fund_names_mother,
        '일반': get_mapping_fund_names_general,
        '클래스펀드': get_mapping_fund_names_class,
        '-': get_mapping_fund_names_nonclassified,
        '주요': get_mapping_fund_names_main
    }
    return mapping.get(keyword_class)(date_ref=date_ref)