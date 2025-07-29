#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 18:59:15 2021

@author: jiemakel
"""

from typing import Iterator
from unicodedata import normalize
import click as click
import lxml.etree
from .bibxml2 import convert



@click.command
@click.option("-o", "--output", help="Output CSV/TSV (gz) / parquet file", required=True)
@click.argument('input', nargs=-1)
def convert_marcxml(input: list[str], output: str):
    """Convert from MARCXML (compressed) INPUT files (actually glob patterns) into (compressed) CSV/TSV/parquet"""
    convert(
        ('{http://www.loc.gov/MARC21/slim}record', 'record'),
        convert_record,
        input,
        output
    )

if __name__ == '__main__':
    convert_marcxml()
