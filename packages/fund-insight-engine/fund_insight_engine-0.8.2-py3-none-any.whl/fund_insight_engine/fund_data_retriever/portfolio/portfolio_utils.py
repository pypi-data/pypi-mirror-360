import pandas as pd
from fund_insight_engine.mongodb_retriever.menu2206_retriever.menu2206_utils import get_df_menu2206_by_fund, get_df_menu2206_snapshot
from .portfolio_consts import COLUMNS_FOR_PORTFOLIO, MAPPING_COLS, VALID_ASSETS, COLUMNS_FOR_PORTFOLIO_SNAPSHOT

get_raw_portfolio_by_fund = get_df_menu2206_by_fund

def filter_df_by_valid_assets(df):    
    if df.empty:
        return df
    df_filtered = df[df['자산'].isin(VALID_ASSETS)].copy()    
    df_filtered['자산'] = pd.Categorical(df_filtered['자산'], categories=VALID_ASSETS, ordered=True)
    df_sorted = df_filtered.sort_values('자산')
    return df_sorted

def project_df_by_columns(df, columns=COLUMNS_FOR_PORTFOLIO):
    return df[columns]

def rename_df_by_columns(df, columns=MAPPING_COLS):
    return df.rename(columns=columns)

def run_pipeline_from_raw_to_portfolio(raw):
    df = (
        raw
        .set_index('일자')
        .pipe(filter_df_by_valid_assets)
        .pipe(project_df_by_columns)
        .pipe(rename_df_by_columns)
    )
    return df

def get_df_portfolio_by_fund(fund_code, date_ref=None, keys_to_project=None):
    raw = get_df_menu2206_by_fund(fund_code=fund_code, date_ref=date_ref, keys_to_project=keys_to_project)
    return run_pipeline_from_raw_to_portfolio(raw)

get_raw_portfolio_snapshot = get_df_menu2206_snapshot

def get_fund_portfolio_snapshot(date_ref=None):
    raw = get_raw_portfolio_snapshot(date_ref)
    df = (
        raw
        .set_index('일자')
        .pipe(filter_df_by_valid_assets)
        .pipe(lambda df: project_df_by_columns(df, COLUMNS_FOR_PORTFOLIO_SNAPSHOT))
        .pipe(rename_df_by_columns)
    )
    return df
