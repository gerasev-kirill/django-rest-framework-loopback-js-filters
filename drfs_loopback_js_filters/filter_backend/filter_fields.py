from rest_framework import exceptions







class ProcessFieldsFilter:
    def __init__(self, request, queryset, _fields):
        if not isinstance(_fields, dict):
            raise exceptions.ParseError("Parameter 'fields' expected to be <type 'json'>, got - " + str(type(_fields)))
        fields = [
            f.name
            for f in queryset.model._meta.get_fields()
        ]
        lb = {'only':[], 'defer':[]}
        for k,v in _fields.items():
            if k in fields:
                if v not in [True, False]:
                    raise exceptions.ParseError("Property '"+k+"' for parameter 'fields' should be <type 'bool'>, got - "+str(type(v)))
                if v:
                    lb['only'].append(k)
                else:
                    lb['defer'].append(k)

        if lb['only'] and lb['defer']:
            raise exceptions.NotAcceptable("For properties in parameter 'fields' you can use true OR false value. Not both at the same time")

        request.LB_FILTER_FIELDS = lb
