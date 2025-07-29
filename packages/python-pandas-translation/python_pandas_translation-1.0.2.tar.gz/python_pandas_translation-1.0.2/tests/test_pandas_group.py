import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from python_pandas_translation.pandas_group import PandasGroup


@pytest.fixture
def pandas_group():
    return PandasGroup()


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        data={
            'category': ['A', 'A', 'B', 'B', 'A'],
            'type': ['X', 'X', 'Y', 'Y', 'Z'],
            'value': [10, 20, 30, 40, 50],
            'score': [1.0, 2.0, 3.0, 4.0, 5.0]
        }
    )


class TestPandasGroup:
    def test_group_mean(self, pandas_group: PandasGroup, sample_df: pd.DataFrame) -> None:
        result = pandas_group.group_mean(df=sample_df, by=['category'])
        expected = pd.DataFrame(
            data={
                'value': [26.666666, 35.0],
                'score': [2.6666667, 3.5]
            },
            index=pd.Index(data=['A', 'B'], name='category')
        )

        assert_frame_equal(result, expected, check_exact=False, rtol=1e-4)

    def test_group_sum(self, pandas_group: PandasGroup, sample_df: pd.DataFrame) -> None:
        result = pandas_group.group_sum(df=sample_df, by=['category'])
        expected = pd.DataFrame(
            data={
                'value': [80, 70],
                'score': [8.0, 7.0]
            },
            index=pd.Index(data=['A', 'B'], name='category')
        )

        assert_frame_equal(result, expected)

    def test_group_count(self, pandas_group: PandasGroup, sample_df: pd.DataFrame) -> None:
        result = pandas_group.group_count(df=sample_df, by=['category'])
        expected = pd.DataFrame(
            data={
                'type': [3, 2],
                'value': [3, 2],
                'score': [3, 2]
            },
            index=pd.Index(data=['A', 'B'], name='category')
        )

        assert_frame_equal(result, expected)


class TestGroupMean:
    def test_group_mean(self):
        df = pd.DataFrame({'a': ['x', 'x', 'y'], 'b': [1, 2, 3]})
        result = PandasGroup.group_mean(df, by=['a'])
        assert result.loc['x', 'b'] == 1.5
        assert result.loc['y', 'b'] == 3


class TestGroupSum:
    def test_group_sum(self):
        df = pd.DataFrame({'a': ['x', 'x', 'y'], 'b': [1, 2, 3]})
        result = PandasGroup.group_sum(df, by=['a'])
        assert result.loc['x', 'b'] == 3
        assert result.loc['y', 'b'] == 3


class TestGroupCount:
    def test_group_count(self):
        df = pd.DataFrame({'a': ['x', 'x', 'y'], 'b': [1, 2, 3]})
        result = PandasGroup.group_count(df, by=['a'])
        assert result.loc['x', 'b'] == 2
        assert result.loc['y', 'b'] == 1


class TestGroupMin:
    def test_group_min(self):
        df = pd.DataFrame({'a': ['x', 'x', 'y'], 'b': [2, 1, 3]})
        result = PandasGroup.group_min(df, by=['a'])
        assert result.loc['x', 'b'] == 1
        assert result.loc['y', 'b'] == 3


class TestGroupMax:
    def test_group_max(self):
        df = pd.DataFrame({'a': ['x', 'x', 'y'], 'b': [2, 1, 3]})
        result = PandasGroup.group_max(df, by=['a'])
        assert result.loc['x', 'b'] == 2
        assert result.loc['y', 'b'] == 3


class TestGroupAgg:
    def test_group_agg(self):
        df = pd.DataFrame({'a': ['x', 'x', 'y'], 'b': [2, 1, 3], 'c': [5, 6, 7]})
        result = PandasGroup.group_agg(df, by=['a'], agg_func={'b': 'sum', 'c': 'mean'})
        assert result.loc['x', 'b'] == 3
        assert result.loc['x', 'c'] == 5.5
        assert result.loc['y', 'b'] == 3
        assert result.loc['y', 'c'] == 7


class TestGroupStd:
    def test_group_std(self):
        df = pd.DataFrame({'a': ['x', 'x', 'y'], 'b': [1, 2, 3]})
        result = PandasGroup.group_std(df, by=['a'])
        assert result.loc['x', 'b'] == 0.7071067811865476
        assert pd.isna(result.loc['y', 'b'])


class TestGroupNunique:
    def test_group_nunique(self):
        df = pd.DataFrame({'a': ['x', 'x', 'y'], 'b': [1, 2, 2]})
        result = PandasGroup.group_nunique(df, by=['a'])
        assert result.loc['x', 'b'] == 2
        assert result.loc['y', 'b'] == 1

    def test_group_nunique_all_unique(self):
        df = pd.DataFrame({'a': ['x', 'y'], 'b': [1, 2]})
        result = PandasGroup.group_nunique(df, by=['a'])
        assert all(result['b'] == 1)
