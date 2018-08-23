# coding: utf-8
""""""
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import pickle
import urllib.request
import http.client
from os import path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from yrttikanta.tables import (Herb, Family, AltName, Section, SectionTitle,
                               Base)
from j24 import home


def list2p(paragraphs):
    """list of paragraphs to html"""
    return ''.join(['<p>{}</p>'.format(p) for p in paragraphs])


def create_herb(session, data, separate_p=False):
    herb = Herb(name=data['kasvi'])
    herb.family = Family.get_or_create(session, name=data['heimo'][0],
                                       name_fi=data['heimo'][1])
    alt_names = set() # prevent duplicates
    for alt_name in data['muut nimet']:
        alt_names.add(AltName.get_or_create(session, alt_name))
    herb.alt_names = list(alt_names)
    sectionsd = data['sections']
    sections = []
    for section_name in sectionsd:
        if separate_p:
            text = list2p(sectionsd[section_name])
        else:
            text = sectionsd[section_name]
        section = Section(text=text)
        section.title = SectionTitle.get_or_create(session, name=section_name)
        sections.append(section)
    herb.sections = sections
    return herb


def data_gen_from_pkl(pkl_fpath):
    """generator from pickle"""
    with open(pkl_fpath, 'rb') as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


def store_all(session, herb_dicts):
    for d in herb_dicts:
        herb = create_herb(session, d)
        session.add(herb)
    session.commit()


def get_all_names(session):
    """Get all herb names as a tuple."""
    q = session.query(Herb.name)
    return tuple(x[0] for x in q.all())


def strip_accents(s):
    """ä -> a, ö -> o"""
    return s.replace('ä','a').replace('ö', 'o')


def herb_url(herb):
    """herb url from herb name"""
    urlfmt = 'http://yrttitarha.fi/kanta/{}'
    return urlfmt.format(strip_accents(herb))


def dl_herb_imgs(session, dl_dir=None):
    """download herb images"""
    dl_dir = dl_dir or path.realpath(path.join('..', 'data', 'img'))
    herbs = get_all_names(session)
    for h in herbs:
        print(h)
        url = herb_url(h)
        dl_fmt = path.join(dl_dir, strip_accents(h)+'_{}.jpg')
        trans = {'kuva': 'drawing', 'valokuva': 'photo'}
        for fi, en in trans.items():
            source = '{}/{}.jpg'.format(url, fi)
            try:
                urllib.request.urlretrieve(source, dl_fmt.format(en))
            except urllib.request.HTTPError:
                print('{} not found. Skipping.'.format(en.capitalize()))


def dl_html(session, dl_dir):
    """download herb texts"""
    import requests
    from bs4 import BeautifulSoup
    for name in get_all_names(session):
        url = herb_url(name)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        out_file = path.join(dl_dir, name+'.html')
        with open(out_file, 'w') as f:
            f.write(soup.prettify())


def create_database(engine, pkl_path='koodi/yrttiharava/output/yrtit.pickle'):
    """Create database and fill with data."""
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    ypkl = path.join(home(), pkl_path)
    ygen = data_gen_from_pkl(ypkl)
    store_all(session, ygen)
    session.close()


if __name__ == '__main__':
    engine = create_engine('sqlite:///../data/yrttikanta.db', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    h = session.query(Herb).first()
    #qfamily = session.query(Family.id, Family.name).order_by(Family.name)
