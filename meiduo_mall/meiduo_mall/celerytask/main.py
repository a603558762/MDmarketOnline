import celery



# 创建app
from celery import Celery

from meiduo_mall.libs.yuntongxun.sms import CCP

from meiduo_mall.apps.verification.views import mobile,sms_code,sms_code_expires
from meiduo_mall.meiduo_mall.utils import contains

app=app = Celery('demo',backend='',broker='')

@app.task()
def send_sms_code():

    ccp = CCP()
    ccp.send_template_sms(mobile, [sms_code, sms_code_expires], contains.SMS_CODE_TEMP_ID)