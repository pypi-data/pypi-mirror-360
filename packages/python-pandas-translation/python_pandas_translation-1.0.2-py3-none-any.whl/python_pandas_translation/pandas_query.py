import logging
import pandas as pd
from typing import Any, Literal

from pandas import Series

logger = logging.getLogger(__name__)


class PandasQuery:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def filter_by_value(df: pd.DataFrame, column: str, value: Any, op: str = '==') -> Series:
        """ Filter DataFrame by a specific value in a column."""
        ops = {
            '==': df[column] == value,
            '!=': df[column] != value,
            '>': df[column] > value,
            '>=': df[column] >= value,
            '<': df[column] < value,
            '<=': df[column] <= value
        }
        return df[ops[op]]

    @staticmethod
    def filter_contains(df: pd.DataFrame, column: str, pattern: str, regex: bool = False) -> pd.DataFrame:
        """ Filter DataFrame by checking if a column contains a specific pattern."""
        return df[df[column].astype(str).str.contains(pattern, regex=regex)]

    @staticmethod
    def replace_value(df: pd.DataFrame, column: str, old_val: Any, new_val: Any) -> pd.DataFrame:
        """ Replace a specific value in a column with a new value."""
        df[column] = df[column].replace(old_val, new_val)
        return df

    @staticmethod
    def conditional_replace(
        df: pd.DataFrame,
        condition_col: str,
        condition_val: Any,
        target_cols: list[str],
        new_vals: list[Any],
        op: str = '=='
    ) -> pd.DataFrame:
        """ Replace values in target columns based on a condition in another column."""
        mask = PandasQuery.filter_by_value(df=df, column=condition_col, value=condition_val, op=op).index
        for col, val in zip(target_cols, new_vals):
            df.loc[mask, col] = val
        return df

    @staticmethod
    def filter_by_range(
        df: pd.DataFrame,
        column: str,
        min_val: Any,
        max_val: Any,
        inclusive: 'Literal["both", "neither", "left", "right"]' = 'both'
    ) -> pd.DataFrame:
        """Filter rows where a column is between min_val and max_val (inclusive: 'both', 'left', 'right', 'neither')."""
        return df[df[column].between(min_val, max_val, inclusive=inclusive)]

    @staticmethod
    def filter_by_multiple_values(df: pd.DataFrame, column: str, values: list[Any]) -> pd.DataFrame:
        """Filter rows where a column is in a list of values."""
        return df[df[column].isin(values)]

    @staticmethod
    def filter_by_regex(df: pd.DataFrame, column: str, pattern: str, case: bool = True) -> pd.DataFrame:
        """Filter rows where a column matches a regex pattern."""
        return df[df[column].astype(str).str.contains(pattern, case=case, regex=True)]

    @staticmethod
    def filter_by_null(df: pd.DataFrame, column: str, is_null: bool = True) -> pd.DataFrame:
        """Filter rows where a column is (or is not) null/NaN."""
        mask = df[column].isnull() if is_null else ~df[column].isnull()
        return df[mask]


pandas_query = PandasQuery()
