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


# OUTPUT_DIR = "./data/10w/apsidb"
output_dir = "./data/100w/apsidb"

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

tmp = Path(here_parent + "/data")
# INPUT_DATA_PATH = str(tmp/"db_10w.csv")
input_data_path = str(tmp/"db_100w.csv")


def hash_sort(ds):
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


ro = ReadOptions()
ro.block_size = 10 << 20


def read_csv(data_path):
    """read data from csv.

    :param data_path: _description_
    :type data_path: _type_
    :return: _description_
    :rtype: _type_
    """
    print(data_path)
    start = time.time()
    dataset = Dataset()
    # ds = dataset.read(format="csv", paths=data_path, parallelism=500)

    ds = ray.data.read_csv(paths=[data_path], **{"read_options": ro})
    ds.schema()
    print("***")
    ds.show(2)
    print("***")
    logger.debug("The CSV file reading {} strip data takes {}s:".format(
        ds.count(), time.time() - start))

    return ds


def pre_data(data_path):
    ds = read_csv(data_path=data_path)
    ds = hash_sort(ds)
    return ds


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


@ray.remote
def get_bucket_dataset(dataset, bucket_value):
    # return dataset.filter(lambda record: record["hash_item"][:2] == bucket_name)
    print(bucket_value, type(bucket_value))
    ds = dataset.filter(lambda record: int(
        record["hash_item"][:2], 16) == bucket_value)
    ds = ds.drop_columns("hash_item")
    return ds


def get_db(db_file_path):
    params_string = get_params(params_path=PARAMS_PATH)
    apsi_server = LabeledServer()
    if os.path.isfile(db_file_path):
        # load db and insert
        apsi_server.load_db(db_file_path=db_file_path)
    else:
        # init db
        apsi_server.init_db(params_string, max_label_length=64)
    return apsi_server


@ray.remote
class AsyncBucketActor:

    def __init__(self, bucket_name, dataset) -> None:
        self.bucket_name = bucket_name
        self.dataset = dataset
        self.output_path = f"{output_dir}/{bucket_name}.db"

    async def run_filter_bucket(self):
        bucket_name = self.bucket_name
        print("bucket_name: ", bucket_name)
        dataset = self.dataset
        # ds = dataset.filter(lambda record: int(record["hash_item"][:2], 16) == bucket_name)
        ds = dataset.filter(
            lambda record: record["hash_item"][:2] == bucket_name)
        # ds = dataset.drop_columns("hash_item")
        # tmp_path = f"{BUCKET_TMP_PATH}/parquet/{bucket_name}"
        # ds.write_parquet(path=tmp_path, try_create_dir=True )
        return ds

    async def run_encrypt(self, output_path=""):
        print("started")
        # server
        bucket_name = self.bucket_name
        dataset = await self.run_filter_bucket()
        db_file_path = "./data/actor_apsidb/apsi_%s.db" % bucket_name
        print(f"encrypt bucket: {bucket_name}, db path: {db_file_path}")
        if not os.path.isdir(path.dirname(db_file_path)):
            os.makedirs(path.dirname(db_file_path))
        apsi_server = get_db(db_file_path)
        print("**********")
        # print(partition.schema())
        # print(partition)
        # bucket_ds = [row for row in partition.iter_rows()]
        # bucket_ds = partition.take_all()
        data = [(d["item"], d["label"]) for d in dataset.iter_rows()]
        # print(bucket_ds)
        print("********** data len: ", len(data))
        if data:
            apsi_server.add_items(data)
            apsi_server.save_db(db_file_path=self.output_path)
        return db_file_path


def display(dir_path=""):
    g = os.walk(dir_path)
    fl = []
    for path, dir_list, file_list in g:
        for file_name in file_list:
            print(os.path.join(path, file_name))
            fl.append(os.path.join(path, file_name))
    return fl

def load_file(path):
    fl = display(path)
    i = 0
    for f in fl:
        apsi_server = get_db(f)
        i += 1
    print(i)


if __name__ == "__main__":

    s = time.time()
    n_bucket = 16**2     # npartitions * step = 16 ** 30
    # step = 16 ** 0

    dataset = pre_data(data_path=input_data_path)
    tasks = []
    for n in range(n_bucket):
        bucket_value = 0xff - n
        if bucket_value < 0:
            break
        print(bucket_value)
        bucket_value_hex = hex(bucket_value)[SEVERAL:]
        if len(bucket_value_hex) < 2:
            bucket_value_hex = f"0{bucket_value_hex}"

        actor = AsyncBucketActor.options(max_concurrency=16).remote(
            bucket_name=bucket_value_hex, dataset=dataset)

        print("*** bucket ***: ", bucket_value_hex)
        # tmp_path = f"{BUCKET_TMP_PATH}/{bucket_value_hex}"
        encrypt = actor.run_encrypt.remote()
        # ray.get(encrypt)
        tasks.append(encrypt)
        print(f"Bucket execution: {(time.time() - s):.3f}")
    ray.get(tasks)
    print(f"Distrubuted execution: {(time.time() - s):.3f}")

    load_file(output_dir)