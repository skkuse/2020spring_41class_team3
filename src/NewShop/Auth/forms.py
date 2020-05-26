from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core import validators
from django import forms

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
                if not check_password(password, user.password):
                    self.add_error('password','비밀번호가 틀렸습니다.')
                    

        return self.cleaned_data
