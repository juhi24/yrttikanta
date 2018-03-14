# coding: utf-8
""""""
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import requests


if __name__ == '__main__':
    response = requests.get('http://yrttitarha.fi/kanta/valkosipuli/index.html')
    sections = parse_texts(response)

