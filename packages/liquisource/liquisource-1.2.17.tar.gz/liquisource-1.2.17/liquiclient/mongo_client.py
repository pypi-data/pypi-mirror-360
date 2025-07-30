#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo

from liquiclient.config import get_property


# 获取mongodb实例
def get_mongo_client():
    url = get_property("mongo.url")
    # 获取mongo链接实例
    client = pymongo.MongoClient(url)

    return client


# 获取mongodb集群实例
def get_mongo_cluster_client(cluster):
    url = get_property(cluster+".mongo.url")
    # 获取mongo链接实例
    client = pymongo.MongoClient(url)

    return client
