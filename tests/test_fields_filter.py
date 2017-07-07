from django.test import TestCase
from rest_framework import exceptions
from rest_framework.test import APIRequestFactory
from rest_framework import viewsets
import json

from .models import TestModel
from .serializers import TestModelSetializer

from drf_loopback_js_filters.filter_backend.filter_fields import ProcessFieldsFilter
from drf_loopback_js_filters import LoopbackJsFilterBackend



class TestModelViewSet(viewsets.ModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestModelSetializer
    filter_backends = (LoopbackJsFilterBackend,)



ERROR_MSGS = ProcessFieldsFilter.error_msgs



class FieldsTest(TestCase):
    fixtures = ['TestModel.json']

    def setUp(self):
        from .models import TestModel
        self.queryset = TestModel.objects.all()
        self.factory = APIRequestFactory()
        self.list_view = TestModelViewSet.as_view({'get': 'list'})

    def test_no_filter(self):
        response = self.list_view(self.factory.get(
            '',
            {}
        ))
        orig_data = [
            {
                'id':o.pk, 'int_field':o.int_field, 'string_field': o.string_field,
                'date_field': str(o.date_field), 'datetime_field': None,
                'foreign_field': None, 'float_field': o.float_field
            }
            for o in self.queryset
        ]
        self.assertEqual(
            response.data,
            orig_data
        )

    def test_invalid_filter(self):
        filter = {
            'fields':1
        }
        request = self.factory.get('', {'filter': json.dumps(filter)})

        pfilter = ProcessFieldsFilter(request, self.queryset, filter)
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['invalid_type'].format(
                property='fields',
                expected_types="<type 'dict'>",
                type=type(1)
            ),
            pfilter.filter_queryset,
        )

        filter = {
            'fields':{'id':1}
        }
        request = self.factory.get('', {'filter': json.dumps(filter)})

        pfilter = ProcessFieldsFilter(request, self.queryset, filter)
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['invalid_type_for_property'].format(
                property='id',
                expected_types="<type 'bool'>",
                type=type(1)
            ),
            pfilter.filter_queryset,
        )

        filter = {
            'fields':{'id':True, 'string_field': False}
        }
        request = self.factory.get('', {'filter': json.dumps(filter)})

        pfilter = ProcessFieldsFilter(request, self.queryset, filter)
        self.assertRaisesMessage(
            exceptions.NotAcceptable,
            ERROR_MSGS['both_true_and_false'],
            pfilter.filter_queryset,
        )



    def test_fields_success(self):
        ##
        #       visible fields
        ##
        filter = {
            'fields':{
                'id': True,
                'int_field': True
            }
        }

        response = self.list_view(self.factory.get(
            '',
            {'filter': json.dumps(filter)}
        ))
        orig_data = [
            {'id':o.pk, 'int_field':o.int_field}
            for o in self.queryset
        ]
        self.assertEqual(
            response.data,
            orig_data
        )


        ##
        #       hidden fields
        ##
        filter = {
            'fields':{
                'id': False,
                'int_field': False,
                'datetime_field': False,
                'foreign_field': False
            }
        }
        response = self.list_view(self.factory.get(
            '',
            {'filter': json.dumps(filter)}
        ))
        orig_data = [
            {'string_field':o.string_field, 'float_field':o.float_field, 'date_field':str(o.date_field)}
            for o in self.queryset
        ]

        self.assertEqual(
            response.data,
            orig_data
        )
