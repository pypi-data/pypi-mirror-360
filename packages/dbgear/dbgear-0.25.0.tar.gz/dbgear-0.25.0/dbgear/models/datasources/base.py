from typing import Any
from abc import ABCMeta, abstractmethod


class BaseDataSource(metaclass=ABCMeta):
    data: list[dict[str, Any]] = []

    @property
    def filename(self) -> str:
        raise RuntimeError("This property should only be called for DATATYPE_YAML data sources.")

    @abstractmethod
    def load(self):
        raise NotImplementedError("This method should be implemented in subclasses.")
