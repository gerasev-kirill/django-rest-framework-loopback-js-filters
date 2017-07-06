from rest_framework import exceptions


SORT_TYPES = {
    'ASC': '',
    'DESC': '-'
}





class ProcessOrderFilter:
    def __init__(self, queryset, _order):
        self.order = _order
        self.model_fields = queryset.model._meta.get_fields()
        self.model_name = queryset.model.__name__
        self.queryset = queryset


    def filter_queryset(self):
        if self.order:
            self.validate_value(self.order)
            field_name, sort_type = self.order.split(' ')
            sort_type = SORT_TYPES[sort_type]
            return self.queryset.order_by(sort_type+field_name)

        return self.queryset


    def validate_value(self, value):
        if not isinstance(value, str) and not isinstance(value, unicode):
            raise exceptions.NotAcceptable("Parameter for 'order' filter should be <type 'str'>, got - "+str(type(value)))

        v = value.split(' ')
        if len(v)!=2:
            raise exceptions.ParseError("Malformed parameter for 'order' filter. See https://loopback.io/doc/en/lb2/Order-filter.html")

        order_field, order_type = v

        if order_type not in SORT_TYPES.keys():
            raise exceptions.ParseError("Malformed parameter for 'order' filter. See https://loopback.io/doc/en/lb2/Order-filter.html")

        field_exists = False
        for p in self.model_fields:
            if p.name == order_field:
                field_exists = True
                break

        if not field_exists:
            raise exceptions.ParseError("Field '"+order_field+"' for model '"+self.model_name+"' does't exists. You can't use order filter")
