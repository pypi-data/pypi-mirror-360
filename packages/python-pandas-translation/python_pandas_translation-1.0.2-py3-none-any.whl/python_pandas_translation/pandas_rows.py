import logging
import pandas as pd
from typing import Optional, Any, Union, Literal

logger = logging.getLogger(__name__)


class PandasRows:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def get_rows(df: pd.DataFrame, start: int = 0, end: Optional[int] = None) -> pd.DataFrame:
        """ Get rows from a DataFrame."""
        if end is None:
            return df.iloc[start:]
        return df.iloc[start:end + 1]

    @staticmethod
    def drop_rows(df: pd.DataFrame, index: Union[int, list[int]]) -> pd.DataFrame:
        """ Drop rows from a DataFrame."""
        if isinstance(index, int):
            index = [index]
        return df.drop(index=index)

    @staticmethod
    def add_row(df: pd.DataFrame, row: list[Any]) -> pd.DataFrame:
        """ Add a row to a DataFrame."""
        if len(row) != len(df.columns):
            raise ValueError("Row length does not match number of columns")
        return pd.concat([df, pd.DataFrame([row], columns=df.columns)], ignore_index=True)

    @staticmethod
    def insert_row(df: pd.DataFrame, index: int, row: list[Any]) -> pd.DataFrame:
        """ Insert a row at a specific index in a DataFrame."""
        new_row = pd.DataFrame([row], columns=df.columns)
        return pd.concat([df.iloc[:index], new_row, df.iloc[index:]]).reset_index(drop=True)

    @staticmethod
    def find_duplicates(
        df: pd.DataFrame,
        subset: Optional[list[str]] = None,
        keep: 'Literal["first", "last", False]' = 'first'
    ) -> pd.DataFrame:
        """ Find duplicates in a DataFrame."""
        return df[df.duplicated(subset=subset, keep=keep)]

    @staticmethod
    def drop_duplicates(
        df: pd.DataFrame,
        subset: Optional[list[str]] = None,
        keep: 'Literal["first", "last", False]' = 'first'
    ) -> pd.DataFrame:
        """ Drop duplicates from a DataFrame."""
        return df.drop_duplicates(subset=subset, keep=keep)

    @staticmethod
    def find_unique(df: pd.DataFrame, column: str) -> pd.Series:
        """ Find unique values in a column."""
        return pd.Series(df[column].unique())

    @staticmethod
    def drop_unique(df: pd.DataFrame, column: str) -> pd.DataFrame:
        """ Drop unique values from a column."""
        unique_values = df[column].unique()
        return df[~df[column].isin(unique_values)]

    @staticmethod
    def find_nan_rows(df: pd.DataFrame) -> pd.DataFrame:
        """ Find rows with NaN values."""
        return df[df.isna().any(axis=1)]

    @staticmethod
    def fill_nan_rows(df: pd.DataFrame, value: Any) -> pd.DataFrame:
        """ Fill NaN values in rows."""
        return df.fillna(value=value)

    @staticmethod
    def fill_nan_rows_in_columns(df: pd.DataFrame, columns: list[str], value: Any) -> pd.DataFrame:
        """ Fill NaN values in specific columns of rows."""
        for col in columns:
            df[col] = df[col].fillna(value)
        return df

    @staticmethod
    def drop_nan_rows(df: pd.DataFrame, how: 'Literal["any", "all"]' = 'any') -> pd.DataFrame:
        """ Drop rows with NaN values."""
        return df.dropna(axis=0, how=how)

    @staticmethod
    def sample_rows(df: pd.DataFrame, n: int = 5, random_state: int = 42) -> pd.DataFrame:
        """Return a random sample of rows."""
        return df.sample(n=min(n, len(df)), random_state=random_state)

    @staticmethod
    def sort_rows(df: pd.DataFrame, by: list[str], ascending: bool = True) -> pd.DataFrame:
        """Sort rows by one or more columns."""
        return df.sort_values(by=by, ascending=ascending)

    @staticmethod
    def reset_index(df: pd.DataFrame, drop: bool = True) -> pd.DataFrame:
        """Reset the DataFrame index."""
        return df.reset_index(drop=drop)

    @staticmethod
    def drop_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
        """Drop rows where all values are NaN or empty."""
        return df.dropna(how='all')

    @staticmethod
    def duplicate_rows(df: pd.DataFrame, indices: list[int]) -> pd.DataFrame:
        """Duplicate rows by index and append them to the DataFrame."""
        df = df.copy()
        to_duplicate = df.iloc[indices]
        return pd.concat([df, to_duplicate], ignore_index=True)


pandas_row = PandasRows()
