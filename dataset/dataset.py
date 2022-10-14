#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by lizhiwei at 2022/9/21

import sys
from enum import Enum
from typing import Union, List

import ray
import ray.data
from loguru import logger
from ray.data import Dataset

# logger.add(sys.stdout, colorize=True)


class Dataset(object):
    """
    >>>
        pip install "ray[data]"
        performance: https://docs.ray.io/en/latest/data/performance-tips.html#data-performance-tips
    """

    class RemoteStorage(str, Enum):
        # S3 = "S3"
        HDFS = "HDFS"
        GCS = "GCS"
        Azure = "Azure"

    def __init__(self, ray_server_addr: str = "auto") -> None:
        super().__init__()
        import ray
        # ray.init()
        self.custom_data_source = None  # YourCustomDataSource() TODO
        self.read_from_dict = {
            "local": self.read_from_local,
            "remote": self.read_from_remote,
            "memory": self.read_from_memory,
            "disframe": self.read_from_disframe,
            "custom": self.custom_data_source

        }

    def read_from_local(self,
                        format: str,
                        paths: Union[str, List[str]],
                        parallelism: int = -1):
        """Reading Files From Storage.

        :param format:
        :param paths:
        :return:
        """
        print(format, paths)
        format_method_dict = {
            "parquet": ray.data.read_parquet,
            "csv": ray.data.read_csv,
            "json": ray.data.read_json,
            "npy": ray.data.read_numpy,
            "txt": ray.data.read_text,
            "bytes": ray.data.read_binary_files,  # TODO

        }
        method = format_method_dict.get(format, None)
        if method:
            print(method.__name__)
            ds = method(paths, parallelism=parallelism)
            print("* " * 20)
            ds = ds.repartition(200)
            print("* " * 20)
            print(ds)
            return ds
        else:
            logger.error("Illegal format.")

    def read_from_remote(self, format: str, path: str, private: bool = False, *args, **kwargs):
        """Reading from Remote Storage.

        :param format:
        :param path:
        :param private:
        :param args:
        :param kwargs:

        :return:
        """
        # TODO s3, HDFS, gcsfs, adlfs
        # Create a tabular Dataset by reading a Parquet file from a private S3 bucket. TODO

        if not private:
            ds = ray.data.read_parquet(path)
            # ds.show(2)
        else:
            if format == "S3":
                pass
                # import pyarrow as pa
                # # Create a tabular Dataset by reading a Parquet file from a private S3 bucket.
                # # required S3 credentials!
                # region = kwargs["region"]
                # access_key = kwargs["access_key"]
                # secret_key = kwargs["secret_key"]
                # ds = ray.data.read_parquet(
                #     paths,
                #     filesystem=pa.fs.S3FileSystem(
                #         region=region,
                #         access_key=access_key,
                #         secret_key=secret_key,
                #     ),
                # )
            elif format == "HDFS":
                import pyarrow as pa
                # Create a tabular Dataset by reading a Parquet file from HDFS, manually specifying a
                # configured HDFS connection via a Pyarrow HDFSFileSystem instance.
                # cluster/data.

                host = kwargs["host"]
                port = kwargs["port"]
                user = kwargs["user"]
                ds = ray.data.read_parquet(
                    path,  # "hdfs://paths/to/file.parquet",
                    filesystem=pa.fs.HDFSFileSystem(host=host, port=port, user=user),
                )
            elif format == "GCS":
                import gcsfs
                # Create a tabular Dataset by reading a Parquet file from GCS, passing the configured
                # GCSFileSystem.
                # and configure your GCP project and credentials.
                project = kwargs["project"]
                ds = ray.data.read_parquet(
                    path,  # "gs://paths/to/file.parquet",
                    filesystem=gcsfs.GCSFileSystem(project=project),
                )

            elif format == "Azure":
                import adlfs

                # Create a tabular Dataset by reading a Parquet file from Azure Blob Storage, passing
                # the configured AzureBlobFileSystem.
                # paths = (
                #     "az://nyctlc/yellow/puYear=2009/puMonth=1/"
                #     "part-00019-tid-8898858832658823408-a1de80bd-eed3-4d11-b9d4-fa74bfbd47bc-426333-4"
                #     ".c000.snappy.parquet"
                # )
                account_name = kwargs["account_name"]
                ds = ray.data.read_parquet(
                    path,
                    filesystem=adlfs.AzureBlobFileSystem(account_name=account_name)
                )
        return ds

    def read_from_memory(self, format: str, path: str = None):
        """From In-Memory Data.

        :param format:
        :param path:
        :return:
        """
        # import pandas as pd
        # from pyarrow as pa
        # import numpy as np
        format_method_dict = {
            "pandas": ray.data.from_pandas,
            "numpy": ray.data.from_numpy,
            "arrow": ray.data.from_arrow,
            "items": ray.data.from_items,

        }
        method = format_method_dict.get(format, None)
        if method:
            ds = method()
            return ds
        else:
            logger.error("Illegal format.")

    def read_from_disframe(self, format: str, path: str = None):
        # TODO dask, spark, modin, mars
        format_method_dict = {
            "dask": ray.data.from_dask,
            "spark": ray.data.from_dask,
            "modin": ray.data.from_modin,
            "mars": ray.data.from_mars,

        }
        method = format_method_dict.get(format, None)
        if method:
            ds = method()
            return ds
        else:
            logger.error("Illegal format.")

    def read_from_custom(self, *args, **kwargs):
        # Read from a custom datasource.
        ds = ray.data.read_datasource(self.custom_data_source, **kwargs)
        return ds

    def read(self, format: str, paths: Union[str, List[str]], read_from: str = 'local', parallelism: int = 200, *args,
             **kwargs):
        """

        :param format:
        :param paths:
        :param read_from:
        :param parallelism:
        :param args:
        :param kwargs:
        :return:
        """
        print("parallelism: ", parallelism)
        read_method = self.read_from_dict.get(read_from, None)
        print(read_method.__name__)
        if not read_method:
            logger.error("Illegal source...")
        return read_method(format=format, paths=paths, *args, **kwargs)

    def write(self, ds: Dataset, format: str, file_path: str, repartition: int = 0):
        if format == "parquet":
            ds.write_parquet(file_path)
            if repartition != 0:
                ds.repartition(repartition).write_parquet(file_path)
        elif format == "csv":
            ds.write_csv(file_path)
            if repartition != 0:
                ds.repartition(repartition).write_csv(file_path)
        elif format == "json":
            ds.write_json(file_path)
            if repartition != 0:
                ds.repartition(repartition).write_json(file_path)
        elif format == "npy":
            ds.write_numpy(file_path)
            if repartition != 0:
                ds.repartition(repartition).write_numpy(file_path)
        else:
            logger.error("Illegal format.")
