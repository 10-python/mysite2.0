from django.shortcuts import render, get_object_or_404,redirect
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models import Q
from .models import *
from comment.models import *
from read_statistics.mytools import read_tool,get_hot_blog
from read_statistics.mytools import get_seven_days_read_date,get_today_hot,get_yesterday_hot,get_week_hot_blog
from django.core.cache import cache
from user.forms import LoginForm,RegisterForm
from notifications.models import Notification
# from comment.forms import CommentForms

# Create your views here.
"""分页器"""
def page(request, element_list):
    context = {}
    paginator = Paginator(element_list, 5)
    # 获取参数页码
    page_num = request.GET.get('page', 1)
    page_of_blogs = paginator.get_page(page_num)
    # 当前页码
    current_page_num=page_of_blogs.number
    # 获取当前页码前后两页
    page_range=list(range(max(current_page_num-2,1),current_page_num))+list(range(current_page_num,min(current_page_num+2,paginator.num_pages)+1))
    # print(page_range)
    context["page_range"] = page_range
    # 加上省略标记
    if page_range[0]-1>=2:
        page_range.insert(0,'...')
    if paginator.num_pages-page_range[-1]>=2:
        page_range.append("...")

    # 加上首页尾页
    if page_range[0]!=1:
        page_range.insert(0,1)
    if page_range[-1]!=paginator.num_pages:
        page_range.append(paginator.num_pages)

    context["page_of_blogs"] = page_of_blogs
    context['blogs'] = page_of_blogs.object_list
    context['current_page_num'] = page_of_blogs.number
    # right
    blogs_type = BlogType.objects.all()
    context["blogs_type"] = blogs_type
    # 日期归档
    context['blogs_dates'] = Blog.objects.dates("created_time", 'month', order='DESC')
    # 统计数量,增加count字段与之type对应(所以必须先有blogs_type键)
    context["blogs_type"] = BlogType.objects.annotate(blogs_count=Count('blog'))
    return context

"""热门标签"""
def blog_with_type(request, blog_type_id):
    # if request.GET.get("today") == '2019':
    # 从GET中获取到相应参数的值
    #     return redirect("http://www.baidu.com")
    blog_type = get_object_or_404(BlogType, id=blog_type_id)
    blogs = Blog.objects.filter(blog_type=blog_type)
    # 分页器
    context = page(request, blogs)
    context["all_num"] = blogs.count()
    context["type"] = blog_type
    hot_blogs = get_hot_blog(content_type=ContentType.objects.get_for_model(Blog))
    context["hot_blogs"] = hot_blogs
    context['register_form'] = RegisterForm()
    context['login_form'] = LoginForm()
    blog_content_type = ContentType.objects.get_for_model(Blog)
    context['get_today_hot_blog'] = get_today_hot(content_type=blog_content_type)
    context['get_yesterday_hot_blog'] = get_yesterday_hot(content_type=blog_content_type)
    context['get_week_hot_blog'] = get_week_hot_blog()
    if request.user.is_authenticated:
        context['mesg_num'] = Notification.objects.filter(recipient=request.user).unread().count()
    return render(request, 'blog_with_type.html', context)

"""日期归档"""
def blog_with_date(request, year, month):


    blogs = Blog.objects.filter(created_time__year=year, created_time__month=month)
    # 分页器
    context = page(request, blogs)
    context['month'] = month
    context['year'] = year
    context["all_num"] = blogs.count()
    hot_blogs = get_hot_blog(content_type=ContentType.objects.get_for_model(Blog))
    context["hot_blogs"] = hot_blogs
    context['register_form'] = RegisterForm()
    context['login_form'] = LoginForm()
    blog_content_type = ContentType.objects.get_for_model(Blog)
    context['get_today_hot_blog'] = get_today_hot(content_type=blog_content_type)
    context['get_yesterday_hot_blog'] = get_yesterday_hot(content_type=blog_content_type)
    context['get_week_hot_blog'] = get_week_hot_blog()
    if request.user.is_authenticated:
        context['mesg_num'] = Notification.objects.filter(recipient=request.user).unread().count()
    return render(request, 'blog_with_date.html', context)


"""博客列表"""
def blog(request):
    search=request.GET.get('search')
    if search:
        #使用Q对象进行联合搜索
        blogs_list=Blog.objects.filter(
            Q(title__icontains=search)| Q(content__icontains=search)
        )
    else:
        search==''
        blogs_list=Blog.objects.all()
    context = page(request, blogs_list)
    context['search_num']=blogs_list.count()
    context['search']=search



    hot_blogs = get_hot_blog(content_type=ContentType.objects.get_for_model(Blog))
    # print(hot_blogs)
    context["hot_blogs"] = hot_blogs

    blog_content_type = ContentType.objects.get_for_model(Blog)
    read_num_sum, each_date_day_list = get_seven_days_read_date(content_type=blog_content_type)
    get_week_hot_blogs = cache.get('get_week_hot_blogs')
    if get_week_hot_blogs is None:
        get_week_hot_blogs = get_week_hot_blog()
        cache.set('get_week_hot_blogs', get_week_hot_blogs, 3600)
    context['read_num_sum_list'] = read_num_sum
    context['each_date_day_list'] = each_date_day_list

    context['get_today_hot_blog'] = get_today_hot(content_type=blog_content_type)
    context['get_yesterday_hot_blog'] = get_yesterday_hot(content_type=blog_content_type)
    context['get_week_hot_blog'] = get_week_hot_blog()
    context['register_form'] = RegisterForm()
    context['login_form'] = LoginForm()
    if request.user.is_authenticated:
        context['mesg_num'] = Notification.objects.filter(recipient=request.user).unread().count()
    return render(request,'blog2.html',context)

"""博客详情"""
def blog_detail(request, blog_id):
    context = {}
    blog = get_object_or_404(Blog, id=blog_id)

    """
    阅读加1,并且返回cookies
    """
    read_cookies_key=read_tool(request,blog)#将blog模型传给content_type:ct=blog

    # 获取该blog的type
    the_blog_type = blog.blog_type
    # 获取该type的blog
    these_blogs = Blog.objects.filter(blog_type=the_blog_type)
    context["all_num"] = these_blogs.count()
    # left
    context['blog'] = blog
    # 获取上一篇(该类型下)
    context['first_blog'] = Blog.objects.filter(blog_type=the_blog_type, created_time__lt=blog.created_time).first()
    # 获取下一篇
    context['last_blog'] = Blog.objects.filter(blog_type=the_blog_type, created_time__gt=blog.created_time).last()
    # right
    blogs_type = BlogType.objects.all()
    context["blogs_type"] = blogs_type
    # 日期归档
    context['blogs_dates'] = Blog.objects.dates("created_time", 'month', order='DESC')
    # 统计数量
    context["blogs_type"] = BlogType.objects.annotate(blogs_count=Count('blog'))
    # 返回评论列表
    content_type_blog=ContentType.objects.get_for_model(blog)
    hot_blogs = get_hot_blog(content_type=ContentType.objects.get_for_model(Blog))
    # print(hot_blogs)
    context["hot_blogs"] = hot_blogs
    context['login_form']=LoginForm()
    context['register_form']=RegisterForm()
    blog_content_type = ContentType.objects.get_for_model(Blog)
    context['get_today_hot_blog'] = get_today_hot(content_type=blog_content_type)
    context['get_yesterday_hot_blog'] = get_yesterday_hot(content_type=blog_content_type)
    context['get_week_hot_blog'] = get_week_hot_blog()
    if request.user.is_authenticated:
        context['mesg_num'] = Notification.objects.filter(recipient=request.user).unread().count()

    response=render(request, 'blog_detail.html', context)
    # 浏览器关闭失效
    response.set_cookie(read_cookies_key,'true')#阅读标记
    return  response
