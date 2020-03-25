from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
# Create your models here.
# 用户扩展对象
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,verbose_name="昵称")
    nickname=models.CharField(max_length=20)
    # 头像
    avatar=models.ImageField(upload_to='avatar/%Y/%m%d',blank=True)

    def __str__(self):
        return '<Profile:%sfor%s>'%(self.nickname,self.user.username)
#

# 收藏夹
class CollectCount(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    collect_num=models.IntegerField(default=0)

class CollectRecord(models.Model):
    # 收藏的文章
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collect_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['id']
