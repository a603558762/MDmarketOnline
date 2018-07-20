
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from itsdangerous import TimedJSONWebSignatureSerializer, BadData

from meiduo_mall.utils import contains



from django.conf import settings


class User(AbstractUser):
    mobile=models.CharField(max_length=11,unique=True,verbose_name='手机号')
    # 邮箱验证
    email_active=models.BooleanField(default=False,verbose_name='邮箱验证状态')

    # mobile2=models.CharField(max_length=11,unique=True,verbose_name='手机号')
    class Meta:
        db_table='tb_user'
        verbose_name='用户'
        verbose_name_plural=verbose_name

    def generate_access_token(self):
        # serializer = Serializer(秘钥, 有效期秒)
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, contains.ACCESS_TOKEN_LIFE_TIME)
        # serializer.dumps(数据), 返回bytes类型
        token = serializer.dumps({'mobile': self.mobile})
        token = token.decode()

        return token
        # 检验token
        # 验证失败，会抛出itsdangerous.BadData异常
        # serializer = Serializer(settings.SECRET_KEY, contains.ACCESS_TOKEN_LIFE_TIME)
        # try:
        #     data = serializer.loads(token)
        # except BadData:
        #     return None

    @staticmethod
    def check_send_sms_code_token(token):
        """
        检验发送短信验证码的token
        """
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=contains.ACCESS_TOKEN_LIFE_TIME)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            return data.get('mobile')

