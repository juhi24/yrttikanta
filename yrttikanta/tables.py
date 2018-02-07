# coding: utf-8
""""""
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()
herb_names = Table('herb_names', Base.metadata,
                   Column('herb_id', ForeignKey('herbs.id'), primary_key=True),
                   Column('name_id', ForeignKey('alt_names.id'), primary_key=True))


class NameID():
    """a mixin providing unique name and id"""
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)


class GetMixin(NameID):
    """a mixin with get-or-create constructor"""

    @classmethod
    def get_or_create(cls, session, name, **kws):
        # get the session cache, creating it if necessary
        cache = session._unique_cache = getattr(session, '_unique_cache', {})
        # create a key for memoizing
        key = (cls, name)
        # check the cache first
        o = cache.get(key)
        if o is None:
            # check the database if it's not in the cache
            o = session.query(cls).filter_by(name=name).first()
            if o is None:
                # create a new one if it's not in the database
                o = cls(name=name, **kws)
                session.add(o)
            # update the cache
            cache[key] = o
        return o


class Herb(NameID, Base):
    """the main herb class"""
    __tablename__ = 'herbs'
    # many to one
    family_id = Column(Integer, ForeignKey('families.id'))
    family = relationship('Family', back_populates='herbs')
    # many to many
    alt_names = relationship('AltName',
                             secondary=herb_names,
                             back_populates='herbs')

    def __init__(self, name, alt_names=None):
        self.name = name
        if alt_names is not None:
            for alt_name in alt_names:
                self.alt_names.append(AltName(alt_name))

    def __repr__(self):
        return '<Herb {}>'.format(self.name)


class Family(GetMixin, Base):
    """herb family in scientific classification"""
    __tablename__ = 'families'
    name_fi = Column(String)
    herbs = relationship('Herb', order_by=Herb.id, back_populates='family')

    def __init__(self, name, name_fi=None):
        self.name = name.capitalize()
        self.name_fi = name_fi

    def __repr__(self):
        return '<Family {}>'.format(self.name)


class AltName(GetMixin, Base):
    """Alternative herb names"""
    __tablename__ = 'alt_names'
    herbs = relationship('Herb',
                         secondary=herb_names,
                         back_populates='alt_names')

    def __init__(self, name):
        self.name = name.lower()

    def __repr__(self):
        return '<AltName {}>'.format(self.name)

