import pandas as pd
from mongodb_controller import COLLECTION_2160, COLLECTION_8186

def fetch_data_stock_portion_2160(fund_code):
    pipeline_2160 = [
        {'$match': {'펀드': fund_code}},
        {'$project': {'_id': 0, '일자': 1, '편입비중: 주식': 1}}
    ]
    cursor_2160 = COLLECTION_2160.aggregate(pipeline_2160)
    data_2160 = list(cursor_2160)
    return data_2160

def fetch_data_stock_portion_8186(fund_code):
    pipeline_8186 = [
        {'$match': {'펀드코드': fund_code}},
        {'$project': {'_id': 0, '일자': 1, '주식비율': 1}}
    ]
    cursor_8186 = COLLECTION_8186.aggregate(pipeline_8186)
    data_8186 = list(cursor_8186)
    return data_8186

def get_df_stock_portion_2160(fund_code):
    data_2160 = fetch_data_stock_portion_2160(fund_code)
    df_2160 = pd.DataFrame(data_2160).set_index('일자').astype(float)
    return df_2160
    
def get_df_stock_portion_8186(fund_code):
    data_8186 = fetch_data_stock_portion_8186(fund_code)
    df_8186 = pd.DataFrame(data_8186).set_index('일자')
    return df_8186

def rename_df_stock_portion(df):
    df.index.name = 'date'
    df.columns = ['stock_portion']
    return df