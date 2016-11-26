# -*- coding: utf-8 -*-
"""
This module provides special classes (mixins) which used for getting data from
SQLAlchemy ORM when work with a model serializers or fields.
"""
from aiorest_ws.conf import settings
from aiorest_ws.db.orm.sqlalchemy.model_meta import model_pk


__all__ = ('ORMSessionMixin', 'SQLAlchemyMixin', )


class ORMSessionMixin(object):
    """
    Special wrapper around SQLALchemy querysets, when user specified them in
    for fields, serializers and etcetera.
    """
    def _get_session(self):
        return settings.SQLALCHEMY_SESSION()

    def get_queryset(self):
        """
        Return queryset, which will be executed during a session.
        Necessary to write queries for field in a models like:
            from sqlalchemy.orm.query import Query
            Query(User).filter(id==5).first()
        """
        # Avoid there "connection leaks", when developer described
        # queries like session.query(User).filter(id==5).first()
        if self.queryset.session:
            self.queryset.session.close()

        self.queryset.session = self._get_session()
        return self.queryset


class SQLAlchemyMixin(object):
    """
    Class which provide opportunity to get primary key from the passed object.
    """
    def _get_filter_args(self, query, data):
        mapper = query._bind_mapper()
        model = mapper.class_
        pk_fields = model_pk(model)
        return (getattr(model, field) == data[field] for field in pk_fields)

    def _get_object_pk(self, obj):
        mapper = obj.__mapper__
        model = mapper.class_
        pk_fields = model_pk(model)
        data = {str(field): getattr(obj, field) for field in pk_fields}
        return data if len(pk_fields) > 1 else data[pk_fields[0]]
