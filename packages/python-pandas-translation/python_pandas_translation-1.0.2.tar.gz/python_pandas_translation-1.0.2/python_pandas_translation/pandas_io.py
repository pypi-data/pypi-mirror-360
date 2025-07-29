import logging
import pandas as pd
from typing import Optional, Union, Literal

logger = logging.getLogger(__name__)


class PandasIO:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def load_csv(
        path: str,
        sep: str = ',',
        header: Optional[int] = 0,
        index_col: Optional[Union[int, str]] = None
    ) -> pd.DataFrame:
        return pd.read_csv(filepath_or_buffer=path, sep=sep, header=header, index_col=index_col)

    @staticmethod
    def load_excel(path: str, sheet_name: Union[str, int] = 0) -> pd.DataFrame:
        return pd.read_excel(io=path, sheet_name=sheet_name)

    @staticmethod
    def load_txt(path: str, sep: str = ',') -> pd.DataFrame:
        return PandasIO.load_csv(path=path, sep=sep)

    @staticmethod
    def save_csv(
        df: pd.DataFrame,
        path: str,
        sep: str = ',',
        mode: 'Literal["w", "a", "x", "wt", "at", "xt", "ab"]' = 'w',
        header: bool = True,
        index: bool = False
    ) -> None:
        df.to_csv(path_or_buf=path, mode=mode, header=header, index=index, sep=sep)

    @staticmethod
    def save_excel(df: pd.DataFrame, path: str, index: bool = False) -> None:
        with pd.ExcelWriter(path) as writer:
            df.to_excel(excel_writer=writer, index=index)

    @staticmethod
    def save_txt(
        df: pd.DataFrame,
        path: str,
        sep: str = ',',
        mode: 'Literal["w", "a", "x", "wt", "at", "xt", "ab"]' = 'w',
        header: bool = True,
        index: bool = False
    ) -> None:
        df.to_csv(path, sep=sep, mode=mode, header=header, index=index)

    @staticmethod
    def load_json(
        path: str,
        orient: 'Literal["split", "records", "index", "columns", "values", "table"]' = 'records'
    ) -> pd.DataFrame:
        """Load a DataFrame from a JSON file."""
        return pd.read_json(path, orient=orient)

    @staticmethod
    def save_json(
        df: pd.DataFrame,
        path: str,
        orient: 'Literal["split", "records", "index", "columns", "values", "table"]' = 'records',
        lines: bool = False
    ) -> None:
        """Save a DataFrame to a JSON file."""
        df.to_json(path, orient=orient, lines=lines)

    @staticmethod
    def preview_file_head(path: str, n: int = 5) -> str:
        """Return the first n lines of a file as a string (for preview)."""
        with open(path, 'r', encoding='utf-8') as f:
            lines = []
            for _ in range(n):
                try:
                    lines.append(next(f))
                except StopIteration:
                    break
        return ''.join(lines)

    @staticmethod
    def append_to_csv(df: pd.DataFrame, path: str, sep: str = ',', header: bool = False, index: bool = False) -> None:
        """Append DataFrame to an existing CSV file."""
        df.to_csv(path, mode='a', sep=sep, header=header, index=index)


pandas_io = PandasIO()
