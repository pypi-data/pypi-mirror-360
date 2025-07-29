# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import os
from django_sorcery.db import databases
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declared_attr


class CustomBase:
    """_summary_"""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def as_dict(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


Base = declarative_base(cls=CustomBase)
db = databases.get(os.environ.get("DB_ALIAS", "default"))
