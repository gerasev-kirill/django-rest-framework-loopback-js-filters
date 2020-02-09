# -*- coding: utf-8 -*-
from rest_framework.exceptions import NotAcceptable







class ProcessLimitSkipFilter:
    error_msgs = {
        'invalid_type': "Parameter for '{property}' filter should be <type 'int'>, got - {type}",
        'less_than_zero': "Parameter for '{property}' filter should be positive number or zero",
        'limit_is_zero': "Parameter for 'limit' filter should be greater than zero"
    }

    def __init__(self, queryset, _filter):
        self.limit = _filter.get('limit', None)
        self.skip = _filter.get('skip', None)
        self.queryset = queryset


    def filter_queryset(self):
        self.validate_value('limit', self.limit)
        self.validate_value('skip', self.skip)
        queryset = self.queryset

        if self.skip and self.queryset.count() < self.skip:
            return queryset.none()

        if self.skip is not None:
            queryset = queryset[self.skip:]
        if self.limit is not None:
            queryset = queryset[:self.limit]

        return queryset


    def validate_value(self, property, value):
        if value is not None:
            if not isinstance(value, int):
                raise NotAcceptable(self.error_msgs['invalid_type'].format(
                    property=property,
                    type=type(value)
                ))
            if value < 0:
                raise NotAcceptable(self.error_msgs['less_than_zero'].format(
                    property=property
                ))

        if property == 'limit' and value == 0:
            raise NotAcceptable(self.error_msgs['limit_is_zero'])
