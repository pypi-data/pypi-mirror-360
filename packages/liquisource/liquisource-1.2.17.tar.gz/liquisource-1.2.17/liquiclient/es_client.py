#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from elasticsearch import Elasticsearch
from liquiclient.config import get_property


# 获取es实例
def get_es_client():
    host = get_property("es.host")
    port = get_property("es.port")
    username = get_property("es.username")
    password = get_property("es.password")
    scheme = get_property("es.scheme")

    # 创建 Elasticsearch 客户端实例
    client = Elasticsearch(
        hosts=[host],
        port=port,
        scheme="http",
        http_auth=(username, password),
    )

    return client
