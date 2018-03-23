from drf_loopback_js_filters.helpers import LbWhereQueryConverter







class ProcessWhereFilter:
    def __init__(self, queryset, _where):
        self.queryset = queryset
        self.where = _where
        self.has_m2m_in_where = False


    def filter_queryset(self):
        converter = LbWhereQueryConverter(self.queryset.model, where=self.where)
        q = converter.to_q()
        self.has_m2m_in_where = converter.has_m2m_in_where
        return self.queryset.filter(q)
