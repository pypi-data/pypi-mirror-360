import logging
import pandas as pd

logger = logging.getLogger(__name__)


class PandasGroup:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def group_mean(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
        """ Group DataFrame by specific columns and calculate the mean."""
        return df.groupby(by=by).mean(numeric_only=True)

    @staticmethod
    def group_sum(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
        """ Group DataFrame by specific columns and calculate the sum."""
        return df.groupby(by=by).sum(numeric_only=True)

    @staticmethod
    def group_count(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
        """ Group DataFrame by specific columns and count the occurrences."""
        return df.groupby(by=by).count()

    @staticmethod
    def group_min(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
        """Group DataFrame by specific columns and calculate the min."""
        return df.groupby(by=by).min(numeric_only=True)

    @staticmethod
    def group_max(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
        """Group DataFrame by specific columns and calculate the max."""
        return df.groupby(by=by).max(numeric_only=True)

    @staticmethod
    def group_agg(df: pd.DataFrame, by: list[str], agg_func: dict) -> pd.DataFrame:
        """Group by columns and aggregate with a custom function dict."""
        return df.groupby(by=by).agg(agg_func)

    @staticmethod
    def group_std(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
        """Group DataFrame by columns and calculate the standard deviation."""
        return df.groupby(by=by).std(numeric_only=True)

    @staticmethod
    def group_nunique(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
        """Group DataFrame by columns and count unique values in each group."""
        return df.groupby(by=by).nunique()


pandas_group = PandasGroup()
