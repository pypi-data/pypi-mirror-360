import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from python_pandas_translation.pandas_query import PandasQuery


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        data={
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'age': [30, 25, 35, 40],
            'city': ['New York', 'Paris', 'Berlin', 'New York']
        }
    )


@pytest.fixture
def pandas_query():
    return PandasQuery()


class TestPandasQueryActions:
    def test_filter_by_value_equal(self, sample_df: pd.DataFrame, pandas_query: PandasQuery) -> None:
        result = pandas_query.filter_by_value(df=sample_df, column='city', value='New York', op='==')
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'David'],
                'age': [30, 40],
                'city': ['New York', 'New York']
            }
        )
        assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))

    def test_filter_by_value_greater(self, sample_df: pd.DataFrame, pandas_query: PandasQuery) -> None:
        result = pandas_query.filter_by_value(df=sample_df, column='age', value=30, op='>')
        expected = pd.DataFrame(
            data={
                'name': ['Charlie', 'David'],
                'age': [35, 40],
                'city': ['Berlin', 'New York']
            }
        )
        assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))

    def test_filter_contains(self, sample_df: pd.DataFrame, pandas_query: PandasQuery) -> None:
        result = pandas_query.filter_contains(df=sample_df, column='name', pattern='li')
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'Charlie'],  # These are the rows that match the pattern 'li'
                'age': [30, 35],  # The corresponding 'age' values
                'city': ['New York', 'Berlin'],  # The corresponding 'city' values
            }
        )
        assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))

    def test_replace_value(self, sample_df: pd.DataFrame, pandas_query: PandasQuery) -> None:
        df = sample_df.copy()
        result = pandas_query.replace_value(df=df, column='city', old_val='New York', new_val='NYC')
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'Bob', 'Charlie', 'David'],
                'age': [30, 25, 35, 40],
                'city': ['NYC', 'Paris', 'Berlin', 'NYC'],
            }
        )

        assert_frame_equal(result, expected)

    def test_conditional_replace_equal(self, sample_df: pd.DataFrame, pandas_query: PandasQuery) -> None:
        df = sample_df.copy()
        result = pandas_query.conditional_replace(
            df=df.copy(),
            condition_col='city',
            condition_val='New York',
            target_cols=['city'],
            new_vals=['NYC'],
            op='=='
        )
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'Bob', 'Charlie', 'David'],
                'age': [30, 25, 35, 40],
                'city': ['NYC', 'Paris', 'Berlin', 'NYC'],
            }
        )

        assert_frame_equal(result, expected)

    def test_conditional_replace_greater(self, sample_df: pd.DataFrame, pandas_query: PandasQuery) -> None:
        df = sample_df.copy()
        result = pandas_query.conditional_replace(
            df=df.copy(),
            condition_col='age',
            condition_val=30,
            target_cols=['name'],
            new_vals=['Senior'],
            op='>'
        )
        expected = pd.DataFrame(
            data={
                'name': ['Alice', 'Bob', 'Senior', 'Senior'],  # names replaced where age > 30
                'age': [30, 25, 35, 40],
                'city': ['New York', 'Paris', 'Berlin', 'New York'],
            }
        )

        assert_frame_equal(result, expected)

    def test_filter_by_value_invalid_op(self, sample_df: pd.DataFrame, pandas_query: PandasQuery) -> None:
        with pytest.raises(KeyError):
            pandas_query.filter_by_value(df=sample_df, column='age', value=30, op='invalid_op')


class TestFilterByValue:
    def test_filter_by_value_eq(self):
        df = pd.DataFrame({'a': [1, 2, 2, 3]})
        result = PandasQuery.filter_by_value(df, 'a', 2)
        assert set(result.index) == {1, 2}

    def test_filter_by_value_gt(self):
        df = pd.DataFrame({'a': [1, 2, 3]})
        result = PandasQuery.filter_by_value(df, 'a', 1, op='>')
        assert set(result.index) == {1, 2}


class TestFilterContains:
    def test_filter_contains(self):
        df = pd.DataFrame({'a': ['foo', 'bar', 'foobar']})
        result = PandasQuery.filter_contains(df, 'a', 'foo')
        assert set(result.index) == {0, 2}


class TestReplaceValue:
    def test_replace_value(self):
        df = pd.DataFrame({'a': [1, 2, 2]})
        result = PandasQuery.replace_value(df, 'a', 2, 9)
        assert set(result['a']) == {1, 9}


class TestConditionalReplace:
    def test_conditional_replace(self):
        df = pd.DataFrame({'a': [1, 2, 2], 'b': [0, 0, 0]})
        result = PandasQuery.conditional_replace(df, 'a', 2, ['b'], [5])
        assert list(result['b']) == [0, 5, 5]


class TestFilterByRange:
    def test_filter_by_range(self):
        df = pd.DataFrame({'a': [1, 2, 3, 4]})
        result = PandasQuery.filter_by_range(df, 'a', 2, 3)
        assert set(result['a']) == {2, 3}


class TestFilterByMultipleValues:
    def test_filter_by_multiple_values(self):
        df = pd.DataFrame({'a': [1, 2, 3, 4]})
        result = PandasQuery.filter_by_multiple_values(df, 'a', [2, 4])
        assert set(result['a']) == {2, 4}


class TestFilterByRegex:
    def test_filter_by_regex(self):
        df = pd.DataFrame({'a': ['foo', 'bar', 'foobar']})
        result = PandasQuery.filter_by_regex(df, 'a', '^foo')
        assert set(result['a']) == {'foo', 'foobar'}

    def test_filter_by_regex_case(self):
        df = pd.DataFrame({'a': ['FOO', 'foo']})
        result = PandasQuery.filter_by_regex(df, 'a', 'foo', case=False)
        assert set(result['a']) == {'FOO', 'foo'}


class TestFilterByNull:
    def test_filter_by_null(self):
        df = pd.DataFrame({'a': [1, None, 3]})
        result = PandasQuery.filter_by_null(df, 'a')
        assert len(result) == 1
        assert pd.isna(result['a'].iloc[0])

    def test_filter_by_not_null(self):
        df = pd.DataFrame({'a': [1, None, 3]})
        result = PandasQuery.filter_by_null(df, 'a', is_null=False)
        assert set(result['a']) == {1, 3}
