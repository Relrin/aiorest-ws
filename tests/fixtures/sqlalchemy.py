# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ENGINE = create_engine('sqlite://')
SESSION = sessionmaker(bind=ENGINE)
