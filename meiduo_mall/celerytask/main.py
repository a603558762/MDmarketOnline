


# 创建app
from celery import Celery


# from meiduo_mall.apps.verification.views import mobile,sms_code,sms_code_expires



import os


if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# app = Celery('demo',backend='',broker='')
celery_app = Celery('meiduo')

# 导入配置文件
celery_app.config_from_object('celerytask.config')

# 自动注册celery任务
celery_app.autodiscover_tasks(['celerytask.sms', 'celerytask.send_email','celerytask.html'])


# 开启celery的命令
#  celery -A 应用路径（.包路径） worker -l info
#  celery -A celery_tasks.main worker -l info
#  celery -A celerytask.main worker -l info


