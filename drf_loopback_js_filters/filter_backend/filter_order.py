# -*- coding: utf-8 -*-
import six
from rest_framework.exceptions import NotAcceptable, ParseError
from django.db.models import Max, Min


ORDER_TYPES = {
    'ASC': '',
    'DESC': '-'
}
STRING_TYPES = tuple(
    [six.text_type] + list(six.string_types)
)

def get_field_name(order):
    if order[0] == '-':
        return order[1:], True
    return order, False




class ProcessOrderFilter:
    error_msgs = {
        'invalid_type': "Filter '{property}' should be {expected_types}, got - {type}",
        'malformed_order': "Malformed parameter for 'order' filter. See https://loopback.io/doc/en/lb2/Order-filter.html",
        'invalid_field_name': "Field '{field_name}' for model '{model_name}' does't exists. You can't use 'order' filter"
    }

    def __init__(self, queryset, _order):
        self.order = _order
        self.model_fields = queryset.model._meta.get_fields()
        self.model_name = queryset.model.__name__
        self.queryset = queryset
        self.order_field = None


    def filter_queryset(self):
        if not self.order:
            return self.queryset
        order = self.validate_value(self.order)
        fieldname, order_type = get_field_name(order)
        if self.is_order_by_m2m():
            # Ordering by related field creates duplicates in resultant querysets
            # https://code.djangoproject.com/ticket/18165
            # WTF django??
            if order_type:
                return self.queryset.annotate(Max(fieldname)).order_by(order+'__max')
            else:
                return self.queryset.annotate(Min(fieldname)).order_by(order+'__min')
        return self.queryset.order_by(order)


    def is_order_by_m2m(self):
        if not self.order_field:
            return False
        if getattr(self.order_field, 'is_relation', False) and getattr(self.order_field, 'm2m_field_name', None):
            return True
        return False


    def validate_value(self, value):
        if not isinstance(value, STRING_TYPES):
            raise NotAcceptable(self.error_msgs['invalid_type'].format(
                property='order',
                expected_types="<type 'str'>",
                type=type(value)
            ))

        if value.strip() == '?':
            return '?'

        if len(value.split(' ')) != 2:
            raise ParseError(self.error_msgs['malformed_order'])

        order_field, order_type = value.split(' ')
        if order_type not in ORDER_TYPES.keys():
            raise ParseError(self.error_msgs['malformed_order'])

        for p in self.model_fields:
            if p.name == order_field.split('__')[0]:
                self.order_field = p
                break

        if not self.order_field:
            raise ParseError(self.error_msgs['invalid_field_name'].format(
                field_name=order_field,
                model_name=self.model_name
            ))

        return ORDER_TYPES[order_type] + order_field
