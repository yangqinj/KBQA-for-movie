"""
@author: Qinjuan Yang
@time: 2022-01-10 15:31
@desc:


"""
from SPARQLWrapper import SPARQLWrapper, JSON


url_base = "http://localhost:3030/kgmovie/"
query_url = url_base + "sparql"
update_url = url_base + "update"


def sparql_request(url, question, query_string, variable=None, is_update=False):
    sparql = SPARQLWrapper(url)
    sparql.setQuery(query_string)
    if is_update:
        sparql.setMethod("POST")
    else:
        sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    print("*" * 10, question, "*" * 10)
    if is_update:
        print(results.decode())
    else:
        for result in results["results"]["bindings"]:
            print(result[variable]["value"])


def test_query_movie():
    query_string = """
        PREFIX : <http://www.kgmovie.com#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
        SELECT ?title WHERE {
             ?movie rdf:type :Movie .
             ?movie :starring ?person .
             ?person :celebrityChineseName "周星驰" .
             ?movie :movieTitle ?title .
        }
    """
    sparql_request(query_url,
                   "周星驰出演了哪些电影？",
                   query_string,
                   "title")


def test_add_movie():
    insert_string = """
        PREFIX : <http://www.kgmovie.com#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX uri_file:  <file:///Users/yangqj/Documents/Workspace/KBQA-for-movie/data/kg_movie_rdfs.nt#movie/>

        INSERT DATA {
            uri_file:1234567 rdf:type :Movie .
            uri_file:1234567 :movieTitle "长津湖" .

        }
    """
    sparql_request(update_url,
                   "增加电影《长津湖》",
                   insert_string,
                   is_update=True)

    query_string = """
        PREFIX : <http://www.kgmovie.com#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
        SELECT ?movie WHERE {
             ?movie rdf:type :Movie .
             ?movie :movieTitle "长津湖" .
        }
    """
    sparql_request(query_url,
                   "查询电影《长津湖》",
                   query_string,
                   "movie")


def test_query_comedian():
    query_string = """
        PREFIX : <http://www.kgmovie.com#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
        SELECT * WHERE {
             ?celebrity rdf:type :Comedian .
             ?celebrity :celebrityChineseName ?name .
        }
        limit 10
    """
    sparql_request(query_url,
                   "查询10位喜剧演员",
                   query_string,
                   "name")


def test_celebrity_direct():
    query_string = """
            PREFIX : <http://www.kgmovie.com#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            SELECT * WHERE {
                 ?person :direct ?movie .
                 ?person :celebrityChineseName ?name .
            }
            limit 10
        """
    sparql_request(query_url,
                   "查询10个电影的导演",
                   query_string,
                   "name")


if __name__ == '__main__':
    test_query_movie()
    test_add_movie()
    test_query_comedian()
    test_celebrity_direct()