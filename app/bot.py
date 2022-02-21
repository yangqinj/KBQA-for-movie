"""
@author: Qinjuan Yang
@time: 2022-02-10 08:32
@desc: 
"""
from app.question2sparql import Question2SPARQL
from app.sparql_server import SPARQLServer


class QABot(object):
    def __init__(self, sparql_endpoint):
        self.q2s = Question2SPARQL()
        self.sparql_server = SPARQLServer(sparql_endpoint)

    def answer(self, question):
        sparql = self.q2s.translate(question)

        ans = None
        if sparql:
            query_result = self.sparql_server.query(sparql)
            value = self.sparql_server.get_query_results_value(query_result)

            if not value:
                ans = "我不知道这个问题的答案"
            elif len(value) == 1:
                ans = value[0]
            else:

                ans = "、".join([" ".join(v) for v in value])
        else:
            ans = "我不理解你的问题"

        return ans


if __name__ == '__main__':
    from config import Config

    bot = QABot(Config.fuseki_endpoint)

    questions = ["周星驰出演了什么电影？"]
    for q in questions:
        print(bot.answer(q))
