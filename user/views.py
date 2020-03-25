import string
import random
import time
from django.shortcuts import render,redirect,reverse
from django.http import JsonResponse
from .forms import LoginForm,RegisterForm,ChangeNicknameForm,BindEmailForm,ChangePasswordForm,ForgetPasswordForm
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from .models import CollectCount,CollectRecord
from comment.models import Comment
from blog.views import page
from blog.models import Blog
from blog.forms import ArticlePostForm
from .forms import ProfileForm
from .models import Profile
from notifications.models import Notification
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def register_ajax(request):
    print("注册开始")
    data={}
    if request.method=='POST':
        register_form_ajax=RegisterForm(request.POST,request=request)
        if register_form_ajax.is_valid():
            username=register_form_ajax.cleaned_data['username']
            email=register_form_ajax.cleaned_data['email']
            password=register_form_ajax.cleaned_data['password']
          # 创建用户
            user=User.objects.create_user(username,email,password)
            user.save()
            #删除验证码的session
            try:
                del request.session['register_code']
            except Exception as e:
                return render(request,'error.html',{'message':'操作出错:请确定验证码是否正确'})
            # 成功后跳转到登录页面
            data['status']='SUCCESS'
        else:
            data['status']='ERRORS'
            data['none'] = register_form_ajax.non_field_errors().as_text()
    return JsonResponse(data)
def login_for_modal(request):
    data = {}
    if request.method == 'POST':
        login_form=LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            data['status']='SUCCESS'
        else:
            data['status'] = 'ERRORS'
            data['none'] = login_form.non_field_errors().as_text()
    return JsonResponse(data)


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from',reverse('blog')))

def user_info(request):
    context={}
    if request.user.is_authenticated:
        collect_list = CollectRecord.objects.filter(user=request.user)
        #使用分页器进行处理
        context=page(request,collect_list)
        context['collect_list'] = collect_list
        if request.method=='POST':
            # 将提交的数据赋值给表单实例
            article_post_form=ArticlePostForm(request.POST,request.FILES)
            if article_post_form.is_valid():
                # 保存数据但是暂时不提交到数据库中
                post_article=article_post_form.save(commit=False)
                # 指定文章作者为请求方
                post_article.author=request.user
                # 然后保存到数据库
                post_article.save()
                context['post_tip']='发送成功'
                return redirect('blog_detail',post_article.pk)
            else:

                context['message']=article_post_form.errors
                return render(request,'error.html',context)
    else:
        context['message'] = '请确认是否登录状态'
        return render(request, 'error.html',context)
    if request.user.is_superuser:
        personal_blog_list = Blog.objects.filter(author=request.user)
        context['personal_blog_list'] = personal_blog_list
        context['article_form']=ArticlePostForm()
    context['login_form']=LoginForm()
    context['register_form']=RegisterForm()
    context['change_password_form']=ChangePasswordForm()
    context['change_nickname_form']=ChangeNicknameForm()
    context['bing_email_form']=BindEmailForm()
    user = request.user
    context['all_msg'] = Notification.objects.filter(recipient=user).unread()
    context['num'] = Notification.objects.filter(recipient=user).unread().count()
    return render(request, 'user_info.html', context)

def change_nickname(request):
    redirect_to=request.GET.get('from',reverse('blog'))
    if request.method=='POST':
        form=ChangeNicknameForm(request.POST,user=request.user)
        if form.is_valid():
            nickname_new=form.cleaned_data['nickname_new']
            profile,created=Profile.objects.get_or_create(user=request.user)
            profile.nickname=nickname_new
            profile.save()
            return redirect(redirect_to)

    else:
        form=ChangeNicknameForm()
    context={}
    context['form']=form
    context['page_title']="修改昵称"
    context['form_title']="修改昵称"
    context['submit_text']="修改"
    context['return_back_href']=redirect_to
    return render(request,'user/form.html',context)


def bindmail_ajax(request):
    data={}
    redirect_to = request.GET.get('from', reverse('blog'))
    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            data['status']='SUCCESS'
            # 清除session
            try:
                del request.session['bind_email_code']
            except Exception as e:
                return render(request,'error.html',{'message':'操作出错:请确定验证码是否正确'})
        else:
            data['status']='ERROR'
            data['none']=form.non_field_errors()
    return JsonResponse(data)

def send_verification_code(request):
    send_for=request.GET.get('send_for','')
    print(send_for)
    data = {}
    email=request.GET.get('email','')
    print(email)
    if email !='':
        #生成验证码
        code=''.join(random.sample(string.ascii_letters+string.digits,4))
        now=int(time.time())
        send_code_time=request.session.get('send_code_time',0)
        if now-send_code_time<30:#限定时间间隔30秒
            data['status']='ERRORS'
        else:
            request.session[send_for]=code#存进session,进行验证
            request.session['send_code_time'] = now
        #发送邮件
        try:
            send_mail(
            '绑定邮箱',#邮件主题
            '验证码:%s'%code,#内容
            '1765300685@qq.com',#from
            [email],
            fail_silently=False,
            )
            data['status'] = "SUCCESS"
        except Exception as e:
            data['status']="验证码获取失败"
    else:
        data['status']="邮箱不能为空"

    return JsonResponse(data)


def change_password_ajax(request):
    data={}
    redrict_to=reverse('blog')
    if request.method=='POST':
        form=ChangePasswordForm(request.POST,user=request.user)
        if form.is_valid():
            new_password=form.cleaned_data['new_password']
            user=request.user
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            data['status']='SUCCESS'
            data['url']=redrict_to
        else:
            data['status']='ERROR'
            data['old_password']=form['old_password'].errors.as_text()

    return JsonResponse(data)

def forget_password(request):
    redirect_to = request.GET.get('from', reverse('blog'))
    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password=form.cleaned_data['new_password']
            user=User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 清除session
            try:
                del request.session['forget_password_code']
            except Exception as e:
                return render(request,'error.html',{'message':'操作出错:请确定验证码是否正确'})

            return redirect(redirect_to)
    else:
        form = ForgetPasswordForm()
    context = {}
    context['form'] = form
    context['page_title'] = "重置密码"
    context['form_title'] = "重置密码"
    context['submit_text'] = "重置"
    context['return_back_href'] = redirect_to
    context['register_form']=RegisterForm()
    context['login_form']=LoginForm()
    return render(request, 'user/forget_password.html', context)

# 收藏
def SuccessResponse(collect_num):
    data={}
    data['status']='SUCCESS'
    data['collect_num']=collect_num
    return JsonResponse(data)

def ErrorResponse(code,message):
    data={}
    data['status']='ERROR'
    data['code']=code
    data['message']=message
    return JsonResponse(data)

def collect_change(request):
    data={}
    #获取数据
    user=request.user
    if not user.is_authenticated:
        return ErrorResponse(400, 'you do not login')

    content_type=request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))

    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj=model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return ErrorResponse(401,'object not exist')

    is_collect=request.GET.get('is_collect')
    # 处理数据
    if is_collect=='true':
        # 要收藏
        collect_record,newcreated=CollectRecord.objects.get_or_create(content_type=content_type,object_id=object_id,user=request.user)
        if newcreated:
            # 未收藏
            collect_count,newcreated=CollectCount.objects.get_or_create(content_type=content_type,object_id=object_id)
            collect_count.collect_num+=1
            collect_count.save()
            return SuccessResponse(collect_count.collect_num)
        else:
            # 已收藏,不能重复收藏
            return ErrorResponse(402,'you have collected')
            # return SuccessResponse(CollectCount.objects.filter(content_type=content_type,object_id=object_id).collect_num)
    else:
        # 要取消收藏
        if CollectRecord.objects.filter(content_type=content_type,object_id=object_id,user=request.user).exists():
            # 有收藏过取消点赞
            collect_record=CollectRecord.objects.get(content_type=content_type,object_id=object_id,user=request.user)
            collect_record.delete()
            # 收藏数减一
            collect_count,newcreated = CollectCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not newcreated:
                collect_count.collect_num -=1
                collect_count.save()
                return SuccessResponse(collect_count.collect_num)
            else:
                return ErrorResponse(404,'data error')
        else:
            # 没有收藏,不能取消
            # return  SuccessResponse(CollectCount.objects.filter(content_type=content_type,object_id=object_id).collect_num)
            return ErrorResponse(403,'you did not collect')

# 检查用户名是否符合要求
def check_username(request):
    data={}
    if request.method=='GET':
        username=request.GET.get('username')

        try:
           User.objects.get(username=username)
           data['status']='ERROR'
        except Exception as e:
           data['status'] = 'SUCCESS'

    return JsonResponse(data)

# 删除博客
def delete_blog(request):
    data={}
    pk=request.GET.get('pk','')
    if pk!='':
        this_blog=Blog.objects.filter(pk=pk,author=request.user)
        if this_blog:
            # 开始删除
            this_blog.delete()
            data['status']='SUCCESS'
        else:
            # 操作失败
            data['status']='ERRORS'
    else:
        data['status']='ERRORS'
    return JsonResponse(data)

# 修改博客内容

def update_blog(request,pk):
    context={}
    redirect_to = request.GET.get('from', reverse('blog'))
    # 判断提交方式
    # 首先获取要重新编辑的博客的id
    article=Blog.objects.filter(pk=pk).first()
    # 判断是否作者本人操作
    if article.author!=request.user:
        context['message']='非本人操作!'
        return render(request,'error.html',context)
    if request.method=='POST':
        article = Blog.objects.filter(pk=pk).first()
        article_form=ArticlePostForm(request.POST,request.FILES)
        # 判断提交数据是否满足模型的要求
        if article_form.is_valid():
            # 保存新写入的博客内容
            article.title=request.POST['title']
            article.content=request.POST['content']
            article.blog_type=article_form.cleaned_data['blog_type']
            article.avatar=article_form.cleaned_data['avatar']
            # print(article.avatar)
            article.save()
            return redirect('blog_detail',pk)
        else:
            context['message']='表单填写内容有误,请检查后重新操作!'
            return render(request,'error.html',context)

    else:
    #     get请求
        article_form=ArticlePostForm(instance=article)
        context={'update_article':article,'update_form':article_form}
        context['return_back_href']=redirect_to

    return render(request,'user/update_blog.html',context)

# 编辑用户信息
def profile_edit(request,id):
    user=User.objects.get(id=id)
    if user!=request.user:
        context={}
        context['message']='(您当前出于离线状态)请确认是否登录!'
        return render(request,'error.html',context)
    if Profile.objects.filter(user_id=id).exists():
        profile=Profile.objects.get(user_id=id)
    else:
        profile=Profile.objects.create(user=user)

    if request.method=='POST':
        if request.user!=user:
            return render(request, 'error.html', {'message': '你没有权限修改此用户信息.'})
        profile_form=ProfileForm(request.POST,request.FILES)
        if profile_form.is_valid():
            profile.nickname=profile_form.cleaned_data['nickname']
            if 'avatar' in request.FILES:
                profile.avatar=profile_form.cleaned_data['avatar']
            profile.save()
            return redirect('edit',id=id)
        else:
            return render(request,'error.html',{'message':'表单输入有误,请重新输入哟!'})
    elif request.method=='GET':
        profile_form=ProfileForm(instance=profile)
        context={'profile_form':profile_form,'profile':profile,'user':user}
        context['change_password_form'] = ChangePasswordForm()
        context['bing_email_form'] = BindEmailForm()
        return render(request,'user/edit.html',context)
    else:
        return render(request, 'error.html', {'message': '请使用GET或POST请求数据'})

# 删除评论
@csrf_exempt
def delete_comment(request):
    data={}
    if request.method=='POST':
        id=request.POST.get('pk','-1')
        this_comment = Comment.objects.filter(id=id).first()
        if this_comment:
            if request.user==this_comment.user:
                # 是否是本人操作
                if id=='':
                    data['status']='ERROR'
                    data['message']='不能为空'
                else:
                    this_comment.delete()
                    data['status'] = 'SUCCESS'
        else:
            data['status'] = 'ERROR'
            data['message'] = '操作失败!'
    else:
        data['status']='ERROR'
        data['message']='操作失败!'


    return JsonResponse(data)

def deal_with_msg(request):
    msg_id=request.GET.get('msg_id')
    # print(msg_id)
    # print(type(msg_id))
    if not msg_id is None:
        msg_id=int(msg_id)
        Notification.objects.get(id=msg_id).mark_as_read()
    else:
        Notification.objects.mark_all_as_read()
    return redirect('user_info')