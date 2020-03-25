from django.contrib import admin
from .models import Profile,CollectCount,CollectRecord
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# Register your models here.
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username','nickname','email','is_staff','is_active','is_superuser')

    def nickname(self,obj):
        return obj.profile.nickname
    nickname.short_description = "昵称"
# 重新注册User
admin.site.unregister(User)
admin.site.register(User,UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','nickname')

@admin.register(CollectRecord)
class LikeRecordAdmin(admin.ModelAdmin):
    list_display = ('id','content_object','user','collect_time')
@admin.register(CollectCount)
class LikeCountAdmin(admin.ModelAdmin):
    list_display = ('id','content_object','collect_num')