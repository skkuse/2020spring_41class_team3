#-*- coding:utf-8 -*-

import os
import sys
import collections
import json
import random
import pandas as pd
from datetime import datetime

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchtext
from torchtext import data
from torchtext.data import TabularDataset, Iterator

from konlpy.tag import Komoran

from Displayer.models import News, NspProduct, SpProduct
from Displayer.news.crawler import make_news_url, Crawler
from Displayer.news.TextRank import keysentence_summarizer


komoran = Komoran()

device = 'cuda' if torch.cuda.is_available() else 'cpu'

def get_recommend_query(query):
    all_products = SpProduct.objects.values('name')
    results = []
    # Query word exist (should be perfect form)
    for i in range(len(all_products)):
        if query in all_products[i]['name']:
            results.append(all_products[i]['name'])
    # Tokenizer
    komoran = Komoran()
    query_tokens = komoran.pos(query)
    all_products_tokens = []
    for i in range(len(all_products)):
        all_products_tokens.append(komoran.pos(all_products[i]['name']))
    # Query word exist (can not be perfect form)
    for i in range(len(all_products_tokens)):
        if query_tokens[0] in all_products_tokens[i]:
            results.append(all_products[i]['name'])
    # Relative Query and target (same NspProduct class)
    all_products_big = NspProduct.objects.values('name')
    all_products_big_tokens = []
    for i in range(len(all_products_big)):
        all_products_big_tokens.append(komoran.pos(all_products_big[i]['name']))
    for i in range(len(all_products_big_tokens)):
        if query_tokens[0] in all_products_big_tokens[i]:
            results.append(all_products_big[i]['name'])
    results = list(set(results))
    return results


# From torch tutorial
class TextSentiment(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_class):
        super().__init__()
        self.embedding = nn.EmbeddingBag(vocab_size, embed_dim, sparse=True)
        self.fc = nn.Linear(embed_dim, num_class)
        self.init_weights()

    def init_weights(self):
        initrange = 0.5
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()

    def forward(self, text, offsets):
        embedded = self.embedding(text, offsets)
        return self.fc(embedded)


def save_json_file(path, data):
    with open(f'{path}\\log.json', "w") as outfile:
        json.dump(data, outfile, indent=2)


def train(model, optimizer, criterion, train_loader, epoch):
    model.train()
    train_loss = 0.0
    correct = 0
    total = 0
    for batch_idx, (inputs, targets) in enumerate(train_loader):
        inputs = inputs.to(device)
        targets = targets.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs, None)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()

    total_loss = train_loss/total
    total_acc = correct/total

    print(f'Train\t[{epoch}] Loss: {total_loss:.4f}\tAccuracy: {total_acc:.4f}')

    log = collections.OrderedDict({
        'epoch': epoch,
        'train': collections.OrderedDict({
            'loss': total_loss,
            'accuracy': total_acc,
        }),
    })
    return log


def test(model, criterion, test_loader, epoch):
    model.eval()
    test_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for batch_idx, (inputs, targets) in enumerate(test_loader):
            inputs = inputs.to(device)
            targets = targets.to(device)
            outputs = model(inputs, None)
            loss = criterion(outputs, targets)

            test_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

    total_loss = test_loss/total
    total_acc = correct/total

    print(f'Test\t[{epoch}] Loss: {total_loss:.4f}\tAccuracy: {total_acc:.4f}')

    log = collections.OrderedDict({
        'epoch': epoch,
        'test': collections.OrderedDict({
            'loss': total_loss,
            'accuracy': total_acc,
        }),
    })
    return log


def train_model():
    # Log settings
    exp_logs = []
    exp_log = collections.OrderedDict({'model': 'LSTM'})
    exp_logs.append(exp_log.copy())
    path = os.path.dirname(os.path.abspath(__file__))
    save_json_file(f'{path}', exp_logs)
    
    random.seed(10)

    # ML settings
    epochs = 100
    batch_size = 10
    n_classes = 4
    lr = 0.1
    tokenizer = komoran

    best_acc = 0.0

    # Data loading
    print("### Data preprocessing ###")
    TEXT = data.Field(sequential=True, use_vocab=True, tokenize=tokenizer.morphs, batch_first=True, tokenizer_language='ko', fix_length=20)
    LABEL = data.Field(sequential=False, use_vocab=False, batch_first=False, is_target=True)
    train_data, test_data = TabularDataset.splits(path='.', train='train_data.csv', test='test_data.csv', format='csv', fields=[('text', TEXT), ('label', LABEL)], skip_header=True)    
    
    TEXT.build_vocab(train_data, min_freq=2, max_size=100000)
    vocab_size = len(TEXT.vocab.stoi)
    vocab = TEXT.vocab

    train_loader = Iterator(dataset=train_data, batch_size=batch_size, shuffle=True, device=device, repeat=False)
    test_loader = Iterator(dataset=test_data, batch_size=batch_size, shuffle=False, device=device, repeat=False)

    print("### Model ###")
    embed_dim = 256
    model = TextSentiment(vocab_size, embed_dim, n_classes).to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss(reduction='sum').to(device)

    print("### Epoch starts ###")
    for epoch in range(epochs):
        train_log = train(model, optimizer, criterion, train_loader, epoch)
        test_log = test(model, criterion, test_loader, epoch)
        exp_log = train_log.copy()
        exp_log.update(test_log)
        exp_logs.append(exp_log)
        save_json_file(f'{path}', exp_logs)

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


def test_model(query, date_range, length, m_path):
    checkpoint = torch.load(m_path, map_location=device)
    model = TextSentiment(checkpoint['vocab_size'], checkpoint['embed_dim'], checkpoint['n_classes']).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    # Crawling & NLP start & Update database
    crawler = Crawler()
    for i, q in enumerate(query):
        url = make_news_url(q, date_range[0], date_range[1], length)
        for url_ in url:
            news = crawler.get_news_link(url_)
            for n_url in news:
                news_contents_ = crawler.get_news_contents(n_url)
                if not news_contents_ == '':
                    print("### News summary")
                    key_sentences_ = keysentence_summarizer(news_contents_, d_f=0.85, epochs=30, threshold=0.001, T=5)
                    print(key_sentences_)
                    tokens = [komoran.morphs(sent) for sent in key_sentences_]
                    vocab = checkpoint['vocab']
                    text = torch.tensor([vocab[token] for token in tokens[0]]).to(device)
                    offsets = torch.tensor([0]).to(device)
                    outputs = model(text, offsets)
                    _, predicted = outputs.max(1)
                    print(f"### Predict: {predicted.item()} \t(0: price, 1: new product, 2: promotion, 3: industry)")

                    # Shold be updated
                    date_ = datetime.now()
                    title_ = 'ex'

                    product_ = NspProduct.objects.filter(name=q)[0]
                    key_sentences_string = ''
                    for i in key_sentences_:
                        key_sentences_string += i
                        key_sentences_string += " "
                    News.objects.create(date=date_, title=title_, subj=predicted.item(), url=n_url, product=product_, piece=key_sentences_string)


""" Usage
    # Arguments:
    #     1) list (Query sentence) (*** Should be product name ***)
    #     2) list (Range of searching news)
    #     3) int (Maximum length of searching news)
    #     4) string (Path to TextSentiment model) (*** Do not touch ***)
(Example)
test_model(['ssd'], ['20200601', '20200608'], 9, 'Displayer/news/best_model.pth'))
"""

    