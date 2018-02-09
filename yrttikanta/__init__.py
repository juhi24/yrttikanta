# coding: utf-8
from os import path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
db_path = path.join(path.dirname(path.dirname(__file__)), 'data', 'yrttikanta.db')
engine = create_engine('sqlite:///{}'.format(db_path), echo=False)
print(engine)
Session = sessionmaker(bind=engine)