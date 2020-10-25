# coding: utf-8
from os import path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
DATA_DIR = path.join(path.dirname(__file__), 'data')
db_path = path.join(DATA_DIR, 'yrttikanta.db')
engine = create_engine('sqlite:///{}'.format(db_path), echo=False)
print(engine)
Session = sessionmaker(bind=engine)