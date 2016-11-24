# -*- coding: utf-8 -*-
from aiorest_ws.routers import SimpleRouter

from app.views import ManufacturerListView, ManufacturerView, CarListView, \
    CarView


router = SimpleRouter()
router.register('/manufacturer/{name}', ManufacturerView, ['GET', 'PUT'],
                name='manufacturer-detail')
router.register('/manufacturer/', ManufacturerListView, ['POST'])
router.register('/cars/{name}', CarView, ['GET', 'PUT'],
                name='car-detail')
router.register('/cars/', CarListView, ['POST'])
