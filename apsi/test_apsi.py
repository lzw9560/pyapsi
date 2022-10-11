#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by lizhiwei at 2022/9/21
from hashlib import blake2b
from typing import List, Union, Dict
from server import LabeledServer, UnlabeledServer
from client import LabeledClient, UnlabeledClient


import pyapsi

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



# from server import LabeledClient, LabeledServer, UnlabeledClient
apsi_server = LabeledServer()
apsi_server.init_db(params_string, max_label_length=10)
# add item 
apsi_server.add_item("item", "17890item")
from hashlib import blake2b

hash_item = blake2b(str.encode("item"), digest_size=16).hexdigest()
# add hash item
apsi_server.add_item(hash_item, "12hashitem")
apsi_server.add_items([("meti", "0987654321"), ("time", "1010101010")])
tmp_path = "."
db_file_path = str("apsi.db")
apsi_server.save_db(db_file_path)



apsi_client = LabeledClient(params_string)

print(_query(apsi_client, apsi_server, ["item"]) == {"item": "17890item"})
print("- * -" * 30)
print("query item: ", _query(apsi_client, apsi_server, ["item"]) )
print("query hash item: ", _query(apsi_client, apsi_server, [hash_item]) )
print("- * -" * 30)
assert _query(apsi_client, apsi_server, ["item"]) == {"item": "17890item"}
assert _query(apsi_client, apsi_server, [hash_item]) == {hash_item: "12hashitem"}
assert _query(apsi_client, apsi_server, ["item", "meti", "unknown"]) == {
    "item": "17890item",
    "meti": "0987654321",
}
assert _query(apsi_client, apsi_server, ["unknown"]) == {}