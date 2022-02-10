# KBQA-for-movie

分词和词性标注
匹配问题模板
问题转换为SPARQL
向FUSEKI查询结果
解析结果并返回答案



bot.py
class QABot   
  - q2s
  - server
  + answer()


question2sparql.py
class Question2Sparql
  - word_tagger
  - templates
  + translate(): translate question to sparql

word_tagging.py
class Word(token, pos)
class Tagger(dict_paths)
  + tag(): segment sentence and get pos of words

question_templates.py
class Template
  + regular expression
  + action
  + apply(): convert to sparql


sparql_server.py
class SPARQLServer(endpoint)
 + get_sparql_result
 + parse_result







   

