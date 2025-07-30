from mongodb_controller import client
import pandas as pd
from fund_insight_engine.fund_data_retriever.fund_codes import get_fund_codes_aum

def fetch_data_for_aum(date_ref=None):
    fund_codes_for_aum = get_fund_codes_aum(date_ref=date_ref)
    collection = client['database-rpa']['dataset-menu8186']
    pipeline = [
        {'$match': {'펀드코드': {'$in': fund_codes_for_aum}, '일자': '2025-04-30'}},
        {'$project': {'_id': 0, '펀드코드': 1, '순자산': 1}}
    ]
    cursor = collection.aggregate(pipeline)
    data = list(cursor)
    return data

def get_df_nav_for_aum(date_ref=None):
    data = fetch_data_for_aum(date_ref=date_ref)
    df = pd.DataFrame(data)
    return df

def get_aum_of_date(date_ref=None):
    df = get_df_nav_for_aum(date_ref=date_ref)
    aum_of_date = df['순자산'].sum()
    return aum_of_date
