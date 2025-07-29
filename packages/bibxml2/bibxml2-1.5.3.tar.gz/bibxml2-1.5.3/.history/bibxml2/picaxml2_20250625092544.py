#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 18:59:15 2021

@author: jiemakel
"""

from unicodedata import normalize
from typing import Iterator

import click as click
import lxml.etree
from .bibxml2 import convert


d

@click.command
@click.option("-o", "--output", help="Output CSV/TSV (gz) / parquet file", required=True)
@click.argument('input', nargs=-1)
def convert_picaxml(input: list[str], output: str):
    """Convert from PICAXML (compressed) INPUT files (actually glob patterns) into (compressed) CSV/TSV/parquet"""
    convert(
        ('{info:srw/schema/5/picaXML-v1.0}record', 'record'),
        convert_record,
        input,
        output
    )


if __name__ == '__main__':
    convert_picaxml()
