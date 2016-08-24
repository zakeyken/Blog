from django.conf.urls import url
from blog.views import *

urlpatterns = [
    url(r'^$',index,name='index'),
    url(r'^article/$',article,name='article'),
    url(r'^archive/$',archive,name='archive'),
]
