from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login_for_modal/',views.login_for_modal,name="login_for_modal"),
    path('register_ajax/',views.register_ajax,name='register_ajax'),
    path('check_username/',views.check_username,name='check_username'),
    path('logout/',views.logout,name='logout'),
    path('user_info/',views.user_info,name='user_info'),
    path('change_nickname/',views.change_nickname,name="change_nickname"),
    path('send_code/',views.send_verification_code,name='send_verification_code'),
    path('bindemail_ajax/',views.bindmail_ajax,name='bindemail_ajax'),
    path('change_password_ajax/',views.change_password_ajax,name='change_password_ajax'),
    path('forget_password/',views.forget_password,name='forget_password'),
    path('collect_change/',views.collect_change,name="collect_change"),
    path('delete_blog/',views.delete_blog,name='delete_blog'),
    path('delete_comment/',views.delete_comment,name='delete_comment'),
    path('update_blog/<int:pk>/',views.update_blog,name='update_blog'),
    path('edit/<int:id>/',views.profile_edit,name='edit'),
    path('dealwith/',views.deal_with_msg,name='dealwith')
]
# add
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
