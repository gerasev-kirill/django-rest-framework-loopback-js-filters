from django.test import TestCase
from rest_framework import exceptions
from django.contrib.auth.models import User as UserModel
from django.db.models import Q

from drf_loopback_js_filters.filter_backend.filter_where import ProcessWhereFilter
from drf_loopback_js_filters.helpers import LbWhereQueryConverter

from .fake_request import FakeRequest
ERROR_MSGS = LbWhereQueryConverter.error_msgs






class InvalidWhereTest(TestCase):
    fixtures = ['TestModel.json']

    def setUp(self):
        from .models import TestModel
        self.queryset = TestModel.objects.all()

    def test_no_filter(self):
        orig_pks = [o.pk   for o in self.queryset]

        pfilter = ProcessWhereFilter(self.queryset, {})
        ordered_pks = [o.pk  for o in pfilter.filter_queryset()]

        self.assertEqual(ordered_pks, orig_pks)

    def test_invalid_where_filter(self):
        queryset = self.queryset

        pfilter = ProcessWhereFilter(queryset, None)
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['invalid_type'].format(
                property='where',
                type=type(None)
            ),
            pfilter.filter_queryset
        )

        pfilter = ProcessWhereFilter(queryset, {'invalid_field': True})
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['field_doesnt_exist'].format(
                property='invalid_field',
                model_name='TestModel'
            ),
            pfilter.filter_queryset
        )

        pfilter = ProcessWhereFilter(queryset, {
            'or': [
                {'invalid_field': True},
                {'invalid_field2': False}
            ]
        })
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['field_doesnt_exist'].format(
                property='invalid_field',
                model_name='TestModel'
            ),
            pfilter.filter_queryset
        )

        pfilter = ProcessWhereFilter(queryset, {
            'and': [
                {'invalid_field3': True},
                {'invalid_field4': False}
            ]
        })
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['field_doesnt_exist'].format(
                property='invalid_field3',
                model_name='TestModel'
            ),
            pfilter.filter_queryset
        )





class WhereTest(TestCase):
    fixtures = ['TestModel.json']

    def setUp(self):
        from .models import TestModel
        self.queryset = TestModel.objects.all()

    def test_or_complex(self):
        where = {
            'int_field': 1,
            'or': [
                {'date_field': '2017-06-08'},
                {'date_field': '2009-03-03'}
            ]
        }

        pfilter = ProcessWhereFilter(self.queryset, where)
        filtered_queryset = pfilter.filter_queryset()

        djfiltered_queryset = self.queryset.filter(int_field=1).filter(
            Q(date_field='2017-06-08') | Q(date_field='2009-03-03')
        )
        self.assertEqual(
            [o.pk for o in filtered_queryset],
            [o.pk for o in djfiltered_queryset]
        )
        self.assertNotEqual(
            [o.pk for o in filtered_queryset],
            [o.pk for o in self.queryset]
        )


    def test_eq_neq(self):
        QUERY = {
            'int_field': 1,
            'float_field': 30.77,
            'date_field': '2017-06-07',
            'string_field': 'tools tools'
        }
        for field_name in QUERY.keys():
            where = {}
            where[field_name] = QUERY[field_name]

            pfilter = ProcessWhereFilter(self.queryset, where)
            filtered_queryset = pfilter.filter_queryset()

            kwargs = {}
            kwargs[field_name] = QUERY[field_name]
            djfiltered_queryset = self.queryset.filter(**kwargs)
            self.assertEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in djfiltered_queryset]
            )
            self.assertNotEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in self.queryset]
            )

        for field_name in QUERY.keys():
            where = {}
            where[field_name] = {
                'neq': QUERY[field_name]
            }

            pfilter = ProcessWhereFilter(self.queryset, where)
            filtered_queryset = pfilter.filter_queryset()

            kwargs = {}
            kwargs[field_name] = QUERY[field_name]
            djfiltered_queryset = self.queryset.exclude(**kwargs)
            self.assertEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in djfiltered_queryset]
            )
            self.assertNotEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in self.queryset]
            )


    def test_gt_lt_gte_lte(self):
        QUERY = {
            'int_field': 20,
            'float_field': 30.3,
            'date_field': '2009-03-03'
        }
        for suffix in ['gt', 'lt', 'gte', 'lte']:
            for field_name in QUERY.keys():
                where = {}
                where[field_name] = {}
                where[field_name][suffix] = QUERY[field_name]

                pfilter = ProcessWhereFilter(self.queryset, where)
                filtered_queryset = pfilter.filter_queryset()

                kwargs = {}
                kwargs[field_name+"__"+suffix] = QUERY[field_name]
                djfiltered_queryset = self.queryset.filter(**kwargs)

                self.assertEqual(
                    [o.pk for o in filtered_queryset],
                    [o.pk for o in djfiltered_queryset]
                )
                self.assertNotEqual(
                    [o.pk for o in filtered_queryset],
                    [o.pk for o in self.queryset]
                )


    def test_between_fail(self):
        pfilter = ProcessWhereFilter(self.queryset, {
            'int_field': {
                'between': 1
            }
        })
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['invalid_type_for_property_with_operator'].format(
                property='int_field',
                operator='between',
                expected_types="<type 'array'>",
                type=type(1)
            ),
            pfilter.filter_queryset
        )

        pfilter = ProcessWhereFilter(self.queryset, {
            'int_field': {
                'between': [1]
            }
        })
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['invalid_type_for_property_with_operator'].format(
                property='int_field',
                operator='between',
                expected_types="<type 'array'> with 2 elements",
                type='1 elements'
            ),
            pfilter.filter_queryset
        )

        pfilter = ProcessWhereFilter(self.queryset, {
            'int_field': {
                'between': [1,2,3]
            }
        })
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['invalid_type_for_property_with_operator'].format(
                property='int_field',
                operator='between',
                expected_types="<type 'array'> with 2 elements",
                type='3 elements'
            ),
            pfilter.filter_queryset
        )


    def test_between(self):
        QUERY = {
            'int_field': [10, 40],
            'float_field': [-3,30.3],
            'date_field': ['2009-03-03', '2017-06-08']
        }
        for field_name in QUERY.keys():
            where = {}
            where[field_name] = {
                'between': QUERY[field_name]
            }

            pfilter = ProcessWhereFilter(self.queryset, where)
            filtered_queryset = pfilter.filter_queryset()

            kwargs = {}
            kwargs[field_name+"__gte"] = QUERY[field_name][0]
            kwargs[field_name+"__lte"] = QUERY[field_name][1]
            djfiltered_queryset = self.queryset.filter(**kwargs)

            self.assertEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in djfiltered_queryset]
            )
            self.assertNotEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in self.queryset]
            )



    def test_inq_nin_fail(self):
        pfilter = ProcessWhereFilter(self.queryset, {
            'int_field': {
                'inq': 1
            }
        })
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['invalid_type_for_property_with_operator'].format(
                property='int_field',
                operator='inq',
                expected_types="<type 'array'>",
                type=type(1)
            ),
            pfilter.filter_queryset
        )

        pfilter = ProcessWhereFilter(self.queryset, {
            'int_field': {
                'nin': 1
            }
        })
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['invalid_type_for_property_with_operator'].format(
                property='int_field',
                operator='nin',
                expected_types="<type 'array'>",
                type=type(1)
            ),
            pfilter.filter_queryset
        )


    def test_inq_nin(self):
        QUERY = {
            'int_field': [20, -10, 100],
            'float_field': [20.2, 20.4, 30.5],
            'date_field': ['2017-02-14', '2009-03-03', '2017-06-07'],
            'string_field': ['tools tools', 'of that Django']
        }

        for field_name in QUERY.keys():
            where = {}
            where[field_name] = {
                'inq': QUERY[field_name]
            }

            pfilter = ProcessWhereFilter(self.queryset, where)
            filtered_queryset = pfilter.filter_queryset()

            kwargs = {}
            kwargs[field_name+"__in"] = QUERY[field_name]
            djfiltered_queryset = self.queryset.filter(**kwargs)

            self.assertEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in djfiltered_queryset]
            )
            self.assertNotEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in self.queryset]
            )

        for field_name in QUERY.keys():
            where = {}
            where[field_name] = {
                'nin': QUERY[field_name]
            }

            pfilter = ProcessWhereFilter(self.queryset, where)
            filtered_queryset = pfilter.filter_queryset()

            kwargs = {}
            kwargs[field_name+"__in"] = QUERY[field_name]
            djfiltered_queryset = self.queryset.exclude(**kwargs)

            self.assertEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in djfiltered_queryset]
            )
            self.assertNotEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in self.queryset]
            )


    def test_ilike_nilike(self):
        # https://docs.djangoproject.com/en/1.11/ref/models/querysets/#contains
        # SQLite doesn`t support case-sensitive LIKE statements; contains acts like icontains for SQLite. See the database note for more information
        QUERY = {
            'string_field': 'Django'
        }

        for field_name in QUERY.keys():
            where = {}
            where[field_name] = {
                'ilike': QUERY[field_name]
            }

            pfilter = ProcessWhereFilter(self.queryset, where)
            filtered_queryset = pfilter.filter_queryset()

            kwargs = {}
            kwargs[field_name+"__icontains"] = QUERY[field_name]
            djfiltered_queryset = self.queryset.filter(**kwargs)

            self.assertEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in djfiltered_queryset]
            )
            self.assertNotEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in self.queryset]
            )


        for field_name in QUERY.keys():
            where = {}
            where[field_name] = {
                'nilike': QUERY[field_name]
            }

            pfilter = ProcessWhereFilter(self.queryset, where)
            filtered_queryset = pfilter.filter_queryset()

            kwargs = {}
            kwargs[field_name+"__icontains"] = QUERY[field_name]
            djfiltered_queryset = self.queryset.exclude(**kwargs)

            self.assertEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in djfiltered_queryset]
            )
            self.assertNotEqual(
                [o.pk for o in filtered_queryset],
                [o.pk for o in self.queryset]
            )





class RelationsWhereTest(TestCase):
    fixtures = ['TestModel.json']

    def setUp(self):
        from .models import TestModel
        self.queryset = TestModel.objects.all()
        self.user1 = UserModel.objects.create(username='user1')
        self.user2 = UserModel.objects.create(username='user2')
        self.user3 = UserModel.objects.create(username='test3')

        obj = self.queryset[3]
        obj.foreign_field = self.user1
        obj.save()
        obj = self.queryset[9]
        obj.foreign_field = self.user2
        obj.save()
        obj = self.queryset[15]
        obj.foreign_field = self.user3
        obj.save()


    def test_invalid(self):
        pfilter = ProcessWhereFilter(self.queryset, {
            'foreign_field.invalid_field': 'some_val'
        })
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['field_doesnt_exist'].format(
                property='foreign_field.invalid_field',
                model_name='TestModel'
            ),
            pfilter.filter_queryset
        )

        pfilter = ProcessWhereFilter(self.queryset, {
            'foreign_field__invalid_field': 'some_val'
        })
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['field_doesnt_exist'].format(
                property='foreign_field__invalid_field',
                model_name='TestModel'
            ),
            pfilter.filter_queryset
        )

        pfilter = ProcessWhereFilter(self.queryset, {
            'foreign_field.no_such_field': 'some_val for invalid property path'
        })
        self.assertRaisesMessage(
            exceptions.ParseError,
            ERROR_MSGS['field_doesnt_exist'].format(
                property='foreign_field.no_such_field',
                model_name='TestModel',
            ),
            pfilter.filter_queryset
        )

        pfilter = ProcessWhereFilter(self.queryset, {
            'foreign_field': 'invalid value for id field'
        })
        self.assertRaisesMessage(
            exceptions.ParseError,
            "'invalid value for id field' value must be an integer.",
            pfilter.filter_queryset
        )

    def test_filter_by_pk(self):
        pfilter = ProcessWhereFilter(self.queryset, {
            'foreign_field': self.user1.pk
        })

        filtered_queryset = pfilter.filter_queryset()
        djfiltered_queryset = self.queryset.filter(foreign_field=self.user1)

        self.assertEqual(
            [o.pk for o in filtered_queryset],
            [o.pk for o in djfiltered_queryset]
        )
        self.assertEqual(
            filtered_queryset.count(),
            1
        )
        self.assertNotEqual(
            [o.pk for o in filtered_queryset],
            [o.pk for o in self.queryset]
        )

    def test_eq_neq_valid(self):
        ##
        #  eq
        ##
        pfilter = ProcessWhereFilter(self.queryset, {
            'foreign_field.username': 'user1'
        })

        filtered_queryset = pfilter.filter_queryset()
        djfiltered_queryset = self.queryset.filter(foreign_field__username='user1')


        self.assertEqual(
            [o.pk for o in filtered_queryset],
            [o.pk for o in djfiltered_queryset]
        )
        self.assertEqual(
            filtered_queryset.count(),
            1
        )
        self.assertNotEqual(
            [o.pk for o in filtered_queryset],
            [o.pk for o in self.queryset]
        )

        ##
        #  neq
        ##
        pfilter = ProcessWhereFilter(self.queryset, {
            'foreign_field.username': {
                'neq': 'user1'
            }
        })

        filtered_queryset = pfilter.filter_queryset()
        djfiltered_queryset = self.queryset.exclude(foreign_field__username='user1')


        self.assertEqual(
            [o.pk for o in filtered_queryset],
            [o.pk for o in djfiltered_queryset]
        )
        self.assertEqual(
            filtered_queryset.count(),
            djfiltered_queryset.count()
        )
        self.assertNotEqual(
            [o.pk for o in filtered_queryset],
            [o.pk for o in self.queryset]
        )


    def test_like_nlike(self):
        ##
        #  like
        ##
        pfilter = ProcessWhereFilter(self.queryset, {
            'foreign_field.username': {
                'ilike': 'user'
            }
        })

        filtered_queryset = pfilter.filter_queryset()
        djfiltered_queryset = self.queryset.filter(foreign_field__username__icontains='user')


        self.assertEqual(
            [o.pk for o in filtered_queryset],
            [o.pk for o in djfiltered_queryset]
        )
        self.assertEqual(
            filtered_queryset.count(),
            2
        )
        self.assertNotEqual(
            [o.pk for o in filtered_queryset],
            [o.pk for o in self.queryset]
        )

        ##
        #  nlike
        ##
        pfilter = ProcessWhereFilter(self.queryset, {
            'foreign_field.username': {
                'nilike': 'user'
            }
        })

        filtered_queryset = pfilter.filter_queryset()
        djfiltered_queryset = self.queryset.exclude(foreign_field__username__icontains='user')


        self.assertEqual(
            [o.pk for o in filtered_queryset],
            [o.pk for o in djfiltered_queryset]
        )
        self.assertEqual(
            filtered_queryset.count(),
            djfiltered_queryset.count()
        )
        self.assertNotEqual(
            [o.pk for o in filtered_queryset],
            [o.pk for o in self.queryset]
        )
