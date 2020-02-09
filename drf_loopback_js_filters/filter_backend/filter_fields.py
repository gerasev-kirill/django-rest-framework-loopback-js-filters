# -*- coding: utf-8 -*-
from rest_framework.exceptions import ParseError, NotAcceptable







class ProcessFieldsFilter:
    error_msgs = {
        'invalid_type': "Filter '{property}' should be {expected_types}, got - {type}",
        'invalid_type_for_property': "Value for property '{property}' with 'fields' filter should be {expected_types}, got - {type}",
        'both_true_and_false': "For properties in filter 'fields' you can use true OR false value. Not both at the same time"
    }

    def __init__(self, request, queryset, _filter):
        self.queryset = queryset
        self.request = request
        self.fields = _filter.get('fields', None)
        self.model_fields = [
            f.name
            for f in queryset.model._meta.get_fields()
        ]


    def filter_queryset(self):
        fields = self.validate_value(self.fields)
        if not fields:
            return self.queryset

        lb = {
            'visible':[],
            'hidden':[]
        }

        for field_name,value in fields.items():
            if not isinstance(value, bool):
                raise ParseError(self.error_msgs['invalid_type_for_property'].format(
                    property=field_name,
                    expected_types="<type 'bool'>",
                    type=type(value)
                ))
            if value:
                lb['visible'].append(field_name)
            else:
                lb['hidden'].append(field_name)

        if lb['visible'] and lb['hidden']:
            raise NotAcceptable(self.error_msgs['both_true_and_false'])

        self.request.LB_FILTER_FIELDS = lb
        return self.queryset


    def validate_value(self, value):
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ParseError(self.error_msgs['invalid_type'].format(
                property='fields',
                expected_types="<type 'dict'>",
                type=type(value)
            ))
        return value
