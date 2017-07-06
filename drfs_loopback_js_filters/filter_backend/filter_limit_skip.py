from rest_framework import exceptions







class ProcessLimitSkipFilter:
    def __init__(self, queryset, _filter):
        limit = _filter.get('limit', None)
        skip = _filter.get('skip', None)

        self.validate_value('limit', limit)
        self.validate_value('skip', skip)

        if limit == 0:
            raise exceptions.NotAcceptable(
                "Parameter for 'limit' filter should be greater than zero")

        if skip and queryset.count() < skip:
            return queryset.none()

        if skip is not None and limit is not None:
            self.queryset = queryset[skip:]
            self.queryset = self.queryset[:limit]
        elif skip is not None:
            self.queryset = queryset[skip:]
        elif limit is not None:
            self.queryset = queryset[:limit]
        else:
            self.queryset = queryset


    def validate_value(self, property, value):
        if value is not None:
            if not isinstance(value, int):
                raise exceptions.NotAcceptable("Parameter for '"+property+"' filter should be <type 'int'>, got - "+str(type(value)))
            if value < 0:
                raise exceptions.NotAcceptable("Parameter for '"+property+"' filter should be positive number or zero")
