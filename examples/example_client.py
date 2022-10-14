#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# example_client.py
# @Author :  ()
# @Link   : 
# @Date   : 10/12/2022, 12:19:03 PM


from os import path
import sys

here = path.abspath(path.join(path.dirname(__file__) ))
print(here)
sys.path.append(path.abspath(path.join(path.dirname(__file__), "../")))
from dataset.dataset import Dataset
from apsi.server import LabeledServer, UnlabeledServer
from apsi.client import LabeledClient, UnlabeledClient

from apsi.utils import _query

from example_server import apsi_server

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
apsi_client = LabeledClient(params_string)


item = "JRIKrInSyZfcBADbXigLiGnHisxpWrEctHEQzrryFjAHFoPQAjEoxQhTPoYgXIFI"
# print(_query(apsi_client, apsi_server, ["item"]) == {"item": "17890item"})
print("- * -" * 30)
print("query item: ", _query(apsi_client, apsi_server, [item]) )
print("- * -" * 30)
assert _query(apsi_client, apsi_server, ["unknown"]) == {}