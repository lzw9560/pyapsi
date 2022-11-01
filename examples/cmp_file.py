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
from dataset.dataset import Dataset

print(str(Path(here) / "apsi.db"))

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

def cmp_file():
    fl = display("./data/dis_apsidb")
    diff = []
    for f in fl:
        try:
            status = filecmp.cmp(f, f.replace("dis_apsidb", "dis_apsidb2"))
            # 为True表示两文件相同
            if status:
                print("files are the same")
            # 为False表示文件不相同
            else:
                print(f)
                if (os.path.getsize(f) == os.path.getsize(f.replace("dis_apsidb", "dis_apsidb2"))):
                    diff.append(f)
                print("files are different")
        # 如果两边路径头文件不都存在，抛异常
        except IOError:
            print("Error:"+ "File not found or failed to read")
    print(diff)
    print(len(diff))


if __name__ == '__main__':
    # display("./data/dis_apsidb")
    cmp_file()