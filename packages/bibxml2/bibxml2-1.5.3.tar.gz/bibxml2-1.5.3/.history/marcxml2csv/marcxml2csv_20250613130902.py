#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 18:59:15 2021

@author: jiemakel
"""

import csv
from functools import reduce
from typing import Generator, Literal, cast

import click as click
import tqdm
import lxml.etree
import fsspec
from fsspec.core import OpenFile, compr, infer_compression

def convert_record(record: Sequence[lxml.etree._Element]) -> Generator[tuple[int, int, str, str, str]]:
    f = 1
    for field in record:
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
            for subfield in field:
                yield f, sf, tag, subfield.attrib['code'], subfield.text
                sf += 1
        else:
            raise Exception('Unknown field ' + field.tag)
        f += 1



if __name__ == '__main__':
    convert()
