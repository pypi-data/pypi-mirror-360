from shining_pebbles import get_yesterday
from fund_insight_engine import Portfolio, get_mapping_fund_names
import pandas as pd
from functools import cached_property

class PortfolioVector:
    def __init__(self, fund_code, date_ref=None):
        self.fund_code = fund_code
        self.date_ref = date_ref if date_ref else get_yesterday()

    @cached_property
    def fund_name(self):
        return get_mapping_fund_names()[self.fund_code]

    @cached_property
    def p(self):
        return Portfolio(fund_code=self.fund_code, date_ref=self.date_ref)
    
    @cached_property
    def raw(self):
        return self.p.raw
    
    @cached_property
    def df(self):
        df_ref = self.p.df
        try:
            df = (
                df_ref[['종목', '종목명', '비중']]
                .sort_values(by='비중', ascending=False)
                .rename(columns={'비중': '비중: 자산대비'})
                .set_index('종목')
            )
            return df
        except Exception as e:
            print(f'PortfolioVector df error: {e}')
            return None
    
    @cached_property
    def assets(self):
        SET_EXCLUSIONS = {'REPO 매수', '기타', '기타(총계정원장)', '외화선물', '외화스왑', '외화현금성'}
        return set(self.raw['자산']) - SET_EXCLUSIONS
    