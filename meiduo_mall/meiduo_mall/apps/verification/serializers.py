from django_redis import get_redis_connection
from rest_framework import serializers


class ImageCodeCheckSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(format='hex_verbose')
    text = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        # 对多个字段验证,attrs是一个字典,可以使get传过来的也可以是POST传过来的
        uuid = attrs['uuid']
        text = attrs['text']
        # 查询真实图片验证码



        redis_conn = get_redis_connection('image_code_store_redis')
        real_text = redis_conn.get("image_{}".format(uuid))
        print("real_text",real_text)
        if not real_text:

            raise serializers.ValidationError('验证码过期!')
        real_text=real_text.decode()
        # 删除此验证码,每个图形验证码只有一次的验证机会:
        # try:
        #     redis_conn.delete("image_{}".format(uuid))
        # except Exception as e:
        #     print(e)

        if real_text.upper() != text.upper():
            raise serializers.ValidationError('图片验证码输入错误')

            # 判断是否在60s内
        redis_conn = get_redis_connection('image_code_store_redis')
        #
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        if send_flag:
            raise serializers.ValidationError('请求次数过于频繁')
        return attrs
