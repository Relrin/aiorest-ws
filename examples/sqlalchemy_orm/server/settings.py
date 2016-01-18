# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_ENGINE = create_engine('sqlite://')
SQLALCHEMY_SESSION = sessionmaker(bind=SQLALCHEMY_ENGINE)
