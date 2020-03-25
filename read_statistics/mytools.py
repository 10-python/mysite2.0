import datetime
from read_statistics.models import *
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from blog.models import Blog

def read_tool(request,obj):
    ct=ContentType.objects.get_for_model(obj)#先获取这个关联模型
    key="%s_%s_read" % (ct,obj.id)
    if not request.COOKIES.get(key):
        # if ReadNum.objects.filter(content_type=ct, object_id=obj.id).count():
        #     # 存在
        #     readnum = ReadNum.objects.get(content_type=ct, object_id=obj.id)
        # else:
        #     readnum = ReadNum(content_type=ct, object_id=obj.id)
        readnum,readnum_is_created=ReadNum.objects.get_or_create(content_type=ct, object_id=obj.id)#在通过关联模型和主键获取被关联模型对象
            # readnum.blog = blog
        readnum.read_num += 1
        readnum.save()

        # 统计 当天 阅读量
        date=timezone.now().date()
        # if ReadDetail.objects.filter(content_type=ct,object_id=obj.id,date=date).count():
        #     readdetail=ReadDetail.objects.get(content_type=ct,object_id=obj.id,date=date)
        # else:
        #     readdetail = ReadDetail(content_type=ct, object_id=obj.id, date=date)
        readdetail,readdetail_is_created=ReadDetail.objects.get_or_create(content_type=ct,object_id=obj.id,date=date)
        readdetail.read_num+=1
        readdetail.save()

    return key

def get_seven_days_read_date(content_type):
    today=timezone.now().date()
    read_num_sum=[]
    each_date_day_list=[]
    # yesterday=today-datetime.timedelta(days=1)#差量1,昨天
    for i in range(7,0,-1):
        each_date_day=today-datetime.timedelta(days=i)
        each_date_day_list.append(each_date_day.strftime("%m/%d"))
        read_details=ReadDetail.objects.filter(content_type=content_type,date=each_date_day)
        result=read_details.aggregate(read_num_sum=Sum('read_num'))#键值对的形式
        read_num_sum.append(result["read_num_sum"]or 0)
    return read_num_sum,each_date_day_list


def get_today_hot(content_type):
    today = timezone.now().date()
    read_detail=ReadDetail.objects.filter(content_type=content_type,date=today).order_by('-read_num')
    return  read_detail[:7]

def get_yesterday_hot(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    read_detail=ReadDetail.objects.filter(content_type=content_type,date=yesterday).order_by('-read_num')
    return  read_detail[:7]

def get_week_hot_blog():
    today=timezone.now().date()
    seven_days=today-datetime.timedelta(days=7)
    the_week_blogs=Blog.objects.filter(read_detail__date__lt=today,read_detail__date__gte=seven_days).\
        values('id','title').\
        annotate(read_num_sum=Sum('read_detail__read_num')).\
        order_by('-read_num_sum')
    return the_week_blogs[:7]
def get_hot_blog(content_type):
    hot_blogs=ReadNum.objects.filter(content_type=content_type).order_by('-read_num')
    # print(hot_blogs)
    return hot_blogs[:6]