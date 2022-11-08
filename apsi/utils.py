#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# utils.py
# @Author :  ()
# @Link   : 
# @Date   : 10/12/2022, 11:03:20 AM
import json
import os
from pathlib import Path
from typing import List, Union, Dict

import cloudpickle as pickle
from pyapsi import utils

from apsi.client import LabeledClient, UnlabeledClient
from apsi.server import LabeledServer, UnlabeledServer

here_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
PARAMS_PATH = str(Path(here_parent) / "src/parameters/100K-1.json")


def set_log_level(level):
    return utils._set_log_level(level)


def _query(
        client: Union[UnlabeledClient, LabeledClient],
        server: Union[UnlabeledServer, LabeledServer],
        items: List[str],
) -> Dict[str, str]:
    oprf_request = client.oprf_request(items)
    # print("oprf_request: ", oprf_request)
    oprf_response = server.handle_oprf_request(oprf_request)
    # print("oprf_response: ", oprf_response)
    query = client.build_query(oprf_response)
    # print("query: ", query)
    response = server.handle_query(query)
    # print("response: ", response)
    result = client.extract_result(response)
    # print(result)
    return result


# pickle save & load
def save_block(tmp_path, data):
    if not os.path.isdir(os.path.dirname(tmp_path)):
        os.makedirs(os.path.dirname(tmp_path))
    with open(tmp_path, "wb") as f:
        pickle.dump(data, f)


def load_block(tmp_path):
    with open(tmp_path, "rb") as f:
        data = pickle.load(f)
    return data


# db
def get_params(params_path=None):
    """Get APSI parameters string.

    :param params_path: _description_, defaults to None
    :type params_path: _type_, optional
    :return: _description_
    :rtype: _type_
    """

    if not params_path:
        params_path = str("src/parameters/100k-1.json")
    print(params_path)
    with open(params_path, "r") as f:
        params_string = json.dumps(json.load(f))
    return params_string


def get_db(db_file_path, params_str):
    set_log_level("all")
    if not params_str:
        params_str = get_params(params_path=PARAMS_PATH)
    apsi_server = LabeledServer()
    if os.path.isfile(db_file_path):
        # load db
        apsi_server.load_db(db_file_path=db_file_path)
    else:
        # init db
        apsi_server.init_db(params_str, max_label_length=64)
    return apsi_server
