#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pre_bucket.py
# @Author :  ()
# @Link   :
# @Date   : 10/25/2022, 3:23:29 PM

from pyarrow import csv
from pyarrow._csv import ReadOptions
import pickle
import cloudpickle as pickle
import ray
from apsi.utils import _query, set_log_level
from dataset.dataset import Dataset
from os import path
import os
import sys
import time
from hashlib import blake2b
from loguru import logger


from pathlib import Path

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


DB_TOTAL = '100w'
tmp = Path(here_parent + "/data")
input_data_path = str(tmp/f"db_{DB_TOTAL}.csv")
# output_dir = f"./data/{DB_TOTAL}/apsidb"
bucket_tmp_path = f"./data/tmp_{DB_TOTAL}/m_buckets"


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
    # dataset = Dataset()
    # ds = dataset.read(format="csv", paths=data_path, parallelism=500)
    ds = ray.data.read_csv(paths=[data_path], **{"read_options": ro})
    # out_path = "./temp/iterative.parquet"
    # ds = ray.data.read_parquet(out_path)
    ds.schema()
    print("***")
    ds.show(2)
    print("***")
    logger.debug("The CSV file reading {} strip data takes {}s:".format(
        ds.count(), time.time() - start))
    return ds


def pre_data(data_path):
    if not os.path.exists(data_path):
        logger.error(f"{data_path} not exists!!!")
    ds = read_csv(data_path=data_path)
    ds = hash_sort(ds)
    return ds


# def map_single(data):
#     # print(type(data), data.count())
#     # outputs = [list() for _ in range(npartitions)]
#     set_log_level("all")
#     m_buckets = {}
#     # outputs = buckets
#     # print("output len: ", len(outputs))
#     for idx, row in data.iterrows():
#         # logger.debug("hash value: hex: {} int: {}".format( {row["hash_item"][:2]}, {int(row["hash_item"][:2], 16)}))
#         index_key = row["hash_item"][:2]
#         row = row.drop(labels="hash_item")
#         if m_buckets.get(index_key, None) is None:
#             m_buckets[index_key] = []

#         m_buckets[index_key].append(row)
#     logger.debug(f"outputs type: {type(m_buckets)}, size: {len(m_buckets)}")
#     # print(len(outputs))
#     tmp_path = f"./tmp/single/m_buckets/{index_key}"
#     if not os.path.isdir(path.dirname(tmp_path)):
#         os.makedirs(path.dirname(tmp_path))

#     # if os.path.isfile(tmp_path):
#     #     # load
#     #     pre_bucket = pickle.load(tmp_path)

#     with open(tmp_path, "wb") as f:
#         pickle.dump(m_buckets, f)
#     return m_buckets


def save_bucket_tmp(tmp_path, data):
    with open(tmp_path, "wb") as f:
        pickle.dump(data, f)
        print(f"pickle dump: {tmp_path}")
    return tmp_path


def load_bucket_tmp(tmp_path):
    with open(tmp_path, "rb") as f:
        data = pickle.load(f)
    return data


@ray.remote
def map(data):
    """Map: pickle item into bucket
    1. calc index key
    2. bucket = buckets[index_key]
    3. drop hash_item
    4. put bucket   

    :param data: _description_
    :type data: _type_
    :return: _description_
    :rtype: _type_
    """
    s = time.time()
    set_log_level("all")
    m_buckets = {}

    for idx, row in data.iterrows():
        index_key = row["hash_item"][:SEVERAL]
        row = row.drop(labels="hash_item")
        if m_buckets.get(index_key, None) is None:
            m_buckets[index_key] = []
        m_buckets[index_key].append(row)

    for k, v in m_buckets.items():

        tmp_path = f"{bucket_tmp_path}/{k}"
        if not os.path.isdir(path.dirname(tmp_path)):
            os.makedirs(path.dirname(tmp_path))

        if os.path.isfile(tmp_path):
            tmp_data = load_bucket_tmp(tmp_path=tmp_path)
            print(f"{type(tmp_data)}, add items: {len(tmp_data)}")
            v.extend(tmp_data)
            # print(v)
            # v = v.extend([t for t in tmp_data if t not in v])
            print(f"total items: {len(v)}")
        save_bucket_tmp(tmp_path, v)
    print(f">>> Map execution: {(time.time() - s):.3f}")
    return m_buckets


@ray.remote
def run():
    # npartitions = UNIT ** SEVERAL     # npartitions * step = 16 ** 30
    # tmp = Path(here_parent + "/data")
    # data_path = str(tmp/"db_10w.csv")
    dataset = pre_data(data_path=input_data_path)
    print(dataset.schema(), dataset.count())
    # print("npartitions: ", npartitions)
    buckets = {}
    map_outputs = []
    for partition in dataset.iter_batches(batch_size=10000):
        # map_outputs.append(map.remote(partition))
        m = map.remote(partition)
        ray.get(m)

    ray.get(map_outputs)


def display(dir_path=""):
    g = os.walk(dir_path)
    fl = []
    for path, dir_list, file_list in g:
        for file_name in file_list:
            print(os.path.join(path, file_name))
            fl.append(os.path.join(path, file_name))
    return fl

    # tmp_path = f"./data/tmp/m_buckets/{index_key}"


def load_file(display_path=None):
    fl = display(display_path)
    i = 0
    for f in fl:
        with open(f, "rb") as f:
            p = pickle.load(f)
            print(type(p))
            i += len(p)
    print(i)


if __name__ == "__main__":
    import json
    # ray.init(
    #     _system_config={
    #         # Allow spilling until the local disk is 99% utilized.
    #         # This only affects spilling to the local file system.
    #         # "local_fs_capacity_threshold": 0.99,

    #         "object_spilling_config": json.dumps(
    #             {
    #                 "type": "filesystem",
    #                 "params": {
    #                     "directory_path": "/tmp/spill",
    #                     # "buffer_size": 1_000_000,
    #                     "buffer_size": 200 * 1024 * 1024, # Use a 100MB buffer for writes

    #                 }
    #             },
    #         )
    #     },
    # )
    s = time.time()
    ray.get(run.remote())
    print(f"Distrubuted execution: {(time.time() - s):.3f}")
    load_file(bucket_tmp_path)
