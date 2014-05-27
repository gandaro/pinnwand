#!/usr/bin/env python
import werkzeug
import datetime
import hashlib
import uuid
import sys
import pygments.lexers
import pygments.formatters

from sqlalchemy import Integer, Column, String, DateTime
from sqlalchemy import create_engine, Text
from sqlalchemy.orm import Session, backref
from sqlalchemy.ext.declarative import declarative_base, declared_attr

engine = create_engine("sqlite:////tmp/pinnwand.sqlite")
session = Session(engine)

class Base(object):
    """Base class which provides automated table names
    and a primary key column."""
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)

Base = declarative_base(cls=Base)

class HasDates(object):
    """Define attributes present on all dated content."""
    pub_date = Column(DateTime)
    chg_date = Column(DateTime)

class Paste(HasDates, Base):
    paste_id = Column(String)
    removal_id = Column(String)

    lexer = Column(String)

    raw = Column(Text)
    fmt = Column(Text)

    exp_date = Column(DateTime)

    def create_hash(self):
        # XXX This should organically grow as more is used, probably depending
        # on how often collissions occur.
        # Aside from that we should never repeat hashes which have been used before
        # without keeping the pastes in the database.
        return hashlib.sha224(str(uuid.uuid4())).hexdigest()[:12]

    def __init__(self, raw, lexer="text", expiry=datetime.timedelta(days=7)):
        self.pub_date = datetime.datetime.utcnow()
        self.chg_date = datetime.datetime.utcnow()

        # Generate a paste_id and a removal_id
        # Unless someone proves me wrong that I need to check for collisions
        # my famous last words will be that the odds are astronomically small
        self.paste_id = self.create_hash()
        self.removal_id = self.create_hash()

        self.raw = raw

        lexer = pygments.lexers.get_lexer_by_name(lexer)
        formatter = pygments.formatters.HtmlFormatter(linenos=True,
                cssclass="source")

        self.fmt = pygments.highlight(self.raw, lexer, formatter)

        # The expires date is the pub_date with the delta of the expiry
        if expiry:
            self.exp_date = self.pub_date + expiry
        else:
            self.exp_date = None

    def __repr__(self):
        return "<Paste(paste_id=%s)>" % (self.paste_id,)
