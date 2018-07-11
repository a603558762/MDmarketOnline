from django.conf.urls import url

from verification import views

urlpatterns=[
    url(r'image_code/(?P<uuid>.*)/$',views.Image_code_generate.as_view()),
]