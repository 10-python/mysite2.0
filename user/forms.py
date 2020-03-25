from django import forms
from .models import Profile
from django.contrib import auth
from django.contrib.auth.models import User
class LoginForm(forms.Form):
    username_or_email=forms.CharField(label='用户名或邮箱',
                             widget=forms.TextInput(
                                 attrs={'class':'form-control','placeholder':'请输入用户名或邮箱'}))
    password=forms.CharField(label='密码',
                             widget=forms.PasswordInput(
                                 attrs={'class':'form-control','placeholder':'请输入密码'}))
    def clean(self):
        username_or_email=self.cleaned_data['username_or_email']
        password=self.cleaned_data['password']

        user = auth.authenticate( username=username_or_email, password=password)
        if user is  None: #email方式登录
            if User.objects.filter(email=username_or_email).exists():
                username=User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)#登录

                if not user is None:#用户登录
                    self.cleaned_data['user']=user
                    return self.cleaned_data
            # print(User.objects.filter(email=username_or_email))
            raise forms.ValidationError('用户名或密码不正确!')
        else:
            self.cleaned_data['user']=user
        return self.cleaned_data

class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名',
                               max_length=30,
                               min_length=3,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入3-30位的用户名','id':'register_username'}))



    password = forms.CharField(label='密码',
                               min_length=6,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入用户密码','id':'register_pwd'}))
    password_agin = forms.CharField(label='密码',
                               min_length=6,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入密码','id':'register_pwd_again'}))
    email = forms.EmailField(label='邮箱',
                            widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入用户邮箱','id':'register_email'}))
    code = forms.CharField(label='验证码',
                           required=False,
                           widget=forms.TextInput(
                               attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"到邮箱'})
                           )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(RegisterForm, self).__init__(*args, **kwargs)
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("用户名已存在")
        return username
    def clean_email(self):
        email = self.cleaned_data['email']
        # if re.match(r'^[0-9a-zA-Z\_\-]+(\.[0-9a-zA-Z\_\-]+)*@[0-9a-zA-Z]+(\.[0-9a-zA-Z]+){1,}$',email) is None:
        #     raise forms.ValidationError('邮箱不合法,请正确输入')
        # else:
        #     raise forms.ValidationError('邮箱合法')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("邮箱已注册")
        return email
    def clean_password_agin(self):
        password = self.cleaned_data['password']
        password_agin=self.cleaned_data['password_agin']
        if password!=password_agin:
            raise forms.ValidationError("两次输入的密码不一致")
        return password
    def clean_verification_code(self):
        verification_code=self.cleaned_data.get('code','').strip()
        if verification_code=='':
            raise forms.ValidationError("验证码不能为空")
        return verification_code
    def clean(self):
        # 判断验证码
        code=self.request.session.get('register_code','')#生成的四位验证码
        verifaction_code=self.cleaned_data.get('code','')#用户填写的验证码
        if not(code!=''and code==verifaction_code):
            raise forms.ValidationError("验证码不正确")
        return self.cleaned_data


class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(label='新的昵称',max_length=20,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', 'placeholder': '请输入新的昵称'}))
    def __init__(self,*args,**kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangeNicknameForm,self).__init__(*args,**kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user']=self.user
        else:
            raise forms.ValidationError('用户未登录')
        return self.cleaned_data
    def clean_nickname_new(self):
        nickname_new=self.cleaned_data.get('nickname_new','').strip()
        if nickname_new == "":
            raise forms.ValidationError("新的昵称不能为空")
        return nickname_new

class BindEmailForm(forms.Form):
    email=forms.EmailField(
        label='邮箱',
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}))

    code=forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"到邮箱'})
    )
    def clean_verification_code(self):
        verification_code=self.cleaned_data.get('code','').strip()
        if verification_code=='':
            raise forms.ValidationError("验证码不能为空")
        return verification_code

    def __init__(self,*args,**kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm,self).__init__(*args,**kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user']=self.request.user
        else:
            raise forms.ValidationError('用户未登录')
        # 判断用户是否已经绑定邮箱
        if self.request.user.email !='':
            raise forms.ValidationError('您已经绑定邮箱')
        # 判断验证码
        code=self.request.session.get('bind_email_code','')#生成的四位验证码
        verifaction_code=self.cleaned_data.get('code','')#用户填写的验证码
        if verifaction_code=='':
            raise forms.ValidationError('验证码不能为空')
        if not(code==verifaction_code):
            raise forms.ValidationError("验证码不正确")
        email = self.cleaned_data.get('email','')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("该邮箱已经绑定")
        return self.cleaned_data

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='旧密码',
                               min_length=6,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入旧的密码'}))

    new_password = forms.CharField(label='新密码',
                               min_length=6,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入新密码'}))
    new_password_agin = forms.CharField(label='新密码',
                                min_length=6,
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入新密码'}))

    def __init__(self,*args,**kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangePasswordForm,self).__init__(*args,**kwargs)
    def clean(self):
        # 验证两次新密码是否输入一致
        new_password=self.cleaned_data.get('new_password','')
        new_password_agin=self.cleaned_data.get('new_password_agin','')
        if new_password==new_password_agin and new_password!='':
            return self.cleaned_data
        else:
            raise forms.ValidationError("两次输入新密码不一致")

    def clean_old_password(self):
        old_password=self.cleaned_data.get('old_password','')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('旧的密码错误')
        return old_password

class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': '请输入邮箱','id':'id_forget_email'}))

    code = forms.CharField(
                    label='验证码',
                    required=False,
                    widget=forms.TextInput(
                        attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"到邮箱','id':'id_forget_code'})
                        )
    new_password = forms.CharField(label='新密码',
                                        min_length=8,
                                        widget=forms.PasswordInput(
                                            attrs={'class': 'form-control', 'placeholder': '请再次输入新密码','id':'id_forget_new_password'}))
    def __init__(self,*args,**kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ForgetPasswordForm,self).__init__(*args,**kwargs)
    def clean_email(self):
        email=self.cleaned_data.get('email').strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("邮箱不存在")
        return email
    def clean_verification_code(self):
        verification_code=self.cleaned_data.get('code','').strip()
        if verification_code=='':
            raise forms.ValidationError("验证码不能为空")
        # 判断验证码
        code = self.request.session.get('forget_password_code','') # 生成的四位验证码
        verifaction_code = self.cleaned_data.get('code', '')  # 用户填写的验证码
        if not (code != '' and code == verifaction_code):
            raise forms.ValidationError("验证码不正确")
        return verification_code

class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=('nickname','avatar')
        labels={
            'nickname':'昵称:',
            'avatar':'头像:',
        }
