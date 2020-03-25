from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_per_page = 8
    list_display = ('id','content_object','user','text','comment_time')
admin.site.site_header="宇航员的个人博客,欢迎"
admin.site.site_title='宇航员的个人博客'
