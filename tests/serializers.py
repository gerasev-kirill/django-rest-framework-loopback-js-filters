from .models import TestModel

from drf_loopback_js_filters.serializers import LoopbackJsModelSerializer




class TestModelSetializer(LoopbackJsModelSerializer):
    class Meta:
        model = TestModel
        fields = ['id', 'string_field', 'int_field', 'float_field', 'date_field', 'datetime_field', 'foreign_field']


class TestModelAllSetializer(LoopbackJsModelSerializer):
    class Meta:
        model = TestModel
        fields = '__all__'
