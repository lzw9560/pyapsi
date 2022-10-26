#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# cmp_file.py
# @Author :  ()
# @Link   : 
# @Date   : 10/20/2022, 5:51:15 PM

from os import path
import os
import sys
import time
from loguru import logger

# logger.remove()
# logger.add(sys.stdout, colorize=True)

from pathlib import Path

here = path.abspath(path.join(path.dirname(__file__) ))
print(here)

sys.path.append(path.abspath(path.join(path.dirname(__file__), "../")))


here_parent = path.abspath(path.join(path.dirname(__file__), "../"))
import filecmp

def display(dir_path=""):
    g = os.walk(dir_path)  
    fl = []
    for path,dir_list,file_list in g:  
        for file_name in file_list:  
            print(os.path.join(path, file_name) )
            fl.append(os.path.join(path, file_name))
    return fl


from apsi.server import LabeledServer
from apsi.utils import _query, set_log_level

set_log_level("all")
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

# tmp_dir = f"./data/tmp/db/"
tmp_dir = "./data/100w/apsidb/"
# db_file_path = "./data/tmp/db/apsi_%s.db" % bucket_name
def load_file():
    fl = display(tmp_dir)
    i = 0
    for f in fl:
        apsi_server = get_db(f)
        i += 1
        print(i, apsi_server)

if __name__ == '__main__':
    load_file()
    # p = "./data/dis_apsidb/apsi_d9.db"
    # get_db(p)
    # get_db("apsi_f1.db")
    