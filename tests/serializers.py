from .models import TestModel

from drfs_loopback_js_filters.serializers import LoopbackJsModelSerializer




class TestModelSetializer(LoopbackJsModelSerializer):
    class Meta:
        model = TestModel
        fields = '__all__'
