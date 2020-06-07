from django.http import Http404
from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib.auth.decorators import login_required
from .news.crawler import crawler
import random
import urllib.parse
from make_dummy_db import make_dummy_db

# Create your views here.
def redir(request):
    return redirect('home',)

def home(request):
    make_dummy_db()
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

def download_file(request):
    filename = request.GET.get('filepath')
    filename = urllib.parse.unquote(filename)
    file_url = SpProduct.objects.filter(name=filename)[0].getPriceByTable()
    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment;filename="downloads.xlsx"'
            return response
    raise Http404

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

@login_required
def hpChange(request):
    if request.method=='GET':       
        return render(request, 'Displayer/hpChange.html', {})
    elif request.method=='POST':
        if request.POST.get('np') is not None:
            msg=''
            msg+=str(random.randint(0,9))
            msg+=str(random.randint(0,9))
            msg+=str(random.randint(0,9))
            msg+=str(random.randint(0,9))
            if PhoneKey.objects.filter(user=request.user.handle):
                PhoneKey.objects.filter(user=request.user.handle).delete()
            PhoneKey(value=int(msg), user=request.user.handle, new_p=request.POST.get('np')).save()
            user = HUser(user=request.user,phone=request.POST.get('np'),permit=True) # 이건 더미임. 저장하면 안됨
            user.sendSMS('[newShop]인증 번호를 입력해 주세요.\n'+msg)
            return render(request, 'Displayer/hpAuth.html')
        elif request.POST.get('key') is not None:
            k = request.POST.get('key')
            hu=request.user.handle
            if hu.phoneAuth(k):
                return redirect('mypage')
            else:
                return render(request, 'Displayer/hpAuth.html', {'err':'인증 번호가 맞지 않습니다.'})
        else:
            return HttpResponse("알 수 없는 오류가 발생했습니다.")
