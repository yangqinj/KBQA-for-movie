"""
@author: Qinjuan Yang
@time: 2022-02-10 08:36
@desc: 
"""
from SPARQLWrapper import SPARQLWrapper, JSON


class SPARQLServer(object):
    def __init__(self, endpoint):
        self.sparql = SPARQLWrapper(endpoint)

    def query(self, query_string):
        self.sparql.setQuery(query_string)
        self.sparql.setReturnFormat(JSON)
        return self.sparql.query().convert()

    @staticmethod
    def parse_query_results(query_results):
        vars = query_results['head']['vars']
        results = []
        for r in query_results["results"]["bindings"]:
            result = []
            for v in vars:
                result.append(r[v]["value"])
            results.append(result)
        print("results", results)
        return results

    @staticmethod
    def get_query_results_value(query_results):
        results = SPARQLServer.parse_query_results(query_results)
        return results

