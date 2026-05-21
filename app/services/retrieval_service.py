from app.utils.similarity import cosine_similarity
from app.services.opensearch_service import (
    search_incidents
)


def calculate_keyword_score(query, text):

    score = 0

    query_words = query.lower().split()

    text = text.lower()

    for word in query_words:

        if word in text:
            score += 0.1

    return score


def retrieve_incidents(
    query,
    model,
    service=None,
    severity=None
):

    query_embedding = model.encode(query)

    results = []
    search_results = search_incidents(
        query_embedding=query_embedding,
        top_k=5,
        service=service,
        severity=severity
    )

    for hit in search_results:
        source = hit["_source"]

        results.append({

            "incident": source["incident"],

            "metadata": {
                "service": source["service"],
                "severity": source["severity"]
            },

            "semantic_score": hit["_score"],

            "keyword_score": 0,

            "final_score": hit["_score"]
        })

    # Sort by hybrid score
    results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return results