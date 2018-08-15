# coding: utf-8
""""""
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

from os import path
from glob import glob
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


DATA_DIR = path.join(path.dirname(path.dirname(__file__)), 'data')

Base = declarative_base()
herb_names = Table('herb_names', Base.metadata,
                   Column('herb_id', ForeignKey('herbs.id'), primary_key=True),
                   Column('name_id', ForeignKey('alt_names.id'), primary_key=True))


class NameID():
    """a mixin providing unique name and id"""
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return '<{0} {1}>'.format(type(self).__name__, self.name)

    def __str__(self):
        return self.name


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
    sections = relationship('Section', back_populates='herb')

    def __init__(self, name, alt_names=None):
        self.name = name
        if alt_names is not None:
            for alt_name in alt_names:
                self.alt_names.append(AltName(alt_name))

    def sections_dict(self):
        return dict(tuple(s.as_tuple() for s in self.sections))

    def sections_html(self):
        return ''.join(s.as_html() for s in self.sections)

    def img_paths(self):
        name_glob = '{}_*.jpg'.format(self.name)
        img_glob = path.join(DATA_DIR, 'img', nameglob)
        return glob(img_glob)

    def as_dict(self):
        return dict(name=self.name,
                    alt_names=list(map(str, self.alt_names)),
                    family=self.family.name,
                    family_fi=self.family.name_fi,
                    html=self.sections_html(),
                    img_paths=self.img_paths())


class Family(GetMixin, Base):
    """herb family in scientific classification"""
    __tablename__ = 'families'
    name_fi = Column(String)
    herbs = relationship('Herb', order_by=Herb.id, back_populates='family')

    def __init__(self, name, name_fi=None):
        self.name = name.capitalize()
        self.name_fi = name_fi


class AltName(GetMixin, Base):
    """alternative herb names"""
    __tablename__ = 'alt_names'
    herbs = relationship('Herb',
                         secondary=herb_names,
                         back_populates='alt_names')

    def __init__(self, name):
        self.name = name.lower()


class Section(Base):
    """text section"""
    __tablename__ = 'sections'
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    title_id = Column(Integer, ForeignKey('section_titles.id'))
    title = relationship('SectionTitle')
    herb_id = Column(Integer, ForeignKey('herbs.id'))
    herb = relationship('Herb', back_populates='sections')

    def __repr__(self):
        return '<Section {}>'.format(self.title.name)

    def __str__(self):
        return self.text

    def as_tuple(self):
        return self.title.name, self.text

    def as_html(self):
        return '<h2>{}</h2>{}'.format(*self.as_tuple())


class SectionTitle(GetMixin, Base):
    """text section type"""
    __tablename__ = 'section_titles'
    priority = Column(Integer, unique=True)

    def __init__(self, name):
        self.name = name.capitalize()


