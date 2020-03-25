# 引入表单类
from django import forms
# 引入模型类
from .models import Blog
# 写文章的表单类
class ArticlePostForm(forms.ModelForm):
    class Meta:
        # 指明数据模型
        model=Blog
        # 定义表单显示的字段
        fields=('title','blog_type','content','avatar')
        labels={
            'title':'文章标题',
            'blog_type':'文章类型',
            'content':'正文内容',
            'avatar':'文章标题图',
        }