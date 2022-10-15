# coding: utf-8

# builtin
from os import path

# pypi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATA_DIR = path.join(path.dirname(__file__), 'data')

_db_path = path.join(DATA_DIR, 'yrttikanta.db')

engine = create_engine('sqlite:///{}'.format(_db_path), echo=False)
Session = sessionmaker(bind=engine)
