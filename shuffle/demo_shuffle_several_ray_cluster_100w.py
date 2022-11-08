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

import json
import os
import sys
import time
from hashlib import blake2b
from os import path
from pathlib import Path

import cloudpickle as pickle
import numpy as np
import pandas
import ray
from loguru import logger
from pyarrow._csv import ReadOptions

from apsi.client import LabeledClient
from apsi.server import LabeledServer
from apsi.utils import _query, set_log_level
from dataset.dataset import Dataset

sys.path.append(path.abspath(path.join(path.dirname(__file__), "../")))

here = path.abspath(path.join(path.dirname(__file__)))
print(here)
here_parent = path.abspath(path.join(path.dirname(__file__), "../"))

set_log_level("all")

# PARAMS_PATH = str( "../src/parameters/100K-1.json")
PARAMS_PATH = str(Path(here_parent) / "src/parameters/100K-1.json")
UNIT = 16
SEVERAL = 4
BUCKET_CAPACITY = UNIT ** SEVERAL

# OUTPUT_DIR = "./data/10w/apsidb"
# OUTPUT_DIR = "./data/100w/apsidb"
OUTPUT_DIR = "/data/100w/apsidb"



tmp = Path(here_parent + "/data")
tmp = Path("/data")
INPUT_DATA_PATH = str(tmp/"db_100w.csv")
# INPUT_DATA_PATH = str(tmp / "db_100w.csv")
BUCKET_TMP_PATH = str(tmp / "bucket_tmp")

ro = ReadOptions()
ro.block_size = 10 << 20


def save_block(tmp_path, data):
    # print("tmp_path: ", tmp_path)
    if not os.path.isdir(path.dirname(tmp_path)):
        os.makedirs(tmp_path)
    if not data:
        return
    else:
        with open(tmp_path, "wb") as f:
            pickle.dump(data, f)


def load_block(tmp_path):
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


def get_db(db_file_path, params_str):
    set_log_level("all")
    if not params_str:
        params_str = get_params(params_path=PARAMS_PATH)
    apsi_server = LabeledServer()
    if os.path.isfile(db_file_path):
        # load db
        apsi_server.load_db(db_file_path=db_file_path)
    else:
        # init db
        apsi_server.init_db(params_str, max_label_length=64)
    return apsi_server


@ray.remote
class Worker:
    def __init__(self, name):
        self.name = name

    def get_block_dataset(self, bucket_name, dataset):
        ds = dataset.map_batches(lambda batch: [record for _, record in batch.iterrows() if
                                                record["hash_item"][:len(bucket_name)] == bucket_name])  # noqa
        return ds

    def block_cut(self, name, dataset):
        # tmp_path = f"{BUCKET_TMP_PATH}/{name}"
        tmp_path = "{bucket_tmp_path}/{name}".format(bucket_tmp_path=BUCKET_TMP_PATH, name=name)
        if dataset:
            save_block(tmp_path=tmp_path, data=dataset)
        return tmp_path

    def encrypt(self, name, dataset, params_str):
        # read
        tmp_path = self.block_cut(name, dataset)
        dataset = load_block(tmp_path=tmp_path)

        db_file_path = f"{OUTPUT_DIR}/{name}.db"
        if not os.path.isdir(path.dirname(db_file_path)):
            os.makedirs(path.dirname(db_file_path))
        apsi_server = get_db(db_file_path, params_str)

        data = [(d["item"], d["label"]) for d in dataset]
        apsi_server.add_items(data)
        apsi_server.save_db(db_file_path=db_file_path)
        return len(dataset)


@ray.remote
class Supervisor:

    def __init__(self, data_path="", several=2,params_str=None) -> None:
        self.several = several
        self.n_bucket = 16 ** several
        self.dataset = self.pre_data(data_path=data_path)
        self.params_str = params_str
        # self.bins = self.get_bins()

    def get_bins(self):
        several = self.several
        # [hex(bin)[2:] if len(hex(bin)[2:]) ==2 else f"0{hex(bin)[2:]}"  for bin in range(0, 16**2)]
        # self.bins = [hex(bin)[2:] if len(hex(bin)[2:]) ==2 else f"0{hex(bin)[2:]}"  for bin in range(0, self.n_bucket)]
        # bins = np.array([hex(bin)[2:] if len(hex(bin)[2:]) ==2 else f"0{hex(bin)[2:]}"  for bin in range(0, 16**4)])
        self.bins = np.array([hex(bin)[2:] if len(hex(bin)[
                             2:]) == several else f"{'0'*(several-len(hex(bin)[2:]))}{hex(bin)[2:]}" for bin in range(0, self.n_bucket)])
        # self.bins = np.array([hex(bin)[2:]  for bin in range(0, self.n_bucket)])
        # self.bins = [bin for bin in range(1, self.n_bucket)]

        print(several, self.n_bucket)
        # print(self.bins)

        # print(len(self.bins))
        # time.sleep(1)
        return self.bins

    def get_bucket(self, bucket_name, dataset):
        # bucket_ds = self.get_bucket_dataset(bucket_name=bucket_name)
        # print("=-=-=", bucket_ds.count())
        bucket = Worker.remote(name=bucket_name, dataset=dataset)
        return bucket

    def set_bucket(self, bucket_name, dataset):
        # bucket_ds = self.get_bucket_dataset(bucket_name=bucket_name)
        # print("=-=-=", bucket_ds.count())
        bucket = Worker.remote(name=bucket_name, dataset=dataset)
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

    def get_bin(self, i):
        if len(hex(i)[2:]) == self.several:
            bin = hex(i)[2:]
        else:
            bin = f"{'0'*(self.several-len(hex(i)[2:]))}{hex(i)[2:]}"
        print("bin: ", bin)
        return bin

    def work(self):
        tasks = []
        i = 0
        l = 0
        block = []
        for record in self.dataset.iter_rows():
            if i > self.n_bucket:
                break
            # bin = self.bins[i]
            bin = self.get_bin(i)
            if record["hash_item"][:self.several] == bin:
                block.append(dict(record))
            else:
                i += 1
                # save bucket and encrypt
                worker = Worker.remote(name=bin)
                tasks.append(worker.encrypt.remote(name=bin, dataset=block, params_str=self.params_str))
                l += len(block)
                print(i - 1, bin, len(block), block[:1], block[-1:])
                block = [dict(record)]
        print(i, bin, len(block), block[:1], block[-1:])
        # last bucket
        worker = Worker.remote(name=bin)
        tasks.append(worker.encrypt.remote(name=bin, dataset=block, params_str=self.params_str))
        l += len(block)
        return tasks


if __name__ == "__main__":
    s = time.time()
    # ray.init()
    # ray.init(address='auto', namespace="pyapsi")
    # ray.init(address='ray://192.168.99.26:10001/')
    # ray.init(address='ray://118.190.39.100:30007/')

    
    params_obj = get_params(params_path=PARAMS_PATH)
    ray.init(address='ray://192.168.99.30:32657/')
    params_obj_id = ray.put(params_obj)
    print(params_obj_id)
    params_str = ray.get(params_obj_id)
    sup = Supervisor.remote(data_path=INPUT_DATA_PATH, several=SEVERAL, params_str=params_str)
    tasks = sup.work.remote()
    # ready_ids, remaining_ids = ray.wait(tasks, num_returns=10, timeout=100)

    ids = ray.get(tasks)

    print(ray.get(ids))

    logger.debug(f"Distributed actor execution: {(time.time() - s):.3f}")
    ray.shutdown()
