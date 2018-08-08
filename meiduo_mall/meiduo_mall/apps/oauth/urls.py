from django.conf.urls import url

from oauth import views

urlpatterns=[
    url(r'^oauth/qq/authorization/$',views.OAuthQQurl.as_view()),
    url(r'^oauth/qq/user/$',views.QQAuthUserView.as_view()),
    # /oauth/qq/user/
]