from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation#反向解析
from read_statistics.models import ReadNumExpand,ReadDetail
from PIL import Image

# Create your models here.
class BlogType(models.Model):
    type_name=models.CharField(max_length=15)
    def __str__(self):
        return self.type_name

class Blog(models.Model,ReadNumExpand):
    title=models.CharField(max_length=50)
    blog_type=models.ForeignKey(BlogType,on_delete=models.CASCADE)
    content=RichTextUploadingField()
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    created_time=models.DateTimeField(auto_now_add=True)
    last_updated_time=models.DateTimeField(auto_now=True)
    # readnum
    read_detail=GenericRelation(ReadDetail)
    # 文章标题
    avatar=models.ImageField(upload_to='article/%Y/%m/%d',blank=True)

    def save(self, *args, **kwargs):
        # 调用原有的 save() 的功能
        article = super(Blog, self).save(*args, **kwargs)
        # 固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)

        return article

    class Meta:
        ordering=['-created_time']
    def __str__(self):
        return self.title
