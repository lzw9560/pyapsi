#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# test_read_csv.py
# @Author :  ()
# @Link   :
# @Date   : 10/26/2022, 1:37:46 PM

from os import path
import sys
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv
from pathlib import Path

here = path.abspath(path.join(path.dirname(__file__)))
print(here)

sys.path.append(path.abspath(path.join(path.dirname(__file__), "../")))

print(str(Path(here) / "apsi.db"))

here_parent = path.abspath(path.join(path.dirname(__file__), "../"))

in_path = '/home/pace/dev/benchmarks-proj/benchmarks/data/nyctaxi_2010-01.csv.gz'
out_path = '/home/pace/dev/benchmarks-proj/benchmarks/data/temp/iterative.parquet'
tmp = Path(here_parent + "/data")

DB_TOTAL = '100w'
in_path = str(tmp/f"db_{DB_TOTAL}.csv")
# OUTPUT_DIR = f"./data/{DB_TOTAL}/apsidb"
bucket_tmp_path = f"./data/tmp_{DB_TOTAL}/m_buckets"

in_path = in_path
out_path = "/Users/lizhiwei/project/code/yuanyu/pyapsi/examples/temp/iterative.parquet"

convert_options = pyarrow.csv.ConvertOptions()
convert_options.column_types = {
    'rate_code': pa.utf8(),
    'store_and_fwd_flag': pa.utf8()
}

writer = None
with pyarrow.csv.open_csv(in_path, convert_options=convert_options) as reader:
    for next_chunk in reader:
        print(len(next_chunk))
        if next_chunk is None:
            break
        if writer is None:
            writer = pq.ParquetWriter(out_path, next_chunk.schema)
        next_table = pa.Table.from_batches([next_chunk])
        writer.write_table(next_table)
writer.close()
