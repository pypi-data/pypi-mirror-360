import pyarrow as pa
import csv
from functools import reduce
from typing import cast

import click as click
import tqdm
import lxml.etree
import fsspec
from fsspec.core import OpenFile, compr, infer_compression

schema = pa.schema([ # R compatibility schema
            pa.field('record_number', pa.int32()),
            pa.field('field_number', pa.int32()),
            pa.field('subfield_number', pa.int32()),
            pa.field('field_code', pa.dictionary(pa.int32(), pa.string())),
            pa.field('subfield_code', pa.dictionary(pa.int32(), pa.string())),
            pa.field('value', pa.string()) 
])

def convert(input: list[str], output: str) -> None:
    """Convert from MARCXML (compressed) INPUT files (actually glob patterns) into (compressed) CSV/TSV/parquet"""
    with cast(OpenFile, fsspec.open(output, 'wt', compression="infer")) as of:
        if output.endswith(".parquet"):
            import pyarrow as pa
            import pyarrow.parquet as pq
            pw = pq.ParquetWriter(of, schema=pa.schema([
                pa.field('record_number', pa.int32()),
                pa.field('field_number', pa.int32()),
                pa.field('subfield_number', pa.uint8()),
                pa.field('field_code', pa.string()),
                pa.field('subfield_code', pa.string()),
                pa.field('value', pa.string()),
            ]))
            
        co = csv.writer(of, delimiter='\t' if '.tsv' in output else ',')
        co.writerow(['record_number', 'field_number', 'subfield_number', 'field_code', 'subfield_code', 'value'])
        n = 1
        input_files = fsspec.open_files(input, 'rb')
        tsize = reduce(lambda tsize, inf: tsize + inf.fs.size(inf.path), input_files, 0)
        pbar = tqdm.tqdm(total=tsize, unit='b', unit_scale=True, unit_divisor=1024)
        processed_files_tsize = 0
        for input_file in input_files:
            pbar.set_description(f"Processing {input_file.path}")
            with input_file as oinf:
                    compression = infer_compression(input_file.path)
                    if compression is not None:
                        inf = compr[compression](oinf, mode='rb') # type: ignore
                    else:
                        inf = oinf
                    context = lxml.etree.iterparse(inf, events=('end',), tag='{http://www.loc.gov/MARC21/slim}record')
                    for _, elem in context:
                        for row in convert_record(n, elem):
                            co.writerow(row)
                        n += 1
                        elem.clear()
                        while elem.getprevious() is not None:
                            del elem.getparent()[0]
                        pbar.n = processed_files_tsize + oinf.tell()
                        pbar.update(0)
                    del context
            processed_files_tsize += input_file.fs.size(input_file.path)