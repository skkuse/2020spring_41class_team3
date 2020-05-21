from django.shortcuts import render, redirect
from .models import *

# Create your views here.
def redir(request):
    return redirect('home',)

def home(request):
    return render(request, 'Displayer/home.html',{'menu':'home','key':'value'})
    # request는 GET/POST 메소드의 모든 정보를 담고 있음. render를 통해 html파일과 연결. templates/Displayer/home.html로 이동

def product(request):
    return render(request, 'Displayer/product.html',{'menu':'product',})

def api(request):
    return render(request, 'Displayer/api.html',{'menu':'api',})

def myPage(request):
    return render(request, 'Displayer/myPage.html',{'menu':'mypage',})