from django.test import TestCase
from rest_framework import exceptions

from drfs_loopback_js_filters.filter_backend.filter_order import ProcessOrderFilter

from .fake_request import FakeRequest







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
            "Parameter for 'order' filter should be <type 'str'>, got - <type 'int'>",
            pfilter.filter_queryset
        )

        pfilter = ProcessOrderFilter(queryset, "INVALID")
        self.assertRaisesMessage(
            exceptions.ParseError,
            "Malformed parameter for 'order' filter. See https://loopback.io/doc/en/lb2/Order-filter.html",
            pfilter.filter_queryset
        )

        pfilter = ProcessOrderFilter(queryset, "invalid_field ASC")
        self.assertRaisesMessage(
            exceptions.ParseError,
            "Field 'invalid_field' for model 'TestModel' does't exists. You can't use order filter",
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
