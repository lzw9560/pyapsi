#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# example_query_from_bucket.py
# @Author :  ()
# @Link   :
# @Date   : 10/19/2022, 10:23:35 AM

from pathlib import Path
from os import path
import sys

here = path.abspath(path.join(path.dirname(__file__)))
print(here)

sys.path.append(path.abspath(path.join(path.dirname(__file__), "../")))

print(str(Path(here) / "apsi.db"))

here_parent = path.abspath(path.join(path.dirname(__file__), "../"))

from apsi.server import LabeledServer
from apsi.client import LabeledClient
from apsi.utils import _query
from dataset.dataset import Dataset
import time
from hashlib import blake2b
from loguru import logger




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


# client
# apsi_client = LabeledClient(params_string)


# item = "JRIKrInSyZfcBADbXigLiGnHisxpWrEctHEQzrryFjAHFoPQAjEoxQhTPoYgXIFI"
# # print(_query(apsi_client, apsi_server, ["item"]) == {"item": "17890item"})
# print("- * -" * 30)
# print("query item: ", _query(apsi_client, apsi_server, [item]) )
# print("- * -" * 30)
# assert _query(apsi_client, apsi_server, ["unknown"]) == {}

def query(client, server, *item):
    return _query(apsi_client, apsi_server, [*item])


def get_apsi_db_path(tmp="./", item=""):
    hash_item = blake2b(str.encode(item), digest_size=16).hexdigest()
    bucket_mark = hash_item[:2]
    return  f"{tmp}/apsi_{bucket_mark}.db"


if __name__ == "__main__":
    client = apsi_client = LabeledClient(params_string)
    server = apsi_server = LabeledServer()
    server.init_db(params_string, max_label_length=64)

    item = ["JRIKrInSyZfcBADbXigLiGnHisxpWrEctHEQzrryFjAHFoPQAjEoxQhTPoYgXIFI"]
    tmp =str(Path(here_parent)/"data/apsidb/")
    print(tmp)
    db_path = get_apsi_db_path(tmp=tmp, item=item[0])
    print(db_path)
    server.load_db(db_file_path=db_path)
    result = query(client, server, *item)
    print(result)
    print(result == {"JRIKrInSyZfcBADbXigLiGnHisxpWrEctHEQzrryFjAHFoPQAjEoxQhTPoYgXIFI": "GukbcSbVKQheaIWdNCSszRGwWEJAWTSOPfeTyHqomeCwPehKZHUEugDMxyXtaJHg"})
