"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from . import views as v
from blog import views
from comment.views import *
from django.conf.urls.static import static
import notifications.urls
urlpatterns = [
    path('yhy/',views.blog),
    path('admin/', admin.site.urls),
    path('user/',include('user.urls')),
    path('blog/',include('blog.urls')),
    path('ckeditor/',include('ckeditor_uploader.urls')),
    path('commit/', commit, name='commit'),
    path('likes/',include('likes.url')),
    path('contact/',v.contact,name='contact'),
    path('test/',v.test,name='test'),
    path('inbox/notifications/',include(notifications.urls,namespace='notifications')),
    path('information/',v.information,name='information'),
]

urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)