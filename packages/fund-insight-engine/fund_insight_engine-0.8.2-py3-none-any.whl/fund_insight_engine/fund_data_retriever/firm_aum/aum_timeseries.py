import pandas as pd
from tqdm import tqdm
from shining_pebbles import get_month_end_dates
from financial_dataset_preprocessor import load_currency
from universal_timeseries_transformer import extend_timeseries_by_all_dates
from fund_insight_engine.mongodb_retriever.menu8186_retriever.menu8186_date import get_latest_date_in_menu8186
from .aum_retriever import get_aum_of_date

def get_timeseries_month_end_aum(start_date=None, end_date=None):
    start_date = start_date or '2020-05-31'
    end_date = end_date or get_latest_date_in_menu8186()
    start_year_month = start_date.replace('-', '')[:6]
    end_year_month = end_date.replace('-', '')[:6]
    month_end_dates = get_month_end_dates(start_year_month=start_year_month, end_year_month=end_year_month, date_format='%Y-%m-%d')
    aums = []
    for end_date in tqdm(month_end_dates):
        try:
            aum_of_date = get_aum_of_date(date_ref=end_date)
            aums.append({'date': end_date, 'aum': aum_of_date})
        except:
            pass
    aum = pd.DataFrame(aums).set_index('date')   
    return aum

def get_timeseries_aum_in_usd(start_date=None, end_date=None):
    end_date = end_date or get_latest_date_in_menu8186()
    timeseries_aum = get_timeseries_aum(end_date=end_date, start_date=start_date)
    df_currency = load_currency(ticker_bbg_currency='USDKRW Curncy').rename(columns={'PX_LAST': 'usdkrw'})
    df_currency = extend_timeseries_by_all_dates(df_currency, start_date=start_date, end_date=end_date)
    timeseries_aum_in_usd = timeseries_aum.join(df_currency, how='left')
    timeseries_aum_in_usd['aum_in_usd'] = timeseries_aum_in_usd['aum'] / timeseries_aum_in_usd['usdkrw']
    return timeseries_aum_in_usd

def get_firm_aum_since_inception(start_date=None, end_date=None, option_unit=True):
    timeseries_aum = get_timeseries_aum_in_usd(end_date=end_date, start_date=start_date)
    if option_unit:
        timeseries_aum['AUM (KRW, Billion)'] = round(timeseries_aum['aum']/ 1e9 ,4)
        timeseries_aum['AUM (USD, Million)'] = round(timeseries_aum['aum_in_usd']/ 1e6, 4)
        timeseries_aum = timeseries_aum[['AUM (KRW, Billion)', 'AUM (USD, Million)']]
    return timeseries_aum


def get_timeseries_aum(start_date=None, end_date=None):
    # dates = None
    aums = []
    for end_date in tqdm(dates):
        try:
            aum_of_date = get_aum_of_date(date_ref=end_date)
            aums.append({'date': end_date, 'aum': aum_of_date})
        except:
            pass
    aum = pd.DataFrame(aums).set_index('date')   
    return aum
