from canonical_transformer import map_data_to_df
from fund_insight_engine.mongodb_retriever.menu2206_retriever.menu2206_utils import fetch_data_menu2206_by_fund
from .portfolio_utils import run_pipeline_from_raw_to_portfolio
from .portfolio_customizer import customize_df_portfolio

class Portfolio:
    def __init__(self, fund_code, date_ref=None):
        self.fund_code = fund_code
        self.date_ref = date_ref
        self.data = None
        self.raw = None
        self.df = None
        self.port = None
        self._load_pipeline()

    def get_data(self):
        if self.data is None:
            self.data = fetch_data_menu2206_by_fund(self.fund_code, self.date_ref)
        return self.data

    def get_raw(self):
        if self.raw is None:
            self.raw = map_data_to_df(self.get_data())
        return self.raw

    def get_df(self):
        if self.df is None:
            self.df = run_pipeline_from_raw_to_portfolio(self.get_raw())
        return self.df

    def get_customized_port(self):
        if self.port is None:
            self.port = customize_df_portfolio(self.get_df())
        return self.port

    def _load_pipeline(self):
        try:
            self.get_data()
            self.get_raw()
            self.get_df()
            self.get_customized_port()
            return True
        except Exception as e:
            print(f'Portfolio _load_pipeline error: {e}')
            return False
    