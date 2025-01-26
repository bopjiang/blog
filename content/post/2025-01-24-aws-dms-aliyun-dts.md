---
title: "数据同步: AWS DMS和Aliyun DTS对比"
date: 2025-01-25T07:31:44+08:00
draft: false
---


在现代化的企业架构中，数据同步是一个至关重要的环节. 无论是跨云迁移、灾备架构，还是多数据中心数据一致性管理，选择合适的同步工具都是实现目标的关键。

一般大家使用数据同步有两种场景
* 场景一：一次性全量同步
* 场景二：全量同步+增量准实时同步。 
  
之前做过一个需求， 是为了内地等保合规，架构设计上需要将海外数据中心的部分数据实时同步到国内， 涉及到跨云、跨数据中心的数据同步， 是场景二中比较复杂的。

本文将对比AWS DMS（Database Migration Service）和阿里云数据传输服务（DTS），帮助大家选择适合自己场景的解决方案。

> 阿里云还有一个产品也叫DMS（Data Management）， 是做数据库运维管理平台。国内竞争对手有[Bytebase](https://bytebase.cc/), [NineData](https://www.ninedata.cloud/), 这个计划后面开篇文章专门讲讲三个数据库工具系统。

## 基本概述

### AWS DMS

AWS Database Migration Service（DMS）是一种托管的服务，主要用于数据库迁移和持续数据同步。DMS 支持从多种数据源（如 MySQL、PostgreSQL、Oracle、SQL Server）迁移到 AWS 上的 RDS、DynamoDB、S3 等目标。

特点：
- 托管服务： 减少运维开销。
- 多样化支持： 支持关系型数据库、NoSQL 和数据湖。
- 数据转换： 配合 AWS Schema Conversion Tool，可实现跨平台的数据迁移。
- 持续同步： 支持 CDC（Change Data Capture）模式。

### Aliyun DTS

阿里云数据传输服务（DTS）是阿里云提供的一个数据迁移、数据订阅与数据实时同步工具。支持从云上、云下的多种数据源迁移到阿里云的数据库产品如 PolarDB、AnalyticDB、以及自建数据库实例。

特点：
- 全链路支持： 兼具数据迁移、同步与订阅功能。
- 高性能： 实时数据同步延迟低。
- 弹性扩展： 支持复杂业务场景下的海量数据同步。
- 生态整合： 与阿里云生态无缝集成。

## 功能对比

| 功能                     | AWS DMS                                  | Aliyun DTS                                 |
|--------------------------|------------------------------------------|-------------------------------------------|
| **支持的数据源与目标**    | 多云与本地数据库，覆盖主流数据库类型     | 主流数据库，专注阿里云生态                |
| **迁移场景**             | 单次迁移、增量迁移、混合场景            | 支持全量、增量与实时同步                  |
| **数据延迟**             | CDC 支持延迟较低，视网络条件而定        | 延迟可低至毫秒级                          |
| **操作界面**             | 简洁但需要熟悉 AWS 控制台                | 界面友好，支持图形化监控                  |
| **监控与告警**           | 支持 CloudWatch 集成监控                | 内置监控与预警机制                        |
| **地域覆盖**             | AWS 全球区域广泛支持                   | 更适合中国大陆及亚太地区用户              |
| **成本**                 | 按迁移数据量和实例使用时长计费          | 按任务规模和链路复杂度计费                |


## 使用限制对比

### AWS DMS 使用限制
1. **MySQL 数据源：**
   - 支持 5.5、5.6、5.7、8.0 版本。
   - 必须启用二进制日志（binlog）并设置为 ROW 格式。
2. **PostgreSQL 数据源：**
   - 支持 9.x、10.x、11.x、12.x、13.x 版本。
   - 必须启用逻辑复制功能（Logical Replication）。
3. **MongoDB 数据源：**
   - 支持 3.6、4.0、4.2 版本。
   - 仅支持 ReplicaSet 集群模式，不支持 Sharded Cluster。
   - 不支持对集合的 TTL 索引进行迁移。
   - 对于 MongoDB Atlas，支持的版本需为 3.6 及以上，并且必须启用 TLS 和 MongoDB Oplog。

### Aliyun DTS 使用限制
1. **MySQL 数据源：**
   - 支持 5.5、5.6、5.7、8.0 版本。
   - 必须启用 binlog 日志功能，且日志格式支持 ROW。
   - 数据库账号需具备 REPLICATION CLIENT 和 REPLICATION SLAVE 权限。
2. **PostgreSQL 数据源：**
   - 支持 9.x、10.x、11.x、12.x、13.x 版本。
   - 需开启 wal_level 参数，并设置为 logical。
   - 数据库账号需具备 rds_superuser 或者 pg_read_all_stats 权限。
3. **MongoDB 数据源：**
   - 支持 3.6、4.0、4.2、4.4 版本。
   - 支持 ReplicaSet 和 Sharded Cluster，但对 Sharded Cluster 的性能要求较高。
   - 必须启用 Oplog。

## 优势与劣势

### AWS DMS
**优势：**
1. 支持多种云环境和本地数据库之间的迁移。
2. 与 AWS 生态集成，适合已有 AWS 云部署的用户。
3. Instance和DMS任务不是一一绑定， 一个Instance上可以跑多个DTS task， 这一点值得称赞。
4. 监控做得更好。

**劣势：**
1. 对中国大陆用户， 国内AWS就只有北京和宁夏两个区域，区域覆盖与网络延迟可能存在劣势。 国内AWS Region貌似和国外AWS Region无法互通。
2. DMS的Schema同步存在问题， 同步Schema时MySQL的主键， 二级索引会丢失。 听说可以通过额外配置 Schema Conversion Tool转换解决， 我暂时还未验证。。
3. 对MySQL DDL变更支持不好
4. 迁移表中有大字段时， LOB存在问题, 会导致ON UPDATE CURRENT_TIMESTAMP属性的时间字段被误更新， 造成数据不一致。
```
AWS DMS migrates LOB data in two phases:

AWS DMS creates a new row in the target table and populates the row with all data except the associated LOB value.

AWS DMS updates the row in the target table with the LOB data.
```
5. 修改同步配置需要停止迁移任务后再修改， 然后再恢复任务
6. 网络需要自己打通
7. 不支持外键


### Aliyun DTS
**优势：**
1. 与阿里云数据库和大数据服务深度整合。
2. 在中国大陆区域有更好的性能与支持。
3. 修改同步配置可以在线进行， 不会中断同步任务。
4. 海外数据中心可以和内地数据中心打通， 而且没有专线的场景， 提供了数据库网关DG方便通过公网隧道进行数据迁移。


**劣势：**
1. 对于非阿里云环境的支持相对有限。
2. 全球区域覆盖范围不如 AWS 广泛。
3. DTS的Instance是和迁移任务一一绑定的， 而且配置只能升级不能降级， 比较坑。 大部分场景， 全量同步阶段， 会需要比较高的配置， 加速同步过程。 云厂商的CPU, 内存， 网络， 磁盘都跟实例规格相关。
4. 阿里云VM管理这块， 各种规格命名混乱。 很多产品的实例规格跟阿里云云主机的规格完全对不上号， 以至于我们都怀疑这些阿里云产品究竟有没有跑在自己的云主机平台上？
5. Serverless还是要指定计算单元个数。


## 性能

* DMS的全量同步性能很好， 而且可以通过临时提机器规格， 提升并发度提升吞吐。 听说有大数据团队使用DMS把MySQL数据导出到S3, 性能比自己写的导出程序好很多。
* DMS的增量写入性能， 在跨区域场景存在瓶颈。 譬如在新加坡-深圳的跨区域增量同步， 写入QPS只有20左右， 后面分析原因是增量同步是单线程的， 新加坡-深圳的网络RT在40～50ms左右， 自然QPS上不去。

## 总结

AWS DMS 和 Aliyun DTS 各有千秋，适用的场景也不尽相同。在选择时，企业应结合自身的业务需求、技术栈和地理分布，综合考虑功能、性能与成本等因素。对于混合云架构或全球化业务，AWS DMS 是一个优秀的选择；而对于深耕阿里云生态或需要中国大陆强支持的用户，Aliyun DTS 更能满足需求。

