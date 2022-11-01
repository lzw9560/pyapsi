#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# single_thread_map.py
# @Author :  ()
# @Link   : 
# @Date   : 10/14/2022, 2:43:08 PM

# single_thread_map
items = list(range(100))
map_func = lambda i : i*2
output = [map_func(i) for i in items]

