# coding: utf-8
""""""
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import pickle
from os import path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from yrttikanta.tables import (Herb, Family, AltName, Section, SectionTitle,
                               Base)
from j24 import home


def list2p(paragraphs):
    """list of paragraphs to html"""
    return ''.join(['<p>{}</p>'.format(p) for p in paragraphs])


def create_herb(session, data):
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
        text = list2p(sectionsd[section_name])
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


def create_database(engine):
    """Create database and fill with data."""
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    ypkl = path.join(home(), 'koodi/yrttiharava/output/yrtit.pickle')
    ygen = data_gen_from_pkl(ypkl)
    store_all(session, ygen)
    session.close()


if __name__ == '__main__':
    engine = create_engine('sqlite:///../data/yrttikanta.db', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    h = session.query(Herb).first()
    #qfamily = session.query(Family.id, Family.name).order_by(Family.name)
