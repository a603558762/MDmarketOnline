from django.conf.urls import url

from meiduo_mall.apps.verification import views

urlpatterns=[
    url(r'image_code/(?P<uuid>.*)/$',views.Image_code_generate.as_view()),
    url(r'smscode/(?P<mobile>\d{11})/$',views.SMScodeView.as_view()),
    # url(r'usernames/(?P<username>)/$',views.CheckUserName.as_view()),
]