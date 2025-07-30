from abc import ABC, abstractmethod

import pandas as pd
from fsspec import AbstractFileSystem


class StorageStrategy(ABC):
    _fs: AbstractFileSystem
    _connection_string: str

    def __init__(self, connection_string: str):
        self._connection_string = connection_string
        self._fs = self.get_filesystem()

    def get_storage_options(self) -> dict:
        return self._fs.storage_options

    @abstractmethod
    def get_filesystem(self) -> AbstractFileSystem:
        raise NotImplementedError(
            "Este método deve ser implementado pela estratégia de armazenamento específica."
        )

    @abstractmethod
    def read_dataframe(self, path: str) -> pd.DataFrame:
        raise NotImplementedError(
            "Este método deve ser implementado pela estratégia de armazenamento específica."
        )

    @abstractmethod
    def write_dataframe(self, df: pd.DataFrame, path: str):
        raise NotImplementedError(
            "Este método deve ser implementado pela estratégia de armazenamento específica."
        )

    @abstractmethod
    def exists_file(self, path: str) -> bool:
        raise NotImplementedError(
            "Este método deve ser implementado pela estratégia de armazenamento específica."
        )

    @abstractmethod
    def delete_file(self, path: str):
        raise NotImplementedError(
            "Este método deve ser implementado pela estratégia de armazenamento específica."
        )

    @abstractmethod
    def copy_file(self, source_path: str, target_path: str):
        raise NotImplementedError(
            "Este método deve ser implementado pela estratégia de armazenamento específica."
        )

    def _parse_connection_string(self) -> dict:
        return dict(
            item.split("=", 1)
            for item in self._connection_string.split(";")
            if "=" in item
        )
