import pandas as pd
from s3fs import S3FileSystem

from .base import StorageStrategy


class AwsStorageStrategy(StorageStrategy):
    def __init__(self, connection_string: str):
        super().__init__(connection_string)

    def get_filesystem(self):
        storage_options = self._parse_connection_string()

        return S3FileSystem(
            key=storage_options["AccessKeyId"],
            secret=storage_options["SecretAccessKey"],
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
