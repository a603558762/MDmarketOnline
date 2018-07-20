from celery_demo.celery import app
import time

# 加上app对象的task装饰器
# 此函数为任务函数
@app.task
def my_task():
    print("任务开始执行....")
    time.sleep(5)
    print("任务执行结束....")
  在views.py模块中创建视图index:

from django.shortcuts import render
from django.http import HttpResponse
from .tasks import my_task


def index(request):
# 将my_task任务加入到celery队列中
# 如果my_task函数有参数，可通过delay()传递
# 例如 my_task(a, b), my_task.delay(10, 20)
    my_task.delay()

    return HttpResponse("<h1>服务器返回响应内容!</h1>")