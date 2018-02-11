# coding: utf-8
""""""
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import pickle
from os import path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from yrttikanta.tables import Herb, Family, AltName, Base
from j24 import home


def create_herb(session, data):
    herb = Herb(name=data['kasvi'])
    herb.family = Family.get_or_create(session, name=data['heimo'][0],
                                       name_fi=data['heimo'][1])
    alt_names = set() # prevent duplicates
    for alt_name in data['muut nimet']:
        alt_names.add(AltName.get_or_create(session, alt_name))
    herb.alt_names = list(alt_names)
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


def create_database(session):
    ypkl = path.join(home(), 'koodi/yrttiharava/output/yrtit.pickle')
    ygen = data_gen_from_pkl(ypkl)
    store_all(session, ygen)


if __name__ == '__main__':
    engine = create_engine('sqlite:///../data/yrttikanta.db', echo=False)
    #Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    qfamily = session.query(Family.id, Family.name).order_by(Family.name)
