import os
import yaml

from .base import BaseDataSource


class DataSource(BaseDataSource):
    folder: str
    environ: str
    name: str
    schema_name: str
    table_name: str
    segment: str | None = None

    def __init__(self, folder: str, environ: str, name: str, schema_name: str, table_name: str, segment: str | None = None, **kwargs):
        self.folder = folder
        self.environ = environ
        self.name = name
        self.schema_name = schema_name
        self.table_name = table_name
        self.segment = segment
        self.data = []

    @property
    def filename(self) -> str:
        if self.segment:
            return f"{self.schema_name}@{self.table_name}#{self.segment}.dat"
        return f"{self.schema_name}@{self.table_name}.dat"

    def load(self):
        path = os.path.join(self.folder, self.environ, self.name, self.filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Data source file {path} does not exist.")
        with open(path, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)

    def save(self):
        path = os.path.join(self.folder, self.environ, self.name, self.filename)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.data,
                f,
                indent=2,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
            )
