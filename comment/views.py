from django.shortcuts import render,redirect,reverse
from .models import Comment
from django.utils.timezone import localtime
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from .forms import CommentForms
from notifications.signals import notify
from django.contrib.auth.models import  User

import json
# Create your views here.
def commit(request):
    data = {}
    if request.method=='POST':
        comment_form=CommentForms(request.POST,user=request.user)
        referer = request.META.get("HTTP_REFERER", reverse('blog'))
        if comment_form.is_valid():
            comment = Comment()
            comment.user = request.user
            comment.text = comment_form.cleaned_data['text']
            comment.content_object = comment_form.cleaned_data['content_object']
            parent=comment_form.cleaned_data['parent']#回复的
            if not parent is None:#有回复
                comment.root=parent.root if not parent.root is None else parent
                comment.parent=parent
                comment.reply_to=parent.user
                # 新增代码,发送通知
                if not parent.user.is_superuser:
                    notify.send(
                        request.user,  # 发送者
                        recipient=parent.user,  # 接受者
                        verb=comment.text,#评论
                        target= comment.content_object,  # 连接到动作的对象:评论文章
                        action_object=comment.parent  # 执行通知时的对象:评论内容

                    )
            comment.save()
            if not parent is None:  #
                if not request.user.is_superuser:
                    notify.send(
                        request.user,
                        recipient=User.objects.filter(is_superuser=1),
                        verb=comment.text,
                        target= comment.content_object,
                        action_object=comment.parent
                    )
            # 返回数据
            data['status']='SUCCESS'
            data['username']=comment.user.username
            data['comment_time']=localtime(comment.comment_time).strftime('%Y-%m-%d %H:%M:%S')
            data['text']=comment.text
            data['content_type']=ContentType.objects.get_for_model(comment).model
            if not parent is None:#回复
                data['reply_to']=comment.reply_to.username
            else:
                data['reply_to'] =''
            data['pk']=comment.pk
            data['root_pk']=comment.root.pk if not comment.root is None else ''
            if comment.user.profile.avatar:
                data['picture_url']=comment.user.profile.avatar.url
        else:
            # return render(request,'error.html',{'message':comment_form.errors,'redirect_to':referer})
            data = {}
            data['status'] = 'ERRORS'
            data['message']=list(comment_form.errors.values())[0][0]
    else:
        return JsonResponse({'status':'error'})
    return JsonResponse(data)