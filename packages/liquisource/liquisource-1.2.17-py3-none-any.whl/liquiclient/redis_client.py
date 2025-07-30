#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
from liquiclient.config import get_property
from redis.cluster import RedisCluster
from urllib.parse import urlencode


# 获取redis实例
def get_redis_client():
    mode = get_property("redis.mode")
    host = get_property("redis.host")
    port = get_property("redis.port")
    username = get_property("redis.username")
    password = get_property("redis.password")
    if mode != "cluster":
        client = redis.Redis(host=host, port=port, username=username, password=password, decode_responses=True)
    else:
        url = "redis://{}:{}@{}".format(urlencode(username), urlencode(password), host)
        client = RedisCluster.from_url(url, decode_responses=True)

    return client


# 获取redis实例
def get_redis_cluster_client(key):
    mode = get_property("redis.mode")
    host = get_property(key + ".redis.host")
    port = get_property(key + ".redis.port")
    username = get_property(key + ".redis.username")
    password = get_property(key + ".redis.password")
    if mode != "cluster":
        client = redis.Redis(host=host, port=port, username=username, password=password, decode_responses=True)
    else:
        url = "redis://{}:{}@{}".format(urlencode(username), urlencode(password), host)
        client = RedisCluster.from_url(url, decode_responses=True)

    return client
