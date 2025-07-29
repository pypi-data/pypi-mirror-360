import pyarrow as pa
import csv
from functools import reduce
from typing import Callable, Iterator, cast

import click as click
import tqdm
import lxml.etree
import fsspec
from fsspec.core import OpenFile, compr, infer_compression
import _csv

schema = pa.schema([ # R compatibility schema
            pa.field('record_number', pa.int32()),
            pa.field('field_number', pa.int32()),
            pa.field('subfield_number', pa.int32()),
            pa.field('field_code', pa.dictionary(pa.int32(), pa.string())),
            pa.field('subfield_code', pa.dictionary(pa.int32(), pa.string())),
            pa.field('value', pa.string()) 
])

def convert(tag: str, convert_record: Callable[[lxml.etree._ElementIterator], Iterator[tuple[int, int, str, str, str]]], input: list[str], output: str) -> None:
    writing_parquet = output.endswith('.parquet')
    with cast(OpenFile, fsspec.open(output, 'wt' if not writing_parquet else 'wb', compression="infer")) as of:
        if writing_parquet:
            import pyarrow as pa
            import pyarrow.parquet as pq
            pw = pq.ParquetWriter(of, schema=pa.schema([
                pa.field('record_number', pa.int32()),
                pa.field('field_number', pa.int32()),
                pa.field('subfield_number', pa.uint8()),
                pa.field('field_code', pa.string()),
                pa.field('subfield_code', pa.string()),
                pa.field('value', pa.string()),
            ]), compression='zstd', use_dictionary=True)
            batch = []
            cw = None
        else:
            pw = None
            cw = csv.writer(of, delimiter='\t' if '.tsv' in output else ',')
            cw.writerow(['record_number', 'field_number', 'subfield_number', 'field_code', 'subfield_code', 'value'])
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
                    context = lxml.etree.iterparse(inf, events=('end',), tag=tag)
                    for _, elem in context:
                        for row in convert_record(elem):
                            if writing_parquet:
                                batch.append((n, *row))
                                if len(batch) == 100: #1024*1024:
                                    batch = [pa.array(entries) for entries in zip(zip(*batch)]
                                    cast(pq.ParquetWriter, pw).write_batch(pa.record_batch(batch,
                                        schema=schema))
                                    batch = []
                            else:
                                cast(_csv.Writer, cw).writerow((n, *row))
                        n += 1
                        elem.clear()
                        while elem.getprevious() is not None:
                            del elem.getparent()[0]
                        pbar.n = processed_files_tsize + oinf.tell()
                        pbar.update(0)
                    del context
            processed_files_tsize += input_file.fs.size(input_file.path)