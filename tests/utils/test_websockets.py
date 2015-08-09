# -*- coding: utf-8 -*-
import pytest

from autobahn.websocket.compress import PerMessageDeflateOffer, \
    PerMessageDeflateOfferAccept

from aiorest_ws.utils.websocket import deflate_offer_accept


@pytest.mark.parametrize("offers, expected", [
    ([PerMessageDeflateOffer(), ], PerMessageDeflateOfferAccept),
    ([None, ], type(None)),
    ([], type(None)),
])
def test_deflate_offer_accept(offers, expected):
    assert type(deflate_offer_accept(offers)) is expected
