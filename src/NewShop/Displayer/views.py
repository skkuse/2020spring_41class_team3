from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from .news.crawler import crawler
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password

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
    market_list = crawler.get_market_real_time('삼성 메모리 DDR4 8G PC4-21300')
    return render(request, 'Displayer/product.html',{'logged':logged, 'market_list': market_list})
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

def change_pw(request):
    logged=request.user.is_authenticated
    context= {}
    if request.method == "POST":
        current_password = request.POST.get("origin_password")
        user = request.user
        if user.is_anonymous:
            return render(request, "Displayer/home.html",{'logged':logged})
        if check_password(current_password,user.password):
            new_password = request.POST.get("password1")
            password_confirm = request.POST.get("password2")
            if new_password == password_confirm:
                user.set_password(new_password)
                user.save()
                return render(request, 'Displayer/home.html',{'logged':logged})
            else:
                context.update({'error':"새로운 비밀번호를 다시 확인해주세요."})
    else:
        context.update({'error':"현재 비밀번호가 일치하지 않습니다."})

    return render(request, "Displayer/change_pw.html",{'logged':logged, 'user':request.user})