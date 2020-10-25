# coding: utf-8
""""""

import requests


if __name__ == '__main__':
    response = requests.get('http://yrttitarha.fi/kanta/valkosipuli/index.html')
    sections = parse_texts(response)

