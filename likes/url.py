from .views import *
from django.urls import path

urlpatterns = [
    path('like_change',like_change,name="like_change"),]