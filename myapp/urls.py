from django.conf.urls import url
from myapp.views import index,sample,home

urlpatterns = [
	url(r'^$',home,name="home"),
	url(r'^index/',index,name="index"),
	url(r'^sample/',sample,name="sample")
]