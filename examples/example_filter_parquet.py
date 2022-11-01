#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author :  ()
# @Link   :
# @Date   : 10/19/2022, 10:20:36 AM

# read
# hash sort
# distribution of block buckets
# to sender

from xml.etree.ElementInclude import include
import pandas
from genericpath import isdir
from pyarrow import csv
from pyarrow._csv import ReadOptions
import json
import os
import sys
import time
from hashlib import blake2b
from os import path
from pathlib import Path

import ray
from apsi.client import LabeledClient
from apsi.server import LabeledServer
from apsi.utils import _query, set_log_level
from dataset.dataset import Dataset
from loguru import logger

here = path.abspath(path.join(path.dirname(__file__)))
print(here)

sys.path.append(path.abspath(path.join(path.dirname(__file__), "../")))

print(str(Path(here) / "apsi.db"))

here_parent = path.abspath(path.join(path.dirname(__file__), "../"))

set_log_level("all")

PARAMS_PATH = str(Path(here_parent) / "src/parameters/100K-1.json")
UNIT = 16
SEVERAL = 2
BUCKET_CAPACITY = UNIT ** SEVERAL

pandas.cut
# OUTPUT_DIR = "./data/10w/apsidb"
output_dir = "./data/10w/apsidb"

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

tmp = Path(here_parent + "/data")
# INPUT_DATA_PATH = str(tmp/"db_10w.csv")
input_data_path = str(tmp/"db_10w.csv")
bucket_tmp_path = str(tmp/"bucket_tmp")


ro = ReadOptions()
ro.block_size = 10 << 20


@ray.remote
def get_bucket_dataset(dataset, bucket_value):
    # return dataset.filter(lambda record: record["hash_item"][:2] == bucket_name)
    print(bucket_value, type(bucket_value))
    ds = dataset.filter(lambda record: int(
        record["hash_item"][:2], 16) == bucket_value)
    ds = ds.drop_columns("hash_item")
    return ds


@ray.remote
class Bucket:
    def __init__(self, name) -> None:
        self.name = name
        # self.dataset = dataset
        # self.dataset = self.get_bucket_dataset(
        #     bucket_name=name, dataset=dataset)

    def get_bucket_dataset(self, bucket_name, dataset):
        # ds = self.dataset.filter(
        # lambda record: record["hash_item"][:len(bucket_name)] == bucket_name)
        # ds = self.dataset.map_batches(lambda batch: [record for record in batch if record["hash_item"][:len(bucket_name)] == bucket_name])
        # ds = dataset
        ds = dataset.map_batches(lambda batch: [record for _, record in batch.iterrows() if record["hash_item"][:len(bucket_name)] == bucket_name])  # noqa
        # ds = ds.map_batches(lambda batch: [x for x in batch if x % 2 == 0])
        print("---", ds.count())
        return ds

    def bucket(self, name, dataset):
        # dataset = dataset.to_arrow_refs(dataset)
        tmp_path = f"{bucket_tmp_path}/parquet/{name}"
        dataset.write_parquet(path=tmp_path, try_create_dir=True)
        return tmp_path
        # TODO drop duplicate item
        # return self.dataset

    def encrypt(self, name, dataset):
        partquet_path = self.bucket(name, dataset)
        dataset = ray.data.read_parquet(paths=[partquet_path])
        dataset.show(1)
        print(dataset.schema())
        #         bucket_ds = partition.take_all()
        # data = [(d["item"], d["label"]) for d in bucket_ds]
        # # print(bucket_ds)
        # print("**********")
        # apsi_server.add_items(data)
        # apsi_server.save_db(db_file_path=db_file_path)
        # return db_file_path


@ray.remote
class Supervisor:

    def __init__(self, data_path="", several=2) -> None:
        self.n_bucket = 16 ** several
        self.dataset = self.pre_data(data_path=data_path)
        # self.buckets = self.pre_buckets(n_bucket=self.n_bucket)
        self.bins = self.get_bins()

        # self.workers = [Worker.remote() for _ in range(self.bins)]

    def get_bins(self):
        import numpy as np
        # [hex(bin)[2:] if len(hex(bin)[2:]) ==2 else f"0{hex(bin)[2:]}"  for bin in range(0, 16**2)]
        # self.bins = [hex(bin)[2:] if len(hex(bin)[2:]) ==2 else f"0{hex(bin)[2:]}"  for bin in range(0, self.n_bucket)]
        # bins = np.array([hex(bin)[2:] if len(hex(bin)[2:]) ==2 else f"0{hex(bin)[2:]}"  for bin in range(0, 16**4)])
        self.bins = np.array([hex(bin)[2:] if len(
            hex(bin)[2:]) == 2 else f"0{hex(bin)[2:]}" for bin in range(0, self.n_bucket)])
        # self.bins = [bin for bin in range(1, self.n_bucket)]
        return self.bins

    def get_bucket(self, bucket_name, dataset):
        # bucket_ds = self.get_bucket_dataset(bucket_name=bucket_name)
        # print("=-=-=", bucket_ds.count())
        bucket = Bucket.remote(name=bucket_name, dataset=dataset)
        return bucket

    def set_bucket(self, bucket_name, dataset):
        # bucket_ds = self.get_bucket_dataset(bucket_name=bucket_name)
        # print("=-=-=", bucket_ds.count())
        bucket = Bucket.remote(name=bucket_name, dataset=dataset)
        return bucket

    def pre_buckets(self, n_bucket):
        buckets = []
        for n in range(n_bucket):
            bucket_value = 0xff - n
            if bucket_value < 0:
                break
            print(bucket_value)
            bucket_value_hex = hex(bucket_value)[SEVERAL:]
            if len(bucket_value_hex) < 2:
                bucket_value_hex = f"0{bucket_value_hex}"
            bucket_name = bucket_value_hex
            # bucket_ds = self.get_bucket_dataset(bucket_name=bucket_name)
            bucket = self.get_bucket(bucket_name=bucket_name)
            buckets.append(bucket)
        return buckets

    def read_csv(self, data_path):
        """read data from csv.

        :param data_path: _description_
        :type data_path: _type_
        :return: _description_
        :rtype: _type_
        """
        print(data_path)
        start = time.time()
        # dataset = Dataset()
        # ds = dataset.read(format="csv", paths=data_path, parallelism=500)

        ds = ray.data.read_csv(
            paths=[data_path], **{"read_options": ro}).repartition(200)
        ds.schema()
        print("***")
        ds.show(2)

        print("***")
        print("The CSV file reading {} strip data takes {}s:".format(
            ds.count(), time.time() - start))

        return ds

    def hash_sort(self, ds):
        """
        1. hash item
        2. sort by hash_item

        :param ds: _description_
        :type ds: _type_
        :return: _description_
        :rtype: _type_
        """
        ds = ds.map(lambda record: {"item": record["item"], "hash_item": blake2b(
            str.encode(record["item"]), digest_size=16).hexdigest(), "label": record["label"]})
        ds = ds.sort("hash_item")
        ds.schema()
        print("***")
        ds.show(2)
        return ds

    def pre_data(self, data_path):
        ds = self.read_csv(data_path=data_path)
        ds = self.hash_sort(ds)
        print(ds.show(1))
        return ds

    def work3(self):
        import pyarrow as pa
        import pandas as pd
        tasks = []
        i = 0
        l = 0
        bucket = []

        for bin in self.bins:
            ds = self.dataset.map_batches(
                fn=lambda batch: [record for _, record in batch.iterrows(
                ) if record["hash_item"][:len(bin)] == bin],
                batch_format="native")
            # noqa
            print(ds.schema(), ds.count())
            worker = Bucket.remote(name=bin)
            ds = pd.Series.to_frame(ds)
            ds = ds.from_pandas(ds)
            print(ds.schema(), ds.count())
            tasks.append(worker.bucket.remote(name=bin, dataset=ds))
        return tasks
        # return ray.get([b.bucket.remote() for b in self.buckets])

    def work(self):
        import pyarrow as pa
        tasks = []
        i = 0
        l = 0
        bucket = []
        for record in self.dataset.iter_rows():
            bin = self.bins[i]
            if record["hash_item"][:2] == bin:
                # bucket.append(record)
                bucket.append(dict(record))
                # print(bucket)
                # time.sleep(100)
            else:
                i += 1
                # save bucket TODO
                # tasks.append(self.set_bucket(bucket_name=bin, dataset=bucket))
                dataset = ray.data.from_items(bucket)
                dataset.schema()
                print("***")
                dataset.show(2)

                print("***")
                # time.sleep(100)

                worker = Bucket.remote(name=bin)
                tasks.append(worker.bucket.remote(name=bin, dataset=dataset))
                # tasks.append(self.set_bucket(bucket_name=bin, dataset=bucket))
                l += len(bucket)
                print(i, bin, len(bucket), bucket[:1], bucket[-1:])
                bucket = [dict(record)]
        print(i, bin, len(bucket), bucket[:1], bucket[-1:])
        # last bucket
        # tasks.append(self.set_bucket(bucket_name=bin, dataset=bucket))
        # dataset = ray.data.from_arrow_refs(bucket)
        dataset = ray.data.from_items(bucket)

        worker = Bucket.remote(name=bin)
        tasks.append(worker.encrypt.remote(name=bin, dataset=dataset))
        # tasks.append(worker.bucket.remote(name=bin, dataset=dataset))
        l += len(bucket)
        return tasks
        # return ray.get([b.bucket.remote() for b in self.buckets])


if __name__ == "__main__":

    import apsi
    s = time.time()
    ray.init()
    # ray.init(address='ray://118.190.39.100:30007/',
    # ray.init(address='ray://118.190.39.100:37937/',runtime_env={"py_modules": [apsi], "excludes": []}, namespace="pyapsi")
    # ray.init(address='ray://118.190.39.100:30007/',runtime_env={"py_modules": [apsi], "pip": ["loguru"]}, namespace="pyapsi")
    sup = Supervisor.remote(data_path=input_data_path, several=SEVERAL)
    tasks = sup.work.remote()
    # ready_ids, remaining_ids = ray.wait(tasks, num_returns=10, timeout=100)

    ids = ray.get(tasks)

    print(ray.get(ids))
    logger.debug(f"Distributed actor execution: {(time.time() - s):.3f}")
