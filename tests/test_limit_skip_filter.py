from django.test import TestCase
from rest_framework import exceptions

from drfs_loopback_js_filters.filter_backend.filter_limit_skip import ProcessLimitSkipFilter

from .fake_request import FakeRequest



ERROR_MSGS = ProcessLimitSkipFilter.error_msgs



class LimitSkipTest(TestCase):
    fixtures = ['TestModel.json']

    def setUp(self):
        from .models import TestModel
        self.queryset = TestModel.objects.all()

    def test_no_filter(self):
        orig_pks = [o.pk   for o in self.queryset]

        pfilter = ProcessLimitSkipFilter(self.queryset, {})
        limited_pks = [o.pk  for o in pfilter.filter_queryset()]

        self.assertEqual(orig_pks, limited_pks)


    def test_invalid_filters(self):
        pfilter = ProcessLimitSkipFilter(self.queryset, {'skip': 1.1})
        self.assertRaisesMessage(
            exceptions.NotAcceptable,
            ERROR_MSGS['invalid_type'].format(
                property='skip',
                type=type(1.1)
            ),
            pfilter.filter_queryset
        )
        pfilter = ProcessLimitSkipFilter(self.queryset, {'skip': -1})
        self.assertRaisesMessage(
            exceptions.NotAcceptable,
            ERROR_MSGS['less_than_zero'].format(property='skip'),
            pfilter.filter_queryset
        )

        pfilter = ProcessLimitSkipFilter(self.queryset, {'limit': 1.1})
        self.assertRaisesMessage(
            exceptions.NotAcceptable,
            ERROR_MSGS['invalid_type'].format(
                property='limit',
                type=type(1.1)
            ),
            pfilter.filter_queryset
        )
        pfilter = ProcessLimitSkipFilter(self.queryset, {'limit': -1})
        self.assertRaisesMessage(
            exceptions.NotAcceptable,
            ERROR_MSGS['less_than_zero'].format(property='limit'),
            pfilter.filter_queryset
        )
        pfilter = ProcessLimitSkipFilter(self.queryset, {'limit': 0})
        self.assertRaisesMessage(
            exceptions.NotAcceptable,
            ERROR_MSGS['limit_is_zero'],
            pfilter.filter_queryset
        )


    def test_success(self):
        total_count = self.queryset.count()

        skip = 5
        limit = 20
        pfilter = ProcessLimitSkipFilter(self.queryset, {'skip': skip, 'limit': limit})
        self.assertEqual(
            pfilter.filter_queryset().count(),
            20
        )

        skip = total_count - 5
        limit = 20
        pfilter = ProcessLimitSkipFilter(self.queryset, {'skip': skip, 'limit': limit})
        self.assertEqual(
            pfilter.filter_queryset().count(),
            5
        )

        pfilter = ProcessLimitSkipFilter(self.queryset, {'skip': 20})
        self.assertEqual(
            pfilter.filter_queryset().count(),
            total_count - 20
        )

        pfilter = ProcessLimitSkipFilter(self.queryset, {'limit': 20})
        self.assertEqual(
            pfilter.filter_queryset().count(),
            20
        )
