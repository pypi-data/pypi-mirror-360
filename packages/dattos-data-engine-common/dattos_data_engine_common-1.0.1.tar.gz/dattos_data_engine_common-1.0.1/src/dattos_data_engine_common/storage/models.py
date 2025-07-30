from enum import Enum
from pydantic import BaseModel


class DataFrameLocator(BaseModel):
    dataframe_name: str
    url: str


class StorageProvider(Enum):
    AZURE = "Azure"
    AWS = "Aws"


class StorageConfig(BaseModel):
    provider: StorageProvider
    connection_string: str


class Column(BaseModel):
    name: str
    data_type: str
