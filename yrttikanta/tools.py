# coding: utf-8
""""""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///../data/yrttikanta.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
