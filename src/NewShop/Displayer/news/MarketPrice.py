import requests
from bs4 import BeautifulSoup
import re
import copy
from urllib import parse

class MarketPrice(object):
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
        self.market = None

    def make_price_url(self, word):
        word = word.split()
        word = '+'.join(word)
        return self.market + word

    def get_data(self, word):
        pass

class Coupang(MarketPrice):
    def __init__(self):
        super().__init__()
        self.market = 'https://www.coupang.com/np/search?component=&q='
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
        for idx in range(10):
            price = int(re.sub('<[^(<|>)]*>|,', '', str(list_price[idx])))
            name = str(re.sub('<[^(<|>)]*>', '', str(list_name[idx])))
            link = 'https://www.coupang.com' + str(list_url[idx]['href'])
            ret.append({'price': price, 'name': name, 'link': link})
        return ret

class Gmarket(MarketPrice):
    def __init__(self):
        super().__init__()
        self.market = 'https://browse.gmarket.co.kr/search?keyword='
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
        for idx in range(10):
            price = int(re.sub('<[^(<|>)]*>|,', '', str(list_price[idx])))
            name = str(list_name[idx]['title'])
            link = str(list_url[2 * idx]['href'])
            ret.append({'price': price, 'name': name, 'link': link})
        return ret


markets = [Coupang(), Gmarket()]