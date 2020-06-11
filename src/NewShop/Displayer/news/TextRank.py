#-*- coding:utf-8 -*-

from konlpy.tag import Komoran
import numpy as np
import pandas as pd

# 이 .py 파일은 "TextRank: Bringing Order into Texts"(Rada Mihalcea and Paul Tarau, 2004)의 논문을 재생산한 것이다.

# 한국어 형태소 분석기 코모란(Komoran)을 사용한다.
komoran = Komoran()

# TextRank is a graph-based model
class Graph(dict):
    def __init__(self):
        super(Graph, self).__init__()
        # Weighted graph의 구현이다.
        self.edge_weight = {}

    def add_vertex(self, v):
        if v in self.edge_weight.keys():
            pass
        else:
            self.edge_weight[v] = {}

    def add_edge(self, e, w):
        u, v = e
        if u in self.edge_weight[v].keys() and v in self.edge_weight[u].keys():
            pass
        else:
            self.edge_weight[u][v] = w
            self.edge_weight[v][u] = w

    def del_edge(self, e):
        u, v = e
        if not u in self.edge_weight[v].keys() and not v in self.edge_weight[u].keys():
            pass
        else:
            del self.edge_weight[v][u]
            del self.edge_weight[u][v]

    def del_vertex(self, v):
        if not v in self.edge_weight.keys():
            pass
        else:
            u = self.edge_weight[v].keys().copy()
            for _u in u:
                self.del_edge((v, _u))
            del self.edge_weight[v]

    def mod_edge_weight(self, e, w):
        u, v = e
        if not u in self.edge_weight.keys() and not v in self.edge_weight.keys():
            pass
        elif not v in self.edge_weight[u].keys() and not u in self.edge_weight[v].keys():
            pass
        else:
            self.edge_weight[u][v] = w
            self.edge_weight[v][u] = w


# Korean tokenizer
def komoran_tokenizer(sent):
    # POS tagger
    try:
        tokens = komoran.pos(sent)
    except:
        return None
    # Interested only in Noun(NNP, NNG), Verb(VV, VX), Adjective(VA, VX)
    tokens = [token for token in tokens if 'NN' in token[1] or 'VV' in token[1] or 'VX' in token[1] or 'VA' in token[1]]
    return tokens


# TextRank uses co-occurence relation to make useful connection (edge)
def cooccurence_relation(tokens, window=2):
    # The window size is between 2 and 10.
    assert 2 <= window <= 10

    g = Graph()
    # Add all the token to the graph
    for token in tokens:
        g.add_vertex(token)
    # Connect edges to another tokens if the token co-occur with thems within a given window size
    for i, token in enumerate(tokens):
        start = max(0, i - window)
        end = min(len(tokens), i + window)
        for j in range(start, end):
            if token != tokens[j]:
                # Unweighted graph
                g.add_edge((token, tokens[j]), 1)

    # Maybe add min co-occurence
    return g


# TextRank uses similarity relation to make useful connection (edge)
# Here, uses TextRank similarity function as a similarity function. Cosine similarity function can be a similarity function as well.
def similarity_relation(sents):
    g = Graph()
    # Add all the sentences to the graph
    for sent in sents:
        g.add_vertex(sent)
    # Add tokens of all sentences to a list
    all_tokens = []
    for sent in sents:
        tokenized_ = komoran_tokenizer(sent)
        if not tokenized_ is None:
            all_tokens += [tokenized_]
    # Connect edges to another sentence with weight (score)
    for i in range(len(all_tokens)):
        for j in range(len(all_tokens)):
            if i == j:
                pass
            else:
                if len(all_tokens[i]) == 0 and len(all_tokens[j]) == 0:
                    pass
                else:
                    rep_tokens = list(set([token for token in all_tokens[i] if token in all_tokens[j]]))
                    score = len(rep_tokens) / (len(all_tokens[i]) + len(all_tokens[j]))
                    g.add_edge((sents[i], sents[j]), score)

    return g


# Google's PageRank (Brin adn Page, 1998) algorithm
def pagerank(graph, d_f=0.85, epochs=30, threshold=0.001):
    assert 0 < d_f < 1
    assert 20 <= epochs <= 30

    # Set the initial value of score associated with each vertex to 1
    scores = dict.fromkeys(graph.edge_weight.keys(), 1.0)
    # Page ranking algorithm with iterations(epochs)
    for i in range(epochs):
        convergence = 0
        for j in graph.edge_weight.keys():
            score = 1 - d_f
            for k in graph.edge_weight[j].keys():
                # Weighted graph
                score += d_f * scores[k] * graph.edge_weight[j][k] / len(graph.edge_weight[k].keys())
            # Check with the threshold
            if abs(scores[j] - score) <= threshold:
                convergence += 1

            scores[j] = score

        # Early stopping
        if convergence == len(scores):
            break

    return scores

# 문장들을 받아 키워드를 반환하는 함수이다.
def keyword_extractor(sents, window=2, d_f=0.85, epochs=30, threshold=0.001, T=20):
    tokens = sum([komoran_tokenizer(sent) for sent in sents if not komoran_tokenizer(sent) is None], [])
    graph = cooccurence_relation(tokens, window)
    scores = pagerank(graph, d_f, epochs, threshold)
    scores_list = list(scores.keys())
    score_order = np.argsort(list(scores.values()))[::-1]
    # The tokens that has high scores be the key words
    _key_words = np.asarray(scores_list)[score_order[:T]]
    _key_words = _key_words.tolist()
    return _key_words

# 문장들을 받아 중요 문장들을 반환하는 함수이다.
def keysentence_summarizer(sents, d_f=0.85, epochs=30, threshold=0.001, T=3):
    graph = similarity_relation(sents)
    scores = pagerank(graph, d_f, epochs, threshold)
    scores_list = list(scores.keys())
    score_order = np.argsort(list(scores.values()))[::-1]
    # The tokens that has high scores be the key words
    _key_sentences = np.asarray(scores_list)[score_order[:T]]
    _key_sentences = _key_sentences.tolist()
    return _key_sentences
