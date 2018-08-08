from django.shortcuts import render

# Create your views here.
from drf_haystack.viewsets import HaystackViewSet

from .serializers import SKUIndexSerializer
from .models import SKU


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer