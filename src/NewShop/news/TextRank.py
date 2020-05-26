#-*- coding:utf-8 -*-

from konlpy.tag import Komoran
import numpy as np


# TextRank is a graph-based model
class Graph(dict):
    def __init__(self):
        super(Graph, self).__init__()
        self.vertex_neighber = {}

    def add_vertex(self, v):
        if v in self.vertex_neighber:
            pass
        else:
            self.vertex_neighber[v] = []

    def add_edge(self, e):
        u, v = e
        if u in self.vertex_neighber[v] and v in self.vertex_neighber[u]:
            pass
        else:
            self.vertex_neighber[u].append(v)
            self.vertex_neighber[v].append(u)

    def del_edge(self, e):
        u, v = e
        if not u in self.vertex_neighber[v] and not v in self.vertex_neighber[u]:
            pass
        else:
            self.vertex_neighber[v].remove(u)
            self.vertex_neighber[u].remove(v)

    def del_vertex(self, v):
        if not v in self.vertex_neighber:
            pass
        else:
            u = self.vertex_neighber[v].copy()
            for _u in u:
                self.del_edge((v, _u))
            del self.vertex_neighber[v]


# Korean tokenizer
def komoran_tokenizer(sent):
    komoran = Komoran()
    # POS tagger
    tokens = komoran.pos(sent)
    # Interested only in Noun(NNP, NNG), Verb(VV, VX), Adjective(VA, VX)
    #tokens = [token for token in tokens if 'NN' in token[1] or 'VV' in token[1] or 'VX' in token[1] or 'VA' in token[1]]
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
                g.add_edge((token, tokens[j]))

    # Maybe add min co-occurence
    return g


# Google's PageRank (Brin adn Page, 1998) algorithm
def pagerank(graph, d_f=0.85, epochs=30, threshold=0.001):
    assert 0 < d_f < 1
    assert 20 <= epochs <= 30

    # Set the initial value of score associated with each vertex to 1
    scores = dict.fromkeys(graph.vertex_neighber.keys(), 1.0)
    # Page ranking algorithm with iterations(epochs)
    for i in range(epochs):
        convergence = 0
        for j in graph.vertex_neighber.keys():
            score = 1 - d_f
            for k in graph.vertex_neighber[j]:
                score += d_f * scores[k] / len(graph.vertex_neighber[k])
            # Check with the threshold
            if abs(scores[j] - score) <= threshold:
                convergence += 1

            scores[j] = score

        # Early stopping
        if convergence == len(scores):
            break

    return scores


def keyword_extractor(sents, window=2, d_f=0.85, epochs=30, threshold=0.001, T=20):
    tokens = sum([komoran_tokenizer(sent) for sent in sents], [])
    graph = cooccurence_relation(tokens, window)
    scores = pagerank(graph, d_f, epochs, threshold)
    scores_list = list(scores.keys())
    score_order = np.argsort(list(scores.values()))[::-1]
    # The tokens that has high scores be the key words
    _key_words = np.asarray(scores_list)[score_order[:T]]
    return _key_words


def test():
    # 기사출처: http://it.chosun.com/site/data/html_dir/2020/05/06/2020050601964.html
    sents = ['HTC 바이브(VIVE)가 업계 최초의 모듈형 가상현실(VR) 헤드셋 ‘바이브 코스모스 엘리트(VIVE Cosmos Elite)’를 정식으로 출시한다.', '바이브 코스모스 엘리트는 업계 최상급의 화질과 성능을 제공하는 바이브 코스모스 헤드셋(HMD)과 베이스 스테이션 1.0, 바이브 컨트롤러로 구성된 패키지 상품이다. 외부 베이스 스테이션을 이용한 아웃사이드-인 트래킹을 지원하는 익스터널 트래킹 페이스 플레이트를 제공, 높은 정밀도와 위치 정확도를 요구하는 VR 마니아 및 전문가들을 위한 제품이다.', '베이스 스테이션 2.0 및 바이브 컨트롤러 2018과도 호환되어 더욱 확장된 규모의 VR 환경을 구현할 수 있다. 국내 공식 공급원 제이씨현시스템을 통해 7일부터 VIVE 공식 몰 ‘바이브닷컴’과 바이브 액세서리 전문몰 ‘바이브스토어’에서 판매를 시작한다. 기본 바이브 제품군 이용자가 업그레이드할 수 있도록 헤드셋만 별도로 선보일 예정이다.', '이와 더불어 HTC 바이브와 제이씨현은 6일 오후 3시부터 바이브 코스모스 엘리트의 ‘버추얼 런칭 간담회’를 진행한다. 가상현실 공간에서 진행하는 신제품 출시 간담회로, HTC 바이브 코리아 공식 페이스북을 통해 생중계할 예정이다. 바이브 코스모스 엘리트와 더불어 새로운 엔터프라이즈 VR 협업 애플리케이션 ‘바이브 싱크(VIVE Sync)’를 선보인다.']
    key_words = keyword_extractor(sents, window=2, d_f=0.85, epochs=30, threshold=0.001, T=20)
    print(key_words)
    # Output: [['바이브' 'NNP'] ['코스모스' 'NNP'] ['공식' 'NNG'] ['헤드셋' 'NNP'] ['엘리트' 'NNP'] ['베이스' 'NNP'] ['수' 'NNB'] ['제공' 'NNG'] ['스테이션' 'NNP'] ['킹' 'NNG'] ['트' 'VV'] ['일' 'NNB'] ['더불' 'VV'] ['간담회' 'NNG'] ['몰' 'VV'] ['통하' 'VV'] ['가상현실' 'NNP'] ['업계' 'NNG'] ['예정' 'NNG'] ['출시' 'NNG']]


if __name__=="__main__":
    test()