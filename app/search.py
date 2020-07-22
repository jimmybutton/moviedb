from flask import current_app
from elasticsearch import NotFoundError
from datetime import datetime


def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__.keys():
        value = getattr(model, field)
        if isinstance(value, datetime):
            payload[field] = value.isoformat()
        else:
            payload[field] = value
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    try:
        current_app.elasticsearch.delete(index=index, id=model.id)
    except NotFoundError as e:
        print(e)


def query_index_full_text(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={
            "query": {"multi_match": {"query": query, "fields": ["*"]}},
            "from": (page - 1) * per_page,
            "size": per_page,
        },
    )
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    return ids, search["hits"]["total"]["value"]


def query_index(index, query, page, per_page, sort_by=None, order="asc"):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={
            "query": query,
            "from": (page - 1) * per_page,
            "size": per_page,
            "sort": [{sort_by: order}] if sort_by else ["_score"],
        },
    )
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    return ids, search["hits"]["total"]["value"]


def clear_index(index, mappings):
    current_app.elasticsearch.indices.delete(index=index, ignore=[400, 404])
    current_app.elasticsearch.indices.create(
        index=index,
        body={
            "settings": {
                "analysis": {
                    "normalizer": {
                        "my_normalizer": {
                            "type": "custom",
                            "char_filter": [],
                            "filter": ["lowercase", "asciifolding"],
                        }
                    }
                }
            },
            "mappings": {"properties": mappings},
        },
    )

