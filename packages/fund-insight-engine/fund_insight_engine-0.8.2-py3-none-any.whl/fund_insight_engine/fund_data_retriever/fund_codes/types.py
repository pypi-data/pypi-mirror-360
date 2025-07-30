from canonical_transformer import get_mapping_of_column_pairs
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_consts import KEY_FOR_FUND_CODE_IN_MENU2110, KEY_FOR_FUND_NAME_IN_MENU2110
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_utils import get_df_menu2110
from .types_consts import VALUES_FOR_TYPE, KEY_FOR_FUND_TYPE
from .main_fund_filter import filter_fund_codes_by_main_filter
from .aum_fund_filter import filter_fund_codes_by_aum_filter

def get_dfs_funds_by_type(date_ref=None):
    df = get_df_menu2110(date_ref=date_ref)
    dfs = dict(tuple(df.groupby(KEY_FOR_FUND_TYPE)))
    return dfs

def get_df_funds_by_type(key_for_type, date_ref=None):
    dfs = get_dfs_funds_by_type(date_ref=date_ref)
    COLS_TO_KEEP = [KEY_FOR_FUND_CODE_IN_MENU2110, KEY_FOR_FUND_NAME_IN_MENU2110, KEY_FOR_FUND_TYPE]
    df = dfs[key_for_type][COLS_TO_KEEP].set_index(KEY_FOR_FUND_CODE_IN_MENU2110)
    return df

    # VALUES_FOR_TYPE = ['주식혼합', '혼합자산', '채권혼합', '주식형', '변액']

def get_df_funds_equity_mixed(date_ref=None):
    return get_df_funds_by_type('주식혼합', date_ref=date_ref)

def get_df_funds_bond_mixed(date_ref=None):
    return get_df_funds_by_type('채권혼합', date_ref=date_ref)

def get_df_funds_multi_asset(date_ref=None):
    return get_df_funds_by_type('혼합자산', date_ref=date_ref)

def get_df_funds_equity(date_ref=None):
    return get_df_funds_by_type('주식형', date_ref=date_ref)

def get_df_funds_variable(date_ref=None):
    return get_df_funds_by_type('변액', date_ref=date_ref)

def get_mapping_fund_names_by_type(key_for_type, date_ref=None):
    df = get_df_funds_by_type(key_for_type, date_ref=date_ref)
    return get_mapping_of_column_pairs(df.reset_index(), key_col=KEY_FOR_FUND_CODE_IN_MENU2110, value_col=KEY_FOR_FUND_NAME_IN_MENU2110)

def get_mapping_fund_names_equity_mixed(date_ref=None):
    return get_mapping_fund_names_by_type('주식혼합', date_ref=date_ref)

def get_mapping_fund_names_bond_mixed(date_ref=None):
    return get_mapping_fund_names_by_type('채권혼합', date_ref=date_ref)

def get_mapping_fund_names_multi_asset(date_ref=None):
    return get_mapping_fund_names_by_type('혼합자산', date_ref=date_ref)

def get_mapping_fund_names_equity(date_ref=None):
    return get_mapping_fund_names_by_type('주식형', date_ref=date_ref)

def get_mapping_fund_names_variable(date_ref=None):
    return get_mapping_fund_names_by_type('변액', date_ref=date_ref)

def get_fund_codes_equity_mixed(date_ref=None):
    return list(get_mapping_fund_names_equity_mixed(date_ref=date_ref).keys())

def get_fund_codes_bond_mixed(date_ref=None):
    return list(get_mapping_fund_names_bond_mixed(date_ref=date_ref).keys())

def get_fund_codes_multi_asset(date_ref=None):
    return list(get_mapping_fund_names_multi_asset(date_ref=date_ref).keys())

def get_fund_codes_equity(date_ref=None):
    return list(get_mapping_fund_names_equity(date_ref=date_ref).keys())

def get_fund_codes_variable(date_ref=None):
    return list(get_mapping_fund_names_variable(date_ref=date_ref).keys())

def get_fund_codes_equity_mixed_main(date_ref=None):
    fund_codes_equity_mixed = get_fund_codes_equity_mixed(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_equity_mixed, date_ref=date_ref)
    return fund_codes

def get_fund_codes_bond_mixed_main(date_ref=None):
    fund_codes_bond_mixed = get_fund_codes_bond_mixed(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_bond_mixed, date_ref=date_ref)
    return fund_codes

def get_fund_codes_multi_asset_main(date_ref=None):
    fund_codes_multi_asset = get_fund_codes_multi_asset(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_multi_asset, date_ref=date_ref)
    return fund_codes

def get_fund_codes_equity_main(date_ref=None):
    fund_codes_equity = get_fund_codes_equity(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_equity, date_ref=date_ref)
    return fund_codes

def get_fund_codes_variable_main(date_ref=None):
    fund_codes_variable = get_fund_codes_variable(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_variable, date_ref=date_ref)
    return fund_codes
    
def get_fund_codes_equity_mixed_aum(date_ref=None):
    fund_codes_equity_mixed = get_fund_codes_equity_mixed(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_aum_filter(fund_codes_equity_mixed, date_ref=date_ref)
    return fund_codes
    
def get_fund_codes_bond_mixed_aum(date_ref=None):
    fund_codes_bond_mixed = get_fund_codes_bond_mixed(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_aum_filter(fund_codes_bond_mixed, date_ref=date_ref)
    return fund_codes
    
def get_fund_codes_multi_asset_aum(date_ref=None):
    fund_codes_multi_asset = get_fund_codes_multi_asset(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_aum_filter(fund_codes_multi_asset, date_ref=date_ref)
    return fund_codes
    
def get_fund_codes_equity_aum(date_ref=None):
    fund_codes_equity = get_fund_codes_equity(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_aum_filter(fund_codes_equity, date_ref=date_ref)
    return fund_codes
    
def get_fund_codes_variable_aum(date_ref=None):
    fund_codes_variable = get_fund_codes_variable(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_aum_filter(fund_codes_variable, date_ref=date_ref)
    return fund_codes