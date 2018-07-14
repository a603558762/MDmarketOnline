from django.conf.urls import url

from users import views

urlpatterns = [
    # url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),  # 重名检测
    # url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),  # 手机号检测
    # url(r'^users/$', views.UserView.as_view()),  # 注册
    url(r'usernames/(?P<username>\w+)/$',views.CheckUserName.as_view()),
]
