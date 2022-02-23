"""
@author: Qinjuan Yang
@time: 2022-02-10 08:32
@desc: 
"""
from app.question2sparql import Question2SPARQL
from app.sparql_server import SPARQLServer


class QABot(object):
    def __init__(self, sparql_endpoint, dict_paths):
        self.q2s = Question2SPARQL(dict_paths)
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
                ans = " ".join(value[0])
            else:

                ans = "、".join([" ".join(v) for v in value])
        else:
            ans = "我不理解你的问题"

        return ans


if __name__ == '__main__':
    from config import Config

    bot = QABot(Config.fuseki_endpoint,
                Config.dict_paths)

    questions = [
        "周星驰出演了什么电影",
         "初恋这件小事有哪些演员出演了",
         "刘德华和梁朝伟一起出演的电影有哪些",
         "周星驰既出演又导演的影片有哪些",
         "法国上映的电影有哪些",
         "周星驰出演了什么类型的电影",
         "刘德华出演了多少部影片",
         "张曼玉出演的评分大于8分的电影",
         "成龙出演的动作片有哪些"
    ]
    for q in questions:
        print("*" * 20)
        print("问题：", q)
        ans = bot.answer(q)
        print("答案：", ans)
