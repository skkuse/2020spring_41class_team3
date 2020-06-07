from django.contrib import admin
from .models import News, Product, NspProduct, SpProduct, History, Favor
# Register your models here.

admin.site.register(News)
admin.site.register(History)
admin.site.register(SpProduct)
admin.site.register(Product)
admin.site.register(NspProduct)
admin.site.register(Favor)