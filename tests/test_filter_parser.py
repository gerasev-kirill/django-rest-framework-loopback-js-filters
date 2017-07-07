from django.test import TestCase
from rest_framework import exceptions

from drf_loopback_js_filters import LoopbackJsFilterBackend

from .fake_request import FakeRequest



ERROR_MSGS = LoopbackJsFilterBackend.error_msgs



class ParserTest(TestCase):
    def setUp(self):
        self.backend = LoopbackJsFilterBackend()

    def test_filter(self):
        request = FakeRequest(filter="{'d':")

        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['malformed_json'].format(property='filter'),
            self.backend.filter_queryset,

            request, None, None
        )


    def test_where(self):
        request = FakeRequest(where="{'d':")

        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['malformed_json'].format(property='where'),
            self.backend.filter_queryset,

            request, None, None
        )


    def test_where_and_filter(self):
        request = FakeRequest(filter="{}", where="{}")

        self.assertRaisesMessage(
            exceptions.NotAcceptable,
            ERROR_MSGS['both_filter_and_where'],
            self.backend.filter_queryset,

            request, None, None
        )
