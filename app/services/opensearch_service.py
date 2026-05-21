import os
from opensearchpy import OpenSearch

from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "incident-index"


client = OpenSearch(
    hosts=[{
        "host": "localhost",
        "port": 9200
    }],
    http_auth=(
        os.getenv("OPENSEARCH_USERNAME"),
        os.getenv("OPENSEARCH_PASSWORD")
    ),
    use_ssl=True,
    verify_certs=False
)


def create_index():

    if client.indices.exists(index=INDEX_NAME):
        return

    index_body = {
        "settings": {
            "index": {
                "knn": True
            }
        },
        "mappings": {
            "properties": {

                "incident": {
                    "type": "text"
                },

                "service": {
                    "type": "keyword"
                },

                "severity": {
                    "type": "keyword"
                },

                "embedding": {
                    "type": "knn_vector",
                    "dimension": 384
                }
            }
        }
    }

    client.indices.create(
        index=INDEX_NAME,
        body=index_body
    )


def index_incident(
    incident,
    embedding
):

    document = {

        "incident": incident.incident,

        "service": incident.metadata.service,

        "severity": incident.metadata.severity,

        "embedding": embedding.tolist()
    }

    client.index(
        index=INDEX_NAME,
        body=document,
        refresh=True
    )


def search_incidents(
    query_embedding,
    top_k=5,
    service=None,
    severity=None
):
    
    filters = []

    if service:
        filters.append({
            "term": {
                "service": service
            }
        })

    if severity:
        filters.append({
            "term": {
                "severity": severity
            }
        })

    search_body = {
        "size": top_k,

        "query": {
            "bool": {

                "filter": filters,

                "must": {
                    "knn": {
                        "embedding": {
                            "vector": query_embedding.tolist(),
                            "k": top_k
                        }
                    }
                }
            }
        }
    }

    response = client.search(
        index=INDEX_NAME,
        body=search_body
    )

    return response["hits"]["hits"]