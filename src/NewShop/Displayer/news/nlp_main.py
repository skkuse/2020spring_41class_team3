#-*- coding:utf-8 -*-

import os
import collections
import json
import random
import pandas as pd

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchtext
from torchtext import data
from torchtext.data import TabularDataset, BucketIterator

from konlpy.tag import Komoran

from NewShop.Displayer.news.crawler import make_news_url, Crawler
from NewShop.Displayer.news.TextRank import keyword_extractor, keysentence_summarizer


device = 'cuda' if torch.cuda.is_available() else 'cpu'
# TODO: 1. Save model 2. Adopt crawling 3. Experiments documents 4. Update database system


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


if __name__=="__main__":
    # Log settings
    exp_logs = []
    exp_log = collections.OrderedDict({'model': 'LSTM'})
    exp_logs.append(exp_log.copy())
    file_name = 'GRU'
    path = "Your path"
    save_json_file(f'{path}', exp_logs)
    
    random.seed(10)

    # Data loading (example) TODO: Change to crawling application
    # columns: 'raw', 'key_word', 'key_sentences', 'classification'
    """ Save the example data
    df = pd.read_csv('example_dataset.csv')
    train_df = df.loc[[0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14]][['key_sentences', 'classification']]
    test_df = df.loc[[3, 7, 11, 15]][['key_sentences', 'classification']]
    train_df.to_csv('train_data.csv', index=False, index_label=False)
    test_df.to_csv('test_data.csv', index=False, index_label=False)
    """
    print("### Data preprocessing ###")
    TEXT = data.Field(sequential=True, use_vocab=True, tokenize=tokenizer.morphs, batch_first=True, tokenizer_language='ko', fix_length=20)
    LABEL = data.Field(sequential=False, use_vocab=False, batch_first=False, is_target=True)
    train_data, test_data = TabularDataset.splits(path='.', train='train_data.csv', test='test_data.csv', format='csv', fields=[('text', TEXT), ('label', LABEL)], skip_header=True)
    
    TEXT.build_vocab(train_data, min_freq=1, max_size=100000)
    vocab_size = len(TEXT.vocab.stoi)

    train_loader = BucketIterator(dataset=train_data, batch_size=batch_size, shuffle=True, repeat=False)
    test_loader = BucketIterator(dataset=test_data, batch_size=batch_size, shuffle=False)

    # ML settings
    epochs = 10
    batch_size = 2
    n_classes = 4
    lr = 0.1
    tokenizer = Komoran()

    print("### Model ###")
    #model = torch.nn.LSTM()
    model = TextSentiment(vocab_size, 256, n_classes)
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    print("### Epoch starts ###")
    for epoch in range(epochs):
        train_log = train(model, optimizer, criterion, train_loader, epoch)
        test_log = test(model, criterion, test_loader, epoch)
        exp_log = train_log.copy()
        exp_log.update(test_log)
        exp_logs.append(exp_log)
        save_json_file(f'{path}', exp_logs)
    