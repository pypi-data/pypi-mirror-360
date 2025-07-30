#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from liquiclient.config import get_property
from confluent_kafka import Producer, Consumer


# 获取kafka生产实例
def get_kafka_producer():
    bootstrap = get_property("kafka.bootstrap")

    client = Producer({'bootstrap.servers': bootstrap})

    return client


# 获取kafka集群生产实例
def get_kafka_cluster_producer(cluster):
    bootstrap = get_property(cluster + "kafka.bootstrap")

    client = Producer({'bootstrap.servers': bootstrap})

    return client


# 获取kafka消费实例
def get_kafka_consumer(group_id, offset="earliest"):
    bootstrap = get_property("kafka.bootstrap")

    client = Consumer({
        'bootstrap.servers': bootstrap,
        'group.id': group_id,
        'auto.offset.reset': offset
    })

    return client


# 获取kafka集群消费实例
def get_kafka_cluster_consumer(cluster, group_id, offset="earliest"):
    bootstrap = get_property(cluster + "kafka.bootstrap")

    client = Consumer({
        'bootstrap.servers': bootstrap,
        'group.id': group_id,
        'auto.offset.reset': offset
    })

    return client
