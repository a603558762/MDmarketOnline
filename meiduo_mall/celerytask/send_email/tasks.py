from django.conf import settings
from django.core.mail import send_mail
from celerytask.main import celery_app


@celery_app.task()
def send_email_verification(email,verify_url):
    # send_mail(subject, message, from_email, recipient_list,html_message=None)
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
    send_mail(subject, "", settings.EMAIL_FROM, [email], html_message=html_message)

    print('已发送邮件!')