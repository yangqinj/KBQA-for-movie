"""
@author: Qinjuan Yang
@time: 2022-02-10 08:34
@desc: 
"""
from app.word import Tokenizer
from app.question_template import rules


class Question2SPARQL(object):
    def __init__(self):
        self.tokenizer = Tokenizer()

    def translate(self, question):
        words = self.tokenizer.tokenize(question)

        # TODO: 取第一个匹配的规则，后续修改更合适的逻辑
        sparql = None
        for r in rules:
            sparql = r.apply(words)
            if sparql:
                break

        return sparql



