from django.shortcuts import render

# Create your views here.

from rest_framework.viewsets import ViewSet, ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .models import Area
from .serializers import AreasViewSetserializer, SubAreaSerializer





class AreasView(CacheResponseMixin,ReadOnlyModelViewSet):
    """
    返回收货地址信息
    """
    # /areas/P?<pk>\w+/

    # queryset = Area.objects.all()
    # 不分页
    pagination_class = None
    def get_queryset(self):
        if self.action=='list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()
    #
    # serializer_class = AreasViewSetserializer
    def get_serializer_class(self):
        if self.action == 'list':
            return AreasViewSetserializer
        else:
            return SubAreaSerializer

