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
from apsi.utils import _query, set_log_level
from apsi.client import LabeledClient
from apsi.server import LabeledServer

set_log_level("all")

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

import cloudpickle as pickle
# @ray.remote
def map_single(data):
    # print(type(data), data.count())
    # outputs = [list() for _ in range(npartitions)]
    set_log_level("all")
    m_buckets = {}
    # outputs = buckets
    # print("output len: ", len(outputs))
    for idx, row in data.iterrows():
        # logger.debug("hash value: hex: {} int: {}".format( {row["hash_item"][:2]}, {int(row["hash_item"][:2], 16)}))
        index_key = row["hash_item"][:2]
        row = row.drop(labels="hash_item")
        if m_buckets.get(index_key, None) is None:
            m_buckets[index_key] = []

        m_buckets[index_key].append(row)
    logger.debug(f"outputs type: {type(m_buckets)}, size: {len(m_buckets)}")
    # print(len(outputs))
    tmp_path = f"./tmp/single/m_buckets/{index_key}"
    if not os.path.isdir(path.dirname(tmp_path)):
        os.makedirs(path.dirname(tmp_path))
    

    # if os.path.isfile(tmp_path):
    #     # load 
    #     pre_bucket = pickle.load(tmp_path)
    
    with open(tmp_path, "wb") as f:
        pickle.dump(m_buckets, f)
    return m_buckets

def save_bucket_tmp(tmp_path, data):
    with open(tmp_path, "wb") as f:
        pickle.dump(data, f) 
        
def load_bucket_tmp(tmp_path):
    with open(tmp_path, "rb") as f:
        data = pickle.load(f) 
    return data
        
@ray.remote
def map(data):
    set_log_level("all")
    m_buckets = {}
    # outputs = buckets
    # print("output len: ", len(outputs))
    for idx, row in data.iterrows():
        # logger.debug("hash value: hex: {} int: {}".format( {row["hash_item"][:2]}, {int(row["hash_item"][:2], 16)}))
        index_key = row["hash_item"][:2]
        row = row.drop(labels="hash_item")
        if m_buckets.get(index_key, None) is None:
            m_buckets[index_key] = []

        m_buckets[index_key].append(row)
        # print(f"append..................{index_key}")
    # logger.debug(f"outputs type: {type(m_buckets)}, size: {len(m_buckets)}")
    # print(len(outputs))
    tmp_path = f"./tmp/dis/m_buckets/{index_key}"
    if not os.path.isdir(path.dirname(tmp_path)):
        os.makedirs(path.dirname(tmp_path))
    

    save_bucket_tmp(tmp_path, m_buckets)
    # if os.path.isfile(tmp_path):
    #     # load 
    #     pre_bucket = pickle.load(tmp_path)
    
    # with open(tmp_path, "wb") as f:
    #     pickle.dump(m_buckets, f)
    return m_buckets

def get_db(db_file_path):
    set_log_level("all")
    apsi_server = LabeledServer()
    if os.path.isfile(db_file_path):
        # load db 
        apsi_server.init_db(params_string, max_label_length=64)
        apsi_server.load_db(db_file_path=db_file_path)
        time.sleep(1)
    else:
        # init db
        apsi_server.init_db(params_string, max_label_length=64)
    return apsi_server

# @ray.remote
def encrypt(partition, k):
    set_log_level("all")
    # server
    db_file_path = "./data/dis_apsidb/apsi_%s.db"%k
    print(f"encrypt bucket: {k}, db path: {db_file_path}")
    if not os.path.isdir(path.dirname(db_file_path)):
        os.makedirs(path.dirname(db_file_path))
    apsi_server = get_db(db_file_path)
    # apsi_server.add_items(partition)
    print(type(partition))
    for p in partition:
        print(type(p), p)
        for i,j in p:
            print(i, j)
        # print(p[0], p[1])
        apsi_server.add_item(p)

    apsi_server.save_db(db_file_path=db_file_path)
    return db_file_path

    
# @ray.remote
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

@ray.remote
def reduce():
    # print("partitions")
    set_log_level("all")
    while True:
        pass
        
    print(type(partitions), len(partitions))
    logger.debug(f"{type(partitions)} partitions: {len(partitions)}")
    outputs = []
    for k, partition in partitions.items():  
        result = encrypt.remote(partition, k)
        outputs.append(result)
    ray.get(outputs)
    return outputs

@ray.remote
class AsyncEncryptActor:
    async def run_task(self, bucket_name, bucket_tmp):
        print("started")
        # server
        db_file_path = "./data/dis_actor_apsidb/apsi_%s.db" % bucket_name
        print(f"encrypt bucket: {bucket_name}, db path: {db_file_path}")
        if not os.path.isdir(path.dirname(db_file_path)):
            os.makedirs(path.dirname(db_file_path))
        apsi_server = get_db(db_file_path)
        print("**********")
        # print(partition.schema())
        # print(partition)
        # bucket_ds = [row for row in partition.iter_rows()]
        bucket_ds = load_bucket_tmp(tmp_path=bucket_tmp)
        try:
            data = [(d["item"], d["label"]) for d in bucket_ds]
        except Exception as e:
            print(type(bucket_ds), bucket_ds)
            print(e)
        # print(bucket_ds)
        print("**********")
        apsi_server.add_items(data)
        apsi_server.save_db(db_file_path=db_file_path)
        return db_file_path

def try_get_db(db_file_path):
    apsi_server = LabeledServer()
    if os.path.isfile(db_file_path):
        # load db and insert
        print("********** ", db_file_path)
        try:
            apsi_server.load_db(db_file_path=db_file_path)

        except Exception as e:
            print("errrrrrrrrrrrrrrrrrrr.........")
            print(str(e))

    # else:
    #     apsi_server.init_db(params_string, max_label_length=64)
    return apsi_server

def display(dir_path=""):
    g = os.walk(dir_path)  
    fl = []
    for path,dir_list,file_list in g:  
        for file_name in file_list:  
            print(os.path.join(path, file_name) )
            fl.append(os.path.join(path, file_name))
    return fl

def load_file():
    fl = display("./data/dis_apsidb")
    i = 0
    for f in fl:
        apsi_server = try_get_db(f)
        i += 1
        print(i, apsi_server)
        del apsi_server


def run_single():
    s = time.time()
    npartitions = 16**2     # npartitions * step = 16 ** 30
    tmp = Path(here_parent + "/data")
    data_path = str(tmp/"db_10w.csv")
    dataset = read_csv(data_path=data_path  )
    print(dataset.schema(), dataset.count())
    print("npartitions: ", npartitions)
    buckets = {}
    map_outputs = []
    for partition in dataset.iter_batches(batch_size=1000):
        map_outputs.append(map_single(partition))
    
    # for m_buckets in map_outputs:
    #     for b_k, b_v in m_buckets.items():
    #         if b_k in buckets:
    #             buckets[b_k].append(b_v)
    #         else:
    #             buckets[b_k] = b_v
    
    # buckets
  
@ray.remote              
def run():
    s = time.time()
    npartitions = 16**2     # npartitions * step = 16 ** 30
    tmp = Path(here_parent + "/data")
    data_path = str(tmp/"db_10w.csv")
    dataset = read_csv(data_path=data_path  )
    print(dataset.schema(), dataset.count())
    print("npartitions: ", npartitions)
    buckets = {}
    map_outputs = []
    for partition in dataset.iter_batches(batch_size=1000):
        # map_outputs.append(map.remote(partition))

        m = map.remote(partition)
        ray.get(m)
    
    ray.get(map_outputs)
    # for m_buckets in map_outputs:
    #     for b_k, b_v in m_buckets.items():
    #         if b_k in buckets:
    #             buckets[b_k].append(b_v)
    #         else:
    #             buckets[b_k] = b_v
    
    # buckets



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
    # ray.get(run.remote())

    npartitions = 16**2     # npartitions * step = 16 ** 30
    step = 16 ** 0 

    actor = AsyncEncryptActor.options(max_concurrency=16).remote()
    tasks = []
    for n in range(npartitions):
            # f'{i:x}'
        bucket_value = 0xff - n * step
        if bucket_value < 0:
            break
        print(bucket_value)
        bucket_value_hex = hex(bucket_value)[2:]
        print("***", bucket_value_hex)
        # bucket_ds = get_bucket_dataset.remote(dataset=dataset, bucket_value=bucket_value_hex)
        tmp_path = f"./tmp/dis/m_buckets/{bucket_value_hex}"
        tasks.append(actor.run_task.remote(bucket_value_hex, tmp_path))
    ray.get(tasks)