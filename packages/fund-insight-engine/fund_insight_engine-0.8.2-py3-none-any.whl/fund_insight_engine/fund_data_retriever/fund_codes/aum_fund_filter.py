from canonical_transformer import get_mapping_of_column_pairs
from fund_insight_engine.fund_data_retriever.fund_codes.classes_consts import KEY_FOR_CLASS
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_utils import get_df_menu2110
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_consts import KEY_FOR_FUND_CODE_IN_MENU2110, KEY_FOR_FUND_NAME_IN_MENU2110

def get_df_funds_aum(date_ref=None):
    df = get_df_menu2110(date_ref=date_ref)
    FUND_CLASSES_FOR_AUM = ['클래스펀드', '일반']
    df = df[df[KEY_FOR_CLASS].isin(FUND_CLASSES_FOR_AUM)]
    return df

def get_mapping_fund_names_aum(date_ref=None):
    df = get_df_funds_aum(date_ref=date_ref)
    return get_mapping_of_column_pairs(df, key_col=KEY_FOR_FUND_CODE_IN_MENU2110, value_col=KEY_FOR_FUND_NAME_IN_MENU2110)

def get_fund_codes_aum(date_ref=None):
    return list(get_mapping_fund_names_aum(date_ref=date_ref).keys())

def filter_fund_codes_by_aum_filter(fund_codes, date_ref=None):
    fund_codes_aum = get_fund_codes_aum(date_ref=date_ref)
    fund_codes = list(set(fund_codes_aum) & set(fund_codes))
    fund_codes_sorted = sorted(fund_codes)
    return fund_codes_sorted
