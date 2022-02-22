"""
@author: Qinjuan Yang
@time: 2022-02-10 10:39
@desc: 
"""
import jieba
import jieba.posseg as pseg


class Word(object):
    def __init__(self, token, pos):
        self.token = token
        self.pos = pos

    def __repr__(self):
        return "{}/{}".format(self.token, self.pos)


class Tokenizer(object):
    def __init__(self, dict_paths=None):
        if dict_paths:
            for path in dict_paths:
                jieba.load_userdict(path)

    def tokenize(self, sentence):
        return [Word(token, pos) for token, pos in pseg.cut(sentence)]
