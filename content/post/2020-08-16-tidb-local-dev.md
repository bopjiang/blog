---
title: "TiDB Local Development Envrionment"
date: 2020-08-16T12:16:07+08:00
draft: false
categories:
  - tech
---


## Run TiDB in Docker

使用的[tidb-docker-compose](https://github.com/bopjiang/tidb-docker-compose/tree/2020-hp-jiang), fork自[pingcap/tidb-docker-compose](https://github.com/pingcap/tidb-docker-compose)仓库.

去掉了TiSpark功能, 暂时用不上, 节省点内存.

TiDB集群(有Prometheus + Grafana)跑起来, 2G内存不够, 至少要分配4G内存.

## Development locally.

在tidb代码目录的同级目录, 增加一个shell脚本, 用于替换容器中的二进制文件.

```bash
# cat ../script/replace_tidb.sh
#!/bin/bash

set -e

make
docker cp bin/tidb-server tidb-docker-compose_tidb_1:/tidb-server
docker restart tidb-docker-compose_tidb_1

echo "replace tidb success"
docker exec -it tidb-docker-compose_tidb_1  /tidb-server -V
```

在tidb代码目录执行`../script/replace_tidb.sh`就能替换版本, 也不用污染tidb的代码目录. 关键不用重新build docker镜像和重新创建container, 速度很快.





