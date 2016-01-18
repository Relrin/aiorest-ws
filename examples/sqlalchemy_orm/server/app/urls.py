# -*- coding: utf-8 -*-
from aiorest_ws.routers import SimpleRouter

from app.views import UserListView, UserView, CreateUserView, AddressView, \
    CreateAddressView

router = SimpleRouter()
router.register('/user/list', UserListView, 'GET')
router.register('/user/{id}', UserView, ['GET', 'PUT'], name='user-detail')
router.register('/user/', CreateUserView, ['POST'])
router.register('/address/{id}', AddressView, ['GET', 'PUT'],
                name='address-detail')
router.register('/address/', CreateAddressView, ['POST'])
