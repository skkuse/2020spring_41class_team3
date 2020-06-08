import requests
from bs4 import BeautifulSoup
import re
import copy
from urllib import parse

class MarketPrice(object):
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
        self.market = None
        self.market_name = None

    def make_price_url(self, word):
        word = word.split()
        word = '+'.join(word)
        return self.market + word

    def get_data(self, word):
        """
        get market price data from open market.
        :param word: search word
        :return: :return: list of dictionary.
                name: name of product in market
                price: price of product in market
                link: market link
        """
        pass

class Coupang(MarketPrice):
    def __init__(self):
        super().__init__()
        self.market = 'https://www.coupang.com/np/search?component=&q='
        self.market_name = 'coupang'
        self.market_info = {'name': ('div', {'class': 'name'}), 'price': ('strong', {'class': 'price-value'}),
                            'link': ('a', {'class': 'search-product-link'})}

    def get_data(self, word):
        url = self.make_price_url(word)
        req = requests.get(url, headers=self.headers)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        ret = []
        list_price = soup.find_all(self.market_info['price'][0], self.market_info['price'][1])
        list_name = soup.find_all(self.market_info['name'][0], self.market_info['name'][1])
        list_url = soup.find_all(self.market_info['link'][0], self.market_info['link'][1])
        print(len(list_price), len(list_name), len(list_url))
        for idx in range(20):
            try:
                market = self.market_name
                price = int(re.sub('<[^(<|>)]*>|,', '', str(list_price[idx])))
                name = str(re.sub('<[^(<|>)]*>', '', str(list_name[idx])))
                link = 'https://www.coupang.com' + str(list_url[idx]['href'])
                ret.append({'price': price, 'name': name, 'link': link, 'market': market})
            except:
                pass
        return ret


class Gmarket(MarketPrice):
    def __init__(self):
        super().__init__()
        self.market = 'https://browse.gmarket.co.kr/search?keyword='
        self.market_name = 'gmarket'
        self.market_info = {'name': ('span', {'class': 'text__item'}), 'price': ('strong', {'class': 'text text__value'}),
                            'link': ('a', {'class': 'link__item'})}

    def get_data(self, word):
        url = self.make_price_url(word)
        req = requests.get(url, headers=self.headers)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        ret = []
        list_price = soup.find_all(self.market_info['price'][0], self.market_info['price'][1])
        list_name = soup.find_all(self.market_info['name'][0], self.market_info['name'][1])
        list_url = soup.find_all(self.market_info['link'][0], self.market_info['link'][1])
        print(len(list_price), len(list_name), len(list_url))
        for idx in range(20):
            try:
                market = self.market_name
                price = int(re.sub('<[^(<|>)]*>|,', '', str(list_price[idx])))
                name = str(re.sub('<[^(<|>)]*>', '', str(list_name[idx])))
                link = str(list_url[idx]['href'])
                ret.append({'price': price, 'name': name, 'link': link, 'market': market})
            except:
                pass
        return ret


class Wemakeprice(MarketPrice):
    def __init__(self):
        super().__init__()
        self.market = 'https://search.wemakeprice.com/search?_service=2&_type=3&search_cate=top&keyword='
        self.market_name = 'Wemakeprice'
        self.market_info={'name': ('img', {'class': "motion-fade"}), 'price': ('em', {'class': 'num'}),
                          'link': ('div', {'class': 'search_box_imagedeal type4'})}

    def get_data(self, word):
        url = self.make_price_url(word)
        req = requests.get(url, headers=self.headers)
        html = req.text
        ret = []
        soup = BeautifulSoup(html, 'html.parser')
        list_price = soup.find_all(self.market_info['price'][0], self.market_info['price'][1])
        list_name = soup.find_all(self.market_info['name'][0], self.market_info['name'][1])
        list_url_temp = soup.find_all(self.market_info['link'][0], self.market_info['link'][1])
        list_url = []
        for url_data in list_url_temp:
            list_url.extend(url_data.find_all('a'))
        for idx in range(20):
            try:
                market = self.market_name
                price = int(re.sub('<[^(<|>)]*>|,', '', str(list_price[idx])))
                name = str(list_name[idx]['alt'])
                link = 'https:' + str(list_url[idx]['href'])
                ret.append({'price': price, 'name': name, 'link': link, 'market': market})
            except:
                pass
        return ret

class G9(MarketPrice):
    def __init__(self):
        super().__init__()
        self.market = 'http://www.g9.co.kr/Display/Search?keyword='
        self.market_name='G9'
        self.market_info={'name': ('span', {'class': 'itemcard__title__name'}), 'price': ('strong', {'class': 'format-price__value'}),
                          'link': ('a', {'class': 'itemcard__link'}), 'brand': ('span', {'class': 'itemcard__title__brand'})}

    def get_data(self, word):
        url = self.make_price_url(word)
        req = requests.get(url, headers=self.headers)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        ret = []
        list_price = soup.find_all(self.market_info['price'][0], self.market_info['price'][1])
        list_name = soup.find_all(self.market_info['name'][0], self.market_info['name'][1])
        list_brand = soup.find_all(self.market_info['brand'][0], self.market_info['brand'][1])
        list_url = soup.find_all(self.market_info['link'][0], self.market_info['link'][1])
        for idx in range(20):
            try:
                market = self.market_name
                price = int(re.sub('<[^(<|>)]*>|,', '', str(list_price[idx])))
                brand = str(re.sub('<[^(<|>)]*>', '', str(list_brand[idx])))
                name = str(re.sub('<[^(<|>)]*>', '', str(list_name[idx])))
                name = brand + ' ' + name
                link = 'http://www.g9.co.kr/' + str(list_url[2 *idx]['href'])
                ret.append({'price': price, 'name': name, 'link': link, 'market': market})
            except:
                pass
        return ret

class Auction(MarketPrice):
    def __init__(self):
        super().__init__()
        self.market = 'http://browse.auction.co.kr/search?keyword='#키워드의 스페이스바는 +로 써짐 ex)삼성+이어폰
        self.market_name = 'Auction'
        self.market_info = {'name': ('span', {'class': 'text--title'}), 'price': ('strong', {'class':'text--price_seller'}),
                            'link': ('a', {'class': 'link--itemcard'})}

    def get_data(self, word):
        url = self.make_price_url(word)
        req = requests.get(url, headers=self.headers)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        ret = []
        list_price = soup.find_all(self.market_info['price'][0], self.market_info['price'][1])
        list_name = soup.find_all(self.market_info['name'][0], self.market_info['name'][1])
        list_url = soup.find_all(self.market_info['link'][0], self.market_info['link'][1])
        for idx in range(20):
            try:
                market = self.market_name
                price = int(re.sub('<[^(<|>)]*>|,', '', str(list_price[idx])))
                name = str(re.sub('<[^(<|>)]*>', '', str(list_name[idx])))
                link = str(list_url[2 * idx]['href'])
                ret.append({'price': price, 'name': name, 'link': link, 'market': market})
            except:
                pass
        return ret


class st11(MarketPrice):
    def __init__(self):
        super().__init__()
        self.market = 'http://search.11st.co.kr/Search.tmall?kwd='#키워드가 복잡함
        self.market_name='11st'
        self.market_info={'name':('a',{'class':'itemcard_title'}), 'price':('span',{'class':'value'}),
        'link':('div>a',{'class':'c_prd_name c_prd_name_row_2'})}#name이 link랑 같은 a안에 data-log-body라는 dictionary 같은 형태 안에
        #"content_name":"상품이름.." 이런식으로 되어있음

    def get_data(self, word):
        url = self.make_price_url(word)
        req = requests.get(url, headers=self.headers)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        ret = []
        list_price = soup.find_all(self.market_info['price'][0], self.market_info['price'][1])
        list_name = soup.find_all(self.market_info['name'][0], self.market_info['name'][1])
        list_url = soup.find_all(self.market_info['link'][0], self.market_info['link'][1])
        for idx in range(20):
            try:
                market = self.market_name
                price = int(re.sub('<[^(<|>)]*>|,', '', str(list_price[idx])))
                name = str(list_name[idx]['title'])
                link = str(list_url[2 * idx]['href'])
                ret.append({'price': price, 'name': name, 'link': link, 'market': market})
            except:
                pass
        return ret


markets = [Gmarket(), Wemakeprice(), Auction(), G9()]
