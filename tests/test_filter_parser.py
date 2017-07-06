from django.test import TestCase
from rest_framework import exceptions

from drfs_loopback_js_filters import LoopbackJsFilterBackend

from .fake_request import FakeRequest







class ParserTest(TestCase):
    def setUp(self):
        self.backend = LoopbackJsFilterBackend()

    def test_filter(self):
        request = FakeRequest(filter="{'d':")

        self.assertRaisesMessage(
            exceptions.ParseError,
            "Malformed json string for query param 'filter'",
            self.backend.filter_queryset,

            request, None, None
        )


    def test_where(self):
        request = FakeRequest(where="{'d':")

        self.assertRaisesMessage(
            exceptions.ParseError,
            "Malformed json string for query param 'where'",
            self.backend.filter_queryset,

            request, None, None
        )


    def test_where_and_filter(self):
        request = FakeRequest(filter="{}", where="{}")

        self.assertRaisesMessage(
            exceptions.NotAcceptable,
            "Provide 'filter' OR 'where' query. Not both at the same time",
            self.backend.filter_queryset,

            request, None, None
        )
