from mongodb_controller.mongodb_collections import COLLECTION_8186
import pandas as pd
from universal_timeseries_transformer import transform_timeseries

def get_timeseries_fund_price(fund_code):
    pipeline = [
    {
        "$match": {
            "펀드코드": fund_code 
        }
    },
    {
        "$project": {
            "_id": 0,
            "date": "$일자",
            fund_code: "$수정기준가" 
        }
    },
    {
        "$sort": {"date": 1}  
    }
]
    cursor = COLLECTION_8186.aggregate(pipeline)
    data = list(cursor)
    df = pd.DataFrame(data)
    if len(df) == 0:
        return pd.DataFrame()
    df = df.set_index('date')
    return df