from elasticsearch import Elasticsearch
from typing import List, Dict, Any

ES_HOST = 'localhost:9200'
DATASET_INDEX = 'datasetindex_v2'
USER_INDEX = 'corpuserindex_v2'
DATAPROCESS_INDEX = 'dataprocessindex_v2'


def create_match_clause(key: str, value: str):
    # For text indexed fields like owners
    return {
        "match": { key: value }
    }

def create_terms_clause(key: str, value: List[str]):
    return {
        "terms": { key: value }
    }


def create_range_clause(key: str, gte: int, lte: int):
    return {
        "range": {
            key: {
                "gte": gte,
                "lte": lte
            }
        }
    }



def create_search_query(clauses: List[dict]):
    return {
        "query": {
            "bool": {
                "must": clauses
            }
        }
    }



def issue_search_query(index_name: str, query: Dict[str, Any]):
    es = Elasticsearch(hosts=[ES_HOST])
    res = es.search(index=index_name, body=query, request_timeout=120)
    return res
