from django.db import models
from django.conf import settings
from NewShop import local_settings
from django.core.mail import EmailMessage
import requests
import abc
import time
import sys, os, hashlib, hmac, base64
# Create your models here.

class HUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='handle')
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=13,null=True)
    interest = models.CharField(max_length=50,null=True)
    # profile = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=None, null=True)
    permit = models.BooleanField(default=False) #역할 변경 : 핸드폰 인증 여부
    alarmMethod = models.IntegerField(default=0) #비트로 다룸 : ex) 2^0자리 이메일, 2^1자리 문자

    #멤버함수 추가 예정
    '''
    DB를 건드리는 기능 : 회원가입, 로그인, 즐겨찾기 저장/삭제, 검색(가격 표시), 마이페이지 이미지/이름/알람 수단 변경, 알람 설정
    '''
    def sendEmail(self, title, content):
        email = EmailMessage(
            subject=title, 
            body=content, 
            to=[self.user.email],
            )
        email.send()

    def sendSMS(self, content):
        url='https://sens.apigw.ntruss.com'
        uri='/sms/v2/services/'+local_settings.svc_id+'/messages'
        data = {
            "type": "SMS",
            "from": local_settings.hp,  
            # 이 부분은 저의 전화번호가 넷상에 남게 되는 실수가 있을 수 있기 때문에 sendSMS()는 로컬 테스트 금지입니다. 
            # 만약 다른 기능 테스트 중 이 함수에서 인터프리터 오류가 발생한다면, local_settings에서 끌어온 것들은 빈 문자열로 수정하여 테스트해주시기 바랍니다.
            "messages":[{"to": self.phone}],
            "content": content
        }
        access_key=local_settings.access_key
        secret_key=bytes(local_settings.secret_key,'UTF-8')
        stamp=str(int(time.time()*1000))
        msg = "POST "+uri+"\n"+stamp+"\n"+access_key
        msg=bytes(msg,'UTF-8')
        sv2=base64.b64encode(hmac.new(secret_key,msg,digestmod=hashlib.sha256).digest())
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "x-ncp-iam-access-key": access_key,
            "x-ncp-apigw-signature-v2":sv2,
            "x-ncp-apigw-timestamp": stamp
        }
        res=requests.post(url+uri, json=data, headers=headers)
        res.raise_for_status()
        

    def __str__(self):
        return self.name
    

class History(models.Model):
    #pk는 전체를 기준으로, 생성 순으로 부여되니 정렬 id는 따로 부여하지 않겠음
    user = models.ForeignKey("HUser", related_name='history', on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)

class Favor(models.Model):
    user = models.ForeignKey("HUser", related_name='favor', on_delete=models.CASCADE)
    product = models.ForeignKey("Product",on_delete=models.CASCADE)

class Alarm(models.Model):
    user = models.ForeignKey("HUser", related_name='alarm', on_delete=models.CASCADE)
    product = models.ForeignKey("Product", related_name='alarm',on_delete=models.CASCADE)
    lower = models.IntegerField(default=0)
    reuse = models.BooleanField()
    news_alarm = models.BooleanField()
    upper = models.IntegerField()

class Product(models.Model):    #상표 없는 것과 있는 것의 공통 규약을 위한 추상 클래스
    name = models.CharField(max_length=100)
    @abc.abstractmethod
    def getNews(self):
        pass
    @abc.abstractmethod
    def getPrice(self):
        pass
    @abc.abstractmethod
    def getInfluence(self):
        pass
    def sendAlarm(self):
        alarms=self.alarm.all()
        for a in alarms:    #getPrice로 방금 넣은 것과 비교, 타임으로 내림차순 sort해서 [0] 고르면 됨
            pass
        pass

class NspProduct(Product): #상표 무관 product 키워드를 말함
    field = models.CharField(max_length=50,null=True)
    influence = models.CharField(max_length=100,null=True)
    def getNews(self):
        return self.news.all()
    def getPrice(self):
        b = self.brand.all()
    def getInfluence(self):
        return self.influence
        

class SpProduct(Product):  #상표가 있는 specific product 키워드를 말함.
    product=models.ForeignKey("NspProduct",related_name='brand',on_delete=models.CASCADE)
    def getNews(self):
        return self.product.getNews()
    def getPrice(self):
        return self.price.all()
    def getInfluence(self):
        return self.product.getInfluence()

class News(models.Model):
    product = models.ForeignKey("NspProduct", related_name='news', on_delete=models.CASCADE)
    date=models.DateField()
    title = models.CharField(max_length=200)
    subj = models.IntegerField()
    url = models.URLField(max_length=200)

class Price(models.Model):
    product = models.ForeignKey("SpProduct",related_name='price', on_delete=models.CASCADE)
    value = models.IntegerField()
    date = models.DateField()

