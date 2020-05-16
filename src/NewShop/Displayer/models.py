from django.db import models
from django.conf import settings
# Create your models here.
'''
Django에서 쿼리는 전용 함수로 감싸져 있습니다.
클래스.objects.all().filter(클래스 속성 조건).order_by(속성, 오름/내림차순) 
이렇게 하면 접근되는 거고(필터 정렬은 비필수)
객체 생성해서 객체.save()하면 DB에 저장되는 식이에요
'''
class HUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='handle')
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=13,null=True)
    favor_id = models.IntegerField(null=True)
    profile = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=None, null=True)
    permit = models.BooleanField(default=False)

    def __str__(self):
        return self.name        
    

class History(models.Model):
    #pk는 전체를 기준으로, 생성 순으로 부여되니 정렬 id는 따로 부여하지 않겠음
    user = models.ForeignKey("HUser", related_name='history', on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)

class Favor(models.Model):
    user = models.ForeignKey("HUser", related_name='history', on_delete=models.CASCADE)
    product = models.ForeignKey("Product",on_delete=models.CASCADE)

class Alarm(models.Model):
    user = models.ForeignKey("HUser", related_name='alarm', on_delete=models.CASCADE)
    product = models.ForeignKey("Product", related_name='alarm',on_delete=models.CASCADE)
    lower = models.IntegerField(default=0)
    reuse = models.BooleanField()
    method = models.IntegerField() #비트로 다룸 : ex) 2^0자리 이메일, 2^1자리 문자
    upper = models.IntegerField()

class Product(models.Model):
    name = models.CharField(max_length=100)

class News(models.Model):
    product = models.ForeignKey("Product", related_name='news', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=200)

class Price(models.Model):
    product = models.ForeignKey("Product",related_name='price', on_delete=models.CASCADE)
    value = models.IntegerField()
    date = models.DateField()