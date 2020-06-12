import requests
from bs4 import BeautifulSoup
import re
from datetime import date as DATE
from datetime import datetime
from Displayer.news.MarketPrice import markets
from Displayer.models import Price, SpProduct

def make_news_url(search_word: str, start_date: str, end_date: str, length: int):
    """
    make self.url using search word, start_date, end_date
    :param search_word: the word that user want to search
    :param start_date: search condition. start date
    :param end_date: search condition. end date
    :param length: search condition. for pagination
    :return: None
    """
    base_url = 'https://search.naver.com/search.naver?where=news'
    search_word = 'query={}'.format(search_word)
    date = 'nso=so%3Ar%2Cp%3Afrom{}to{}%2Ca%3Aall'.format(start_date, end_date)
    start = ['start=1']
    for i in range(length//10):
        start.append(f'start={i+1}1')
    url_all = []
    for i in range(len(start)):
        query_list = [base_url, search_word, date, start[i]]
        url = '&'.join(query_list)
        url_all.append(url)
    return url_all

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

    def get_news_title_date(self, url):
        req = requests.get(url)
        if self.verbose:
            print("Crawling url is ", url)

        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        try:
            title = str(soup.select('#articleTitle'))
            date = str(soup.find_all('span', {'class': 't11'})[0])
        except:
            return '', ''

        title = str(re.sub('<[^(<|>)]*>', '', title))
        date = str(re.sub('<[^(<|>)]*>', '', date))

        return title, date

    def get_news_contents(self, url):
        """
        make usable data
        :param url: news site url
        :return: news contents split by sentence
        """
        req = requests.get(url)
        if self.verbose:
            print("Crawling url is ", url)

        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        try:
            ret_str = str(soup.select('#articleBodyContents')[0])
        except:
            return ''

        cutting = re.compile('<[^(<|>)]*>')
        cutting_list = cutting.findall(ret_str)
        for cutting_str in cutting_list:
            ret_str = ret_str.replace(cutting_str, '', 1)
        ret_str = ret_str.replace('// flash 오류를 우회하기 위한 함수 추가', '')
        ret_str = ret_str.replace('function _flash_removeCallback() {}', '')
        ret_str = ret_str.replace('\n', '', 100)
        ret_str = ret_str.replace('\t', '', 100)
        ret_str = ret_str.split('.')
        ret = []
        for sentence in ret_str:
            if '[' in sentence or ']' in sentence or '▶' in sentence or 'Copyright' in sentence or '@' in sentence:
                continue
            if sentence == 'co' or sentence =='kr' or sentence =='com':
                continue
            if len(sentence) == 0:
                continue
            ret.append(sentence)
        return ret

    def get_market_real_time(self, product_name, num_of_item=15):
        """
        crawling the market price for given keyword.
        :param key_word: search word
        :return: list of dictionary.
                name: name of product in market
                price: price of product in market
                link: market link
        """
        ret = []
        key = product_name.lower().split()
        for market in markets:
            get_data = market.get_data(product_name, 20)
            for element in get_data:
                check = 1
                for keyword in key:
                    if keyword not in element['name'].lower():
                        check = 0
                        break
                if check == 1:
                    ret.append(element)
        ret = sorted(ret, key=lambda dict: dict['price'])
        return ret[:num_of_item]

    def update_market_price(self, product_name):
        data = self.get_market_real_time(product_name)
        product = SpProduct.objects.filter(name=product_name)[0]
        # SpProduct 하나당 가장 낮은 가격 하나만 저장됨
        low = 999999999999
        for data_row in data:            
            if data_row['price']<low:
                low=data_row['price']
        Price.objects.create(product=product, value=data_row['price'], date=DATE.today())


crawler = Crawler()

if __name__ == '__main__':
    ret = crawler.get_market_real_time("삼성", 10)
    for _ret in ret:
        print(_ret['price'], _ret['name'])
