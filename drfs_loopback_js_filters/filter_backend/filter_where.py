from django.core import exceptions as djExceptions
from rest_framework import exceptions
from django.db.models import Q









class ProcessWhereFilter:
    def __init__(self, queryset, _where):
        if not isinstance(_where, dict):
            raise exceptions.ParseError("Parameter 'where' expected to be <type 'json'>, got - " + str(type(_where)))
        self.model_fields = queryset.model._meta.get_fields()
        q = Q()

        if 'or' in _where.keys():
            if not isinstance(_where['or'], list):
                raise exceptions.ParseError("Parameter 'or' for parameter 'where' expected to be <type 'array'>, got - " + str(type(_where['or'])))
            for v in _where['or']:
                q |= self.generate_rawq(v)
        elif 'and' in _where.keys():
            if not isinstance(_where['and'], list):
                raise exceptions.ParseError("Parameter for 'and' operator expected to be <type 'array'>, got - "+str(type(_where['and'])))
            m = {}
            for o in _where['and']:
                m.update(m)
            q = self.generate_rawq(m)
        else:
            q = self.generate_rawq(_where)
        self.queryset = queryset.filter(q)


    def validate_value(self, property, value):
        for p in self.model_fields:
            if p.name == property:
                try:
                    value = p.to_python(value)
                except djExceptions.ValidationError as e:
                    raise exceptions.ParseError("Field '"+property+"' validation error: "+str(e))
        return value

    def generate_rawq(self, data):
        q = Q()
        for k,v in data.items():
            djQ = self.lb_query_to_rawq(k, v)
            if djQ['filter']:
                q &= Q(**djQ['filter'])
            if djQ['exclude']:
                q &= ~Q(**djQ['exclude'])
        return q




    def _default(self, q, property, key, value):
        q['filter'][property+'__'+key] = value

    def _gt(self, q, property, value):
        self._default(q, property, 'gt', value)

    def _gte(self, q, property, value):
        self._default(q, property, 'gte', value)

    def _lt(self, q, property, value):
        self._default(q, property, 'lt', value)

    def _lte(self, q, property, value):
        self._default(q, property, 'lte', value)

    def _between(self, q, property, value):
        if not isinstance(value, list):
            raise exceptions.ParseError("Parameter for property '"+property+"' with operator 'between' expected to be <type 'array'>, got - "+str(type(value)))
        if len(value)!=2:
            raise exceptions.ParseError("Parameter for property '"+property+"' with operator 'between' expected to be <type 'array'> with 2 elements. Got "+len(value)+" elements")
        q['filter'][property+'__gte'] = value[0]
        q['filter'][property+'__lte'] = value[1]

    def _inq(self, q, property, value):
        if not isinstance(value, list):
            raise exceptions.ParseError("Parameter for property '"+property+"' with operator 'inq' expected to be <type 'array'>, got - "+str(type(value)))
        if value:
            q['filter'][property+'__in'] = value

    def _nin(self, q, property, value):
        if not isinstance(value, list):
            raise exceptions.ParseError("Parameter for property '"+property+"' with operator 'nin' expected to be <type 'array'>, got - "+str(type(value)))
        if value:
            q['exclude'][property+'__in'] = value

    def _neq(self, q, property, value):
        q['exclude'][property] = value

    def _like(self, q, property, value):
        q['filter'][property+'__contains'] = value

    def _nlike(self, q, property, value):
        q['exclude'][property+'__contains'] = value




    def lb_query_to_rawq(self, property, data):
        q = {'filter':{}, 'exclude':{}}
        if isinstance(data, unicode) or isinstance(data, str) or isinstance(data, bool) or isinstance(data, int) or isinstance(data, float) or data is None:
            data = self.validate_value(property, data)
            q['filter'][property] = data
            return q
        if not isinstance(data, dict):
            raise exceptions.ParseError("Parameters for property '"+property+"' expected to be <type 'str'>, <type 'number'>, <type 'bool'> or <type 'json'>, got - " + str(type(data)))

        for k,v in data.items():
            func = getattr(self, '_' + k, None)
            if not func:
                raise exceptions.ParseError("Unknown parameter '"+k+"' for property '"+property+"' for 'where' filter")
            func(q, property, v)

        return q
