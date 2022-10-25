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


from pathlib import Path

here = path.abspath(path.join(path.dirname(__file__) ))
print(here)

sys.path.append(path.abspath(path.join(path.dirname(__file__), "../")))
from dataset.dataset import Dataset

print(str(Path(here) / "apsi.db"))

here_parent = path.abspath(path.join(path.dirname(__file__), "../"))
from apsi.utils import _query, set_log_level
from apsi.client import LabeledClient
from apsi.server import LabeledServer

set_log_level("all")

def hash_sort(ds):
    """
    1. hash item
    2. sort by hash_item

    :param ds: _description_
    :type ds: _type_
    :return: _description_
    :rtype: _type_
    """
    ds = ds.map(lambda record: { "item": record["item"], "hash_item": blake2b(str.encode(record["item"]), digest_size=16).hexdigest(), "label": record["label"]})
    ds = ds.sort("hash_item")
    ds.schema()
    print("***")
    ds.show(2) 
    return ds 

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

    return ds


def pre_data(data_path):
    ds = read_csv(data_path=data_path)
    ds = hash_sort(ds)
    return ds
    

# 100k-1
params_string = """
{
    "table_params": {
        "hash_func_count": 1,
        "table_size": 409,
        "max_items_per_bin": 20
    },
    "item_params": {
        "felts_per_item": 5
    },
    "query_params": {
        "ps_low_degree": 0,
        "query_powers": [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 ]
    },
    "seal_params": {
        "plain_modulus": 65537,
        "poly_modulus_degree": 2048,
        "coeff_modulus_bits": [ 48 ]
    }
}

"""



import ray

@ray.remote
def map(data):
    # print(type(data), data.count())
    # outputs = [list() for _ in range(npartitions)]
    set_log_level("all")
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
    set_log_level("all")
    apsi_server = LabeledServer()
    if os.path.isfile(db_file_path):
        # load db 
        # apsi_server.init_db(params_string, max_label_length=64)
        apsi_server.load_db(db_file_path=db_file_path)
        time.sleep(1)
    else:
        # init db
        apsi_server.init_db(params_string, max_label_length=64)
    return apsi_server
output_dir = "./data/dis_apsidb/"
@ray.remote
def encrypt(partition, k):
    set_log_level("all")
    # server
    db_file_path = f"{output_dir}{k}.db"
    print(f"encrypt bucket: {k}, db path: {db_file_path}")
    if not os.path.isdir(path.dirname(db_file_path)):
        os.makedirs(path.dirname(db_file_path))
    apsi_server = get_db(db_file_path)
    data = [(p["item"], p["label"]) for p in partition]
    print(data)
    apsi_server.add_items(data)

    apsi_server.save_db(db_file_path=db_file_path)
    return db_file_path

    
@ray.remote
def reduce(partitions):
    # print("partitions")
    set_log_level("all")
    print(type(partitions), len(partitions))
    logger.debug(f"{type(partitions)} partitions: {len(partitions)}")
    outputs = []
    for k, partition in partitions.items():  
        result = encrypt.remote(partition, k)
        outputs.append(result)
    ray.get(outputs)
    return outputs

def display(dir_path=""):
    g = os.walk(dir_path)  
    fl = []
    for path,dir_list,file_list in g:  
        for file_name in file_list:  
            print(os.path.join(path, file_name) )
            fl.append(os.path.join(path, file_name))
    return fl

def load_file(path):
    fl = display(path)
    i = 0
    for f in fl:
        apsi_server = get_db(f)
        i += 1
        print(i, apsi_server)
        del apsi_server


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
        ready_ids, remaining_ids = ray.wait(outputs_ids, num_returns=step, timeout=100)
        print(f"redy ids: {len(ready_ids)}, remaining ids: {len(remaining_ids)}") 
        for ready_id in ready_ids:
            # print(ready_id)
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
    dataset = read_csv(data_path=data_path  )

    run(npartitions=npartitions, step=step, data_path=data_path)
    
    load_file(path=output_dir)