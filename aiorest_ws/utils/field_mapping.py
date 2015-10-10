# -*- coding: utf-8 -*-
"""
    Helper functions for mapping model fields to a dictionary of default
    keyword arguments that should be used for serializers.
"""
__all__ = ('extract_model_data', )


def extract_model_data(model):
    model_data = {}
    for key, value in model.__dict__.items():
        if key.startswith('_'):
            key = key.replace('_', '', 1)
            model_data[key] = value
        else:
            model_data[key] = value
    return model_data
