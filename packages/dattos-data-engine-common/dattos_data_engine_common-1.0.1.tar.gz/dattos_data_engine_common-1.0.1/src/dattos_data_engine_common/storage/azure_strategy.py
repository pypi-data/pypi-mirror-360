import pandas as pd
from adlfs import AzureBlobFileSystem

from .base import StorageStrategy


class AzureStorageStrategy(StorageStrategy):
    def __init__(self, connection_string: str):
        super().__init__(connection_string)

    def get_filesystem(self) -> AzureBlobFileSystem:
        storage_options = self._parse_connection_string()

        return AzureBlobFileSystem(
            account_name=storage_options["AccountName"],
            account_key=storage_options["AccountKey"],
            connection_string=self._connection_string,
        )

    def read_dataframe(self, path: str) -> pd.DataFrame:
        return pd.read_parquet(path, storage_options=self.get_storage_options())

    def write_dataframe(self, df: pd.DataFrame, path: str):
        df.to_parquet(path, storage_options=self.get_storage_options(), index=False)

    def exists_file(self, path: str) -> bool:
        return self._fs.exists(path)

    def delete_file(self, path: str):
        self._fs.rm(path)

    def copy_file(self, source_path: str, target_path: str):
        self._fs.copy(source_path, target_path)
