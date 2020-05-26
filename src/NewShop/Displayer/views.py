from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.decorators import login_required

# Create your views here.
def redir(request):
    return redirect('home',)

def home(request):    
    logged=request.user.is_authenticated
    return render(request, 'Displayer/home.html',{'logged':logged})
    # request는 GET/POST 메소드의 모든 정보를 담고 있음. render를 통해 html파일과 연결.

def product(request):
    logged=request.user.is_authenticated
    return render(request, 'Displayer/product.html',{'logged':logged})    

def api(request):
    logged=request.user.is_authenticated
    return render(request, 'Displayer/api.html',{'logged':logged})

@login_required(login_url='login/')
def myPage(request):
    logged=request.user.is_authenticated    
    return render(request, 'Displayer/myPage.html',{'logged':logged, 'user':request.user})