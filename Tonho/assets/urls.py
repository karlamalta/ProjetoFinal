from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^fedre/$', views.fedre, name='fedre'),
]
