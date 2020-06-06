from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import auth
from Displayer.models import HUser
from .forms import SigninForm, SignupForm, IDFindForm, PWFindForm, ResetForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
# Create your views here.

# qu: 로그인 next 쿼리.
qu=''

def sign_in(request):
    global qu
    if request.method == "GET":
        qu=request.GET.get('next')
        return render(request, 'Auth/signin.html', {'form':SigninForm()} )

    elif request.method == "POST":
        form = SigninForm(request.POST)
        username = request.POST["username"]
        password = request.POST["password"]
        if form.is_valid():
            user = auth.authenticate(request, username=username, password=password)
            auth.login(request, user)
            if qu:      
                return redirect(qu) #홈페이지로 이동
            else:
                return redirect('home')

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
            
            hd = HUser(user=user)
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
            hd.sendEmail(mail_subject, message)
            return redirect('verification')

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

def id_finder(request):
    if request.method == "GET":
        return render(request, 'Auth/idFinder.html',{'form':IDFindForm()})
    elif request.method == "POST":
        form=IDFindForm(request.POST)
        return render(request, "Auth/idFinder.html", {"form": form})

def pw_finder(request):
    if request.method == "GET":        
        return render(request, 'Auth/pwFinder.html',{'form':PWFindForm(initial={'domain':get_current_site(request).domain})})
    elif request.method == "POST":
        form=PWFindForm(request.POST)
        return render(request, "Auth/pwFinder.html", {"form": form})
    else:
        return render(request, "Auth/pwFinder.html", {"form": form})

def pw_reset_by_mail(request, uidb64, token):
    uid = force_text(urlsafe_base64_decode(uidb64))
    User = auth.get_user_model()
    user = User.objects.get(pk=uid)
    if user is not None:
        auth.login(request, user)
        return redirect('pw_reset2',usr=user.pk)
    else:
        return HttpResponse('비정상적인 접근입니다.')

def pw_reset(request, usr):
    if request.user.pk == usr:
        if request.method=='GET':
            return render(request, "Auth/pwset.html",{'form':ResetForm(),'usr':usr})
        elif request.method=='POST':
            form=ResetForm(request.POST)
            if form.is_valid():
                newpw=form.cleaned_data['password1']
                user = auth.get_user_model().objects.get(pk=usr)
                user.set_password(newpw)
                user.save()
                return redirect('home',{})
            else:
                return render(request, "Auth/pwset.html",{'form':form})
        else:
            return render(request, "Auth/pwset.html",{'form':ResetForm()})
    else:
        return HttpResponse('비정상적인 접근입니다.')

def pw_reset2(request):
    if request.method=='POST':
        pid=request.user.pk
        form=ResetForm(request.POST)
        if form.is_valid():
            newpw=form.cleaned_data['password1']
            user = auth.get_user_model().objects.get(pk=pid)
            user.set_password(newpw)
            user.save()
            auth.logout(request)
            messages.info(request,'비밀번호가 변경되었습니다. 새로운 비밀번호로 다시 로그인해주세요.')
            return redirect('home')
        else:
            return render(request,"Auth/pwset.html",{'form':form})
    else:
        return HttpResponse('비정상적인 접근입니다.')
