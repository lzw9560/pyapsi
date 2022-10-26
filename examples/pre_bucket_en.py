#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pre_bucket.py
# @Author :  ()
# @Link   :
# @Date   : 10/25/2022, 3:23:29 PM

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

import json
import pickle
import cloudpickle as pickle
import ray
from apsi.server import LabeledServer
from apsi.client import LabeledClient
from apsi.utils import _query, set_log_level
from dataset.dataset import Dataset
from os import path
import os
import sys
import time


from pathlib import Path

here = path.abspath(path.join(path.dirname(__file__)))
print(here)

sys.path.append(path.abspath(path.join(path.dirname(__file__), "..")))

print(str(Path(here) / "apsi.db"))

here_parent = path.abspath(path.join(path.dirname(__file__), ".."))

set_log_level("all")


PARAMS_PATH = str(Path(here_parent) / "src/parameters/100K-1.json")
UNIT = 16
SEVERAL = 2
BUCKET_CAPACITY = UNIT ** SEVERAL

DB_TOTAL = '100w'
bucket_tmp_path = f"./data/tmp_{DB_TOTAL}/m_buckets"
output_dir = f"./data/{DB_TOTAL}/apsidb"


def save_bucket_tmp(tmp_path, data):
    with open(tmp_path, "wb") as f:
        pickle.dump(data, f)


def load_bucket_tmp(tmp_path):
    with open(tmp_path, "rb") as f:
        data = pickle.load(f)
    return data


def get_params(params_path=None):
    """Get APSI parameters string.

    :param params_path: _description_, defaults to None
    :type params_path: _type_, optional
    :return: _description_
    :rtype: _type_
    """

    if not params_path:
        params_path = str(Path(here_parent) / "src/parameters/100k-1.json")
    print(params_path)
    with open(params_path, "r") as f:
        params_string = json.dumps(json.load(f))
    return params_string


def get_db(db_file_path):
    set_log_level("all")
    params_string = get_params(params_path=PARAMS_PATH)
    apsi_server = LabeledServer()
    if os.path.isfile(db_file_path):
        # load db
        apsi_server.load_db(db_file_path=db_file_path)
        time.sleep(1)
    else:
        # init db
        apsi_server.init_db(params_string, max_label_length=64)
    return apsi_server


@ray.remote
class AsyncEncryptActor:
    async def run_task(self, bucket_name, bucket_tmp):

        if not os.path.isfile(bucket_tmp):
            print(f"{bucket_tmp} no bucket, will pass.")
        else:
            print("started")
            # server
            # output_dir
            # db_file_path = "./data/tmp/db/apsi_%s.db" % bucket_name
            db_file_path = f"{output_dir}/{bucket_name}.db"
            print(f"encrypt bucket: {bucket_name}, db path: {db_file_path}")
            if not os.path.isdir(path.dirname(db_file_path)):
                os.makedirs(path.dirname(db_file_path))
            apsi_server = get_db(db_file_path)

            bucket_ds = load_bucket_tmp(tmp_path=bucket_tmp)
            data = [(d["item"], d["label"]) for d in bucket_ds]
            # print(data)
            apsi_server.add_items(data)
            apsi_server.save_db(db_file_path=db_file_path)
            os.remove(bucket_tmp)  # remove tmp
            return db_file_path


def display(dir_path=""):
    g = os.walk(dir_path)
    fl = []
    for path, dir_list, file_list in g:
        for file_name in file_list:
            print(os.path.join(path, file_name))
            fl.append(os.path.join(path, file_name))
    return fl


if __name__ == "__main__":

    s = time.time()
    n_bucket = 16**2     # npartitions * step = 16 ** 30
    # step = 16 ** 0

    actor = AsyncEncryptActor.options(max_concurrency=16).remote()
    tasks = []
    for n in range(n_bucket):
        bucket_value = 0xff - n
        if bucket_value < 0:
            break
        print(bucket_value)
        bucket_value_hex = hex(bucket_value)[SEVERAL:]
        if len(bucket_value_hex) < 2:
            bucket_value_hex = f"0{bucket_value_hex}"
        print("*** bucket ***: ", bucket_value_hex)
        tmp_path = f"{bucket_tmp_path}/{bucket_value_hex}"
        tasks.append(actor.run_task.remote(bucket_value_hex, tmp_path))
    ray.get(tasks)
    print(f"Distrubuted execution: {(time.time() - s):.3f}")
