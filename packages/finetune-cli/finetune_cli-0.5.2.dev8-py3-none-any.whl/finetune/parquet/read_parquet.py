import pandas as pd
import os


class ParquetReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self._data = None

    def __enter__(self):
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"文件路径不存在：{self.file_path}")

            self._data = pd.read_parquet(self.file_path)
            return self
        except Exception as e:
            raise RuntimeError(f"无法打开 Parquet 文件：{e}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_line(self, row_number, column_name=None):
        """
        读取指定行的数据，并返回字符串格式。

        :param row_number: 行索引（从0开始）
        :param column_name: 可选，指定要返回的列名称
        :return: 指定行数据的字符串表示
        """
        if row_number >= len(self._data):
            raise IndexError(f"行号越界，总共有 {len(self._data)} 行，无效索引：{row_number}")
        row_data = self._data.iloc[row_number]

        if column_name is not None:
            if column_name not in self._data.columns:
                raise ValueError(f"列名不存在：{column_name}")
            return str(row_data[column_name])
        else:
            return ", ".join([f"{col}: {row_data[col]}" for col in self._data.columns])

    def get_raw_line(self, row_number, column_name=None):
        """
        读取指定行的数据，并返回字符串格式。

        :param row_number: 行索引（从0开始）
        :param column_name: 可选，指定要返回的列名称
        :return: 指定行数据的字符串表示
        """
        if row_number >= len(self._data):
            raise IndexError(f"行号越界，总共有 {len(self._data)} 行，无效索引：{row_number}")
        row_data = self._data.iloc[row_number]

        if column_name is not None:
            if column_name not in self._data.columns:
                raise ValueError(f"列名不存在：{column_name}")
            return row_data[column_name]
        else:
            return row_data

    @property
    def num_rows(self):
        """返回文件中的总行数"""
        return len(self._data) if self._data is not None else 0

    @property
    def num_columns(self):
        """返回文件中的总列数"""
        return len(self._data.columns) if self._data is not None else 0

    def get_all_columns(self):
        """返回所有的列名"""
        return list(self._data.columns) if self._data is not None else []

