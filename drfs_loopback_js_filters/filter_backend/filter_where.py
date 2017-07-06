from django.core import exceptions as djExceptions
from rest_framework import exceptions
from django.db.models import Q









class ProcessWhereFilter:
    def __init__(self, queryset, _where):
        self.model_fields = queryset.model._meta.get_fields()
        self.queryset = queryset
        self.model_name = queryset.model.__name__
        self.where = _where


    def filter_queryset(self):
        if not isinstance(self.where, dict):
            raise exceptions.ParseError(
                "Parameter 'where' expected to be <type 'dict'>, got - " + str(type(self.where))
            )

        q = Q()

        if 'or' in self.where.keys():
            if not isinstance(self.where['or'], list):
                raise exceptions.ParseError(
                    "Parameter 'or' for parameter 'where' expected to be <type 'array'>, got - " + str(type(self.where['or']))
                )
            for v in self.where['or']:
                q |= self.generate_rawq(v)
        elif 'and' in self.where.keys():
            if not isinstance(self.where['and'], list):
                raise exceptions.ParseError(
                    "Parameter for 'and' operator expected to be <type 'array'>, got - "+str(type(self.where['and']))
                )
            _q = {}
            for o in self.where['and']:
                _q.update(o)
            q = self.generate_rawq(_q)
        else:
            q = self.generate_rawq(self.where)

        return self.queryset.filter(q)


    def get_field_by_path(self, property):
        def get_field(model_fields, _property_path):
            if not _property_path:
                return None
            field_instance = None
            property_name = _property_path.pop(0)
            for field in model_fields:
                if field.name == property_name:
                    related_model = getattr(field, 'related_model', None)
                    if related_model and _property_path:
                        # relational field
                        field_instance = get_field(
                            related_model._meta.get_fields(),
                            _property_path
                        )
                        break
                    elif related_model and not _property_path:
                        # can't query by related_model and not by field
                        raise exceptions.NotAcceptable(
                            "To filter queryset against related model '"+related_model.__name__+"' use '"+property+".some_field' instead '"+property+"'"
                        )
                    elif not related_model:
                        # regular field
                        field_instance = field
                        break
            return field_instance

        _property = property.split('.')
        if len(_property) == 1:
            _property = property.split('__')
        return get_field(self.model_fields, list(_property)), '__'.join(_property)



    def validate_value(self, property, value):
        field_instance, normalized_property = self.get_field_by_path(property)
        if not field_instance:
            raise exceptions.ParseError("Field '"+property+"' for model '"+self.model_name+"' does't exists. You can't use where filter")

        try:
            value = field_instance.to_python(value)
        except djExceptions.ValidationError as e:
            raise exceptions.ParseError("Field '"+property+"' validation error: "+str(e))
        return normalized_property, value



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
            raise exceptions.ParseError(
                "Parameter for property '"+property+"' with operator 'between' expected to be <type 'array'>, got - "+str(type(value))
            )
        if len(value)!=2:
            raise exceptions.ParseError(
                "Parameter for property '"+property+"' with operator 'between' expected to be <type 'array'> with 2 elements. Got "+str(len(value))+" elements"
            )
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

    def _ilike(self, q, property, value):
        q['filter'][property+'__icontains'] = value

    def _nilike(self, q, property, value):
        q['exclude'][property+'__icontains'] = value


    def lb_query_to_rawq(self, property, data):
        q = {'filter':{}, 'exclude':{}}
        if isinstance(data, (unicode, str, bool, int, float)) or data is None:
            property, data = self.validate_value(property, data)
            q['filter'][property] = data
            return q
        if not isinstance(data, dict):
            raise exceptions.ParseError("Parameters for property '"+property+"' expected to be <type 'str'>, <type 'number'>, <type 'bool'> or <type 'dict'>, got - " + str(type(data)))

        field_instance, normalized_property = self.get_field_by_path(property)

        for k,v in data.items():
            func = getattr(self, '_' + k, None)
            if not func:
                raise exceptions.ParseError("Unknown parameter '"+k+"' for property '"+property+"' for 'where' filter")
            func(q, normalized_property, v)

        return q
