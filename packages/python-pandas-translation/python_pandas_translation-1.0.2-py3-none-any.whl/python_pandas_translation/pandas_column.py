import logging
import pandas as pd
from typing import Any, Literal

logger = logging.getLogger(__name__)


class PandasColumn:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def get_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """ Get specific columns from a DataFrame."""
        return df[columns]

    @staticmethod
    def drop_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """ Drop specific columns from a DataFrame."""
        return df.drop(columns=columns)

    @staticmethod
    def rename_columns(df: pd.DataFrame, new_names: dict[str, str]) -> pd.DataFrame:
        """ Rename columns in a DataFrame."""
        return df.rename(columns=new_names)

    @staticmethod
    def add_column(df: pd.DataFrame, column_name: str, values: list[Any]) -> pd.DataFrame:
        """ Add a new column to a DataFrame."""
        if len(values) != len(df):
            raise ValueError("Length of values does not match number of rows in DataFrame")
        df[column_name] = values
        return df

    @staticmethod
    def insert_column(df: pd.DataFrame, index: int, column_name: str, values: Any) -> pd.DataFrame:
        """ Insert a new column at a specific index in a DataFrame."""
        if len(values) != len(df):
            raise ValueError("Length of values does not match number of rows in DataFrame")
        df.insert(loc=index, column=column_name, value=values)
        return df

    @staticmethod
    def find_nan_columns(df: pd.DataFrame) -> pd.DataFrame:
        """ Find columns with NaN values. """
        return df.loc[:, df.isna().any(axis=0)]

    @staticmethod
    def fill_nan(df: pd.DataFrame, value: Any) -> pd.DataFrame:
        """ Fill NaN values in a DataFrame."""
        return df.fillna(value=value)

    @staticmethod
    def fill_nan_columns(df: pd.DataFrame, columns: list[str], value: Any) -> pd.DataFrame:
        """ Fill NaN values in specific columns of a DataFrame."""
        for col in columns:
            df[col] = df[col].fillna(value)
        return df

    @staticmethod
    def drop_nan_columns(df: pd.DataFrame, how: 'Literal["any", "all"]' = 'any') -> pd.DataFrame:
        """ Drop columns with NaN values."""
        return df.dropna(axis=1, how=how)

    @staticmethod
    def drop_nan_in_columns(df: pd.DataFrame, columns: list[str], how: 'Literal["any", "all"]' = 'any') -> pd.DataFrame:
        """ Drop rows with NaN values in specific columns."""
        return df.dropna(subset=columns, how=how)

    @staticmethod
    def swap_columns(df: pd.DataFrame, col1: str, col2: str) -> pd.DataFrame:
        """Swap the positions of two columns."""
        cols = list(df.columns)
        idx1, idx2 = cols.index(col1), cols.index(col2)
        cols[idx1], cols[idx2] = cols[idx2], cols[idx1]
        return df[cols]

    @staticmethod
    def move_column(df: pd.DataFrame, column: str, new_position: int) -> pd.DataFrame:
        """Move a column to a new position."""
        cols = list(df.columns)
        cols.remove(column)
        cols.insert(new_position, column)
        return df[cols]

    @staticmethod
    def get_column_types(df: pd.DataFrame) -> dict[str, str]:
        """Return a dict of column names and their dtypes as strings."""
        types = {str(col): str(dtype) for col, dtype in df.dtypes.items()}
        return types

    @staticmethod
    def cast_column_type(df: pd.DataFrame, column: str, dtype: Any) -> pd.DataFrame:
        """Cast a column to a specific dtype (e.g., 'int', 'float', 'str', 'datetime64')."""
        df = df.copy()
        df[column] = df[column].astype(dtype)
        return df

    @staticmethod
    def clip_column(df: pd.DataFrame, column: str, min_value, max_value) -> pd.DataFrame:
        """Clip values in a column between min_value and max_value."""
        df = df.copy()
        df[column] = df[column].clip(lower=min_value, upper=max_value)
        return df


pandas_column = PandasColumn()
