#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 18:59:15 2021

@author: jiemakel
"""

from typing import Iterator

import click as click
import lxml.etree
from .lib import convert

def convert_record(record: lxml.etree._ElementIterator) -> Iterator[tuple[int, int, str, str, str]]:
    for f, field in enumerate(record, start = 1):
        if field.tag == '{http://www.loc.gov/MARC21/slim}leader':
            yield f, 1, 'leader', '', field.text
        elif field.tag == '{http://www.loc.gov/MARC21/slim}controlfield':
            yield f, 1, field.attrib['tag'], '', field.text
        elif field.tag == '{http://www.loc.gov/MARC21/slim}datafield':
            tag = field.attrib['tag']
            if field.attrib['ind1'] != ' ':
                yield f, 1, tag, 'ind1', field.attrib['ind1']
            if field.attrib['ind2'] != ' ':
                yield f, 1, tag, 'ind2', field.attrib['ind2']
            sf = 1
            for sf, subfield in enumerate(field, start=1):
                yield f, sf, tag, subfield.attrib['code'], subfield.text
                sf += 1
        else:
            raise Exception('Unknown field ' + field.tag)

@click.command
@click.option("-o", "--output", help="Output CSV/TSV (gz) / parquet file", required=True)
@click.argument('input', nargs=-1)
def convert_marcxml(input: list[str], output: str):
    """Convert from MARCXML (compressed) INPUT files (actually glob patterns) into (compressed) CSV/TSV/parquet"""
    convert(
        '{http://www.loc.gov/MARC21/slim}record',
        convert_record,
        input,
        output
    )

if __name__ == '__main__':
    convert_marcxml()
