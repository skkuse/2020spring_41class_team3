from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.decorators import login_required

# Create your views here.
def redir(request):
    return redirect('home',)

def home(request):    
    return render(request, 'Displayer/home.html',{'logged':request.user.is_authenticated})
    # request는 GET/POST 메소드의 모든 정보를 담고 있음. render를 통해 html파일과 연결. templates/Displayer/home.html로 이동

def product(request):
    return render(request, 'Displayer/product.html',{'logged':request.user.is_authenticated})

def api(request):
    return render(request, 'Displayer/api.html',{'logged':request.user.is_authenticated})

@login_required(login_url='login/')
def myPage(request):
    return render(request, 'Displayer/myPage.html',{'logged':request.user.is_authenticated})