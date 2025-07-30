from functools import partial
from fund_series_issue_audit.functionals import pipe
from .pairs import get_df_pairs
from .inception_dates import filter_6_months
from .investors import filter_investors


def get_filtered_pairs(date_ref=None, option_concise=True):
    filter_6_months_of_date_ref = partial(filter_6_months, date_ref=date_ref, option_concise=option_concise)
    filter_investors_of_date_ref = partial(filter_investors, date_ref=date_ref, option_concise=option_concise)
    return pipe(
        get_df_pairs,
        filter_6_months_of_date_ref,
        filter_investors_of_date_ref
    )(date_ref)