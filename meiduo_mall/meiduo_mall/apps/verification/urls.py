from django.conf.urls import url

from verification import views

urlpatterns=[
    url(r'image_code/(?P<uuid>.*)/$',views.Image_code_generate.as_view()),
    url(r'smscode/(?P<mobile>\d{11})/$',views.SMScodeView.as_view()),
    url(r'sms_codes/$',views.SMSsend_by_access_token.as_view()),

]