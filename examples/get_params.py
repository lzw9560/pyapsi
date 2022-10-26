#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# get_params.py
# @Author :  ()
# @Link   :
# @Date   : 10/25/2022, 5:20:05 PM

import json
from os import path
from pathlib import Path


def get_params(params_path):
    return json.load(params_path)


if __name__ == "__main__":
    here_parent = path.abspath(path.join(path.dirname(__file__), "../"))

    params_path = str(Path(here_parent) / "src/parameters/100k-1.json")
    print(params_path)
    with open(params_path, "r") as f:
        print(1)
        params_string = json.load(f)
        
    print(type(params_string))
    print(type(json.dumps(params_string)))
