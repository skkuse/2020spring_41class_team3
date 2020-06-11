from .crawler import crawler
from .nlp_main import test_model
from Displayer.models import Price, Product
import datetime

# 주기적으로 수행되기 위한 함수. 현재 가격 축적->알림->뉴스 축적->알림
def run():
    today = datetime.date.today
    all_p=Product.objects.all()
    for p in all_p:
        crawler.update_market_price(p.name)
        p.sendPriceAlarm()
        lastdate = p.getNews().first().date
        if lastdate is None:
            lastdate='20200101'
        test_model([p.name], [lastdate,today], 4000, 'Displayer/news/best_model.pth')        
        p.sendNewsAlarm()        
