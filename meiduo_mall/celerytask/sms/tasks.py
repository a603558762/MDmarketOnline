
from meiduo_mall.libs.yuntongxun.sms import CCP

from meiduo_mall.utils import contains

from celerytask.main import celery_app


@celery_app.task()
def send_sms_code(mobile,sms_code,sms_code_expires):

    # ccp = CCP()
    print("开始发送短信验证码:测试阶段不真发送节约短信")
    # ccp.send_template_sms('18506255964', [sms_code, sms_code_expires], contains.SMS_CODE_TEMP_ID)
