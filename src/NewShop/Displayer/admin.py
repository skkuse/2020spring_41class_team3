from django.contrib import admin
from .models import News, Product, NspProduct, SpProduct, History, Favor, Price, Report, Alarm, HUser, WordCloudImg
# Register your models here.

admin.site.register(News)
admin.site.register(HUser)
admin.site.register(Favor)
admin.site.register(Price)
admin.site.register(Report)
admin.site.register(Alarm)
admin.site.register(WordCloudImg)
admin.site.register(NspProduct)