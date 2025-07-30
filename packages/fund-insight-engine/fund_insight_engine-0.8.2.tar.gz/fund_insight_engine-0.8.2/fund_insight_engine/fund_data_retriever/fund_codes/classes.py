from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_utils import get_df_menu2110
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_consts import KEY_FOR_FUND_CODE_IN_MENU2110
from .classes_consts import KEY_FOR_CLASS

def get_dfs_funds_by_class(date_ref=None):
    df = get_df_menu2110(date_ref=date_ref)
    df_code_class = df[[KEY_FOR_FUND_CODE_IN_MENU2110, KEY_FOR_CLASS]]
    dfs = dict(tuple(df_code_class.groupby(KEY_FOR_CLASS)))
    return dfs

def get_df_funds_by_class(key_for_class, date_ref=None):
    dfs = get_dfs_funds_by_class(date_ref=date_ref)
    df = dfs[key_for_class].set_index(KEY_FOR_FUND_CODE_IN_MENU2110)
    return df

def get_df_funds_mothers(date_ref=None):
    return get_df_funds_by_class('운용펀드', date_ref=date_ref)

def get_df_funds_generals(date_ref=None):
    return get_df_funds_by_class('일반', date_ref=date_ref)

def get_df_funds_class(date_ref=None):
    return get_df_funds_by_class('클래스펀드', date_ref=date_ref)

def get_df_funds_nonclassified(date_ref=None):
    return get_df_funds_by_class('-', date_ref=date_ref)

def get_fund_codes_by_class(key_for_class, date_ref=None):
    df = get_df_funds_by_class(key_for_class, date_ref=date_ref)
    return df.index.tolist()

def get_fund_codes_mothers(date_ref=None):
    return get_fund_codes_by_class('운용펀드', date_ref=date_ref)

def get_fund_codes_generals(date_ref=None):
    return get_fund_codes_by_class('일반', date_ref=date_ref)

def get_fund_codes_class(date_ref=None):
    return get_fund_codes_by_class('클래스펀드', date_ref=date_ref)

def get_fund_codes_nonclassified(date_ref=None):
    return get_fund_codes_by_class('-', date_ref=date_ref)
