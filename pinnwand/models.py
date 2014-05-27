#!/usr/bin/env python
import random
import werkzeug
import datetime
import os
import hashlib
import re
import unicodedata
import pygments.lexers
import pygments.formatters

from sqlalchemy import Integer, Column, String, ForeignKey, Table, DateTime
from sqlalchemy import Boolean, create_engine, Text
from sqlalchemy.orm import relationship, Session, backref
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
    paste_id = Column(Integer)
    removal_id = Column(Integer)

    lexer = Column(String)

    raw = Column(Text)
    fmt = Column(Text)

    exp_date = Column(DateTime)

    def __init__(self, raw, lexer="text", expiry=datetime.timedelta(days=7)):
        self.pub_date = datetime.datetime.utcnow()
        self.chg_date = datetime.datetime.utcnow()

        # Generate a paste_id and a removal_id
        self.paste_id = random.randint(1, 100000)
        self.removal_id = random.randint(1, 100000)

        self.raw = raw

        lexer = pygments.lexers.get_lexer_by_name(lexer)
        formatter = pygments.formatters.HtmlFormatter(linenos=True,
                cssclass="source")

        self.fmt = pygments.highlight(self.raw, lexer, formatter)

        # The expires date is the pub_date with the delta of the expiry
        self.exp_date = self.pub_date + expiry

    def __repr__(self):
        return "<Paste(paste_id=%s)>" % (self.paste_id,)
