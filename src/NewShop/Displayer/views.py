from django.shortcuts import render, redirect, HttpResponse
from .models import *
from .forms import ReportForm
from Displayer.news.nlp_main import get_recommend_query
from django.contrib.auth.decorators import login_required
from .news.crawler import crawler
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.core import serializers
from django.http import Http404
import random
import datetime
import urllib.parse

news_category=['가격', '신제품', '프로모션', '동향']

# Create your views here.
def redir(request):
    return redirect('home',)

def toHome(request):
    messages.info(request, '검색창에 검색어를 입력하여 시작합니다.')
    return redirect('home',)

def home(request):
    usr=request.user
    logged=usr.is_authenticated
    hist=None
    bookmarks=None
    prod = None
    newz=None
    if logged:
        bookmarks=usr.handle.favor.all()
        hist = usr.handle.history.order_by('-pk')
        if hist.count()>0:
            prod=hist[0].product
        newz=News.objects.none()
        for mark in bookmarks:
            newz |= mark.product.getNews()
        if newz.count()>0:
            newz.order_by('-date')
    return render(request, 'Displayer/home.html',{'logged':logged, 'bookmarks':bookmarks, 'news':newz, 'user':usr, 'history':hist,'product':prod,'theme':news_category})
    # request는 GET/POST 메소드의 모든 정보를 담고 있음. render를 통해 html파일과 연결.

def q2key(request):
    # 검색 기록이 없는 상태에서 검색어 입력 시 반드시 이곳으로 옴.
    logged=request.user.is_authenticated
    if request.method=='POST':        
        related = get_recommend_query(request.POST.get('query'))
        return render(request, 'Displayer/related.html',{'logged':logged, 'related': related})
    else:
        return HttpResponse('Not Found')

def search(request, keyword):
    logged=request.user.is_authenticated
    market_list=[]
    market_list = crawler.get_market_real_time(keyword)    
    prod=Product.objects.get(name=keyword)
    price=prod.getPrice()
    pr_dates=[]
    pr_values=[]
    avg=0
    count=0
    low=99999999999
    nnewz=prod.getNews()
    booked=False
    alarmed = False
    ap=request.build_absolute_uri('/').strip("/")
    cl = prod.getInfluence()    

    if cl is not None:
        cloud_path = ap+prod.getInfluence().img.url
    else:
        cloud_path = None
        
    if logged:
        History.objects.filter(user=request.user.handle,product=prod).delete()
        History(user=request.user.handle, product=prod).save()
        if Favor.objects.filter(user=request.user.handle, product=prod).count()>0:
            booked=True
        if Alarm.objects.filter(user=request.user.handle, product=prod).count()>0:
            alarmed=True
 
    for dv in price.values('date','value'):
        pr_dates.append(str(dv['date']))
        pr_values.append(dv['value'])
    for market in market_list:
        avg+=market['price']
        if low>market['price']:
            low=market['price']            
        count+=1
    if avg!=0:
        avg/=count

    scan_start=0
    news_hover = []
    for pr_date in pr_dates:
        pr_date = datetime.datetime.strptime(pr_date, '%Y-%m-%d')
        newslen = len(nnewz)
        i=scan_start
        while i < newslen:
            news_date = datetime.datetime.strptime(nnewz[i].date, '%Y-%m-%d')
            if(pr_date < news_date):
                break
            i+=1
        if i>=1 and i <= newslen:
            news_hover.append(nnewz[i-1].title+", ("+nnewz[i-1].date+")")
        else:
            news_hover.append("Not found")
        scan_start = i
    # 검색어 입력/즐겨찾기 등.. 알림 설정은 팝업을 생각 중
    return render(request, 'Displayer/product.html',{'logged':logged, 'market_list':market_list, 'pr_dt':pr_dates,'pr_vl':pr_values, 'booked':booked, 'news':nnewz,'news_hover':news_hover, 'product':prod,'average':avg, 'low':low,'alarmed':alarmed,'theme':news_category, 'cloud':cloud_path})
    # 현재의 html을 사용할 것

def api_search(request, keyword):
    logged=request.user.is_authenticated
    prod=Product.objects.get(name=keyword)
    pr_dates=[]
    pr_values=[]
    price=prod.getPrice()
    ap=request.build_absolute_uri('/').strip("/")
    for dv in price.values('date','value'):
        pr_dates.append(str(dv['date']))
        pr_values.append(dv['value'])
    return render(request, 'Displayer/api.html',{'logged':logged,'product':prod, 'price':price, 'pr_dt':pr_dates, 'pr_vl':pr_values, 'apiurl':ap})
    # 현재의 html을 사용할 것

@login_required
def toggleBook(request, keyword):
    prod=Product.objects.get(name=keyword)
    if Favor.objects.filter(user=request.user.handle,product=prod).count()>0:
        Favor.objects.get(user=request.user.handle,product=prod).delete()
    else:
        Favor(user=request.user.handle,product=prod).save()
    return redirect('search',keyword=keyword)

def api_xlsx(request, keyword):
    filename = keyword
    Product.objects.get(name=keyword).getPriceByTable()
    try:
        filename = urllib.parse.unquote(filename)
        file_url = SpProduct.objects.filter(name=filename)[0].getPriceByTable()
        if os.path.exists(file_url):
            with open(file_url, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type='application/vnd.ms-excel')
                return response
    except:
        raise Http404

def api_json(request, keyword):
    filename = keyword
    try:
        filename = urllib.parse.unquote(filename)
        query = SpProduct.objects.filter(name=filename)[0].getPrice()
        query_list = serializers.serialize('json', query)
        return HttpResponse(query_list, content_type="text/json-comment-filtered")
    except:
        raise Http404


@login_required
def delBook(request, keyword, next):
    prod=Product.objects.get(name=keyword)
    Favor.objects.get(user=request.user.handle,product=prod).delete()
    return redirect(next)

@login_required
def delHist(request, keyword):
    prod=Product.objects.get(name=keyword)
    History.objects.get(user=request.user.handle,product=prod).delete()
    return redirect('home')

@login_required
def alarm_set(request, keyword):
    logged=request.user.is_authenticated
    product = Product.objects.get(name=keyword)
    yours=None
    if Alarm.objects.filter(user=request.user.handle,product=product).count()>0:
        yours=Alarm.objects.get(user=request.user.handle,product=product)
    context = ""
    if request.method == "POST":
        upper = request.POST.get("upper")
        lower = request.POST.get("lower")
        news_alarm = request.POST.get("news_alarm",False)
        if news_alarm == "on":
            news_alarm=True
        if upper == "":
            upper=100000000
        if lower == "":
            lower=0
        if lower > 0 or news_alarm:
            if Alarm.objects.filter(user=request.user.handle,product=product).count()>0:
                Alarm.objects.filter(user=request.user.handle,product=product).delete()
            Alarm(user=request.user.handle,product=product,lower=int(lower),upper=int(upper),reuse=True,news_alarm=news_alarm).save()
        return HttpResponse('<script type="text/javascript">window.close();window.opener.location.reload();</script>') 
    return render(request, "Displayer/alarmSet.html",{'logged':logged, 'user':request.user, 'keyword':keyword,'context':context, 'Alarm':yours})
    
@login_required
def alarmDelete(request, keyword):
    logged=request.user.is_authenticated
    prod=Product.objects.get(name=keyword)
    if Alarm.objects.filter(user=request.user.handle,product=prod).count()>0:
        Alarm.objects.filter(user=request.user.handle,product=prod).delete()
    return HttpResponse('<script type="text/javascript">window.close();window.opener.location.reload();</script>')
    

@login_required
def myPage(request):
    usr=request.user
    logged=usr.is_authenticated
    alarms=usr.handle.alarm.all()
    prod=None
    hs = usr.handle.history.order_by('-pk')
    if hs.count()>0:
        prod=hs[0].product
    bookmarks=None
    if logged:
        bookmarks=usr.handle.favor.all()
    return render(request, 'Displayer/myPage.html',{'logged':logged, 'user':request.user,'bookmarks':bookmarks, 'product':prod, 'alarms':alarms})

@login_required
def change_pw(request):
    logged=request.user.is_authenticated
    context= {}
    if request.method == "POST":
        current_password = request.POST.get("origin_password")
        user = request.user
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


def report(request):
    if request.method=='GET':
        return render(request, 'Displayer/report.html',{'form':ReportForm()})
    elif request.method=='POST':
        rep = ReportForm(request.POST)
        if rep.is_valid():
            Report(subj=rep.cleaned_data['title'],content=rep.cleaned_data['content']).save()
            messages.info(request,'제보가 완료되었습니다.')
            return redirect('home')

@login_required
def setMethod(request, delta):
    user=request.user.handle
    if delta == 1:
        if user.alarmMethod % 2 == 1:
            user.alarmMethod-=1
        else:
            user.alarmMethod+=1
    elif delta == 2:
        if user.alarmMethod >= 2:
            user.alarmMethod-=2
        else:
            user.alarmMethod+=2
    else:
        return Http404
    user.save()
    return redirect('mypage')
