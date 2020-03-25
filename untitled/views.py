from django.shortcuts import render
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# 关于我们
def test(request):
    pass
    return render(request,'information.html')
@csrf_exempt
def contact(request):
    name=request.POST.get('name','')
    email=request.POST.get('email','')
    content=request.POST.get('content','')
    data={}
    if email!='':
        try:
            send_mail(
                '博客有消息啦!',  # 邮件主题
                '用户:%s(%s):%s'% (name,email,content),  # 内容
                ['1765300685@qq.com '],  # from
               ['1765300685@qq.com '],#to
                fail_silently=False,
            )
            data['status'] = "SUCCESS"
        except Exception as e:
            print(e)
            data['status'] = "发送失败"
    else:
        data['status']='请输入正确的邮箱格式!'

    return JsonResponse(data)
def information(request):
    return render(request,'information.html')