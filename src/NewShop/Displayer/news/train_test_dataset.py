import os
import pandas as pd
import numpy as np

from TextRank import keysentence_summarizer, keyword_extractor
from crawler import make_news_url, Crawler

# 모델 학습-테스트를 위해 데이터를 저장하는 함수이다.
def make_train_test_dataset(query, date_range, length, df, cur_dir):
    crawler = Crawler()
    news_contents = []
    classification = []
    # 크롤링을 시작해 관련된 뉴스를 저장한다.
    #print("### Crawling start ###")
    for i, q in enumerate(query):
        url = make_news_url(q, date_range[0], date_range[1], length)
        for url_ in url:
            news = crawler.get_news_link(url_)
            for n_url in news:
                news_contents.append(crawler.get_news_contents(n_url))
                classification.append(i)
    #    print(f"Length of classification {i}: {len([x for x in classification if x==i])}")
    #print(f"Total length of crawled news: {len(classification)}")
    #print("### TextRank start ###")
    key_words_ = []
    key_sentences_ = []
    # TextRank 기법을 활용해 키워드와 요약문장을 알아내 저장한다.
    for i in range(len(classification)):
        key_words_.append(keyword_extractor(news_contents[i], window=2, d_f=0.85, epochs=30, threshold=0.001, T=20))
        key_sentences_.append(keysentence_summarizer(news_contents[i], d_f=0.85, epochs=30, threshold=0.001, T=5))
        if not key_words_[i] is None and not key_sentences_[i] is None:
            df_ = pd.DataFrame({'raw': [news_contents[i]], 'key_word': [key_words_[i]], 'key_sentences': [key_sentences_[i]], 'classification': [classification[i]]}, columns=df.columns)
            df = pd.concat([df, df_])
            # 데이터는 csv 파일로 저장한다.
            df.to_csv(f'{cur_dir}/pre_dataset_3.csv')
    return df

# 쿼리를 통해 뉴스 데이터와 가공된 데이터를 저장하는 함수이다.
def get_save_news_data():
    query = ['ssd 가격', 'ssd 신제품', 'ssd 프로모션', 'ssd 업계']
    date_range = ['20100101', '20200602']
    length = 100
    df = pd.DataFrame(columns=['raw', 'key_word', 'key_sentences', 'classification'])
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    df = make_train_test_dataset(query, date_range, length, df, cur_dir)
    query = ['사과 가격', '사과 신제품', '사과 프로모션', '사과 업계']
    df = make_train_test_dataset(query, date_range, length, df, cur_dir)

# csv를 가공하는 함수이다.
def modify_csv(file_name):
    df = pd.read_csv(file_name)
    for i in range(len(df)):
        print(f'### News summary for {i}th news')
        print(df.iloc[i]['key_sentences'])
        print(f'### Classification: {df.iloc[i]["classification"]}')
        print(f'### Type your choice (0: price, 1: new product, 2: promotion, 3: industry) 4: delete, 5: finish')
        input_ = int(input())
        print(f'### You typed {input_}')
        df.loc[i, "classification"] = input_
        print()
    df.to_csv(f'{file_name}_final.csv')

# 전체 데이터셋을 학습-테스트 데이터셋으로 분리하는 함수이다.
def split_dataset(file_name):
    df = pd.read_csv(file_name)
    shuffle_idx = np.arange(len(df))
    np.random.shuffle(shuffle_idx)
    train_idx = shuffle_idx[:int(3*len(df)/4)]
    test_idx = shuffle_idx[int(3*len(df)/4):]
    train_df = df.loc[train_idx][['key_sentences', 'classification']]
    test_df = df.loc[test_idx][['key_sentences', 'classification']]
    train_df.to_csv('train_data.csv', index=False, index_label=False)
    test_df.to_csv('test_data.csv', index=False, index_label=False)

"""
if __name__=='__main__':
    #get_save_news_data()

    #modify_csv('pre_dataset_3.csv')

    split_dataset('pre_dataset_3.csv')
"""