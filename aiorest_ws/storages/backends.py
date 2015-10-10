# -*- coding: utf-8 -*-
"""
    Backend classes for storages.
"""
__all__ = ('BaseStorageBackend', )


class BaseStorageBackend(object):
    """Base interface for storage."""
    def get(self, *args, **kwargs):
        """Get object from the storage."""
        pass

    def save(self, *args, **kwargs):
        """Save object in the storage."""
        pass
