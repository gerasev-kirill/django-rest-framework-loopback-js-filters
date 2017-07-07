from rest_framework.filters import BaseFilterBackend
from django.core import exceptions as djExceptions
from rest_framework.exceptions import NotAcceptable, ParseError

import json

from .filter_where import ProcessWhereFilter
from .filter_fields import ProcessFieldsFilter
from .filter_limit_skip import ProcessLimitSkipFilter
from .filter_order import ProcessOrderFilter





class LoopbackJsFilterBackend(BaseFilterBackend):
    error_msgs = {
        'malformed_json': "Malformed json string for query param '{param}'",
        'both_filter_and_where': "Provide 'filter' OR 'where' query. Not both at the same time"
    }

    def _filter_queryset(self, request, queryset, _filter):
        p = ProcessOrderFilter(queryset, _filter.get('order', None))
        queryset = p.filter_queryset()

        if _filter.get('fields',None):
            p = ProcessFieldsFilter(request, queryset, _filter['fields'])
            queryset = p.filter_queryset()

        if _filter.get('where', None):
            p = ProcessWhereFilter(queryset, _filter['where'])
            queryset = p.filter_queryset()

        p = ProcessLimitSkipFilter(queryset, _filter)
        return p.filter_queryset()


    def filter_queryset(self, request, queryset, view):
        query = request.query_params or {}
        _where = query.get('where', None)
        _filter = query.get('filter', None)

        if _where and _filter:
            raise NotAcceptable(self.error_msgs['both_filter_and_where'])
        if not _filter and not _where:
            return queryset

        if _filter:
            try:
                _filter = json.loads(_filter)
            except:
                raise ParseError(self.error_msgs['malformed_json'].format(
                    param='filter'
                ))
        elif _where:
            try:
                _where = json.loads(_where)
                _filter = {'where': _where}
            except:
                raise ParseError(self.error_msgs['malformed_json'].format(
                    param='where'
                ))

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
