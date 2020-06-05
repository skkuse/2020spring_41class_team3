from TextRank import keysentence_summarizer, keyword_extractor
from crawler import make_news_url, Crawler

def make_train_test_dataset(query, date_range, length):
    crawler = Crawler()
    news_contents = []
    classification = []
    for i, q in enumerate(query):
        print(f'{q} {date_range}')
        url = make_news_url(q, date_range[0], date_range[1], length)
        for url_ in url:
            print(url_)
            news = crawler.get_news_link(url_)
            for n_url in news:
                news_contents.append(crawler.get_news_contents(n_url))
                classification.append(i)

    for i in range(len(classification)):
        print(f'### {classification[i]} ###')
        print(news_contents[i])
        print('#########')
    print(f'len: {len(classification)}')
    


if __name__=='__main__':
    query = ['ssd%가격', 'ssd%신제품', 'ssd 프로모션', 'ssd 업계']
    date_range = ['20180101', '20200602']
    length = 100
    make_train_test_dataset(query, date_range, length)