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
# tmp = Path(here_parent + "/data")
# data_path = str(tmp/"db_10w.csv")
# print(data_path)
# start = time.time()
# dataset = Dataset()
# ds = dataset.read(format="csv", paths=data_path, parallelism=500)
# ds.schema()
# print("***")
# ds.show(2)
# print("***")
# logger.debug("The CSV file reading 10w strip data takes {}s:".format(time.time() - start))


# ## hash sort
# # Add a new column equal to hash item.
# # ds = ds.add_column(
# #     "hash_item", lambda df: df["item"]
# # )
# ds.schema()
# print("add column ***")
# ds.show(2)
# print("add column ***")
# # TODO 并行优化
# ds = ds.map(lambda record: { "item": record["item"], "hash_item": blake2b(str.encode(record["item"]), digest_size=16).hexdigest(), "label": record["label"]})
# # ds = ds.map(lambda record: {"item": record["item"], "hash_item": blake2b(str.encode(record["item"]), digest_size=16).hexdigest(), "label": record["label"]})

# ds.schema()
# print("hash item ***")
# ds.show(2)
# print("hash item ***")
# ds = ds.sort("hash_item")
# ds.schema()
# print("***")
# ds.show(2)


def read_csv(data_path):
    # tmp = Path(here_parent + "/data")
    # data_path = str(tmp/"db_10w.csv")
    print(data_path)
    start = time.time()
    dataset = Dataset()
    ds = dataset.read(format="csv", paths=data_path, parallelism=500)
    ds.schema()
    print("***")
    ds.show(2)
    print("***")
    logger.debug("The CSV file reading 10w strip data takes {}s:".format(time.time() - start))


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

# server
apsi_server = LabeledServer()
apsi_server.init_db(params_string, max_label_length=64)
i = 0 
# for batch in ds.iter_batches(): 
#     # start = time.time()
#     # [apsi_server.add_item(data[0], data[1]) for idx, data in batch.iterrows()]
#     # print("batch time add item:", time.time() - start) # 40 s

#     b_start = time.time()
#     items = [(data[0], data[1]) for idx, data in batch.iterrows()] 
#     # print(items)
#     print("add itemssssssssssssss: ", i)
#     i += 1
#     apsi_server.add_items(items)
#     print("batch time add items:", time.time() - b_start) # 40 s

# print("time add all items:", time.time() - start) # 40 s
# # out put
# tmp_path = "."
# db_file_path = str(Path(here) / "apsi_10w.db")
# print(db_file_path)
# apsi_server.save_db(db_file_path)


# # client 
# apsi_client = LabeledClient(params_string)


# item = "JRIKrInSyZfcBADbXigLiGnHisxpWrEctHEQzrryFjAHFoPQAjEoxQhTPoYgXIFI"
# # print(_query(apsi_client, apsi_server, ["item"]) == {"item": "17890item"})
# print("- * -" * 30)
# print("query item: ", _query(apsi_client, apsi_server, [item]) )
# print("- * -" * 30)
# assert _query(apsi_client, apsi_server, ["unknown"]) == {}

import ray

# @ray.remote
def map(data, buckets):
    print(type(data), data.count())
    # outputs = [list() for _ in range(npartitions)]
    outputs = buckets
    print("output len: ", len(outputs))
    for idx, row in data.iterrows():
        print("hash value: ", row["hash_item"][:2], int(row["hash_item"][:2], 16))
        index_key = row["hash_item"][:2]
        row = row.drop(labels="hash_item")
        if outputs.get(index_key, None) is None:
            outputs[index_key] = []
        outputs[index_key].append(row)
    print(len(outputs))
    return outputs

# @ray.remote
def reduce(partitions):
    print("partitions")
    # Flatten and sort the πpartitions.
    print(len(partitions))
    for k, partition in partitions.items():
        print(k)
        print(len(partition), type(partition))    
        
        apsi_server.add_items(partition)
        print(type(partition))
        db_file_path = "./data/apsidb/apsi_%s.db"%k
        if not os.path.isdir(path.dirname(db_file_path)):
            os.makedirs(path.dirname(db_file_path))
        apsi_server.save_db(db_file_path=db_file_path)

def get_db(db_file_path):
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
    fl = display("./data/apsidb")
    i = 0
    for f in fl:
        apsi_server = get_db(f)
        i += 1
        print(i, apsi_server)
        del apsi_server
        
if __name__ == "__main__":
    s = time.time()
    npartitions = 16**2
    tmp = Path(here_parent + "/data")
    data_path = str(tmp/"db_10w.csv")
    dataset = read_csv(data_path=data_path  )
    print(dataset.schema(), dataset.count())
    print("npartitions: ", npartitions)
    # buckets = [list() for _ in range(npartitions)]
    buckets = {}

    for partition in dataset.iter_batches(batch_size=1000):
        outputs = map(partition, buckets=buckets)

    outputs = []
    reduce(buckets)

    print(len(outputs))
    print(f"Sequential execution: {(time.time() - s):.3f}")

    load_file()