"""
@author: Qinjuan Yang
@time: 2022-02-10 10:39
@desc: 
"""
import jieba.posseg as pseg


class Word(object):
    def __init__(self, token, pos):
        self.token = token
        self.pos = pos


class Tokenizer(object):
    def __init__(self):
        pass

    def tokenize(self, sentence):
        return [Word(token, pos) for token, pos in pseg.cut(sentence)]
