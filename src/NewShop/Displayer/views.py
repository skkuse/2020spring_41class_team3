from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.decorators import login_required
# from .news.crawler import *

# Create your views here.
def redir(request):
    return redirect('home',)

def home(request):    
    logged=request.user.is_authenticated
    return render(request, 'Displayer/home.html',{'logged':logged})
    # request는 GET/POST 메소드의 모든 정보를 담고 있음. render를 통해 html파일과 연결.

def product(request):
    #아마 검색창만 띄우게 될 듯?
    logged=request.user.is_authenticated
    return render(request, 'Displayer/product.html',{'logged':logged})
    # 현재와 다른 html을 사용할 것

def search(request, keyword):
    logged=request.user.is_authenticated
    if request.method=='GET':
        pass
    elif request.method=='POST':
        # 검색어 입력/즐겨찾기 등.. 알림 설정은 팝업을 생각 중
        pass
    return render(request, 'Displayer/product.html',{'logged':logged})
    # 현재의 html을 사용할 것


def api(request):
    logged=request.user.is_authenticated
    return render(request, 'Displayer/api.html',{'logged':logged})

def api_search(request, keyword):
    logged=request.user.is_authenticated
    if request.method=='GET':
        pass
    elif request.method=='POST':
        # 검색어 입력/즐겨찾기 등.. 알림 설정은 팝업을 생각 중
        pass
    return render(request, 'Displayer/api.html',{'logged':logged})
    # 현재의 html을 사용할 것

@login_required
def myPage(request):
    logged=request.user.is_authenticated
    return render(request, 'Displayer/myPage.html',{'logged':logged, 'user':request.user})