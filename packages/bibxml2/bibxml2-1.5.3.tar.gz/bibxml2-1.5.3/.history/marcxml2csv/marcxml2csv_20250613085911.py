#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 18:59:15 2021

@author: jiemakel
"""

import csv
from functools import reduce
from pathlib import Path
from typing import Iterator, Tuple, cast

import click as click
import tqdm
import lxml.etree
import fsspec
from fsspec.core import OpenFiles, OpenFile, compr, infer_compression


def convert_record(n, record, co):
    f = 1
    for field in record:
        if field.tag == '{http://www.loc.gov/MARC21/slim}leader':
            co.writerow([n, f, '', 'leader', '', field.text])
        elif field.tag == '{http://www.loc.gov/MARC21/slim}controlfield':
            co.writerow(([n, f, '', field.attrib['tag'], '', field.text]))
        elif field.tag == '{http://www.loc.gov/MARC21/slim}datafield':
            tag = field.attrib['tag']
            if field.attrib['ind1'] != ' ':
                co.writerow([n, f, '', tag, 'ind1', field.attrib['ind1']])
            if field.attrib['ind2'] != ' ':
                co.writerow([n, f, '', tag, 'ind2', field.attrib['ind2']])
            sf = 1
            for subfield in field:
                co.writerow([n, f, sf, tag, subfield.attrib['code'], subfield.text])
                sf += 1
        else:
            raise Exception('Unknown field ' + field.tag)
        f += 1


@click.command
@click.option("-o", "--output", help="Output CSV/TSV (gz) / parquet file", required=True)
@click.argument('input', nargs=-1)
def convert(input: list[str], output: str) -> None:
    """Convert from MARCXML (gz/zip) INPUT files (actually glob patterns, parsed recursively) into (gzipped) CSV/TSV"""
    with cast(OpenFile, fsspec.open(output, 'wt', compression="infer")) as of:
        co = csv.writer(of, delimiter='\t' if '.tsv' in output else ',')
        co.writerow(['record_number', 'field_number', 'subfield_number', 'field_code', 'subfield_code', 'value'])
        n = 1
        input_files = fsspec.open_files(input, 'rb')
        tsize = reduce(lambda tsize, inf: tsize + inf.fs.size(inf.path), input_files, 0)
        pbar = tqdm.tqdm(total=tsize, unit='b', unit_scale=True, unit_divisor=1024)
        processed_files_tsize = 0
        for input_file in input_files:
            pbar.set_description(f"Processing {input_file.path}")
            with input_file as inf:
                    comp = compr[infer_compression(input_file.path)]
                    context = lxml.etree.iterparse(inf, events=('end',), tag='{http://www.loc.gov/MARC21/slim}record')
                    for _, elem in context:
                        convert_record(n, elem, co)
                        n += 1
                        elem.clear()
                        while elem.getprevious() is not None:
                            del elem.getparent()[0]
                        pbar.n = processed_files_tsize + inf.tell()
                        pbar.update(0)
                    del context
            processed_files_tsize += input_file.size


if __name__ == '__main__':
    convert()
