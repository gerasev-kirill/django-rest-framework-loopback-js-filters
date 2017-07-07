from django.test import TestCase
from rest_framework import exceptions

from drf_loopback_js_filters.filter_backend.filter_order import ProcessOrderFilter

from .fake_request import FakeRequest
ERROR_MSGS = ProcessOrderFilter.error_msgs






class OrderTest(TestCase):
    fixtures = ['TestModel.json']

    def setUp(self):
        from .models import TestModel
        self.queryset = TestModel.objects.all()

    def test_no_filter(self):
        orig_pks = [o.pk   for o in self.queryset]

        pfilter = ProcessOrderFilter(self.queryset, None)
        ordered_pks = [o.pk  for o in pfilter.filter_queryset()]

        self.assertEqual(ordered_pks, orig_pks)


    def test_invalid_order_filter(self):
        queryset = self.queryset

        pfilter = ProcessOrderFilter(queryset, 1)
        self.assertRaisesMessage(
            exceptions.NotAcceptable,
            ERROR_MSGS['invalid_type'].format(
                property='order',
                expected_types="<type 'str'>",
                type=type(1)
            ),
            pfilter.filter_queryset
        )

        pfilter = ProcessOrderFilter(queryset, "INVALID")
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['malformed_order'],
            pfilter.filter_queryset
        )

        pfilter = ProcessOrderFilter(queryset, "invalid_field ASC")
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['invalid_field_name'].format(
                field_name='invalid_field',
                model_name='TestModel'
            ),
            pfilter.filter_queryset
        )


    def test_order_success(self):
        orig_pks = [o.pk   for o in self.queryset]

        ###
        #       ASC
        ###
        pfilter = ProcessOrderFilter(self.queryset, "int_field ASC")
        filtered_queryset = pfilter.filter_queryset()

        dj_pks = [o.pk for o in self.queryset.order_by('int_field')]
        ordered_pks = [o.pk  for o in filtered_queryset]

        self.assertEqual(ordered_pks, dj_pks)
        self.assertNotEqual(ordered_pks, orig_pks)

        ##
        #      DESC
        ##
        pfilter = ProcessOrderFilter(self.queryset, "int_field DESC")
        filtered_queryset = pfilter.filter_queryset()

        dj_pks = [o.pk for o in self.queryset.order_by('-int_field')]
        ordered_pks = [o.pk  for o in filtered_queryset]

        self.assertEqual(ordered_pks, dj_pks)
        self.assertNotEqual(ordered_pks, orig_pks)
