import importlib

from .base import BaseDataSource


class Factory:
    @staticmethod
    def create(data_type: str, **kwargs) -> BaseDataSource:
        """
        動的にdata_typeに対応するDataSourceクラスのインスタンスを生成する

        Args:
            data_type (str): データソースの種類（例: 'mysql', 'postgres' など）
            *args, **kwargs: DataSourceクラスのコンストラクタ引数

        Returns:
            DataSource: 指定されたデータソースのインスタンス
        """
        module_name = f".{data_type}source"
        class_name = "DataSource"
        try:
            module = importlib.import_module(module_name, __package__)
            data_source_class = getattr(module, class_name)
            return data_source_class(**kwargs)
        except (ModuleNotFoundError, AttributeError) as e:
            raise ValueError(f"DataSource for '{data_type}' not found: {e}")
