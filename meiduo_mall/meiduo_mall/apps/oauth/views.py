from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import GenericAPIView

from .utils import GetQQlogin
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import QQAPIException

from .models import OAuthQQUser
from rest_framework_jwt.settings import api_settings

from .serializers import OAuthQQUserSerializer


class OAuthQQurl(GenericAPIView):
    #
    # def __init__(self, app_id=None, app_key=None, redirect_uri=None, state=None):
    #     self.app_id = app_id or settings.QQ_APP_ID
    #     self.app_key = app_key or settings.QQ_APP_KEY
    #     self.redirect_url = redirect_uri or settings.QQ_REDIRECT_URL
    #     self.state = state or '/'  # 用于保存登录成功后的跳转页面路径

    def get(self, request):
        # 拼接字符串返回
        state = request.query_params.get('state')
        qq_login_obj = GetQQlogin()

        url = qq_login_obj.get_auth_url()
        return Response({"url": url})


# GET /oauth/qq/user/?code=xxx
class QQAuthUserView(GenericAPIView):
    serializer_class = OAuthQQUserSerializer

    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        qqoath = GetQQlogin()
        try:
            # 构造请求获得qq的access_token
            token = qqoath.get_access_token(code)

            # 构造请求获得qq的openid
            openid = qqoath.get_openid(token)
        except QQAPIException:
            return Response({'message': '获取QQ用户数据异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # 判断openid是否绑定过账户
        try:
            oauthqq = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果未绑定，手动创建接下来绑定身份使用的access_token, 并返回
            access_token = OAuthQQUser.generate_save_user_token(openid)
            return Response({'access_token': access_token})

        else:
            # 找到用户, 生成token
            user = oauthqq.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })
            return response

    def post(self, request):
        """
        保存QQ登录用户数据
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 生成已登录的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        response = Response({
            'token': token,
            'user_id': user.id,
            'username': user.username
        })

        return response