import requests
from bs4 import BeautifulSoup
import re
import copy
import time
from Displayer.news.MarketPrice import markets
from Displayer.models import News, Price, SpProduct
from urllib import parse

def make_news_url(search_word: str, start_date: str, end_date: str):
    """
    make self.url using search word, start_date, end_date
    :param search_word: the word that user want to search
    :param start_date: search condition. start date
    :param end_date: search condition. end date
    :return: None
    """
    base_url = 'https://search.naver.com/search.naver?where=news'
    search_word = 'query={}'.format(search_word)
    start_date = 'ds={}.{}.{}'.format(start_date[:4], start_date[4:6], start_date[6:])
    end_date = 'de={}.{}.{}'.format(end_date[:4], end_date[4:6], end_date[6:])
    query_list = [base_url, search_word, start_date, end_date]
    url = '&'.join(query_list)
    return url

class Crawler(object):
    def __init__(self, verbose=0):
        self.verbose = verbose

    def get_news_link(self, url):
        """
        get news_link list using url
        :param url:
        :return: html string
        """
        req = requests.get(url)
        if self.verbose:
            print("Crawling url is ", url)

        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        ret_str = soup.select('ul.type01 > li > dl > dd > a')
        news_list = []
        for get_str in ret_str:
            news_list.append(get_str['href'])
        return news_list

    def get_news_contents(self, url):
        """
        make usable data
        :param url: news site url
        :return: data
        """
        req = requests.get(url)
        if self.verbose:
            print("Crawling url is ", url)

        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        try:
            ret_str = str(soup.select('#articleBodyContents')[0])
        except:
            if self.verbose:
                print("엔터테인먼트 뉴스입니다. 아직 구현 안됨.")

        cutting = re.compile('<[^(<|>)]*>')
        cutting_list = cutting.findall(ret_str)
        for cutting_str in cutting_list:
            ret_str = ret_str.replace(cutting_str, '', 1)
        ret_str = ret_str.replace('// flash 오류를 우회하기 위한 함수 추가', '')
        ret_str = ret_str.replace('function _flash_removeCallback() {}', '')
        ret_str = ret_str.replace('\n', '', 100)
        return ret_str

    def get_market_price(self, key_word):
        ret = []
        key = key_word.split()
        for market in markets:
            get_data = market.get_data(key_word)
            for element in get_data:
                check = 1
                for keyword in key:
                    if keyword not in element['name']:
                        check = 0
                        break
                if check == 1:
                    ret.append(element)
        return ret

    def save_price(self, product_name, price):
        product = SpProduct.objects.filter(name=product_name)
        Price.objects.create(product=product, value=price, date=time.time())

if __name__ == '__main__':
    crawler = Crawler()
    print(crawler.get_market_price('삼성전자 DDR4 8G PC4-21300'))

    # url = make_news_url('검색', '20200320', '20200511')
    # print(crawler.get_news_link(url))
    # news = crawler.get_news_link(url)
    # del news[2]
    # for news_url in news:
    #     print(crawler.get_news_contents(news_url))