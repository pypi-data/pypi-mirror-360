#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 18:59:15 2021

@author: jiemakel
"""

import csv
import gzip
import itertools
import os
import zipfile
from functools import reduce
from pathlib import Path
from typing import Iterator, Tuple

import click as click
from hsciutil.fs import expand_globs
import tqdm
from lxml import etree


def convert_record(n, record, co) -> None:
    f = 1
    for field in record:
        tag = field.attrib['tag']
        sf = 1
        for subfield in field:
            co.writerow([n, f, sf, tag, subfield.attrib['code'], subfield.text])
            sf += 1
        f += 1


@click.command
@click.option("-o", "--output", help="Output CSV/TSV (gz) file", required=True)
@click.argument('input', nargs=-1, type=click.Path(exists=True))
def convert_picaxml(input: list[str], output: str) -> None:
    """Convert from PICAXML (gz/zip) INPUT files (actually glob patterns, parsed recursively) into (gzipped) CSV/TSV"""
    convert(
        '{http://www.loc.gov/MARC21/slim}record',
        convert_record,
        input,
        output
    )


@click.command
@click.option("-o", "--output", help="Output CSV/TSV (gz) / parquet file", required=True)
@click.argument('input', nargs=-1)
def convert_picaxml(input: list[str], output: str):
    """Convert from PICAXML (compressed) INPUT files (actually glob patterns) into (compressed) CSV/TSV/parquet"""
    convert(
        '{info:srw/schema/5/picaXML-v1.0}record',
        convert_record,
        input,
        output
    )


if __name__ == '__main__':
    convert_picaxml()
