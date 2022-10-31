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
import cloudpickle as pickle

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
# output_dir = "./data/10w/apsidb"
output_dir = "./data/100w/apsidb"

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

tmp = Path(here_parent + "/data")
# input_data_path = str(tmp/"db_10w.csv")
input_data_path = str(tmp/"db_100w.csv")
bucket_tmp_path = str(tmp/"bucket_tmp")


ro = ReadOptions()
ro.block_size = 10 << 20


def save_bucket_tmp(tmp_path, data):
    with open(tmp_path, "wb") as f:
        pickle.dump(data, f)


def load_bucket_tmp(tmp_path):
    with open(tmp_path, "rb") as f:
        data = pickle.load(f)
    return data


def get_params(params_path=None):
    """Get APSI parameters string.

    :param params_path: _description_, defaults to None
    :type params_path: _type_, optional
    :return: _description_
    :rtype: _type_
    """

    if not params_path:
        params_path = str(Path(here_parent) / "src/parameters/100k-1.json")
    print(params_path)
    with open(params_path, "r") as f:
        params_string = json.dumps(json.load(f))
    return params_string


def get_db(db_file_path):
    set_log_level("all")
    params_string = get_params(params_path=PARAMS_PATH)
    apsi_server = LabeledServer()
    if os.path.isfile(db_file_path):
        # load db
        apsi_server.load_db(db_file_path=db_file_path)
        time.sleep(1)
    else:
        # init db
        apsi_server.init_db(params_string, max_label_length=64)
    return apsi_server


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
        tmp_path = f"{bucket_tmp_path}/{name}"
        save_bucket_tmp(tmp_path=tmp_path, data=dataset)
        return tmp_path

    def encrypt(self, name, dataset):
        # read
        tmp_path = self.bucket(name, dataset)
        dataset = load_bucket_tmp(tmp_path=tmp_path)

        db_file_path = f"{output_dir}/{name}.db"
        if not os.path.isdir(path.dirname(db_file_path)):
            os.makedirs(path.dirname(db_file_path))
        apsi_server = get_db(db_file_path)

        data = [(d["item"], d["label"]) for d in dataset]
        apsi_server.add_items(data)
        apsi_server.save_db(db_file_path=db_file_path)
        return len(dataset)


@ray.remote
class Supervisor:

    def __init__(self, data_path="", several=2) -> None:
        self.n_bucket = 16 ** several
        self.dataset = self.pre_data(data_path=data_path)
        # self.buckets = self.pre_buckets(n_bucket=self.n_bucket)
        self.bins = self.get_bins()

        # self.workers = [Bucket.remote() for _ in range(self.bins)]

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

    def work(self):
        import pyarrow as pa
        tasks = []
        i = 0
        l = 0
        block = []
        for record in self.dataset.iter_rows():
            bin = self.bins[i]
            if record["hash_item"][:2] == bin:
                block.append(dict(record))
            else:
                i += 1
                # save bucket TODO

                worker = Bucket.remote(name=bin)
                tasks.append(worker.encrypt.remote(name=bin, dataset=block))
                l += len(block)
                print(i-1, bin, len(block), block[:1], block[-1:])
                block = [dict(record)]
        print(i, bin, len(block), block[:1], block[-1:])
        # last bucket
        worker = Bucket.remote(name=bin)
        tasks.append(worker.encrypt.remote(name=bin, dataset=block))
        l += len(block)
        return tasks


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
