import pandas as pd
import pytest
from python_pandas_translation.pandas_rows import PandasRows


class TestGetRows:
    def test_get_rows(self):
        df = pd.DataFrame({'a': range(5)})
        result = PandasRows.get_rows(df, 1, 3)
        assert list(result['a']) == [1, 2, 3]

    def test_get_rows_end_none(self):
        df = pd.DataFrame({'a': range(5)})
        result = PandasRows.get_rows(df, 2)
        assert list(result['a']) == [2, 3, 4]


class TestDropRows:
    def test_drop_rows(self):
        df = pd.DataFrame({'a': [1, 2, 3]})
        result = PandasRows.drop_rows(df, 1)
        assert 1 not in result.index

    def test_drop_rows_list(self):
        df = pd.DataFrame({'a': [1, 2, 3]})
        result = PandasRows.drop_rows(df, [0, 2])
        assert list(result['a']) == [2]


class TestAddRow:
    def test_add_row(self):
        df = pd.DataFrame({'a': [1, 2]})
        result = PandasRows.add_row(df, [3])
        assert result.iloc[-1]['a'] == 3

    def test_add_row_wrong_length(self):
        df = pd.DataFrame({'a': [1, 2]})
        with pytest.raises(ValueError):
            PandasRows.add_row(df, [1, 2])


class TestInsertRow:
    def test_insert_row(self):
        df = pd.DataFrame({'a': [1, 2]})
        result = PandasRows.insert_row(df, 1, [9])
        assert result.iloc[1]['a'] == 9


class TestFindDuplicates:
    def test_find_duplicates_first(self):
        df = pd.DataFrame({'a': [1, 1, 2]})
        result = PandasRows.find_duplicates(df, subset=['a'])
        # Only the second occurrence of 1 is returned
        assert len(result) == 1
        assert result.iloc[0]['a'] == 1

    def test_find_duplicates_keep_false(self):
        df = pd.DataFrame({'a': [1, 1, 2]})
        result = PandasRows.find_duplicates(df, subset=['a'], keep=False)
        # Both occurrences of 1 are returned
        assert len(result) == 2
        assert all(result['a'] == 1)


class TestDropDuplicates:
    def test_drop_duplicates(self):
        df = pd.DataFrame({'a': [1, 1, 2]})
        result = PandasRows.drop_duplicates(df, subset=['a'])
        assert list(result['a']) == [1, 2]


class TestFindUnique:
    def test_find_unique(self):
        df = pd.DataFrame({'a': [1, 2, 2, 3]})
        result = PandasRows.find_unique(df, 'a')
        assert set(result) == {1, 2, 3}


class TestDropUnique:
    def test_drop_unique(self):
        df = pd.DataFrame({'a': [1, 2, 2, 3]})
        result = PandasRows.drop_unique(df, 'a')
        assert result.empty


class TestFindNanRows:
    def test_find_nan_rows(self):
        df = pd.DataFrame({'a': [1, None], 'b': [2, 3]})
        result = PandasRows.find_nan_rows(df)
        assert len(result) == 1


class TestFillNanRows:
    def test_fill_nan_rows(self):
        df = pd.DataFrame({'a': [1, None]})
        result = PandasRows.fill_nan_rows(df, 0)
        assert result.isnull().sum().sum() == 0


class TestFillNanRowsInColumns:
    def test_fill_nan_rows_in_columns(self):
        df = pd.DataFrame({'a': [1, None], 'b': [None, 2]})
        result = PandasRows.fill_nan_rows_in_columns(df, ['a'], 0)
        assert result['a'].isnull().sum() == 0
        assert result['b'].isnull().sum() == 1


class TestDropNanRows:
    def test_drop_nan_rows(self):
        df = pd.DataFrame({'a': [1, None], 'b': [2, 3]})
        result = PandasRows.drop_nan_rows(df)
        assert result['a'].isnull().sum() == 0


class TestSampleRows:
    def test_sample_rows(self):
        df = pd.DataFrame({'a': range(10)})
        result = PandasRows.sample_rows(df, n=3, random_state=1)
        assert len(result) == 3


class TestSortRows:
    def test_sort_rows(self):
        df = pd.DataFrame({'a': [3, 1, 2]})
        result = PandasRows.sort_rows(df, by=['a'])
        assert list(result['a']) == [1, 2, 3]


class TestResetIndex:
    def test_reset_index(self):
        df = pd.DataFrame({'a': [1, 2]}, index=[5, 6])
        result = PandasRows.reset_index(df)
        assert list(result.index) == [0, 1]


class TestDropEmptyRows:
    def test_drop_empty_rows(self):
        df = pd.DataFrame({'a': [None, 1], 'b': [None, 2]})
        result = PandasRows.drop_empty_rows(df)
        assert len(result) == 1

    def test_no_empty_rows(self):
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        result = PandasRows.drop_empty_rows(df)
        assert len(result) == 2


class TestDuplicateRows:
    def test_duplicate_rows(self):
        df = pd.DataFrame({'a': [1, 2, 3]})
        result = PandasRows.duplicate_rows(df, [0, 2])
        assert list(result['a']) == [1, 2, 3, 1, 3]

    def test_duplicate_rows_empty(self):
        df = pd.DataFrame({'a': [1, 2]})
        result = PandasRows.duplicate_rows(df, [])
        assert result.equals(df)
