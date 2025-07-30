# liquibase数据源驱动
> liquibase引入python3脚本，统一管理管理mongo、clickhouse的库表结构。changelog记录还是选在记录到mysql中，这样业务上会更加灵活
```xml
<changeSet id="xxxxx" author="xxxxxx" labels="mongo">
    <comment>xxxxx</comment>
    <executeCommand executable="python3">
        <arg value="script/db_tag/creat_collection.py"/>
    </executeCommand>
</changeSet>
```
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from liquibase_datasource import *


def create_tag_database():
    # 获取mongo链接实例
    client = get_client(filepath)


    return client[db]


def create_tag_collection():
    # 获取mongo链接实例
    db_name = get_tenant_shard(tag_database)
    client = get_client()
    db = client[db_name]

    # db开启分片
    client.admin.command("enableSharding", db_name)

    db.create_collection(tag_collection)

    # 创建索引
    coll = db[tag_collection]
    coll.create_index(
        [("id", 1), ("name", 1)])


if __name__ == "__main__":
    # 创建标签集合
    create_tag_database()[run.py](..%2F..%2F..%2FDownloads%2Frun.py)
    create_tag_collection()

```

## 发布包
```python
python3 -m pip install --upgrade build
python3 -m build
python3 -m pip install --upgrade twine
python3 -m twine upload  dist/*

```