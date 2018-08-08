import logging
import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework_jwt.settings import api_settings

from celerytask.send_email.tasks import send_email_verification
from goods.models import SKU
from meiduo_mall.utils import contains
from .models import User, Address

# from meiduo_mall.celerytask.main import send_email

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


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'email_active']


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        # 发送邮件使用celery异步任务
        email = validated_data['email']
        verify_url = instance.generate_verify_email_url()
        send_email_verification.delay(email, verify_url)

        return instance

        # super(EmailSerializer, self).update(instance, validated_data)


class VerifyEmailserializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)

    # def validate_token(self, value):
    #
    #     user_id=User.check_verify_email_url(value)
    #     if not user_id:
    #         raise AuthenticationFailed('验证token有误')
    #     try:
    #         user=User.objects.get(id=user_id)
    #     except Exception as e:
    #         logger.error(e)
    #         raise AuthenticationFailed('验证token有误')
    #     if not user:
    #         raise AuthenticationFailed('验证token有误')
    #     return value

    def update(self, instance, validated_data):
        print('instance:', instance)
        print('validated_data:', validated_data)
        instance.email_active = True

        instance.save()
        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """
        保存
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """

    class Meta:
        model = Address
        fields = ('title',)

class AddUserBrowsingHistorySerializer(serializers.Serializer):
    """
    添加用户浏览历史序列化器
    """
    sku_id = serializers.IntegerField(label="商品SKU编号", min_value=1)

    def validate_sku_id(self, value):
        """
        检验sku_id是否存在
        """
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('该商品不存在')
        return value

    def create(self, validated_data):
        """
        保存
        """
        user_id = self.context['request'].user.id
        sku_id = validated_data['sku_id']

        redis_conn = get_redis_connection("history")
        pl = redis_conn.pipeline()

        # 移除已经存在的本商品浏览记录
        pl.lrem("history_%s" % user_id, 0, sku_id)
        # 添加新的浏览记录
        pl.lpush("history_%s" % user_id, sku_id)
        # 只保存最多5条记录
        pl.ltrim("history_%s" % user_id, 0, contains.USER_BROWSING_HISTORY_COUNTS_LIMIT-1)

        pl.execute()

        return validated_data