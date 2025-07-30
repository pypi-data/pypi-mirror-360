from fund_insight_engine.fund_data_retriever.fund_mappings.mappings_divisions import get_mapping_fund_names_by_division
from .main_fund_filter import filter_fund_codes_by_main_filter
from .aum_fund_filter import filter_fund_codes_by_aum_filter

def get_fund_codes_division_01(date_ref=None):
    return list(get_mapping_fund_names_by_division('division_01', date_ref=date_ref).keys())

def get_fund_codes_division_02(date_ref=None):
    return list(get_mapping_fund_names_by_division('division_02', date_ref=date_ref).keys())

def get_fund_codes_division_01_main(date_ref=None):
    fund_codes_division_01 = get_fund_codes_division_01(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_division_01, date_ref=date_ref)
    return fund_codes

def get_fund_codes_division_02_main(date_ref=None):
    fund_codes_division_02 = get_fund_codes_division_02(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_division_02, date_ref=date_ref)
    return fund_codes

def get_fund_codes_division_01_aum(date_ref=None):
    fund_codes_division_01 = get_fund_codes_division_01(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_aum_filter(fund_codes_division_01, date_ref=date_ref)
    return fund_codes

def get_fund_codes_division_02_aum(date_ref=None):
    fund_codes_division_02 = get_fund_codes_division_02(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_aum_filter(fund_codes_division_02, date_ref=date_ref)
    return fund_codes
