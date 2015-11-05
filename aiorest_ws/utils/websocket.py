# -*- coding: utf-8 -*-
"""
    This module contains classes and functions, used for configuration
    issues with websockets.
"""
from autobahn.websocket.compress import PerMessageDeflateOffer, \
    PerMessageDeflateOfferAccept

__all__ = ('deflate_offer_accept', )


def deflate_offer_accept(offers):
    """Function to accept offers from the client.

    :param offers: iterable object (list, tuple), where every object
                   is instance of PerMessageDeflateOffer.
    """
    for offer in offers:
        if isinstance(offer, PerMessageDeflateOffer):
            return PerMessageDeflateOfferAccept(offer)
