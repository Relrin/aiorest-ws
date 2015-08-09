# -*- coding: utf-8 -*-
"""
    This module contains classes and functions, used for configuration
    issue with websockets.
"""
__all__ = ('deflate_offer_accept', )

from autobahn.websocket.compress import PerMessageDeflateOffer, \
    PerMessageDeflateOfferAccept


def deflate_offer_accept(offers):
    """Function to accept offers from the client."""
    for offer in offers:
        if isinstance(offer, PerMessageDeflateOffer):
            return PerMessageDeflateOfferAccept(offer)
