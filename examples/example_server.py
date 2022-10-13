#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# read_csv.py
# @Author :  ()
# @Link   : 
# @Date   : 10/12/2022, 10:43:41 AM
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by lizhiwei at 2022/9/21
# from hashlib import blake2b

from os import path
import sys

from pathlib import Path
here = path.abspath(path.join(path.dirname(__file__) ))
print(here)
sys.path.append(path.abspath(path.join(path.dirname(__file__), "../")))
from apsi.dataset import Dataset
from apsi.server import LabeledServer, UnlabeledServer
from apsi.client import LabeledClient, UnlabeledClient

print( str(Path(here) / "apsi.db"))

import time
here_parent = path.abspath(path.join(path.dirname(__file__), "../"))
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

print("read:", time.time() - start)


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


apsi_server = LabeledServer()
apsi_server.init_db(params_string, max_label_length=64)
# # add item 
# apsi_server.add_item("item", "17890item")
# from hashlib import blake2b

# hash_item = blake2b(str.encode("item"), digest_size=16).hexdigest()
# # add hash item
# apsi_server.add_item(hash_item, "12hashitem")
# apsi_server.add_items([("meti", "0987654321"), ("time", "1010101010")])

# ds = ds.map(lambda record: {"item": record['item'], "label": record["label"]})

# Transform in parallel with map_batches().
# ds.map_batches(lambda batch: [apsi_server.add_item(v) for v in batch]) 
i = 0
for batch in ds.iter_batches(): 
    print(i, len(batch)) 
    # start = time.time()
    # [apsi_server.add_item(data[0], data[1]) for idx, data in batch.iterrows()]
    i += 1
    # print("batch time add item:", time.time() - start) # 40 s

    start = time.time()
    items = [(data[0], data[1]) for idx, data in batch.iterrows()] 
    # print(items)
    print("add itemssssssssssssss")
    apsi_server.add_items(items)
    print("batch time add items:", time.time() - start) # 40 s

    if i == 1:
        break
# out put
tmp_path = "."
db_file_path = str(Path(here) / "apsi.db")
print(db_file_path)
apsi_server.save_db(db_file_path)


# TODO 并行优化
# ds = ds.map(lambda record: {"item": blake2b(str.encode(record["item"]), digest_size=16).hexdigest(), "label": record["label"]})
# ds = ds.map(lambda record: {"item": blake2b(str.encode(record["item"]), digest_size=16).hexdigest(), "label": record["label"]})

# ds = ds.sort("item")

# ds = ds.repartition(int(100000/128))
# ds_list = ds.split(int(100000/128), equal=True)
# ds = ds.repartition(20)
# ds_list = ds.split(21, equal=True)

# print("list count", len(ds_list))
# i = 0
# for ds in ds_list:
#     print("*** split count", ds.count())
#     print(ds.show(2))
#     i += 1
#     print("iiiiii", i)

# print("*** split ds record count", ds.count())
# print(ds.show(2))
# print("end:", time.time() - start)

# repartition
# ds.write_csv(path="./output")
# ds = ds.repartition(1000)