from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_utils import get_df_menu2110

def get_df_funds_trust(date_ref=None):
    df = get_df_menu2110(date_ref)
    df = df[df['펀드구분']=='투자신탁']
    return df

def get_df_funds_discretionary(date_ref=None):
    df = get_df_menu2110(date_ref)
    df = df[df['펀드구분']=='투자일임']
    return df

def get_fund_codes_trust(date_ref=None):
    df = get_df_funds_trust(date_ref)
    return list(df['펀드코드'])

def get_fund_codes_discretionary(date_ref=None):
    df = get_df_menu2110(date_ref)
    df = df[df['펀드구분']=='투자일임']
    return list(df['펀드코드'])
