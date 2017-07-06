from rest_framework.filters import BaseFilterBackend
from django.core import exceptions as djExceptions
from rest_framework import exceptions

import json

from .filter_where import ProcessWhereFilter
from .filter_fields import ProcessFieldsFilter
from .filter_limit_skip import ProcessLimitSkipFilter
from .filter_order import ProcessOrderFilter




class LoopbackJsFilterBackend(BaseFilterBackend):


    def _filter_queryset(self, request, queryset, _filter):
        e = ProcessOrderFilter(queryset, _filter)
        queryset = e.queryset
        if _filter.get('fields',None):
            ProcessFieldsFilter(request, queryset, _filter['fields'])
        if _filter.get('where', None):
            e = ProcessWhereFilter(queryset, _filter['where'])
            queryset = e.queryset

        e = ProcessLimitSkipFilter(queryset, _filter)
        return e.queryset


    def filter_queryset(self, request, queryset, view):
        query = request.query_params or {}
        _where = query.get('where', None)
        _filter = query.get('filter', None)

        if _where and _filter:
            raise exceptions.NotAcceptable("Provide 'filter' OR 'where' query. Not both at the same time.")
        if not _filter and not _where:
            return queryset

        if _filter:
            try:
                _filter = json.loads(_filter)
            except:
                raise exceptions.ParseError("Malformed json string for query param 'filter'")
        elif _where:
            try:
                _where = json.loads(_where)
                _filter = {'where': _where}
            except:
                raise exceptions.ParseError("Malformed json string for query param 'where'")

        return self._filter_queryset(request, queryset, _filter)



    def get_schema_fields(self, view):
        try:
            import coreapi
            return [
                coreapi.Field(
                    name='filter',
                    required=False,
                    location='query',
                    description="Filter defining fields, where, include, order, offset, and limit"
                )
            ]
        except:
            return []
