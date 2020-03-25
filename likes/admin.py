from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(LikeRecord)
class LikeRecordAdmin(admin.ModelAdmin):
    list_display = ('id','content_object','user','like_time')
@admin.register(LikeCount)
class LikeCountAdmin(admin.ModelAdmin):
    list_display = ('id','content_object','liked_num')