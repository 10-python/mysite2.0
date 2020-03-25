from .views import *
from django.urls import path


urlpatterns = [
    path('type/<int:blog_type_id>',blog_with_type,name='blog_with_type'),
    path('<int:blog_id>',blog_detail,name='blog_detail'),
    path('type/<int:year>/<int:month>', blog_with_date, name='blog_with_date'),
    path('index/',blog,name='blog'),
]
