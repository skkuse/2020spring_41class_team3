from Displayer.news.crawler import crawler
from Displayer.news.nlp_main import test_model
from Displayer.models import Price, SpProduct, NspProduct, Product
import datetime

# 주기적으로 수행되기 위한 함수. 현재 가격 축적->알림->뉴스 축적->알림
def run():
    today = datetime.date.today().isoformat() 
    all_p=Product.objects.all()
    all_sp=SpProduct.objects.all()
    all_nsp=NspProduct.objects.all()
    for sp in all_sp:
        crawler.update_market_price(sp.name)
    for nsp in all_nsp:
        lastdate = nsp.getNews().first().date.isoformat()
        if lastdate is None:
            lastdate='20200601'
        test_model([nsp.name], [lastdate,today], 50, 'Displayer/news/best_model.pth')
    for p in all_p:
        p.sendNewsAlarm()
        p.sendPriceAlarm()

