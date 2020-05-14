import requests
from bs4 import BeautifulSoup

# crawling at naver news
class Crawler(object):
    def __init__(self):
        self.url = None

    def make_url(self, search_word: str, start_date: str, end_date: str) -> str:
        """
        make self.url using search word, start_date, end_date
        :param search_word: the word that user want to search
        :param start_date: search condition. start date
        :param end_date: search condition. end date
        :return: None
        """
        base_url = 'https://search.naver.com/search.naver?where=news'
        search_word = 'query={}'.format(search_word)

    def get_html(self):
        """
        get html string using self.url
        :return: html string
        """

    def get_data(self):
        """
        make usable data
        :return: data
        """

if __name__ == '__main__':
    req = requests.get('https://search.naver.com/search.naver?query=%EA%B2%80%EC%83%89&where=news&ie=utf8&sm=nws_hty')
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    print(soup)