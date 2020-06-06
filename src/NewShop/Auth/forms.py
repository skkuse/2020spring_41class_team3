from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core import validators
from django import forms
from Displayer.models import HUser

class SigninForm(forms.Form): #로그인을 제공하는 class이다.
    username = forms.CharField(label="사용자 이름", max_length=30)
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput())

    def clean(self):
        clean_data=super().clean()
        # This method will set the cleaned_data attribute
        username = clean_data.get('username')
        password = clean_data.get('password')

        if username and password:
            User = get_user_model()
            if not User.objects.filter(username=username).exists():
                self.add_error('username', "존재하지 않는 사용자입니다.")    
                
            else:
                user = User.objects.get(username=username)
                if not user.is_active:
                    self.add_error('username', '인증을 진행해 주세요.')
                if not check_password(password, user.password):
                    self.add_error('password','비밀번호가 틀렸습니다.')                
                    

        return self.cleaned_data


class SignupForm(forms.Form):

    email = forms.EmailField(required=True, label='e-mail', help_text="알림을 위한 이메일") 

    username = forms.RegexField(required=True, label="사용자 이름",max_length=30,
                                regex=r'^[\w.@+-]+$',
                                help_text="로그인에 사용되는 이름으로, 30개 이하의 숫자나 문자 그리고 @ . + - _ 만 입력하실 수 있습니다.",
                                validators=[
                                    validators.RegexValidator(r'^[\w.@+-]+$',
                                    '유효한 사용자 이름을 입력하세요.'),
                                    ],
                                error_messages={'unique': "이미 존재하는 사용자 이름입니다."},
                                )
    password1 = forms.CharField(required=True, label="비밀번호",
                                help_text="비밀번호를 입력해 주세요.",
                                widget=forms.PasswordInput())
    password2 = forms.CharField(required=True, label="비밀번호 확인",
                                help_text="비밀번호를 다시 한번 입력해 주세요.",
                                widget=forms.PasswordInput())                            
    field_order=['email','username','password1','password2']

    def clean(self):
        clean_data=super().clean()
        # This method will set the cleaned_data attribute
        email = clean_data.get('email')
        username = clean_data.get('username')
        password1 = clean_data.get('password1')
        password2 = clean_data.get('password2')
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            self.add_error('email', "이미 존재하는 이메일 입니다.")

        if User.objects.filter(username=username).exists():
            self.add_error('username', "이미 존재하는 이름입니다.")
        
        if not password1 == password2:
            self.add_error('password2', '비밀번호가 서로 일치하지 않습니다.')
        
        return self.cleaned_data

class IDFindForm(forms.Form):
    email = forms.EmailField(required=True, label='e-mail', help_text="가입할 때 인증에 사용한 이메일을 입력해 주세요.")
    
    def clean(self):
        clean_data=super().clean()
        email = clean_data.get('email')
        User = get_user_model()
        if User.objects.filter(email=email).exists():            
            you = User.objects.get(email=email)
            if you.is_active:
                self.add_error('email','이름은 '+you.username[0]+'으로 시작합니다. 기억이 잘 나지 않으신다면 이메일을 보냈으니 확인해 주세요.')
                you.handle.sendEmail("[newShop]이름 찾기","안녕하세요. 회원님이 newShop 로그인에 사용하시는 이름은 "+you.username+"입니다. 감사합니다.")
            else:
                self.add_error('email','이메일 인증을 하지 않은 계정입니다. 원하는 경우 로그인 페이지에서 이 계정을 지우고 다시 만들 수 있습니다.')
        else:
            self.add_error('email','해당하는 정보가 없습니다.')            

        return self.cleaned_data
