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
import ray
from apsi.server import LabeledServer
from apsi.client import LabeledClient
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

PARAMS_PATH = str(Path(here_parent) / "src/parameters/100k-1.json")
UNIT = 16
SEVERAL = 2
BUCKET_CAPACITY = UNIT ** SEVERAL


output_dir = "./data/linux/dis_apsidb/"


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
    ds = dataset.read(format="csv", paths=data_path, parallelism=500)
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
def map(data):
    """Map: put item into bucket.
    1. calc index key
    2. bucket = buckets[index_key]
    3. drop hash_item
    4. put bucket    

    :param data: _description_
    :type data: _type_
    :return: _description_
    :rtype: _type_
    """
    set_log_level("all")  # set cpp log level
    buckets = {}
    for idx, row in data.iterrows():
        # logger.debug("hash value: hex: {} int: {}".format( {row["hash_item"][:2]}, {int(row["hash_item"][:2], 16)}))
        index_key = row["hash_item"][:SEVERAL]
        row = row.drop(labels="hash_item")
        if buckets.get(index_key, None) is None:
            buckets[index_key] = []

        buckets[index_key].append(row)
    logger.debug(f"outputs type: {type(buckets)}, size: {len(buckets)}")
    return buckets


def get_apsi_db(db_file_path):
    set_log_level("all")
    apsi_server = LabeledServer()
    params_string = get_params(params_path=PARAMS_PATH)
    if os.path.isfile(db_file_path):
        # load db
        apsi_server.load_db(db_file_path=db_file_path)
    else:
        # init db
        apsi_server.init_db(params_string, max_label_length=64)
    return apsi_server



@ray.remote
def encrypt(k, partition):
    # set_log_level("all")
    # server
    db_file_path = f"{output_dir}{k}.db"
    print(f"encrypt bucket: {k}, db path: {db_file_path}")
    if not os.path.isdir(path.dirname(db_file_path)):
        os.makedirs(path.dirname(db_file_path))
    apsi_server = get_apsi_db(db_file_path)
    data = [(p["item"], p["label"]) for p in partition]
    # print(data)
    apsi_server.add_items(data)
    apsi_server.save_db(db_file_path=db_file_path)
    return db_file_path


# @ray.remote
# class AsyncEncryptActor:
#     async def run_task(self, k, partition):
#         set_log_level("all")
#         # server
#         db_file_path = f"{output_dir}{k}.db"
#         print(f"encrypt bucket: {k}, db path: {db_file_path}")
#         if not os.path.isdir(path.dirname(db_file_path)):
#             os.makedirs(path.dirname(db_file_path))
#         apsi_server = get_apsi_db(db_file_path)
#         data = [(p["item"], p["label"]) for p in partition]
#         # print(data)
#         apsi_server.add_items(data)
#         apsi_server.save_db(db_file_path=db_file_path)
#         return db_file_path

@ray.remote
def reduce(partitions):
    set_log_level("all")
    print(type(partitions), len(partitions))
    logger.debug(f"{type(partitions)} partitions: {len(partitions)}")
    outputs = []
    for k, partition in partitions.items():
        result = encrypt.remote(k, partition)
        outputs.append(result)
    ray.get(outputs)
    return outputs


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
        apsi_server = get_apsi_db(f)
        i += 1


def run(npartitions, step, data_path):
    s = time.time()
    dataset = pre_data(data_path)
    print(dataset.schema(), dataset.count())
    print("npartitions: ", npartitions)
    buckets = {}
    outputs_ids = []
    for partition in dataset.iter_batches(batch_size=1000):
        outputs_ids.append(map.remote(partition))

    # map_output = [buckets.update(out) for out in ray.get(outputs)]
    results = []
    import math
    for _ in range(math.ceil(len(outputs_ids)/step)):
        if len(outputs_ids) < step:
            step = len(outputs_ids)
        ready_ids, remaining_ids = ray.wait(
            outputs_ids, num_returns=step, timeout=100)
        print(
            f"redy ids: {len(ready_ids)}, remaining ids: {len(remaining_ids)}")
        for ready_id in ready_ids:
            result = reduce.remote(ready_id)
            outputs_ids.remove(ready_id)
            results.append(result)
    ray.get(results)
    print((len(results)))

    logger.debug(f"Distributed execution: {(time.time() - s):.3f}")


if __name__ == "__main__":
    npartitions = 16**2
    step = 100
    tmp = Path(here_parent + "/data")
    data_path = str(tmp/"db_10w.csv")
    dataset = read_csv(data_path=data_path)

    run(npartitions=npartitions, step=step, data_path=data_path)

    # load_file(path=output_dir)
