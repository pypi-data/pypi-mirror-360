import os
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from tempfile import NamedTemporaryFile
from python_pandas_translation.pandas_io import PandasIO
import tempfile


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            'name': ['Alice', 'Bob'],
            'age': [30, 25]
        }
    )


@pytest.fixture
def pandas_io():
    return PandasIO()


class TestCSVIO:
    def test_save_csv(self, sample_df: pd.DataFrame, pandas_io: PandasIO) -> None:
        with NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            pandas_io.save_csv(df=sample_df, path=tmp_path)

            # Verify if the file is saved and content is correct
            saved_df = pandas_io.load_csv(path=tmp_path)
            assert_frame_equal(saved_df, sample_df)
        finally:
            os.remove(path=tmp_path)

    def test_load_csv(self, sample_df: pd.DataFrame, pandas_io: PandasIO) -> None:
        with NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            pandas_io.save_csv(df=sample_df, path=tmp_path, index=False)
            loaded_df = pandas_io.load_csv(path=tmp_path)
            assert_frame_equal(loaded_df, sample_df)
        finally:
            os.remove(path=tmp_path)

    def test_load_csv_error_handling(self, pandas_io: PandasIO) -> None:
        with pytest.raises(Exception):
            pandas_io.load_csv(path="non_existent_file.csv")

    def test_save_csv_error_handling(self, sample_df: pd.DataFrame, pandas_io: PandasIO) -> None:
        # Simulate an error during save by providing invalid file path
        with pytest.raises(OSError):
            pandas_io.save_csv(df=sample_df, path="/invalid/path/to/file.csv")


class TestExcelIO:
    def test_save_excel(self, sample_df: pd.DataFrame, pandas_io: PandasIO) -> None:
        with NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            pandas_io.save_excel(df=sample_df, path=tmp_path)
            # Verify if the file is saved and content is correct
            saved_df = pandas_io.load_excel(path=tmp_path)
            assert_frame_equal(saved_df, sample_df)
        finally:
            os.remove(path=tmp_path)

    def test_load_excel(self, sample_df: pd.DataFrame, pandas_io: PandasIO) -> None:
        with NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            pandas_io.save_excel(df=sample_df, path=tmp_path, index=False)
            loaded_df = pandas_io.load_excel(path=tmp_path)
            assert_frame_equal(loaded_df, sample_df)
        finally:
            os.remove(path=tmp_path)

    def test_load_excel_error_handling(self, pandas_io: PandasIO) -> None:
        with pytest.raises(Exception):
            pandas_io.load_excel(path="non_existent_file.xlsx")

    def test_save_excel_error_handling(self, sample_df: pd.DataFrame, pandas_io: PandasIO) -> None:
        # Simulate an error during save by providing invalid file path
        with pytest.raises(OSError):
            pandas_io.save_excel(df=sample_df, path="/invalid/path/to/file.xlsx")


class TestTXTIO:
    def test_save_txt(self, sample_df: pd.DataFrame, pandas_io: PandasIO) -> None:
        with NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            pandas_io.save_txt(df=sample_df, path=tmp_path, sep='\t')
            # Verify if the file is saved and content is correct
            saved_df = pandas_io.load_txt(path=tmp_path, sep='\t')
            assert_frame_equal(saved_df, sample_df)
        finally:
            os.remove(path=tmp_path)

    def test_load_txt(self, sample_df: pd.DataFrame, pandas_io: PandasIO) -> None:
        with NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            pandas_io.save_csv(df=sample_df, path=tmp_path, index=False, sep='\t')
            loaded_df = pandas_io.load_txt(path=tmp_path, sep='\t')
            assert_frame_equal(loaded_df, sample_df)
        finally:
            os.remove(path=tmp_path)

    def test_load_txt_error_handling(self, pandas_io: PandasIO) -> None:
        with pytest.raises(Exception):
            pandas_io.load_txt(path="non_existent_file.txt")

    def test_save_txt_error_handling(self, sample_df: pd.DataFrame, pandas_io: PandasIO) -> None:
        # Simulate an error during save by providing invalid file path
        with pytest.raises(OSError):
            pandas_io.save_txt(df=sample_df, path="/invalid/path/to/file.txt", sep='\t')


class TestLoadCSV:
    def test_load_csv(self):
        df = pd.DataFrame({'a': [1, 2]})
        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            tmp.flush()
            loaded = PandasIO.load_csv(tmp.name)
        assert loaded.equals(df)
        os.remove(tmp.name)


class TestLoadExcel:
    def test_load_excel(self):
        df = pd.DataFrame({'a': [1, 2]})
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            df.to_excel(tmp.name, index=False)
            loaded = PandasIO.load_excel(tmp.name)
        assert loaded.equals(df)
        os.remove(tmp.name)


class TestLoadTxt:
    def test_load_txt(self):
        df = pd.DataFrame({'a': [1, 2]})
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w+', delete=False) as tmp:
            df.to_csv(tmp.name, sep='|', index=False)
            tmp.flush()
            loaded = PandasIO.load_txt(tmp.name, sep='|')
        assert loaded.equals(df)
        os.remove(tmp.name)


class TestSaveCSV:
    def test_save_csv(self):
        df = pd.DataFrame({'a': [1, 2]})
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            PandasIO.save_csv(df, tmp.name)
            loaded = pd.read_csv(tmp.name)
        assert loaded.equals(df)
        os.remove(tmp.name)


class TestSaveExcel:
    def test_save_excel(self):
        df = pd.DataFrame({'a': [1, 2]})
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            PandasIO.save_excel(df, tmp.name)
            loaded = pd.read_excel(tmp.name)
        assert loaded.equals(df)
        os.remove(tmp.name)


class TestSaveTxt:
    def test_save_txt(self):
        df = pd.DataFrame({'a': [1, 2]})
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            PandasIO.save_txt(df, tmp.name, sep='|')
            loaded = pd.read_csv(tmp.name, sep='|')
        assert loaded.equals(df)
        os.remove(tmp.name)


class TestLoadJson:
    def test_load_json(self):
        df = pd.DataFrame({'a': [1, 2]})
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w+', delete=False) as tmp:
            df.to_json(tmp.name, orient='records')
            tmp.flush()
            loaded = PandasIO.load_json(tmp.name, orient='records')
        assert loaded.equals(df)
        os.remove(tmp.name)


class TestSaveJson:
    def test_save_json(self):
        df = pd.DataFrame({'a': [1, 2]})
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            PandasIO.save_json(df, tmp.name, orient='records')
            loaded = pd.read_json(tmp.name, orient='records')
        assert loaded.equals(df)
        os.remove(tmp.name)


class TestPreviewFileHead:
    def test_preview_file_head(self):
        import tempfile
        lines = ['a,b\n', '1,2\n', '3,4\n']
        with tempfile.NamedTemporaryFile('w+', delete=False) as tmp:
            tmp.writelines(lines)
            tmp.flush()
            preview = PandasIO.preview_file_head(tmp.name, n=2)
        assert preview == ''.join(lines[:2])
        os.remove(tmp.name)

    def test_preview_file_head_short_file(self):
        import tempfile
        lines = ['a,b\n']
        with tempfile.NamedTemporaryFile('w+', delete=False) as tmp:
            tmp.writelines(lines)
            tmp.flush()
            preview = PandasIO.preview_file_head(tmp.name, n=5)
        assert preview == ''.join(lines)
        os.remove(tmp.name)


class TestAppendToCSV:
    def test_append_to_csv(self):
        import tempfile
        df1 = pd.DataFrame({'a': [1, 2]})
        df2 = pd.DataFrame({'a': [3, 4]})
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', delete=False) as tmp:
            df1.to_csv(tmp.name, index=False)
            tmp.flush()
            PandasIO.append_to_csv(df2, tmp.name, header=False, index=False)
            loaded = pd.read_csv(tmp.name)
        assert list(loaded['a']) == [1, 2, 3, 4]
        os.remove(tmp.name)

    def test_append_to_csv_empty(self):
        import tempfile
        df = pd.DataFrame({'a': [1]})
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', delete=False) as tmp:
            tmp.flush()
            PandasIO.append_to_csv(df, tmp.name, header=True, index=False)
            loaded = pd.read_csv(tmp.name)
        assert list(loaded['a']) == [1]
        os.remove(tmp.name)
