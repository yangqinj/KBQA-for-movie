"""
@author: Qinjuan Yang
@time: 2022-02-10 08:32
@desc: 
"""
from app.question2sparql import Question2SPARQL
from app.sparql_server import SPARQLServer


class QABot(object):
    def __init__(self):
        self.q2s = Question2SPARQL()
        self.sparql_server = SPARQLServer()

    def answer(self, question):
        sparql = self.q2s.translate(question)
        query_result = self.sparql_server.query(sparql)
        result = self.sparql_server.parse_query_result(query_result)
        return result


if __name__ == '__main__':
    bot = QABot()

    questions = ["周星驰出演了什么电影？"]
    for q in questions:
        print(bot.answer(q))
