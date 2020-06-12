#-*- coding:utf-8 -*-

import os
import sys
import collections
import json
import random
import io
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Pytorch: 파이토치는 GPU 리소스를 사용할 수 있는 머신러닝 오픈소스 라이브러리이다.
import torch
import torch.nn as nn
import torch.nn.functional as F
# TorchText: 토치텍스트는 텍스트에 중점을 둬 머신러닝 알고리즘을 편리하게 적용시키게 한 머신러닝 오픈소스 라이브러리이다.
import torchtext
from torchtext import data
from torchtext.data import TabularDataset, Iterator

# KoNLPy: 코엔엘파이는 한국어 정보처리를 위한 파이썬 패키지이다. 여기서는 코모란 토크나이저를 사용한다.
from konlpy.tag import Komoran
# WordCloud: 워드클라우드를 만들기 위한 라이브러리이다.
from wordcloud import WordCloud

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from NewShop.settings import MEDIA_ROOT

from Displayer.models import News, NspProduct, SpProduct, WordCloudImg
from Displayer.news.crawler import make_news_url, Crawler
from Displayer.news.TextRank import keysentence_summarizer, komoran_tokenizer


komoran = Komoran()

device = 'cuda' if torch.cuda.is_available() else 'cpu'

def get_recommend_query(query):
    all_products = SpProduct.objects.values('name')
    results = []
    # Query word exist (should be perfect form): 쿼리값과 정확하게 일치하는 값을 찾는다.
    for i in range(len(all_products)):
        if query in all_products[i]['name']:
            results.append(all_products[i]['name'])
    # Tokenizer
    komoran = Komoran()
    query_tokens = komoran.pos(query)
    all_products_tokens = []
    for i in range(len(all_products)):
        all_products_tokens.append(komoran.pos(all_products[i]['name']))
    # Query word exist (can not be perfect form): 쿼리값과 토큰값이 일치하는 값을 찾는다.
    for i in range(len(all_products_tokens)):
        if query_tokens[0] in all_products_tokens[i]:
            results.append(all_products[i]['name'])
    # Relative Query and target (same NspProduct class): 같은 NspProduct 클래스에 있는 값을 찾는다.
    all_products_big = NspProduct.objects.values('name')
    all_products_big_tokens = []
    for i in range(len(all_products_big)):
        all_products_big_tokens.append(komoran.pos(all_products_big[i]['name']))
    for i in range(len(all_products_big_tokens)):
        if query_tokens[0] in all_products_big_tokens[i]:
            results.append(all_products_big[i]['name'])
    # 위의 세 가지 경우를 모두 찾아 결과값을 반환한다.
    results = list(set(results))
    return results


# From torch tutorial
class TextSentiment(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_class):
        super().__init__()
        # 한 개의 임베딩 레이어
        self.embedding = nn.EmbeddingBag(vocab_size, embed_dim, sparse=True)
        # 한 개의 Feed-Forward Neural Network 레이어
        self.fc = nn.Linear(embed_dim, num_class)
        self.init_weights()

    # 가중치를 초기화하는 함수
    def init_weights(self):
        initrange = 0.5
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()

    # 포워딩을 하는 함수
    def forward(self, text, offsets):
        embedded = self.embedding(text, offsets)
        return self.fc(embedded)

# 모델을 학습시킬 때 학습되는 과정과 결과를 json 파일로 저장하기 위한 함수이다.
def save_json_file(path, data):
    with open(f'{path}\\log.json', "w") as outfile:
        json.dump(data, outfile, indent=2)

# 모델을 학습시키는 함수이다.
def train(model, optimizer, criterion, train_loader, epoch):
    model.train()
    train_loss = 0.0
    correct = 0
    total = 0
    # 배치(Batch) 단위로 나누어 학습한다.
    for batch_idx, (inputs, targets) in enumerate(train_loader):
        inputs = inputs.to(device)
        targets = targets.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs, None)
        loss = criterion(outputs, targets)
        # 역전파 단계를 수행한다.
        loss.backward()
        # 역전파 단계를 통해 얻어진 손실값을 바탕으로 정해진 옵티마이저(optimizer)를 통해 모델의 가중치를 갱신한다.
        optimizer.step()

        train_loss += loss.item()
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()

    # 이번 에포크(epoch) 동안의 전체 손실값과 정확도값을 계산한다.
    total_loss = train_loss/total
    total_acc = correct/total

    print(f'Train\t[{epoch}] Loss: {total_loss:.4f}\tAccuracy: {total_acc:.4f}')

    # 정보를 dict 형식으로 반환한다.
    log = collections.OrderedDict({
        'epoch': epoch,
        'train': collections.OrderedDict({
            'loss': total_loss,
            'accuracy': total_acc,
        }),
    })
    return log

# 모델을 테스트하는 함수이다.
def test(model, criterion, test_loader, epoch):
    model.eval()
    test_loss = 0.0
    correct = 0
    total = 0
    # 가중치를 갱신하지 않도록 제한한다.
    with torch.no_grad():
        # 배치(Batch) 단위로 나누어 실험한다.
        for batch_idx, (inputs, targets) in enumerate(test_loader):
            inputs = inputs.to(device)
            targets = targets.to(device)
            outputs = model(inputs, None)
            loss = criterion(outputs, targets)

            test_loss += loss.item()
            # 얻어진 아웃풋(outputs) 중 가장 큰 값이 예측한 값이다.
            _, predicted = outputs.max(1)
            total += targets.size(0)
            # 앞서 얻어진 predicted 값과 targets(정답) 값이 같은지를 계산한다.
            correct += predicted.eq(targets).sum().item()

    # 이번 에포크(epoch) 동안의 전체 손실값과 정확도값을 계산한다.
    total_loss = test_loss/total
    total_acc = correct/total

    print(f'Test\t[{epoch}] Loss: {total_loss:.4f}\tAccuracy: {total_acc:.4f}')

    # 정보를 dict 형식으로 반환한다.
    log = collections.OrderedDict({
        'epoch': epoch,
        'test': collections.OrderedDict({
            'loss': total_loss,
            'accuracy': total_acc,
        }),
    })
    return log

# 모델을 학습-테스트 하는 함수이다.
def train_model():
    # Log settings: 로그 파일을 만들기 위한 설정값들이다.
    exp_logs = []
    exp_log = collections.OrderedDict({'model': 'TextSentiment'})
    exp_logs.append(exp_log.copy())
    path = os.path.dirname(os.path.abspath(__file__))
    save_json_file(f'{path}', exp_logs)
    
    random.seed(10)

    # ML settings: 모델을 학습시키기 위한 하이퍼파라미터(hyperparameter) 값들이다.
    epochs = 100
    batch_size = 10
    n_classes = 4
    lr = 0.1
    # 토크나이저(tokenizer)는 한국어 형태소 분석기인 코모란(Komoran)을 사용한다.
    tokenizer = komoran

    # 가장 결과가 좋게 나온 모델을 알아내기 위한 변수이다.
    best_acc = 0.0

    # Data loading: 학습-테스트 과정을 위한 데이터셋(dataset)을 불러오는 과정이다.
    print("### Data preprocessing ###")
    TEXT = data.Field(sequential=True, use_vocab=True, tokenize=tokenizer.morphs, batch_first=True, tokenizer_language='ko', fix_length=20)
    LABEL = data.Field(sequential=False, use_vocab=False, batch_first=False, is_target=True)
    train_data, test_data = TabularDataset.splits(path='.', train='train_data.csv', test='test_data.csv', format='csv', fields=[('text', TEXT), ('label', LABEL)], skip_header=True)    
    
    TEXT.build_vocab(train_data, min_freq=2, max_size=100000)
    vocab_size = len(TEXT.vocab.stoi)
    vocab = TEXT.vocab

    train_loader = Iterator(dataset=train_data, batch_size=batch_size, shuffle=True, device=device, repeat=False)
    test_loader = Iterator(dataset=test_data, batch_size=batch_size, shuffle=False, device=device, repeat=False)

    # 모델과 관련된 함수들을 불러온다.
    print("### Model ###")
    embed_dim = 256
    model = TextSentiment(vocab_size, embed_dim, n_classes).to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss(reduction='sum').to(device)

    # 학습-테스트를 실행한다.
    print("### Epoch starts ###")
    for epoch in range(epochs):
        # 학습
        train_log = train(model, optimizer, criterion, train_loader, epoch)
        # 테스트
        test_log = test(model, criterion, test_loader, epoch)
        exp_log = train_log.copy()
        exp_log.update(test_log)
        exp_logs.append(exp_log)
        save_json_file(f'{path}', exp_logs)

        # 가장 테스트 정확도가 높은 모델을 필요한 정보와 함께 저장한다.
        if best_acc < test_log['test']['accuracy']:
            torch.save({
                'model_state_dict': model.state_dict(),
                'vocab_size': vocab_size,
                'embed_dim': embed_dim,
                'n_classes': n_classes,
                'vocab': vocab,
                }, f'{path}/best_model.pth')
            best_acc = test_log['test']['accuracy']
    print(f"### Best accuracy: {best_acc} ###")

# 실제 데이터에서 학습된 모델을 통해 아웃풋(output)을 얻어내는 함수이다.
def test_model(query, date_range, length, m_path):
    """ Usage
        # Arguments:
        #     1) list (Query sentence) (*** Should be product name ***)
        #     2) list (Range of searching news)
        #     3) int (Maximum length of searching news)
        #     4) string (Path to TextSentiment model) (*** Do not touch ***)
    (Example)
    test_model(['ssd'], ['20200601', '20200608'], 9, 'Displayer/news/best_model.pth'))
    """
    # 저장된 모델을 불러온다.
    checkpoint = torch.load(m_path, map_location=device)
    model = TextSentiment(checkpoint['vocab_size'], checkpoint['embed_dim'], checkpoint['n_classes']).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    # Crawling & NLP start & Update database
    # 크롤링을 통해 얻어진 뉴스 데이터를 가공 후 데이터베이스에 저장하는 과정이다.
    crawler = Crawler()
    for i, q in enumerate(query):
        url = make_news_url(q, date_range[0], date_range[1], length)
        for url_ in url:
            news = crawler.get_news_link(url_)
            for n_url in news:
                # 크롤링을 통해 뉴스 데이터를 가져온다.
                news_contents_ = crawler.get_news_contents(n_url)
                if not news_contents_:
                    pass
                elif not news_contents_ == '':
                    print("### News summary")
                    # 뉴스 데이터를 TexTrank의 keysentence summarizer 기법을 활용해 T줄 만큼 요약한다.
                    key_sentences_ = keysentence_summarizer(news_contents_, d_f=0.85, epochs=30, threshold=0.001, T=5)
                    print(key_sentences_)
                    tokens = [komoran.morphs(sent) for sent in key_sentences_]
                    vocab = checkpoint['vocab']
                    text = torch.tensor([vocab[token] for token in tokens[0]]).to(device)
                    offsets = torch.tensor([0]).to(device)
                    outputs = model(text, offsets)
                    # 모델에 얻어진 뉴스 데이터를 넣어 결과(output)을 반환한다.
                    # '0'이라면 가격과 관련된 뉴스, '1'이라면 신 제품에 관련된 뉴스,
                    #'2'라면 프로모션과 관련된 뉴스, '3'이라면 업계 동향과 관련된 뉴스이다.
                    _, predicted = outputs.max(1)
                    print(f"### Predict: {predicted.item()} \t(0: price, 1: new product, 2: promotion, 3: industry)")

                    title_, date_ = crawler.get_news_title_date(n_url)
                    date_arr = date_.split('.')
                    date_ = datetime(int(date_arr[0]), int(date_arr[1]), int(date_arr[2]))
                    title_ = title_[1:-1]
                    # 중복을 검사하는 과정이다.
                    if News.objects.filter(title=title_).count() == 0:
                        product_ = NspProduct.objects.filter(name=q)[0]
                        key_sentences_string = ''
                        for i in key_sentences_:
                            key_sentences_string += i
                            key_sentences_string += " "
                        # 크롤링을 통해 얻어진 뉴스 날짜, 뉴스 제목, 뉴스 url과 모델을 통해 가공된 분류(subj), 요약문단(piece),
                        # 그리고 관련된 상품(쿼리, query)의 정보를 데이터베이스에 저장한다.
                        key_sentences_string = key_sentences_string[:40]+'...'
                        News.objects.create(date=date_, title=title_, subj=predicted.item(), url=n_url, product=product_, piece=key_sentences_string)


# 각 상품별로 관련된 뉴스 제목를 통해 워드 클라우드를 만드는 함수이다.
def make_word_cloud(query, num_words=30):
    """ Usage
        # Arguments:
        #     1) list (Query sentence) (*** Should be product name ***)
        #     2) int (# of words)
        Image will be saved in 'MEDIA_ROOT/img' folder (MEDIA_ROOT in settings.py)
    (Example)
    make_word_cloud(['ssd'], 30)
    """
    for q in query:
        product_id_ = NspProduct.objects.filter(name=q).values()[0]['id']
        news_related = News.objects.filter(product=product_id_).values()
        # 뉴스 제목들을 워드 클라우딩 한다.
        titles = [news_related[i]['title'] for i in range(len(news_related))]
        titles_tokens = sum([komoran_tokenizer(title_) for title_ in titles], [])
        # Only nouns
        titles_tokens = [i[0] for i in titles_tokens if 'NN' in i[1] and len(i[0]) > 1]
        counter_ = collections.Counter(titles_tokens)
        # num_words 만큼의 단어를 추출한다.
        words_ = dict(counter_.most_common(num_words))

        WordCloud_ = WordCloud(background_color='white', width=800, height=600, font_path='Displayer/news/NanumBarunGothic.ttf', colormap='gist_gray')
        word_cloud = WordCloud_.generate_from_frequencies(words_)
        plt.figure(figsize=(10, 8))
        plt.axis('off')
        plt.imshow(word_cloud)

        # Django에 저장하기 위해 bytes로 변환
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        img_ = buffer.getvalue()
        buffer.close()
        img_ = ContentFile(img_)
        file_name = f'{q}.jpg'
        if file_name in os.listdir(f'{MEDIA_ROOT}/img'):
            os.remove(f'{MEDIA_ROOT}/img/{file_name}')
        img_ = InMemoryUploadedFile(img_, None, file_name, 'image/jpeg', img_.tell, None)
        product_ = NspProduct.objects.filter(name=q)[0]
        WordCloudImg(img=img_, product=product_).save()
