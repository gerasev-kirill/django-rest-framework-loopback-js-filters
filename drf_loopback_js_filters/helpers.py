from django.core import exceptions as djExceptions
from rest_framework.exceptions import ParseError, NotAcceptable
from django.db.models import Q, fields as djFields
from django.utils import six
from collections import OrderedDict
from django.db.models.fields.reverse_related import ManyToOneRel as ManyToOneRelReversed, ManyToManyRel as ManyToManyRelReversed
from django.db.models.fields.related import ManyToManyField


SIMPLE_TYPES = tuple(
    [ bool, float, six.text_type ] \
    + list(six.string_types) \
    + list(six.integer_types)
)



def convert_value_to_python(field, value):
    if not value:
        return value
    if isinstance(value, list):
        return [
            convert_value_to_python(field, v)
            for v in value
        ]
    # don't use isinstance here!
    if field.__class__ == djFields.DateField:
        if value in [None, 'null', 'undefined']:
            return None
        return field.to_python(value.split('T')[0])
    return value

def is_m2m(f):
    if getattr(f, 'is_relation', False) and getattr(f, 'm2m_field_name', None):
        return True
    if f.__class__ in [ManyToOneRelReversed, ManyToManyRelReversed]:
        return True
    if f.__class__ in [ManyToManyField]:
        return True
    return False



class LbWhereQueryConverter(object):
    error_msgs = {
        'invalid_type': "Filter '{property}' should be <type 'dict'>, got - {type}",
        'invalid_type_for_operator': "Value for operator '{operator}' for parameter '{property}' expected to be {expected_types}, got - {type}",
        'invalid_type_for_property': "Value for property '{property}' expected to be {expected_types}, got - {type}",
        'invalid_type_for_property_with_operator': "Value for property '{property}' with operator '{operator}' expected to be {expected_types}, got - {type}",
        'unknown_operator_for_property': "Unknown operator '{operator}' for property '{property}' for 'where' filter",

        'no_related_model_field': "To filter queryset against related model '{model_name}' use '{property}.some_field' instead of '{property}'",
        'field_doesnt_exist': "Field '{property}' for model '{model_name}' does't exists. You can't use 'where' filter",
        'field_validation_fail': "Field '{property}' validation error: {error}"
    }

    def __init__(self, model_class, where={}, custom_where_filter_resolver=None):
        if not isinstance(where, dict):
            raise ParseError(self.error_msgs['invalid_type'].format(
                property='where',
                type=type(where)
            ))
        self.where = where
        self.model_class = model_class
        self.model_fields = model_class._meta.get_fields()
        self.model_name = model_class.__name__
        self.has_m2m_in_where = False
        self.custom_where_filter_resolver = custom_where_filter_resolver





    def get_field_by_path(self, property):
        def get_field(model_fields, _property_path):
            if not _property_path:
                return None, False
            m2m = False
            field_instance = None
            property_name = _property_path.pop(0)
            for field in model_fields:
                if field.name == property_name:
                    related_model = getattr(field, 'related_model', None)
                    if is_m2m(field):
                        m2m = True
                    if related_model and _property_path:
                        # relational field
                        field_instance, _m2m = get_field(
                            related_model._meta.get_fields(),
                            _property_path
                        )
                        m2m = _m2m or m2m
                        break
                    elif related_model and not _property_path:
                        id_field, _m2m = get_field(related_model._meta.get_fields(), ['id'])
                        m2m = _m2m or m2m
                        if id_field:
                            # try to filter by id property
                            return id_field, m2m
                        # 'id' field doesn't exists??
                        # can't query by related_model and not by field
                        raise NotAcceptable(self.error_msgs['no_related_model_field'].format(
                            model_name=related_model.__name__,
                            property=property
                        ))
                    elif not related_model:
                        # regular field
                        field_instance = field
                        break
            return field_instance, m2m

        _property = property.split('.')
        if len(_property) == 1:
            _property = property.split('__')
        field, field_is_m2m = get_field(self.model_fields, list(_property))
        return field, field_is_m2m, '__'.join(_property)



    def validate_value(self, property, value):
        field_instance, m2m, normalized_property = self.get_field_by_path(property)
        if not field_instance:
            raise ParseError(self.error_msgs['field_doesnt_exist'].format(
                property=property,
                model_name=self.model_name
            ))

        try:
            value = field_instance.to_python(value)
        except djExceptions.ValidationError as e:
            raise ParseError(self.error_msgs['field_validation_fail'].format(
                property=property,
                error=e
            ))
        return normalized_property, value



    def generate_rawq(self, data):
        q = Q()
        for k,v in data.items():
            djQ = None
            if self.custom_where_filter_resolver:
                if hasattr(self.custom_where_filter_resolver, 'resolve_%s_query' % k):
                    func = getattr(self.custom_where_filter_resolver, 'resolve_%s_query' % k)
                    djQ, has_m2m = func(k,v)
                    if has_m2m:
                        self.has_m2m_in_where = True
            if not djQ:
                djQ = self.lb_query_to_rawq(k, v)
            if djQ['filter']:
                if isinstance(djQ['filter'], Q):
                    q &= djQ['filter']
                else:
                    q &= Q(**djQ['filter'])
            if djQ['exclude']:
                if isinstance(djQ['exclude'], Q):
                    q &= djQ['exclude']
                else:
                    q &= ~Q(**djQ['exclude'])
        return q




    def _default(self, q, property, key, value, options=None):
        q['filter'][property+'__'+key] = value

    def _gt(self, q, property, value, options=None):
        self._default(q, property, 'gt', value)

    def _gte(self, q, property, value, options=None):
        self._default(q, property, 'gte', value)

    def _lt(self, q, property, value, options=None):
        self._default(q, property, 'lt', value)

    def _lte(self, q, property, value, options=None):
        self._default(q, property, 'lte', value)

    def _between(self, q, property, value, options=None):
        if not isinstance(value, list):
            raise ParseError(self.error_msgs['invalid_type_for_property_with_operator'].format(
                property=property,
                operator='between',
                expected_types="<type 'array'>",
                type=type(value)
            ))
        if len(value)!=2:
            raise ParseError(self.error_msgs['invalid_type_for_property_with_operator'].format(
                property=property,
                operator='between',
                expected_types="<type 'array'> with 2 elements",
                type=str(len(value))+" elements"
            ))
        q['filter'][property+'__gte'] = value[0]
        q['filter'][property+'__lte'] = value[1]

    def _inq(self, q, property, value, options=None):
        if not isinstance(value, list):
            raise ParseError(self.error_msgs['invalid_type_for_property_with_operator'].format(
                property=property,
                operator='inq',
                expected_types="<type 'array'>",
                type=type(value)
            ))
        if value:
            q['filter'][property+'__in'] = value

    def _nin(self, q, property, value, options=None):
        if not isinstance(value, list):
            raise ParseError(self.error_msgs['invalid_type_for_property_with_operator'].format(
                property=property,
                operator='nin',
                expected_types="<type 'array'>",
                type=type(value)
            ))
        if value:
            q['exclude'][property+'__in'] = value

    def _neq(self, q, property, value, options=None):
        q['exclude'][property] = value

    def _like(self, q, property, value, options=None):
        if options == 'i':
            q['filter'][property+'__icontains'] = value
        else:
            q['filter'][property+'__contains'] = value

    def _nlike(self, q, property, value, options=None):
        if options == 'i':
            q['exclude'][property+'__icontains'] = value
        else:
            q['exclude'][property+'__contains'] = value

    def _ilike(self, q, property, value, options=None):
        q['filter'][property+'__icontains'] = value

    def _nilike(self, q, property, value, options=None):
        q['exclude'][property+'__icontains'] = value



    def lb_query_to_rawq(self, property, data):
        q = {
            'filter':{},
            'exclude':{}
        }

        field_instance, has_m2m, normalized_property = self.get_field_by_path(property)
        if has_m2m:
            self.has_m2m_in_where = True


        if isinstance(data, SIMPLE_TYPES) or data is None:
            if property.startswith('$'):
                return q
            property, data = self.validate_value(property, data)
            q['filter'][property] = data
            return q

        if not isinstance(data, dict):
            raise ParseError(self.error_msgs['invalid_type_for_property'].format(
                property=property,
                expected_types="<type 'str'>, <type 'number'>, <type 'bool'> or <type 'dict'>",
                type=type(data)
            ))


        for operator,value in data.items():
            if operator == 'options' or operator.startswith('$'):
                continue
            operator_func = getattr(self, '_' + operator, None)
            if not operator_func:
                raise ParseError(self.error_msgs['unknown_operator_for_property'].format(
                    property=property,
                    operator=operator
                ))
            value = convert_value_to_python(field_instance, value)
            operator_func(
                q,
                normalized_property,
                value,
                options=data.get('options', None)
            )
        return q



    def to_q(self):
        q = Q()

        if 'or' in self.where:
            if not isinstance(self.where['or'], list):
                raise ParseError(self.error_msgs['invalid_type_for_operator'].format(
                    operator='or',
                    property='where',
                    expected_types="<type 'array'>",
                    type=type(self.where['or'])
                ))

            for k,v in self.where.items():
                if k=='or':
                    orQ = Q()
                    for orWhere in v:
                        orQ |= self.generate_rawq(orWhere)
                    q = q & orQ
                    continue
                djQ = self.lb_query_to_rawq(k, v)
                if djQ['filter']:
                    q &= Q(**djQ['filter'])
                if djQ['exclude']:
                    q &= ~Q(**djQ['exclude'])

        elif 'and' in self.where:
            if not isinstance(self.where['and'], list):
                raise ParseError(self.error_msgs['invalid_type_for_operator'].format(
                    operator='and',
                    property='where',
                    expected_types="<type 'array'>",
                    type=type(self.where['and'])
                ))
            _q = OrderedDict()
            for o in self.where['and']:
                _q.update(o)
            q = self.generate_rawq(_q)

        else:
            q = self.generate_rawq(self.where)

        return q
