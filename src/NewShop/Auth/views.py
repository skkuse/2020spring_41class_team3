from django.shortcuts import render, redirect
from django.contrib import auth
from Displayer.models import HUser
from .forms import SigninForm
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
    pass

def verify(request):
    pass

def sign_out(request):
    auth.logout(request)    
    return redirect('home')