#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# utils.py
# @Author :  ()
# @Link   : 
# @Date   : 10/12/2022, 11:03:20 AM

from typing import List, Union, Dict
from apsi.server import LabeledServer, UnlabeledServer
from apsi.client import LabeledClient, UnlabeledClient



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
    print(result)
    return result