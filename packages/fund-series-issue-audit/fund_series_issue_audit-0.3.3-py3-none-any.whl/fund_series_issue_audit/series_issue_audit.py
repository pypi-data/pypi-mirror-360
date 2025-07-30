from functools import cached_property
import numpy as np
from shining_pebbles import get_yesterday
from fund_series_issue_audit.audit_result.result_utils import (
    get_df_filtered_series_issue_audit,
    load_series_issue_audit_result,
    get_comparison_of_row_in_df,
    save_postprocess_result
)
from fund_series_issue_audit.audit_postprocess.post_filter import (
    filter_heterogeneous_funds,
    filter_discretionary_funds,
    filter_different_holdings_funds,
)
from .functionals import pipe

class SeriesIssueAudit:
    def __init__(self, date_ref=None, option_threshold=0.8):
        self.date_ref = date_ref if date_ref else get_yesterday()
        self.option_threshold = option_threshold

    @cached_property
    def generate(self):
        print(f'date_ref: {self.date_ref}')
        return get_df_filtered_series_issue_audit(date_ref=self.date_ref)

    @cached_property
    def load(self):
        print(f'date_ref: {self.date_ref}')
        return load_series_issue_audit_result(date_ref=self.date_ref, option_threshold=self.option_threshold, option_concise=False)

    @cached_property
    def result(self):
        return self.load

    @cached_property
    def concise(self):
        print(f'date_ref: {self.date_ref}')
        return load_series_issue_audit_result(date_ref=self.date_ref, option_threshold=self.option_threshold, option_concise=True)

    def filter_discretionary(self):
        return filter_discretionary_funds(self.load)

    def filter_different_holdings(self):
        return filter_different_holdings_funds(self.load)

    def filter_heterogeneous(self):
        return filter_heterogeneous_funds(self.load)
    
    def operate_postprocess(self):
        df = self.load.copy()
        df = pipe(
            filter_discretionary_funds,
            filter_different_holdings_funds,
            filter_heterogeneous_funds,
        )(df)
        save_postprocess_result(df, date_ref=self.date_ref)
        return df

    @cached_property
    def effective_result(self):
        return self.operate_postprocess()
    
    @cached_property
    def filtered_result(self):
        return self.effective_result
    
    def comparison(self, index, option_df='effective_result'):
        mapping_df = {
            'result': self.result,
            'effective_result': self.effective_result
        }
        try:
            df = mapping_df[option_df]
        except KeyError:
            raise ValueError(f'option_df must be either "result" or "effective_result", but got {option_df}')
        df = get_comparison_of_row_in_df(df, index, date_ref=self.date_ref).copy()
        df['delta'] = df['delta'].map(lambda x: x if x!='-' else np.nan)
        df = df.sort_values(by='delta', ascending=False)
        df['delta'] = df['delta'].fillna('-')
        return df
    
    def clear_all_caches(self):
        for attr_name in list(self.__dict__.keys()):
            if hasattr(type(self), attr_name):
                attr = getattr(type(self), attr_name)
                if isinstance(attr, cached_property):
                    delattr(self, attr_name)

    def clear_cache(self, attr_name):
        if hasattr(self, attr_name):
            delattr(self, attr_name)
