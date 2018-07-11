from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_mall.utils import contains
from meiduo_mall.utils.captcha import captcha


class Image_code_generate(APIView):
    """
    get方式生成验证码图形
    """
    def get(self,request,uuid):
        # image_code_id实际是uuid,依据uuid生成对应的验证码图形
        name, text,image=captcha.captcha.generate_captcha()
        # 将生成的验证码对应的text保存到redis中,image_uuid的保存方式
        redis_conn=get_redis_connection('image_code_store_redis')
        redis_conn.setex(name="image_{}".format(uuid),time=contains.MAX_IMAGE_CODE_LIVE_TIME,value=text)
        # return Response(data=image,content_type='image/jpg')
        # content=b'', *args, **kwargs 源码content是byte类型
        return HttpResponse(content=image,content_type='image/jpg')