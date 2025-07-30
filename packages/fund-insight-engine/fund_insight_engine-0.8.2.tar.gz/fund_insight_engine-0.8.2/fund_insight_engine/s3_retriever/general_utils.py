from financial_dataset_preprocessor import get_mapping_fund_names

def get_fund_codes_from_df(df):
    return list(df.index)

def get_mapping_fund_names_filtered_by_fund_codes(fund_codes, date_ref=None):
    mapping_fund_names = get_mapping_fund_names(date_ref=date_ref)
    mapping = {k: v for k, v in mapping_fund_names.items() if k in fund_codes}
    return mapping

generate_mapping_from_fund_codes = get_mapping_fund_names_filtered_by_fund_codes
