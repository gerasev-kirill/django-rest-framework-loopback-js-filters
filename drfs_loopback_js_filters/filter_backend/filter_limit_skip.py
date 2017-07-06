from rest_framework import exceptions







class ProcessLimitSkipFilter:
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
                raise exceptions.NotAcceptable(
                    "Parameter for '"+property+"' filter should be <type 'int'>, got - "+str(type(value))
                )
            if value < 0:
                raise exceptions.NotAcceptable(
                    "Parameter for '"+property+"' filter should be positive number or zero"
                )

        if property == 'limit' and limit == 0:
            raise exceptions.NotAcceptable(
                "Parameter for 'limit' filter should be greater than zero"
            )
