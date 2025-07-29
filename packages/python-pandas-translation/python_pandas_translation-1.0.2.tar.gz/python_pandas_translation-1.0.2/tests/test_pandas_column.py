import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from python_pandas_translation.pandas_column import PandasColumn
from pandas import DataFrame


# Sample fixture for DataFrame with field names
@pytest.fixture
def sample_df() -> DataFrame:
    return pd.DataFrame(
        data={
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': pd.Series([30, 25, None], dtype='Int64'),
            'score': [85.5, None, 92.0]
        }
    )


# Fixture for the PandasColumn instance
@pytest.fixture
def pandas_column() -> PandasColumn:
    return PandasColumn()


class TestPandasColumn:
    def test_get_columns(self, sample_df: DataFrame, pandas_column: PandasColumn) -> None:
        result = pandas_column.get_columns(df=sample_df, columns=['name', 'score'])

        # Manually constructing expected DataFrame
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'Bob', 'Charlie'],
                'score': [85.5, None, 92.0]
            }
        )

        assert_frame_equal(result, expected)

    def test_drop_columns(self, sample_df: DataFrame, pandas_column: PandasColumn) -> None:
        result = pandas_column.drop_columns(df=sample_df, columns=['age'])

        # Manually constructing expected DataFrame
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'Bob', 'Charlie'],
                'score': [85.5, None, 92.0]
            }
        )

        assert_frame_equal(result, expected)

    def test_rename_columns(self, sample_df: DataFrame, pandas_column: PandasColumn) -> None:
        result = pandas_column.rename_columns(df=sample_df, new_names={'name': 'full_name'})

        # Manually constructing expected DataFrame with 'name' column renamed to 'full_name'
        expected = pd.DataFrame(
            data={
                'full_name': ['Alice', 'Bob', 'Charlie'],
                'age': pd.Series([30, 25, None], dtype='Int64'),
                'score': [85.5, None, 92.0]
            }
        )

        assert_frame_equal(result, expected)

    def test_add_column(self, sample_df: DataFrame, pandas_column: PandasColumn) -> None:
        values: list[str] = ['A', 'B', 'C']
        result = pandas_column.add_column(df=sample_df.copy(), column_name='grade', values=values)

        # Manually constructing expected DataFrame with the new column 'grade' added
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': pd.Series([30, 25, None], dtype='Int64'),
                'score': [85.5, None, 92.0],
                'grade': ['A', 'B', 'C']
            }
        )

        assert_frame_equal(result, expected)

    def test_add_column_invalid_length(self, sample_df: DataFrame, pandas_column: PandasColumn) -> None:
        with pytest.raises(ValueError):
            pandas_column.add_column(df=sample_df.copy(), column_name='grade', values=['A'])

    def test_insert_column(self, sample_df: DataFrame, pandas_column: PandasColumn) -> None:
        values: list[str] = ['A', 'B', 'C']
        result = pandas_column.insert_column(
            df=sample_df.copy(),
            index=1,
            column_name='grade',
            values=values
        )

        # Manually constructing expected DataFrame with 'grade' inserted at index 1
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'Bob', 'Charlie'],
                'grade': ['A', 'B', 'C'],
                'age': pd.Series([30, 25, None], dtype='Int64'),
                'score': [85.5, None, 92.0]
            }
        )

        assert_frame_equal(result, expected)

    def test_insert_column_invalid_length(self, sample_df: DataFrame, pandas_column: PandasColumn) -> None:
        with pytest.raises(ValueError):
            pandas_column.insert_column(df=sample_df.copy(), index=1, column_name='grade', values=['A'])

    def test_find_nan_columns(self, sample_df: DataFrame, pandas_column: PandasColumn) -> None:
        result = pandas_column.find_nan_columns(df=sample_df)

        # Manually constructing expected DataFrame with columns containing NaN values ('age', 'score')
        expected = pd.DataFrame(
            data=
            {
                'age': pd.Series([30, 25, None], dtype='Int64'),
                'score': [85.5, None, 92.0]
            }
        )

        assert_frame_equal(result, expected)

    def test_fill_nan(self, sample_df: DataFrame, pandas_column: PandasColumn) -> None:
        result = pandas_column.fill_nan(df=sample_df.copy(), value=0)

        # Manually constructing expected DataFrame with NaN values filled with 0
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': pd.Series([30, 25, 0], dtype='Int64'),
                'score': [85.5, 0, 92.0]
            }
        )

        assert_frame_equal(result, expected)

    def test_fill_nan_columns(self, sample_df: DataFrame, pandas_column: PandasColumn) -> None:
        result = pandas_column.fill_nan_columns(df=sample_df.copy(), columns=['age'], value=99)

        # Manually constructing expected DataFrame with NaN values in 'age' column filled with 99
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': pd.Series([30, 25, 99], dtype='Int64'),
                'score': [85.5, None, 92.0]
            }
        )

        assert_frame_equal(result, expected)

    def test_drop_nan_columns_any(self, sample_df: DataFrame, pandas_column: PandasColumn) -> None:
        result = pandas_column.drop_nan_columns(df=sample_df.copy(), how='any')

        # Manually constructing expected DataFrame after dropping columns with any NaN values
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'Bob', 'Charlie']
            }
        )

        assert_frame_equal(result, expected)

    def test_drop_nan_columns_all(self, pandas_column: PandasColumn) -> None:
        df = pd.DataFrame(
            data={
                'A': [None, None],
                'B': [1, 2]
            }
        )
        result = pandas_column.drop_nan_columns(df=df, how='all')

        # Manually constructing expected DataFrame after dropping columns with all NaN values
        expected = pd.DataFrame(
            data={
                'B': [1, 2]
            }
        )

        assert_frame_equal(result, expected)

    def test_drop_nan_in_columns(self, sample_df: DataFrame, pandas_column: PandasColumn) -> None:
        result = pandas_column.drop_nan_in_columns(df=sample_df.copy(), columns=['score'], how='any')

        # Manually constructing expected DataFrame after dropping rows where 'score' has NaN
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'Charlie'],
                'age': pd.Series([30, None], dtype='Int64'),
                'score': [85.5, 92.0]
            }
        )

        assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


class TestGetColumns:
    def test_get_columns(self):
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6]})
        result = PandasColumn.get_columns(df, ['a', 'c'])
        assert list(result.columns) == ['a', 'c']


class TestDropColumns:
    def test_drop_columns(self):
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        result = PandasColumn.drop_columns(df, ['b'])
        assert 'b' not in result.columns


class TestRenameColumns:
    def test_rename_columns(self):
        df = pd.DataFrame({'a': [1], 'b': [2]})
        result = PandasColumn.rename_columns(df, {'a': 'x'})
        assert 'x' in result.columns and 'a' not in result.columns


class TestAddColumn:
    def test_add_column(self):
        df = pd.DataFrame({'a': [1, 2]})
        result = PandasColumn.add_column(df, 'b', [3, 4])
        assert 'b' in result.columns
        assert list(result['b']) == [3, 4]

    def test_add_column_wrong_length(self):
        df = pd.DataFrame({'a': [1, 2]})
        with pytest.raises(ValueError):
            PandasColumn.add_column(df, 'b', [1])


class TestInsertColumn:
    def test_insert_column(self):
        df = pd.DataFrame({'a': [1, 2]})
        result = PandasColumn.insert_column(df, 0, 'b', [3, 4])
        assert result.columns[0] == 'b'

    def test_insert_column_wrong_length(self):
        df = pd.DataFrame({'a': [1, 2]})
        with pytest.raises(ValueError):
            PandasColumn.insert_column(df, 0, 'b', [1])


class TestFindNanColumns:
    def test_find_nan_columns(self):
        df = pd.DataFrame({'a': [1, None], 'b': [2, 3]})
        result = PandasColumn.find_nan_columns(df)
        assert 'a' in result.columns and 'b' not in result.columns


class TestFillNan:
    def test_fill_nan(self):
        df = pd.DataFrame({'a': [1, None]})
        result = PandasColumn.fill_nan(df, 0)
        assert result.isnull().sum().sum() == 0


class TestFillNanColumns:
    def test_fill_nan_columns(self):
        df = pd.DataFrame({'a': [1, None], 'b': [None, 2]})
        result = PandasColumn.fill_nan_columns(df, ['a'], 0)
        assert result['a'].isnull().sum() == 0
        assert result['b'].isnull().sum() == 1


class TestDropNanColumns:
    def test_drop_nan_columns(self):
        df = pd.DataFrame({'a': [1, None], 'b': [2, 3]})
        result = PandasColumn.drop_nan_columns(df)
        assert 'a' not in result.columns


class TestDropNanInColumns:
    def test_drop_nan_in_columns(self):
        df = pd.DataFrame({'a': [1, None], 'b': [2, 3]})
        result = PandasColumn.drop_nan_in_columns(df, ['a'])
        assert result['a'].isnull().sum() == 0


class TestSwapColumns:
    def test_swap_columns(self):
        df = pd.DataFrame({'a': [1], 'b': [2], 'c': [3]})
        result = PandasColumn.swap_columns(df, 'a', 'c')
        assert list(result.columns) == ['c', 'b', 'a']


class TestMoveColumn:
    def test_move_column(self):
        df = pd.DataFrame({'a': [1], 'b': [2], 'c': [3]})
        result = PandasColumn.move_column(df, 'a', 2)
        assert list(result.columns) == ['b', 'c', 'a']


class TestGetColumnTypes:
    def test_get_column_types(self):
        df = pd.DataFrame({'a': [1], 'b': [2.0], 'c': ['x']})
        types = PandasColumn.get_column_types(df)
        assert types == {'a': 'int64', 'b': 'float64', 'c': 'object'}


class TestCastColumnType:
    def test_cast_to_float(self):
        df = pd.DataFrame({'a': ['1', '2', '3']})
        result = PandasColumn.cast_column_type(df, 'a', float)
        assert result['a'].dtype == float

    def test_cast_to_datetime(self):
        df = pd.DataFrame({'a': ['2020-01-01', '2020-01-02']})
        result = PandasColumn.cast_column_type(df, 'a', 'datetime64[ns]')
        assert str(result['a'].dtype).startswith('datetime64')

    def test_cast_invalid(self):
        df = pd.DataFrame({'a': ['x', 'y']})
        with pytest.raises(ValueError):
            PandasColumn.cast_column_type(df, 'a', int)


class TestClipColumn:
    def test_clip_column(self):
        df = pd.DataFrame({'a': [1, 5, 10]})
        result = PandasColumn.clip_column(df, 'a', 2, 8)
        assert list(result['a']) == [2, 5, 8]

    def test_clip_column_all_below(self):
        df = pd.DataFrame({'a': [0, 1]})
        result = PandasColumn.clip_column(df, 'a', 2, 5)
        assert all(result['a'] == 2)

    def test_clip_column_all_above(self):
        df = pd.DataFrame({'a': [10, 20]})
        result = PandasColumn.clip_column(df, 'a', 2, 5)
        assert all(result['a'] == 5)
