"""
@author: Qinjuan Yang
@time: 2022-02-10 10:44
@desc:
"""
import re

from refo import finditer, search, Predicate, Star, Any

from app.decorators import print_func_name


SPARQL_PREFIX = """
    PREFIX : <http://www.kgmovie.com#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""

SPARQL_SELECT = """
    {prefix}
    
    SELECT DISTINCT {select} WHERE {{
        {expression}
    }}
"""

SPARQL_COUNT = """
    {prefix}
    
    SELECT COUNT({select}) WHERE {{
        {expression}
    }}
"""


class W(Predicate):
    def __init__(self, token=".*", pos=".*"):
        self.token = re.compile(token + "$")
        self.pos = re.compile(pos + "$")
        super(W, self).__init__(self.match)

    def match(self, word):
        m1 = self.token.match(word.token)
        m2 = self.pos.match(word.pos)
        return m1 and m2


class Rule(object):
    def __init__(self, condition, condition_num, action):
        self.condition = condition
        self.condition_num = condition_num
        self.action = action

    def apply(self, sentence):
        for m in finditer(self.condition, sentence):
            i, j = m.span()
            return self.condition_num, self.action(sentence[i:j])
        return None, None


class KeywordRule(object):
    def __init__(self, condition, action):
        """condition (class::`W`): the keyword"""
        self.condition = condition
        self.action = action

    def apply(self, sentence):
        res = search(self.condition, sentence)
        if res:
            i, j = res.span()
            return self.action(sentence[i])


class QuestionSet(object):

    @staticmethod
    @print_func_name
    def which_movie_does_actor_star(words):
        """某个演员出演了什么电影？"""
        select = "?title"

        sparql = None
        for w in words:
            if w.pos == pos_person:
                expression = """
                    ?movie rdf:type :Movie .
                    ?movie :starring ?person .
                    ?person :celebrityChineseName "{}" .
                    ?movie :movieTitle ?title .
                """.format(w.token)
                sparql = SPARQL_SELECT.format(prefix=SPARQL_PREFIX,
                                              select=select,
                                              expression=expression)
                break

        return sparql

    @staticmethod
    @print_func_name
    def which_actor_star_in_movie(words):
        """某个电影有哪些演员参演？"""
        select = "?name"

        sparql = None
        for w in words:
            if w.pos == pos_movie:
                expression = """
                    ?movie rdf:type :Movie .
                    ?movie :movieTitle "{}" .
                    ?movie :starring ?person .
                    ?person :celebrityChineseName ?name .
                """.format(w.token)
                sparql = SPARQL_SELECT.format(prefix=SPARQL_PREFIX,
                                              select=select,
                                              expression=expression)
                break

        return sparql

    @staticmethod
    @print_func_name
    def movie_with_rating(words):
        """评分为X/以上/以下的电影有哪些？"""
        select = "?title"

        operator = None
        for r in compare_rules:
            operator = r.apply(words)
            if operator:
                break

        number = None
        for w in words:
            if w.pos == pos_number:
                number = w.token
                break

        sparql = None
        if operator and number:
            expression = """
                ?movie rdf:type :Movie .
                ?movie :movieTitle ?title .
                ?movie :movieRate ?rate .
                filter(?rate {operator} {number})
            """.format(operator=operator, number=number)
            sparql = SPARQL_SELECT.format(prefix=SPARQL_PREFIX,
                                          expression=expression,
                                          select=select)

        return sparql

    @staticmethod
    @print_func_name
    def movie_with_rating_and_actor(words):
        """某个演员参演的某个评分为X/以上/以下的电影"""
        select = "?title"

        operator = None
        for r in compare_rules:
            operator = r.apply(words)
            if operator:
                break

        number = None
        actor = None
        for w in words:
            if w.pos == pos_number:
                number = w.token

            if w.pos == pos_person:
                actor = w.token

        sparql = None
        if operator and number and actor:
            expression = """
                        ?movie rdf:type :Movie .
                        ?movie :movieTitle ?title .
                        ?movie :movieRate ?rate .
                        ?movie :starring ?person .
                        ?person :celebrityChineseName "{name}" .
                        filter(?rate {operator} {number})
                    """.format(operator=operator, number=number, name=actor)
            sparql = SPARQL_SELECT.format(prefix=SPARQL_PREFIX,
                                          expression=expression,
                                          select=select)

        return sparql

    @staticmethod
    @print_func_name
    def movie_with_two_actors(words):
        """演员A和演员B共同出演的电影？"""
        actors = [w.token for w in words if w.pos == pos_person]
        if len(actors) != 2:
            return None

        select = "?title"
        expression = """
            ?movie rdf:type :Movie .
            ?movie :movieTitle ?title .
            ?movie :starring ?person1 .
            ?movie :starring ?person2 .
            ?person1 :celebrityChineseName "{}" .
            ?person2 :celebrityChineseName "{}" .
        """.format(actors[0], actors[1])
        sparql = SPARQL_SELECT.format(prefix=SPARQL_PREFIX,
                                      select=select,
                                      expression=expression)
        return sparql

    @staticmethod
    @print_func_name
    def movie_with_celebrity_as_actor_and_director(words):
        """某个演员既是演员又是导演的电影？"""
        select = "?title"

        sparql = None
        for w in words:
            if w.pos == pos_person:
                expression = """
                ?movie rdf:type :Movie .
                ?movie :starring ?person .
                ?movie :directedBy ?person .
                ?person :celebrityChineseName "{}" .
                ?movie :movieTitle ?title .
                """.format(w.token)
                sparql = SPARQL_SELECT.format(prefix=SPARQL_PREFIX,
                                              expression=expression,
                                              select=select)
                break

        return sparql

    @staticmethod
    @print_func_name
    def movie_published_in_country(words):
        """某个国家上映的电影"""
        select = "?title"

        special_countries = {
            "中国": ("中国大陆", "中国香港", "中国台湾"),
            "大陆": "中国大陆",
            "香港": "中国香港",
            "台湾": "中国台湾"
        }

        sparql = None
        for w in words:
            if w.pos == pos_country:
                canonical_country = special_countries.get(w.token)
                if not canonical_country:
                    canonical_country = w.token

                if isinstance(canonical_country, (list, set, tuple)):
                    expression = """
                    ?movie rdf:type :Movie .
                    ?movie :movieCountry ?country .
                    ?movie :movieTitle ?title .
                    FILTER(?country IN ({})).
                    """.format(", ".join(['"{}"'.format(c) for c in canonical_country]))
                else:
                    expression = """
                    ?movie rdf:type :Movie .
                    ?movie :movieCountry "{}" .
                    ?movie :movieTitle ?title .
                    """.format(canonical_country)

                sparql = SPARQL_SELECT.format(prefix=SPARQL_PREFIX,
                                              expression=expression,
                                              select=select)
                break

        return sparql

    @staticmethod
    @print_func_name
    def what_genre_actor_star(words):
        """某个演员出演了哪些类型的电影"""
        select = "?name"

        sparql = None
        for w in words:
            if w.pos == pos_person:
                expression = """
                ?movie rdf:type :Movie .
                ?movie :starring ?person .
                ?person :celebrityChineseName "{}" .
                ?movie :isGenre ?genre .
                ?genre :genreName ?name .
                """.format(w.token)
                sparql = SPARQL_SELECT.format(prefix=SPARQL_PREFIX,
                                              expression=expression,
                                              select=select)
                break

        return sparql

    @staticmethod
    @print_func_name
    def movie_the_actor_star_with_genre(words):
        """某个演员出演的某个指定类型的电影有哪些"""
        genre_name = genre_rule.apply(words)

        actor = None
        for w in words:
            if w.pos == pos_person:
                actor = w.token
                break

        select = "?title"
        sparql = None
        if genre_name and actor:
            expression = """
                ?movie rdf:type :Movie .
                ?movie :isGenre ?genre .
                ?genre :genreName "{genre_name}" .
                ?movie :starring ?person .
                ?person :celebrityChineseName "{actor}" .
            """.format(genre_name=genre_name, actor=actor)
            sparql = SPARQL_SELECT.format(prefix=SPARQL_PREFIX,
                                          expression=expression,
                                          select=select)

        return sparql

    @staticmethod
    @print_func_name
    def how_many_movie_actor_star(words):
        """某个演员出演了多少部电影"""
        select = "?title"

        sparql = None
        for w in words:
            if w.pos == pos_person:
                expression = """
                ?movie rdf:type :Movie .
                ?movie :starring ?person .
                ?person :celebrityChineseName "{}" .
                ?movie :movieTitle ?title .
                """.format(w.token)

                sparql = SPARQL_COUNT.format(prefix=SPARQL_PREFIX,
                                             expression=expression,
                                             select=select)
                break

        return sparql


class KeywordSet(object):
    @staticmethod
    @print_func_name
    def get_equal_operator(keyword):
        return '='

    @staticmethod
    @print_func_name
    def get_higher_operator(keyword):
        return '>'

    @staticmethod
    @print_func_name
    def get_lower_operator(keyword):
        return '<'

    @staticmethod
    @print_func_name
    def get_genre_name(keyword):
        return keyword.token

# 词性
pos_person = "nr"
pos_movie = "nz"
pos_country = "ns"
pos_number = "m"

# 词性对应实体
entity_person = W(pos=pos_person)
entity_movie = W(pos=pos_movie)
entity_country = W(pos=pos_country)
entity_number = W(pos=pos_number)

# 具体词语
movie = (W("电影") | W("影片") | W("片"))
actor = (W("演员"))
star = (W("出演") | W("参演"))
direct = (W("导演"))
rating = (W("评分") | W("分数") | W("分"))
publish = (W("上映") | W("发行"))
category = (W("类型"))
birth_date = (W("出生日期"))
birth_place = (W("出生地"))

equal = (W("等于") | W("为") | W("是"))
higher = (W("大于") | W("高于") | W("以上"))
lower = (W("小于") | W("低于") | W("以下"))
compare = (equal | higher | lower)

which = (W("哪些") | W("什么"))
how_many = (W("多少"))


disaster = (W("灾难"))
biography = (W("传记"))
song_and_dance = (W("歌舞"))
ancient = (W("古装"))
action = (W("动作"))
adventure = (W("冒险"))
affection = (W("爱情"))
science_fiction = (W("科幻"))
war = (W("战争"))
children = (W("儿童"))
homosexual = (W("同性"))
horror = (W("恐怖"))
crime = (W("犯罪"))
story = (W("剧情"))
thriller = (W("惊悚"))
sport = (W("运动"))
history = (W("历史"))
record = (W("纪录片"))
music = (W("音乐"))
suspense = (W("悬疑"))
fantastic = (W("奇幻"))
comedy = (W("喜剧"))
erotic = (W("情色"))
martial_arts = (W("武侠"))
family = (W("家庭"))
western = (W("西部"))
animation = (W("动画"))

genre = disaster | biography | song_and_dance | ancient | action | adventure | affection | \
        science_fiction | war | children | homosexual | horror | crime | story | thriller | \
        sport | history | record | music | suspense | fantastic | comedy | erotic | martial_arts | \
        family | western | animation


# 问题模板
rules = [
    # 某个演员出演了什么电影？
    Rule(entity_person + Star(Any(), greedy=False) + movie + Star(Any(), greedy=False),
         2,
         QuestionSet.which_movie_does_actor_star),
    # 某个电影有哪些演员参演？
    Rule(entity_movie + Star(Any(), greedy=False) + actor + Star(Any(), greedy=False),
         2,
         QuestionSet.which_actor_star_in_movie),
    # 评分为X/以上/以上/之间的电影有哪些？
    Rule(rating + (compare + entity_number) | (entity_number + compare) + Star(Any(), greedy=False) + movie + Star(Any(), greedy=False),
         4,
         QuestionSet.movie_with_rating),
    # 某个演员参演的某个评分为X/以上/以下/之间的电影
    Rule(entity_person + Star(Any(), greedy=False) + rating + (compare + entity_number) | (entity_number + compare) + Star(Any(), greedy=False) + movie + Star(Any(), greedy=False),
         5,
         QuestionSet.movie_with_rating_and_actor),
    # 演员A和演员B共同出演的电影？
    Rule(entity_person + Star(Any(), greedy=False) + entity_person + Star(Any(), greedy=False) + movie + Star(Any(), greedy=False),
         3,
         QuestionSet.movie_with_two_actors),
    # 某个演员即出演又是导演的电影？
    Rule(entity_person + Star(Any(), greedy=False) + star + Star(Any(), greedy=False) + direct + Star(Any(), greedy=False) + movie + Star(Any(), greedy=False),
         4,
         QuestionSet.movie_with_celebrity_as_actor_and_director),
    # 某个国家上映的电影
    Rule(entity_country + publish + Star(Any(), greedy=False) + movie + Star(Any(), greedy=False),
         3,
         QuestionSet.movie_published_in_country),
    # 某个演员出演了哪些类型的电影
    Rule(entity_person + Star(Any(), greedy=False) + which + category + Star(Any(), greedy=False) + movie,
         4,
         QuestionSet.what_genre_actor_star),
    # 某个演员出演的某个类型的电影有哪些
    Rule(entity_person + Star(Any(), greedy=False) + genre + Star(Any(), greedy=False) + movie + Star(Any(), greedy=False),
         3,
         QuestionSet.movie_the_actor_star_with_genre),
    # 某个演员出演了多少部电影
    Rule(entity_person + star + Star(Any(), greedy=False) + how_many + Star(Any(), greedy=False) + movie + Star(Any(), greedy=False),
         3,
         QuestionSet.how_many_movie_actor_star)
]


compare_rules = [
    KeywordRule(higher, KeywordSet.get_higher_operator),
    KeywordRule(lower, KeywordSet.get_lower_operator),
]

genre_rule = KeywordRule(genre, KeywordSet.get_genre_name)

