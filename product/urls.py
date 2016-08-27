from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.front, name='front'),   
    #url(r'^template/$', views.front_template, name='front_template'),   
    #url(r'^(?P<item_id>[0-9]+)/$', views.item, name='item_detail')
]