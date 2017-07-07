=====
A loopback.Js-like system for filtering Django Rest Framework QuerySets based on user selections
=====


.. image:: https://travis-ci.org/gerasev-kirill/django-rest-loopback-js-filters.svg?branch=master
    :target: https://travis-ci.org/gerasev-kirill/django-rest-loopback-js-filters


.. image:: https://coveralls.io/repos/github/gerasev-kirill/django-rest-loopback-js-filters/badge.svg?branch=master
    :target: https://coveralls.io/github/gerasev-kirill/django-rest-loopback-js-filters?branch=master

Using django-rest-loopback-js-filters, we can easily do stuff like this:

.. code-block:: javascript

    // js code in browser
    // try to find all users with first name 'Nick' and last login date
    // between 2017-03-10 and 2017-06-01
    var filter = {
        where: {
            first_name: 'Nick',
            last_login:{
                between: ['2017-03-10', '2017-06-01']
            }
        }
    };
    var url = "/api/v1/Users/?filter=" + encodeURIComponent(JSON.stringify(filter));
    // output:
    //
    // /api/v1/Users/?filter=%7B%22where%22%3A%7B%22first_name%22%3A%22Nick%22%2C%22last_login%22%3A%7B%22between%22%3A%5B%222017-03-10%22%2C%222017-06-01%22%5D%7D%7D%7D
    //
    // now you can query server for result with this url.

    // try to find all users with first name 'Nick' OR 'Jane', and order them by
    // 'last_login' field. then we will skip 5 first results and limit queryset
    // to 10 objects
    filter = {
        where:{
            or: [
                {first_name: 'Nick'},
                {first_name: 'Jane'}
            ]
        },
        order: 'last_login DESC',
        skip: 5,
        limit: 10
    };
    url = "/api/v1/Users/?filter=" + encodeURIComponent(JSON.stringify(filter))

    // or we can even specify properties (fields) to include or exclude from the results
    // NOTE: you should use LoopbackJsSerializerMixin from drf_loopback_js_filters.serializers
    // for this functionality in your model serializer!
    // a. return only 3 fields:
    filter = {
        order: 'last_login DESC',
        limit: 30,
        fields: {
            id: true,
            last_login: true,
            username: true
        }
    }
    url = "/api/v1/Users/?filter=" + encodeURIComponent(JSON.stringify(filter))

    // b. hide 2 fields from data:
    filter = {
        order: 'last_login DESC',
        limit: 30,
        fields: {
            last_login: false,
            username: false
        }
    }
    url = "/api/v1/Users/?filter=" + encodeURIComponent(JSON.stringify(filter))


Requirements
------------

* **Python**: 2.7 or 3.4+
* **Django**: >= 1.11
* **DRF**: >= 3.6


Installation
-----------

.. code-block:: bash

    pip install git+https://github.com/gerasev-kirill/django-rest-loopback-js-filters.git


Quick start
-----------

1. Add "drf_loopback_js_filters" to your INSTALLED_APPS in settings.py like this:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'drf_loopback_js_filters',
        ...
    )

2. To use the django-rest-loopback-js-filters backend, add the following to your settings.py:

.. code-block:: python

    REST_FRAMEWORK = {
        ...
        'DEFAULT_FILTER_BACKENDS': (
            'drf_loopback_js_filters.LoopbackJsFilterBackend',
        ),
        ...
    }
