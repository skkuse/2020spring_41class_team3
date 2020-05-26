from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import auth
from Displayer.models import HUser
from .forms import SigninForm, SignupForm

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
# Create your views here.

def sign_in(request):
    if request.method == "GET":
        return render(request, 'Auth/signin.html', {'form':SigninForm()} )

    elif request.method == "POST":
        form = SigninForm(request.POST)
        username = request.POST["username"]
        password = request.POST["password"]
        if form.is_valid():
            user = auth.authenticate(request, username=username, password=password)
            auth.login(request, user)

            return redirect('home') #홈페이지로 이동

        return render(request, "Auth/signin.html", {"form": form})
    else:
        return render(request, 'Auth/signin.html',{'form':SigninForm()})

def sign_up(request):
    if request.method == "GET":
        return render(request, 'Auth/signup.html',{'form':SignupForm()})
    elif request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            User = auth.get_user_model()
            user = User.objects.create_user(form.cleaned_data['username'],form.cleaned_data['email'],form.cleaned_data['password1'])
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['username']
            user.is_active = False
            user.save()
            
            hd = HUser(name=user.username, user=user)
            hd.save()
            current_site = get_current_site(request)
            # localhost:8000

            message = render_to_string('Auth/ver_email.html',{
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).encode().decode(),
                'token': account_activation_token.make_token(user),
            })            

            mail_subject = "[newShop] 회원가입 인증 메일."
            email = EmailMessage(
                subject=mail_subject, 
                body=message, 
                to=[user.email],
                )
            email.send()
            return redirect(reverse("verification"))

        return render(request, "Auth/signup.html", {"form": form})

def verify(request):
    return render(request, "Auth/verifyinfo.html")

def sign_out(request):
    auth.logout(request)    
    return redirect('home')

def activate(request, uidb64, token):
    uid = force_text(urlsafe_base64_decode(uidb64))
    User = auth.get_user_model()
    user = User.objects.get(pk=uid)

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth.login(request, user)
        return render(request, 'Auth/signupend.html')
    else:
        return HttpResponse('비정상적인 접근입니다.')