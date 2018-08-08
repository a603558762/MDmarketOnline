from django.conf.urls import url
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from users import views

urlpatterns = [
    # url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),  # 重名检测
    # url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),  # 手机号检测
    # url(r'^users/$', views.UserView.as_view()),  # 注册
    url(r'usernames/(?P<username>\w+)/$',views.CheckUserName.as_view()),
    url(r'mobile_check/(?P<mobile>\d{11})/$',views.CheckMobile.as_view()),
    url(r'users/$',views.Register.as_view()),
    # 登录验证
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^accounts/(?P<mobile>\w{5,20})/sms/token/$', views.FindPasswd.as_view()),
    url(r'^accounts/(?P<account>.{5,20})/password/token/$', views.SMScode_ckeckView.as_view()),
    url(r'^users/(?P<pk>\d+)/password/$',views.ResetPasswd.as_view()),
    url(r'^user/$',views.UserDetailView.as_view()),
    url(r'^emails/$',views.EmailView.as_view()),
    url(r'^emails/verification/$',views.VerifyEmailView.as_view()),
    url(r'^browse_histories/$',views.UserBrowsingHistoryView.as_view()),
    url(r'^categories/(?P<category_id>\d+)/skus/$',views.SKUListView.as_view()),
]

router = routers.DefaultRouter()
router.register(r'addresses', views.AddressViewSet, base_name='addresses')

urlpatterns += router.urls