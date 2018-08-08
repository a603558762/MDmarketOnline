import re

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.filters import OrderingFilter

from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from users import serializers

from goods.serializers import SKUSerializer

from goods.models import SKU
from meiduo_mall.utils import contains
from .serializers import Userserializers, VerifyEmailserializer, AddUserBrowsingHistorySerializer

from verification.serializers import ImageCodeCheckSerializer

from .serializers import SMScode_ckeckserializer

from .serializers import ResetPasswdserializer

from .serializers import UserDetailSerializer

from .serializers import EmailSerializer
from .models import User
import logging

logger = logging.getLogger()


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


class FindPasswd(RetrieveModelMixin, GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ImageCodeCheckSerializer
    lookup_field = 'mobile'

    def get(self, request, mobile):
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

        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        if re.match(r'^((13[0-9])|(14[5|7])|(15([0-3]|[5-9]))|(18[0,5-9]))\d{8}$', mobile):
            user = self.get_object()
            if not user:
                return Response(data={'user': None}, status=HTTP_400_BAD_REQUEST)

            mobile = user.mobile
            mobile = re.sub(r'(\d{3})(\d{4})(\d{4})', r'\1****\2', mobile)

            token = user.generate_access_token()
            data = {
                'mobile': mobile,
                'access_token': token,
            }
            return Response(data)
        user = None
        try:
            user = User.objects.filter(username=mobile)[0]
        except Exception as e:
            logger.error(e)
        print(user)
        if not user:
            return Response(data={'user': None}, status=HTTP_404_NOT_FOUND)

        token = user.generate_access_token()
        mobile = user.mobile
        mobile = re.sub(r'(\d{3})(\d{4})(\d{4})', r'\1****\2', mobile)
        data = {
            'mobile': mobile,
            'access_token': token,
        }
        return Response(data)


class SMScode_ckeckView(GenericAPIView):
    queryset = User.objects.all()
    lookup_field = 'mobile'
    lookup_url_kwarg = 'account'
    serializer_class = SMScode_ckeckserializer

    def get(self, request, account):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        if re.match(r'^((13[0-9])|(14[5|7])|(15([0-3]|[5-9]))|(18[0,5-9]))\d{8}$', account):
            user = self.get_object()
            if not user:
                return Response(data={'user': None}, status=HTTP_400_BAD_REQUEST)

            mobile = user.mobile
            mobile = re.sub(r'(\d{3})(\d{4})(\d{4})', r'\1****\2', mobile)

            token = user.generate_access_token()
            data = {
                'mobile': mobile,
                'access_token': token,
            }
            return Response(data)
        user = None
        try:
            user = User.objects.filter(username=account)[0]
        except Exception as e:
            logger.error(e)
        print(user)
        if not user:
            return Response(data={'user': None}, status=HTTP_404_NOT_FOUND)

        token = user.generate_access_token()
        user_id = user.id
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

    def post(self, request, pk):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        data = {
            'user_id': user.id,
        }

        return Response(data)


class UserDetailView(RetrieveAPIView):
    # queryset = User.objects.all()
    # RetrieveAPIView使用query_set就要指定路由中的pk,然后会用get_object()获得对象,
    # 但实际User对象是从request中获得的
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    # 序列化器验证email
    serializer_class = EmailSerializer
    # 认证
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    # def get_serializer(self, *args, **kwargs):
    #     return EmailSerializer(self.request.user, data=self.request.data)
    # 发送邮箱验证短信


class VerifyEmailView(UpdateAPIView):
    """验证邮箱"""
    serializer_class = VerifyEmailserializer

    # GET /emails/verification/
    def get_object(self):
        token = self.request.data.get('token')
        user_id = User.check_verify_email_url(token)
        if not user_id:
            raise AuthenticationFailed('验证token有误')
        try:
            user = User.objects.get(id=user_id)
        except Exception as e:
            logger.error(e)
            raise AuthenticationFailed('验证token有误')
        if not user:
            raise AuthenticationFailed('验证token有误')

        return user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({'message': 'OK'})
    # def put(self):
    #     serializer = self.get_serializer(data=request.query_params)
    #     serializer.is_valid()
    #     serializer.save()
    #     return Response({'msg':'ok'})

    # def put(self,request):
    #     serializer=self.get_serializer(data=request.query_params)
    #     serializer.is_valid()
    #     serializer.save()
    #     return Response({'msg':'ok'})


class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = serializers.UserAddressSerializer
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            "user_id": user.id,
            # user.default_adress是一个对象,对象不能返回,json解析会出错
            "default_address_id": user.default_adress_id,
            "limit": contains.USER_ADDRESS_COUNTS_LIMIT,
            "addresses": serializer.data,
        })

    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        # 检查用户地址数据数目不能超过上限
        count = request.user.addresses.count()
        if count >= contains.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None, address_id=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_adress = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None, address_id=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserBrowsingHistoryView(mixins.CreateModelMixin, GenericAPIView):
    """
    用户浏览历史记录
    """
    serializer_class = AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        保存
        """
        return self.create(request)

    def get(self, request):
        """
        获取
        """
        user_id = request.user.id

        redis_conn = get_redis_connection("history")
        history = redis_conn.lrange("history_%s" % user_id, 0, contains.USER_BROWSING_HISTORY_COUNTS_LIMIT - 1)
        skus = []
        # 为了保持查询出的顺序与用户的浏览历史保存顺序一致
        for sku_id in history:
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)

        s = SKUSerializer(skus, many=True)
        return Response(s.data)


class SKUListView(ListAPIView):

    # /categories/(?P<category_id>\d+)/skus/
    # queryset = SKU.objects.all()
    serializer_class = SKUSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)



