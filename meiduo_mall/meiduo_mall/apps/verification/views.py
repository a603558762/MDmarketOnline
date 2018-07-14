import random

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_mall.libs.yuntongxun.sms import CCP
from meiduo_mall.utils import contains
from meiduo_mall.utils.captcha import captcha

from meiduo_mall.apps.verification.serializers import ImageCodeCheckSerializer


class Image_code_generate(APIView):
    """
    get方式生成验证码图形
    """

    def get(self, request, uuid):
        # image_code_id实际是uuid,依据uuid生成对应的验证码图形
        name, text, image = captcha.captcha.generate_captcha()
        # 将生成的验证码对应的text保存到redis中,image_uuid的保存方式
        redis_conn = get_redis_connection('image_code_store_redis')
        redis_conn.setex(name="image_{}".format(uuid), time=contains.MAX_IMAGE_CODE_LIVE_TIME, value=text)
        # return Response(data=image,content_type='image/jpg')
        # content=b'', *args, **kwargs 源码content是byte类型
        return HttpResponse(content=image, content_type='image/jpg')

    """ /smscode/mobile/?text=&uuid=  """


class SMScodeView(GenericAPIView):
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, mobile):
        # 验证的这部分工作是序列化器完成的,视图部分完成的是:生成短信验证码
        # 60秒内是否发过短信 > 在反序列化中完成

        # /?id=xxx&name=xxxx  >  request.query_params
        # serializer = self.get_serializer(data=request.query_params)
        # print('request.query_params:',request.query_params)
        # serializer.is_valid(raise_exception=True)

        serializer = self.get_serializer(data=request.query_params)
        # print('request.query_params:',request.query_params)
        # 教研参数的工作在序列化器中
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)
        # print('验证码是:',sms_code)
        # 保存短信验证码与发送记录
        redis_conn = get_redis_connection('image_code_store_redis')
        # pl = redis_conn.pipeline()
        # pl.multi()
        redis_conn.setex("sms_%s" % mobile, contains.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 设置一个短信已发状态
        redis_conn.setex("send_flag_%s" % mobile, contains.SEND_SMS_CODE_INTERVAL, 1)

        sms_code_expires = contains.SMS_CODE_REDIS_EXPIRES // 60
        # 服务商发送短信验证码

        ccp = CCP()
        ccp.send_template_sms(mobile, [sms_code, sms_code_expires], contains.SMS_CODE_TEMP_ID)

        return Response({"message": "OK"}, status.HTTP_200_OK)


