# -*- coding: utf-8 -*-
from app.db import Base, User, Address
from settings import SQLALCHEMY_ENGINE, SQLALCHEMY_SESSION


if __name__ == '__main__':
    Base.metadata.create_all(SQLALCHEMY_ENGINE)
    session = SQLALCHEMY_SESSION()

    session.add_all([
        User(name='ed', fullname='Ed Jones', password='edspassword'),
        User(name='wendy', fullname='Wendy Williams', password='foobar'),
        User(name='mary', fullname='Mary Contrary', password='xxg527'),
        User(name='fred', fullname='Fred Flinstone', password='blah')
    ])

    jack = User(name='jack', fullname='Jack Bean', password='gjffdd')
    jack.addresses = [
        Address(email_address='jack@google.com'),
        Address(email_address='j25@yahoo.com')
    ]
    session.add(jack)
    session.commit()
