from shining_pebbles import get_yesterday
from .full_audit_utils import generate_full_audit, load_full_audit
from .result_utils import get_comparison_of_row_in_df

class FullAudit:
    def __init__(self, date_ref=None, option_threshold=0.8):
        self.date_ref = date_ref if date_ref else get_yesterday()
        self.option_threshold = option_threshold
        self._generate = None
        self._load = None

    @property
    def generate(self):
        if self._generate is None:
            self._generate = generate_full_audit(date_ref=self.date_ref)
        return self._generate

    @property
    def load(self):
        if self._load is None:
            self._load = load_full_audit(date_ref=self.date_ref, option_threshold=self.option_threshold)
        return self._load

    def comparison(self, index):
        df = self.load.copy()
        comparison = get_comparison_of_row_in_df(df, index, date_ref=self.date_ref)
        return comparison
