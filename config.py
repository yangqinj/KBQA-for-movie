"""
@author: Qinjuan Yang
@time: 2022-02-21 15:57
@desc: 
"""
import os


cur_dir = os.path.dirname(os.path.realpath(__file__))


class Config(object):
    fuseki_endpoint = "http://localhost:3030/kgmovie/sparql"
    dict_paths = [os.path.join(cur_dir, "data", "user_dicts", "movie_title.txt"),
                  os.path.join(cur_dir, "data", "user_dicts", "celebrity_name.txt")]


