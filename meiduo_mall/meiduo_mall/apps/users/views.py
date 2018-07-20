import re

from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView, UpdateAPIView, \
    RetrieveUpdateDestroyAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from users.serializers import Userserializers



from meiduo_mall.apps.verification.serializers import ImageCodeCheckSerializer

from users.serializers import SMScode_ckeckserializer

from users.serializers import ResetPasswdserializer
from .models import User
import logging


logger=logging.getLogger()
class CheckUserName(APIView):
    """
    验证用户名是否可以使用
    """

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'count': count,
            'username': username
        }
        return Response(data=data)


class CheckMobile(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'count': count,
            'mobile': mobile,
        }
        return Response(data=data)


class Register(CreateAPIView):
    serializer_class = Userserializers




class FindPasswd(RetrieveModelMixin,GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ImageCodeCheckSerializer
    lookup_field='mobile'
    def get(self,request,mobile):
        """ GET accounts/(?P<account>\w{5,20})/sms/token/"""
        # user=self.get_object()
        # user=None
        # try:
        #     user=User.objects.filter(mobile=mobile)[0]
        # except Exception as e:
        #     logger.error(e)
        # print(user)
        # print('type(user):',type(user))
        # genericAPIView没有自动调用验证需要手动调用

        serializer=self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        if re.match(r'^((13[0-9])|(14[5|7])|(15([0-3]|[5-9]))|(18[0,5-9]))\d{8}$',mobile):
            user=self.get_object()
            if not user:
                return Response(data={'user':None},status=HTTP_400_BAD_REQUEST)

            mobile=user.mobile
            mobile=re.sub(r'(\d{3})(\d{4})(\d{4})',r'\1****\2',mobile)

            token=user.generate_access_token()
            data={
                'mobile':mobile,
                'access_token':token,
            }
            return Response(data)
        user=None
        try:
            user=User.objects.filter(username=mobile)[0]
        except Exception as e:
            logger.error(e)
        print(user)
        if not user:
            return Response(data={'user': None}, status=HTTP_404_NOT_FOUND)

        token = user.generate_access_token()
        mobile=user.mobile
        mobile = re.sub(r'(\d{3})(\d{4})(\d{4})', r'\1****\2', mobile)
        data = {
            'mobile': mobile,
            'access_token': token,
        }
        return Response(data)

class SMScode_ckeckView(GenericAPIView):
    queryset=User.objects.all()
    lookup_field = 'mobile'
    lookup_url_kwarg='account'
    serializer_class = SMScode_ckeckserializer
    def get(self,request,account):
        serializer=self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        if re.match(r'^((13[0-9])|(14[5|7])|(15([0-3]|[5-9]))|(18[0,5-9]))\d{8}$',account):
            user=self.get_object()
            if not user:
                return Response(data={'user':None},status=HTTP_400_BAD_REQUEST)

            mobile=user.mobile
            mobile=re.sub(r'(\d{3})(\d{4})(\d{4})',r'\1****\2',mobile)

            token=user.generate_access_token()
            data={
                'mobile':mobile,
                'access_token':token,
            }
            return Response(data)
        user=None
        try:
            user=User.objects.filter(username=account)[0]
        except Exception as e:
            logger.error(e)
        print(user)
        if not user:
            return Response(data={'user': None}, status=HTTP_404_NOT_FOUND)

        token = user.generate_access_token()
        user_id=user.id
        # mobile=user.mobile
        # mobile = re.sub(r'(\d{3})(\d{4})(\d{4})', r'\1****\2', mobile)
        data = {
            'user_id': user_id,
            'access_token': token,
        }
        return Response(data)
        # return Response(data={'msg':'ok'})

class ResetPasswd(GenericAPIView):
    # users/(?P<pk>\d+)/password/?access_token=xxx
    queryset = User.objects.all()
    serializer_class = ResetPasswdserializer
    def post(self,request,pk):
        user=self.get_object()
        serializer=self.get_serializer(user,data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        data={
            'user_id':user.id,
        }

        return Response(data)






