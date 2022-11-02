#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by lizhiwei at 2022/9/21
import time
from apsi.client import LabeledClient, UnlabeledClient
from apsi.server import LabeledServer, UnlabeledServer
from dataset.dataset import Dataset
from typing import List, Union, Dict
from os import path
import sys

here = path.abspath(path.join(path.dirname(__file__)))
print(here)
sys.path.append(path.abspath(path.join(path.dirname(__file__), "../")))


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


def _query(
    client: Union[UnlabeledClient, LabeledClient],
    server: Union[UnlabeledServer, LabeledServer],
    items: List[str],
) -> Dict[str, str]:
    oprf_request = client.oprf_request(items)
    oprf_response = server.handle_oprf_request(oprf_request)
    query = client.build_query(oprf_response)
    response = server.handle_query(query)
    result = client.extract_result(response)
    return result


apsi_server = LabeledServer()
apsi_server.init_db(params_string, max_label_length=64)
# add item

items = [('JRIKrInSyZfcBADbXigLiGnHisxpWrEctHEQzrryFjAHFoPQAjEoxQhTPoYgXIFI',
          'GukbcSbVKQheaIWdNCSszRGwWEJAWTSOPfeTyHqomeCwPehKZHUEugDMxyXtaJHg')]


start = time.time()
for item in items:
    start = time.time()
    apsi_server.add_item(item[0], item[1])
    print(time.time() - start)


print("time: ", time.time() - start)
tmp_path = "."
db_file_path = str("apsi.db")
apsi_server.save_db(db_file_path)


apsi_client = LabeledClient(params_string)

print("query item: ", _query(apsi_client, apsi_server, [
      "JRIKrInSyZfcBADbXigLiGnHisxpWrEctHEQzrryFjAHFoPQAjEoxQhTPoYgXIFI"]))

assert _query(apsi_client, apsi_server, ["unknown"]) == {}
