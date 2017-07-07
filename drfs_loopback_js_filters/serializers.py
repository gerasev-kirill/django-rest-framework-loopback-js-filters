from rest_framework import serializers



class LoopbackJsSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        super(LoopbackJsSerializerMixin, self).__init__(*args, **kwargs)
        context = kwargs.get('context', {})
        request = context.get('request', {})
        lb_fields = getattr(request, 'LB_FILTER_FIELDS', None)

        if lb_fields:
            if not isinstance(lb_fields, dict):
                raise TypeError("LB_FILTER_FIELDS in request context should be 'dict'. Got '"+str(type(lb_fields))+"'")

            existing_fields = self.fields.keys()

            if lb_fields.get('visible', None):
                for name in existing_fields:
                    if name not in lb_fields['visible']:
                        self.fields.pop(name)

            elif lb_fields.get('hidden', None):
                for name in lb_fields['hidden']:
                    if name in existing_fields:
                        self.fields.pop(name)


class LoopbackJsModelSerializer(LoopbackJsSerializerMixin, serializers.ModelSerializer):
    pass
