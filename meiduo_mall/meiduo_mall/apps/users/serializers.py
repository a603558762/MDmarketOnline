import logging
import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework_jwt.settings import api_settings

from users.models import User

logger = logging.getLogger()


class Userserializers(serializers.ModelSerializer):
    """
        创建用户序列化器
        """
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)  # 增加token字段

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2',
                  'sms_code', 'mobile', 'allow', 'token')
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        # 判断两次密码
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断短信验证码
        redis_conn = get_redis_connection('image_code_store_redis')
        mobile = attrs['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return attrs

    def create(self, validated_data):
        """
        创建用户
        """
        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        # 使用createAPIView的create方法
        # type(user): <class 'users.models.User'>
        user = super().create(validated_data)

        # 调用django的认证系统加密密码
        # print(validated_data['password'])
        user.set_password(validated_data['password'])
        user.save()

        # 补充生成记录登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        #
        return user


class SMScode_ckeckserializer(serializers.Serializer):
    sms_code = serializers.CharField(min_length=6, max_length=6)

    # sms_code = serializers.IntegerField(read_only=True)

    def validate_sms_code(self, value):
        print(value)
        # sms_code=attrs.get('sms_code')
        # access_token=attrs.get('access_token')
        # user=User.check_send_sms_code_token(access_token)
        # if not user:
        #     raise serializers.ValidationError('token错误!')
        # mobile=user.mobile

        # 查询redis中real_sms_code
        account = self.context['view'].kwargs.get('account')
        redis_conn = get_redis_connection('image_code_store_redis')
        real_sms_code = None
        if re.match(r'^((13[0-9])|(14[5|7])|(15([0-3]|[5-9]))|(18[0,5-9]))\d{8}$', account):
            account = account
        else:
            user = None
            try:
                user = User.objects.filter(username=account)[0]
            except Exception as e:
                logger.error(e)
            if not user:
                raise NotFound('用户名输入错误')  # 404
            account = user.mobile

        try:
            real_sms_code = redis_conn.get("sms_%s" % account).decode()
        except Exception as e:
            logger.error(e)

        if not real_sms_code:
            raise serializers.ValidationError('无效的短信验证码')  # 400
        if real_sms_code != value:
            raise AuthenticationFailed('验证码错误')  # 401
        return value


class ResetPasswdserializer(serializers.ModelSerializer):
    password2 = serializers.CharField(max_length=20, min_length=5, label='确认密码', write_only=True)
    access_token = serializers.CharField(label='操作token', write_only=True)

    class Meta:
        model = User
        fields = ['id', 'password', 'password2', 'access_token']

    def validate_access_token(self, value):

        mobile = User.check_send_sms_code_token(value)
        if not mobile:
            raise serializers.ValidationError('手机号格式错误')
        return mobile

    def validate(self, attrs):
        password = attrs['password']
        password2 = attrs['password2']
        if password != password2:
            raise HTTP_400_BAD_REQUEST('两次密码不一致')
        return attrs

    def update(self, instance, validated_data):

        instance.set_password(validated_data.get('password2'))
        instance.save()
        return instance