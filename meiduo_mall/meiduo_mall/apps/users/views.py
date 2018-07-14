from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User


class CheckUserName(APIView):
    """
    验证用户名是否可以使用
    """
    def get(self,request,username):
        count=User.objects.filter(username=username).count()
        return Response(data={'count':count,'username':username})