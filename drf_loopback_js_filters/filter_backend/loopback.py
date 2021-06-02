# -*- coding: utf-8 -*-
from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import NotAcceptable, ParseError
from django.db import connections

import json, warnings

from .filter_where import ProcessWhereFilter
from .filter_fields import ProcessFieldsFilter
from .filter_limit_skip import ProcessLimitSkipFilter
from .filter_order import ProcessOrderFilter





class LoopbackJsFilterBackend(BaseFilterBackend):
    error_msgs = {
        'malformed_json': "Malformed json string for query param '{property}'",
        'both_filter_and_where': "Provide 'filter' OR 'where' query. Not both at the same time"
    }

    def _filter_queryset(self, request, queryset, _filter):
        p = ProcessOrderFilter(queryset, _filter.get('order', None))
        queryset = p.filter_queryset()
        has_m2m_in_order = p.is_order_by_m2m()
        has_m2m_in_where = False

        p = ProcessFieldsFilter(request, queryset, _filter)
        queryset = p.filter_queryset()

        if _filter.get('where', None):
            if hasattr(self, 'custom_where_filter_resolver'):
                p = ProcessWhereFilter(
                    queryset,
                    _filter['where'],
                    custom_where_filter_resolver=self.custom_where_filter_resolver()
                )
            else:
                p = ProcessWhereFilter(queryset, _filter['where'])
            queryset = p.filter_queryset()
            has_m2m_in_where = p.is_where_with_m2m()


        # Ordering by related field creates duplicates in resultant querysets
        # https://code.djangoproject.com/ticket/18165
        # WTF django??
        if has_m2m_in_where and not has_m2m_in_order:
            queryset = queryset.distinct()
        '''
        if has_m2m_in_order or has_m2m_in_where:
            if has_m2m_in_order:
                ids = []
                base_queryset = queryset.model.objects.all()

                for id in queryset.values_list(queryset.model._meta.pk.name, flat=True).iterator():
                    if id not in ids:
                        ids.append(id)

                preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
                queryset = base_queryset.filter(id__in=ids).order_by(preserved)
            else:
                queryset = queryset.distinct()
            #
            using = queryset.db
            if connections[using].vendor in ['sqlite', 'sqlite3']:
                # we can't use distinct with fields in sqlite provider
                if has_m2m_in_order:
                    ids = []
                    base_queryset = queryset.model.objects.all()

                    for id in queryset.values_list(queryset.model._meta.pk.name, flat=True).iterator():
                        if id not in ids:
                            ids.append(id)

                    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
                    queryset = base_queryset.filter(id__in=ids).order_by(preserved)
                else:
                    queryset = queryset.distinct()
            else:
                queryset = queryset.distinct()
        '''
        p = ProcessLimitSkipFilter(queryset, _filter)
        queryset = p.filter_queryset()
        return queryset


    def filter_queryset(self, request, queryset, view):
        ignore_filter_backend = []
        if view:
            method = getattr(view, view.action)
            ignore_filter_backend = getattr(method, 'ignore_filter_backend', False)
            if ignore_filter_backend is True:
                return queryset

        if isinstance(ignore_filter_backend, (list, tuple)) and queryset.model.__name__ in ignore_filter_backend:
            return queryset

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
                    property='filter'
                ))
        elif _where:
            try:
                _where = json.loads(_where)
                _filter = {'where': _where}
                if query.get('limit', None):
                    _filter['limit'] = int(query['limit'])
                if query.get('skip', None):
                    _filter['skip'] = int(query['skip'])
            except:
                raise ParseError(self.error_msgs['malformed_json'].format(
                    property='where'
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
                    description="Stringified JSON filter defining fields, where, include, order, offset, and limit. See https://loopback.io/doc/en/lb2/Querying-data.html#using-stringified-json-in-rest-queries"
                )
            ]
        except:
            return []

    def get_schema_operation_parameters(self, view):
        return [{
            'name': 'filter',
            'required': False,
            'in': 'query',
            'description': 'Filter defining fields, where, order, skip, and limit. <a target="_blank" href="https://loopback.io/doc/en/lb2/Querying-data.html#using-stringified-json-in-rest-queries">Docs here</a>',
            'schema':{
                'type': 'object',
                'properties': {
                    'where': {
                        'type': 'object'
                    },
                    'limit': {
                        'type': 'integer'
                    },
                    'skip': {
                        'type': 'integer'
                    },
                    'order': {
                        'type': 'string'
                    }
                }
            }
        }]
