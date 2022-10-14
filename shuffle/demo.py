#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# demo.py
# @Author :  ()
# @Link   : 
# @Date   : 10/14/2022, 2:58:31 PM

# read
# hash sort
# distribution of block buckets
# to sender

from os import path
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
tmp = Path(here_parent + "/data")
data_path = str(tmp/"db_10w.csv")
print(data_path)
start = time.time()
dataset = Dataset()
ds = dataset.read(format="csv", paths=data_path, parallelism=500)
ds.schema()
print("***")
ds.show(2)
print("***")
logger.debug("The CSV file reading 10w strip data takes {}s:".format(time.time() - start))


def fn(df):
    
    print(type(df["item"]), df['item'])
    return df["item"] + "-" 
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

ds = ds.drop_columns("hash_item")
ds.schema()
print("***")
ds.show(2)

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

# server
apsi_server = LabeledServer()
apsi_server.init_db(params_string, max_label_length=64)
i = 0 
for batch in ds.iter_batches(): 
    # start = time.time()
    # [apsi_server.add_item(data[0], data[1]) for idx, data in batch.iterrows()]
    # print("batch time add item:", time.time() - start) # 40 s

    b_start = time.time()
    items = [(data[0], data[1]) for idx, data in batch.iterrows()] 
    # print(items)
    print("add itemssssssssssssss: ", i)
    i += 1
    apsi_server.add_items(items)
    print("batch time add items:", time.time() - b_start) # 40 s

print("time add all items:", time.time() - start) # 40 s
# out put
tmp_path = "."
db_file_path = str(Path(here) / "apsi_10w.db")
print(db_file_path)
apsi_server.save_db(db_file_path)


# client 
apsi_client = LabeledClient(params_string)


item = "JRIKrInSyZfcBADbXigLiGnHisxpWrEctHEQzrryFjAHFoPQAjEoxQhTPoYgXIFI"
# print(_query(apsi_client, apsi_server, ["item"]) == {"item": "17890item"})
print("- * -" * 30)
print("query item: ", _query(apsi_client, apsi_server, [item]) )
print("- * -" * 30)
assert _query(apsi_client, apsi_server, ["unknown"]) == {}