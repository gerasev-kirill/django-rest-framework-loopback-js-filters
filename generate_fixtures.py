
import random, json



strings = "Django provides a small set of tools that come in handy when writing tests"
int_fields = [-20,1, 10, 20, -10, 100, 200, -300, 33, 55]
float_fields = [10.3, 20.2, 20.4, 30.5, 30.77, -10.3, -20.3, -10.4, -10.5]
date_fields = ['2000-10-10', '2017-02-14', '2009-03-03', '2017-06-07', '2017-06-08', '2017-05-20']


FIXTURES = []

for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]:
    obj = {
        'model': 'tests.TestModel',
        'pk': i,
        'fields': {
            'string_field': random.choice(strings.split(' ')) + " " + random.choice(strings.split(' ')),
            'int_field': random.choice(int_fields),
            'float_field': random.choice(float_fields),
            'date_field': random.choice(date_fields)
        }
    }
    if i%3 == 0 :
        obj['fields']['string_field'] += " " + random.choice(strings.split(' '))

    FIXTURES.append(obj)


print json.dumps(FIXTURES, indent=4)
