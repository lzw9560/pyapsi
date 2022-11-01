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

from os import path
import os
import sys
import time
from hashlib import blake2b
from loguru import logger

# logger.remove()
# logger.add(sys.stdout, colorize=True)

from pathlib import Path

here = path.abspath(path.join(path.dirname(__file__) ))
print(here)

sys.path.append(path.abspath(path.join(path.dirname(__file__), "../")))
from dataset.dataset import Dataset

print(str(Path(here) / "apsi.db"))

here_parent = path.abspath(path.join(path.dirname(__file__), "../"))
from apsi.utils import _query
from apsi.client import LabeledClient
from apsi.server import LabeledServer


def read_csv(data_path):
    print(data_path)
    start = time.time()
    dataset = Dataset()
    ds = dataset.read(format="csv", paths=data_path, parallelism=500)
    ds.schema()
    print("***")
    ds.show(2)
    print("***")
    logger.debug("The CSV file reading {} strip data takes {}s:".format(ds.count(), time.time() - start))


    ## hash sort
    # Add a new column equal to hash item.
    # ds = ds.add_column(
    #     "hash_item", lambda df: df["item"]
    # )
    ds.schema()
    print("add column ***")
    ds.show(2)
    print("add column ***")
    # TODO 并行优化
    ds = ds.map(lambda record: { "item": record["item"], "hash_item": blake2b(str.encode(record["item"]), digest_size=16).hexdigest(), "label": record["label"]})
    # ds = ds.map(lambda record: {"item": record["item"], "hash_item": blake2b(str.encode(record["item"]), digest_size=16).hexdigest(), "label": record["label"]})

    ds.schema()
    print("hash item ***")
    ds.show(2)
    print("hash item ***")
    ds = ds.sort("hash_item")
    ds.schema()
    print("***")
    ds.show(2) 
    return ds


# ds = ds.drop_columns("hash_item")
# ds.schema()
# print("***")
# ds.show(2)

params_string = """{
    "table_params": {
        "hash_func_count": 1,
        "table_size": 1638,
        "max_items_per_bin": 8100
    },
    "item_params": {
        "felts_per_item": 5
    },
    "query_params": {
        "ps_low_degree": 310,
        "query_powers": [ 1, 4, 10, 11, 28, 33, 78, 118, 143, 311, 1555]
    },
    "seal_params": {
        "plain_modulus_bits": 22,

        "poly_modulus_degree": 8192,
        "coeff_modulus_bits": [ 56, 56, 56, 32 ]
    }
}
"""



import ray

@ray.remote
def map(data):
    # print(type(data), data.count())
    # outputs = [list() for _ in range(npartitions)]
    buckets = {}
    outputs = buckets
    # print("output len: ", len(outputs))
    for idx, row in data.iterrows():
        # logger.debug("hash value: hex: {} int: {}".format( {row["hash_item"][:2]}, {int(row["hash_item"][:2], 16)}))
        index_key = row["hash_item"][:2]
        row = row.drop(labels="hash_item")
        if outputs.get(index_key, None) is None:
            outputs[index_key] = []

        outputs[index_key].append(row)
    logger.debug(f"outputs type: {type(outputs)}, size: {len(outputs)}")
    # print(len(outputs))
    return outputs

def get_db(db_file_path):
    apsi_server = LabeledServer()
    if os.path.isfile(db_file_path):
        # load db and insert
        apsi_server.load_db(db_file_path=db_file_path)
    else:
        # init db
        apsi_server.init_db(params_string, max_label_length=64)
    return apsi_server

@ray.remote
def encrypt(partition, k):
    # server
    db_file_path = "./data/dis_apsidb/apsi_%s.db"%k
    print(f"encrypt bucket: {k}, db path: {db_file_path}")
    if not os.path.isdir(path.dirname(db_file_path)):
        os.makedirs(path.dirname(db_file_path))

    apsi_server = get_db(db_file_path)

    apsi_server.add_items(partition)
    apsi_server.save_db(db_file_path=db_file_path)
    return db_file_path

    
@ray.remote
def reduce(partitions):
    # print("partitions")
    print(type(partitions), len(partitions))
    logger.debug(f"{type(partitions)} partitions: {len(partitions)}")
    outputs = []
    for k, partition in partitions.items():  
        result = encrypt.remote(partition, k)
        outputs.append(result)
    ray.get(outputs)
    return outputs

import asyncio

@ray.remote
class AsyncEncryptActor:
    async def run_task(self, bucket_name, partition):
        print("started")
        # server
        db_file_path = "./data/actor_apsidb/apsi_%s.db" % bucket_name
        print(f"encrypt bucket: {bucket_name}, db path: {db_file_path}")
        if not os.path.isdir(path.dirname(db_file_path)):
            os.makedirs(path.dirname(db_file_path))
        apsi_server = get_db(db_file_path)
        print("**********")
        print(partition.schema())
        # print(partition)
        # bucket_ds = [row for row in partition.iter_rows()]
        bucket_ds = partition.take_all()
        data = [(d["item"], d["label"]) for d in bucket_ds]
        # print(bucket_ds)
        print("**********")
        apsi_server.add_items(data)
        apsi_server.save_db(db_file_path=db_file_path)
        return db_file_path

@ray.remote
def get_bucket_dataset(dataset, bucket_value):
    # return dataset.filter(lambda record: record["hash_item"][:2] == bucket_name)
    print(bucket_value, type(bucket_value))
    ds =  dataset.filter(lambda record: int(record["hash_item"][:2], 16) == bucket_value)
    ds = ds.drop_columns("hash_item")
    return ds
    
if __name__ == "__main__":
    import json
    ray.init(
    _system_config={
        "object_spilling_config": json.dumps(
            {"type": "filesystem", "params": {"directory_path": "./tmp/spill"}},
        )
    },
    )
    s = time.time()
    npartitions = 16**2
    tmp = Path(here_parent + "/data")
    data_path = str(tmp/"db_10w.csv")
    dataset = read_csv(data_path=data_path)
    print(dataset.schema(), dataset.count())
    print("npartitions: ", npartitions)

    actor = AsyncEncryptActor.options(max_concurrency=16).remote()

    tasks = []
    step = 16 ** 0
    for n in range(npartitions):
        # f'{i:x}'
        bucket_value = 0xff - n * step
        if bucket_value < 0:
            break
        print(bucket_value)
        bucket_value_hex = hex(bucket_value)[2:]
        print("***", bucket_value_hex)
        bucket_ds = get_bucket_dataset.remote(dataset=dataset, bucket_value=bucket_value_hex)
        tasks.append(actor.run_task.remote(bucket_value_hex, bucket_ds))
    print(len(tasks))
    ray.get(tasks)
    logger.debug(f"Distributed actor execution: {(time.time() - s):.3f}")