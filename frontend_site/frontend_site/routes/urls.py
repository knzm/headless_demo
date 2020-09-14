from django.urls import re_path

from . import views


urlpatterns = [
    re_path('^(?P<path>.*)$', views.page_view, name='routes_page'),
]
