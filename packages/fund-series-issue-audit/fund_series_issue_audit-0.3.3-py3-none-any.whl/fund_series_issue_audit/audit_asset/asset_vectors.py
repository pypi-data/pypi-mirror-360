from shining_pebbles import open_df_in_file_folder_by_regex
from ..basis import get_lexicographical_orderd_df

class AssetVectors:
    def __init__(self):
        self.dashboard = None
        self.investment_targets = None
        self.df = None
        self.vector = None
        self._load_pipeline()

    def load_dashboard(self):
        if self.dashboard is None:
            self.dashboard = open_df_in_file_folder_by_regex(file_folder='dataset-dashboard', regex='fund_dashboard')
        return self.dashboard

    def get_investment_targets(self, option_ordered=True):
        if self.investment_targets is None:
            cols_to_keep = ['주식', '채권', 'ETF', '집합투자증권', '장내파생', '장외파생(TRS등)', '메자닌', '비상장', '공매도', '증권차입', '금전차입', '해외투자', '외화헷지']
            investment_targets = self.load_dashboard()[cols_to_keep].copy()
            investment_targets['주식'] = investment_targets['주식'].fillna(1)
            for col in investment_targets.columns:
                investment_targets[col] = investment_targets[col].fillna('X').apply(lambda x: 0 if x == 'X' else 1)
            self.investment_targets = investment_targets
            if option_ordered:
                self.df = self.get_df_ordered()
        return self.investment_targets
    
    def get_df_ordered(self):
        if self.df is None:
            df = get_lexicographical_orderd_df(df=self.get_investment_targets())
            self.df = df
        return self.df

    def get_collection_of_vectors(self):
        if self.vector is None:
            self.vector = self.get_investment_targets().T.to_dict('list')
        return self.vector
    
    def get_vector_by_fund_code(self, fund_code):
        if self.vector is None:
            self.vector = self.get_collection_of_vectors()
        return self.vector[fund_code]
    
    def _load_pipeline(self):
        try:
            self.load_dashboard()
            self.get_investment_targets()
            self.get_collection_of_vectors()
            return True
        except Exception as e:
            print(f'AssetVectors _load_pipeline error: {e}')
            return False
        