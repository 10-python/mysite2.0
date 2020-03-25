from django import template
from ..models import Blog
from django.contrib.auth.models import User
from read_statistics.models import ReadNum
#自定义模板标签
register=template.Library()
@register.simple_tag
def get_blog_avatar_url(blog):
    try:
        id=ReadNum.objects.filter(id=blog.pk).first().object_id
        avatar=Blog.objects.filter(pk=id).first().avatar.url
    except:
        avatar=None
    # print(avatar)
    return avatar
@register.simple_tag
def get_blog_user_avatar_url(blog):
    try:
        profile_avatar=User.objects.filter(username=blog.author).first().profile.avatar.url
    except Exception as e:
        profile_avatar=None
    # print(profile_avatar)
    return profile_avatar