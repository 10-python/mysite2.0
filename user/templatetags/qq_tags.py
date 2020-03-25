from django import template
from urllib.parse import urlencode
from django.contrib.contenttypes.models import ContentType
from ..models import CollectCount,CollectRecord

#自定义模板标签
register=template.Library()

@register.simple_tag
def get_login_qq_url():
    params={
        'response_type':'code',
        'client_id':'1110149281',
        'redirect_uri':'http://app1110149281.qzoneapp.com',
        'state':'python',
    }
    return "https://graph.qq.com/oauth2.0/authorize?"+urlencode(params)




#自定义模板标签
register=template.Library()
@register.simple_tag
def get_collect_count(obj):
    content_type = ContentType.objects.get_for_model(obj)

    collect_count,created=CollectCount.objects.get_or_create(content_type=content_type,object_id=obj.pk)
    return collect_count.collect_num

@register.simple_tag
def get_collect_status(user,obj):
    content_type = ContentType.objects.get_for_model(obj)
    # user=context['user']
    if not user.is_authenticated:
        return ''
    if CollectRecord.objects.filter(content_type=content_type,object_id=obj.pk,user=user).exists():
        return 'active'
    else:
        return ''
@register.simple_tag
def get_content_type(obj):
    content_type=ContentType.objects.get_for_model(obj)
    return content_type.model
# 用户认证
@register.simple_tag
def is_user(user,obj):
    if user.pk!=obj.pk:
        return 'hidden'
    else:
        return ''