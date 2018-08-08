from rest_framework import serializers
from serializers import serializer


from .models import Area


class AreasViewSetserializer(serializers.ModelSerializer):
    class Meta:
        model=Area
        fields=['id','name','parent']

class SubAreaSerializer(serializers.ModelSerializer):
    """
        子行政区划信息序列化器
        """
    # TODO 这里是什么原理
    subs = AreasViewSetserializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'name', 'subs')