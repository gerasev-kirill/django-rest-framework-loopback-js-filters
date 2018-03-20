from drf_loopback_js_filters.helpers import LbWhereQueryConverter







class ProcessWhereFilter:
    def __init__(self, queryset, _where):
        self.queryset = queryset
        self.where = _where


    def filter_queryset(self):
        converter = LbWhereQueryConverter(self.queryset.model, where=self.where)
        return self.queryset.filter(
            converter.to_q()
        )
