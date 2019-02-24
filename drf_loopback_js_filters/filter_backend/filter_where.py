from drf_loopback_js_filters.helpers import LbWhereQueryConverter
from rest_framework.exceptions import APIException





class ProcessWhereFilter:
    def __init__(self, queryset, _where, custom_where_filter_resolver=None):
        self.queryset = queryset
        self.where = _where
        self.has_m2m_in_where = False
        self.custom_where_filter_resolver =  custom_where_filter_resolver

    def is_where_with_m2m(self):
        return getattr(self, 'has_m2m_in_where', False)

    def filter_queryset(self):
        converter = LbWhereQueryConverter(
            self.queryset.model,
            where=self.where,
            custom_where_filter_resolver=self.custom_where_filter_resolver
        )
        q = converter.to_q()
        self.has_m2m_in_where = converter.has_m2m_in_where
        return self.queryset.filter(q)
