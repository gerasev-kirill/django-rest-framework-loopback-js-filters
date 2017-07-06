from rest_framework import exceptions


SORT_TYPES = {
    'ASC': '',
    'DESC': '-'
}





class ProcessOrderFilter:
    def __init__(self, queryset, _filter):
        order = _filter.get('order', None)
        if order:
            self.model_fields = queryset.model._meta.get_fields()
            self.model_name = queryset.model.__name__
            self.validate_value(order)

            field_name, sort_type = order.split(' ')
            sort_type = SORT_TYPES[sort_type]
            self.queryset = queryset.order_by(sort_type+field_name)

        else:
            self.queryset = queryset


    def validate_value(self, value):
        if not isinstance(value, str) and not isinstance(value, unicode):
            raise exceptions.NotAcceptable("Parameter for 'order' filter should be <type 'str'>, got - "+str(type(value)))
        v = value.split(' ')
        exists = False
        if len(v)!=2:
            raise exceptions.ParseError("Malformed parameter for 'order' filter. See https://loopback.io/doc/en/lb2/Order-filter.html")
        if v[1] not in ['ASC', 'DESC']:
            raise exceptions.ParseError("Malformed parameter for 'order' filter. See https://loopback.io/doc/en/lb2/Order-filter.html")

        for p in self.model_fields:
            if p.name == v[0]:
                exists = True
                break
        if not exists:
            raise exceptions.ParseError("Field '"+v[0]+"' for model '"+self.model_name+"' does't exists. You can't use order filter")
