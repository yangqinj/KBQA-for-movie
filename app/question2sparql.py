"""
@author: Qinjuan Yang
@time: 2022-02-10 08:34
@desc: 
"""
from collections import defaultdict

from app.word import Tokenizer
from app.question_template import rules


class Question2SPARQL(object):
    def __init__(self, dict_paths):
        self.tokenizer = Tokenizer(dict_paths)

    def translate(self, question):
        words = self.tokenizer.tokenize(question)
        print("question {} is tokenized to {}".format(question, words))

        # 找到所有匹配的规则，然后取条件数最多的规则
        # 相同条件数下取匹配到的第一条规则
        match_rules = defaultdict(list)
        for r in rules:
            condition_num, sparql = r.apply(words)
            if sparql:
                match_rules[condition_num].append(sparql)

        match_rules = sorted(match_rules.items(), key=lambda x: x[0], reverse=True)
        if match_rules:
            return match_rules[0][1][0]

        return None



