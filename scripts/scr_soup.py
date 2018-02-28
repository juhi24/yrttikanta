# coding: utf-8
""""""
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

from bs4 import BeautifulSoup, NavigableString, Tag
import requests

if __name__ == '__main__':
    response = requests.get('http://yrttitarha.fi/kanta/valkosipuli/index.html')
    soup = BeautifulSoup(response.text, 'lxml')
    sections = {}
    for t in ('a', 'b', 'i'):
        for tag in soup.find_all(t):
            tag.replace_with_children()
    for h2 in soup.find_all('h2'):
        if h2.parent.name == 'p':
            h2.parent.replace_with_children()
        p_texts = []
        for s in h2.next_siblings:
            if s.name == 'h2':
                break
            if hasattr(s, 'descendants'):
                br = False
                for d in s.descendants:
                    if d.name == 'h2':
                        br = True
                if br:
                    break
            if hasattr(s, 'text'):
                if s.text:
                    p_texts.append(s.text)
        sections[h2.text] = p_texts

