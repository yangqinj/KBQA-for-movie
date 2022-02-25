"""
@author: Qinjuan Yang
@time: 2022-02-10 10:39
@desc: 
"""
import jieba
import jieba.posseg as pseg

pos_person = "nr"
pos_person_trans = "nrt"


class Word(object):
    def __init__(self, token, pos):
        self.token = token
        self.pos = pos

    def __repr__(self):
        return "{}/{}".format(self.token, self.pos)


class Tokenizer(object):
    def __init__(self, dict_paths=None):
        self.delimiter = "·"
        if dict_paths:
            for path in dict_paths:
                jieba.load_userdict(path)

    def splice_foreign_name_with_token(self, words):
        splice_words = []
        first, second = 0, 1
        while second < len(words):
            if words[second].token != self.delimiter:
                splice_words.append(words[first])
                first += 1
                second += 1
            else:
                while second + 2 < len(words) and words[second+2].token == self.delimiter:
                    second += 2
                splice_words.append(Word("".join([w.token for w in words[first:second+2]]), pos_person))
                first = second + 2
                second = first + 1
        if first < len(words):
            splice_words.append(words[first])

        return splice_words

    def splice_foreign_name_with_pos(self, words):
        splice_words = []
        first, second = 0, 0
        while first < len(words):
            if words[first].pos != pos_person and words[first].pos != pos_person_trans:
                splice_words.append(words[first])
                first += 1
            else:
                second = first + 1
                while second < len(words) and (words[second].pos == pos_person or words[second].pos == pos_person_trans):
                    second += 1
                splice_words.append(Word("".join([w.token for w in words[first:second]]), pos_person))
                first = second
        return splice_words

    def tokenize(self, sentence):
        words = [Word(token, pos) for token, pos in pseg.cut(sentence)]
        # 外文音译名称无法正确分词，如"娜塔莉·波特曼"被分词为"娜塔莉/·/波特曼"
        if self.delimiter in sentence:
            return self.splice_foreign_name_with_pos(self.splice_foreign_name_with_token(words))
        else:
            return words


if __name__ == '__main__':
    from config import Config

    tokenizer = Tokenizer(Config.dict_paths)

    for name in [
        "弗朗西丝卡·德·萨维奥测试娜塔莉·波特曼测试结果",
        "理查德·E·格兰特"
    ]:
        print(tokenizer.tokenize(name))
