---
title: "数据同步: AWS DMS和Aliyun DTS对比"
date: 2025-01-25T07:31:44+08:00
draft: false
---


在现代化的企业架构中,数据同步是一个至关重要的环节. 无论是跨云迁移、灾备架构,还是多数据中心数据一致性管理,选择合适的同步工具都是实现目标的关键.

一般大家使用数据同步有两种场景
* 场景一：一次性全量同步
* 场景二：全量同步+增量准实时同步 
  
之前做过一个国内等保合规需求,架构设计上需要将国内和海外的数据库独立部署, 并且海外数据中心的部分数据要实时同步到国内. 涉及到跨云、跨数据中心的数据同步,是场景二中比较复杂的.

本文将对比AWS DMS（Database Migration Service）和阿里云数据传输服务（DTS）,帮助大家选择适合自己场景的解决方案.

> 阿里云还有另一个产品也叫DMS（Data Management）, 功能定位为数据库运维管理平台.国内竞争对手有[Bytebase](https://bytebase.cc/), [NineData](https://www.ninedata.cloud/), 这个计划后面开篇文章专门讲讲三个数据库工具系统.

## 基本概述

### AWS DMS

AWS Database Migration Service（DMS）是一种托管的服务,主要用于数据库迁移和持续数据同步.DMS 支持从多种数据源（如 MySQL、PostgreSQL、Oracle、SQL Server）迁移到 AWS 上的 RDS、DynamoDB、S3 等目标.

### Aliyun DTS

阿里云数据传输服务（DTS）是阿里云提供的一个数据迁移、数据订阅与数据实时同步工具.支持从云上、云下的多种数据源迁移到阿里云的数据库产品如PolarDB、AnalyticDB.


## 使用限制对比


### MySQL 数据源
- 都要求必须启用二进制日志（binlog）并设置为 ROW 格式.
- AWS DMS实时同步期间不支持MySQL在线变更工具如(pt-osc, gh-ost)作变更. 阿里云DTS支持gh-os, 但不支持pt-osc
- AWS DMS不支持MySQL外键
- AWS DMS Schema同步存在问题, 同步Schema时MySQL的主键, 二级索引会丢失. 
  听说可以通过额外配置 Schema Conversion Tool转换解决, 暂时还未验证.

  阿里云的Schema同步会丢失Comment信息.

### PostgreSQL 数据源

### MongoDB
- AWS DMS仅支持 3.6、4.0、4.2 版本.
- AWS DMS不支持MongoDB Atlas mongodb+srv://协议.


## 优势与劣势

### AWS DMS
**优势：**
1. 支持多种云环境和本地数据库之间的迁移.
2. 与 AWS 生态集成,适合已有 AWS 云部署的用户.
3. Instance和DMS任务不是一一绑定, 一个Instance上可以跑多个DTS task, 这一点值得称赞. 
   在全量数据比较大, 但增量CDC数据不大的场景, 可以在全量阶段使用较高配置的机器, 但在增量同步阶段, 使用低配机器降低成本.
4. DMS监控数据比较完善.
5. 故障定位比较方便, 有专门的辅助表记录同步/对比失败的库/表信息.

**劣势：**
1. 对中国大陆用户, 国内AWS就只有北京和宁夏两个区域,区域覆盖与网络延迟可能存在劣势. 国内AWS Region貌似和国外AWS Region无法互通.
2. 修改同步配置需要停止迁移任务后再修改, 然后再恢复任务
3. 网络层需要自己打通.
3. 迁移表中有大字段时, LOB存在问题, 会导致ON UPDATE CURRENT_TIMESTAMP属性的时间字段被误更新, 造成数据不一致.
```
AWS DMS migrates LOB data in two phases:

AWS DMS creates a new row in the target table and populates the row with all data except the associated LOB value.

AWS DMS updates the row in the target table with the LOB data.
```

实际使用中, 为避免数据不一致问题, 我们一般使用Limited LOB mode, 但是要事先要了解数据中字段的最大长度.


### Aliyun DTS
**优势：**
1. 修改同步配置可以在线进行, 不会中断同步任务.
2. 海外数据中心可以和内地数据中心打通, 而且没有专线的场景, 提供了数据库网关DG方便通过公网隧道进行数据迁移.
3. 在中国大陆区域有更多的区域可选择.
4. 支持双向同步.

**劣势：**
1. DTS的Instance是和迁移任务一一绑定的, 而且配置只能升级不能降级, 比较坑. 大部分场景, 全量同步阶段, 会需要比较高的配置, 加速同步过程. 云厂商的CPU, 内存, 网络, 磁盘都跟实例规格相关.
2. 阿里云VM管理这块, 各种规格命名混乱. 很多产品的实例规格跟阿里云云主机的规格完全对不上号, 以至于我们都怀疑这些阿里云产品究竟有没有跑在自己的云主机平台上？
3. Serverless还是要指定计算单元个数.
4. 监控数据种类较少, 而且通过控制台能看到的监控数据, 有些通过API拿不到.

## 性能

* DMS的全量同步性能很好, 而且可以通过临时提机器规格, 提升并发度提升吞吐. 听说有大数据团队使用DMS把MySQL数据导出到S3, 性能比自己写的导出程序好很多.
* DMS的增量写入性能, 在跨区域场景存在瓶颈. 譬如在新加坡-深圳的跨区域增量同步, 写入QPS只有20左右, 后面分析原因是增量同步是单线程的, 新加坡-深圳的网络RT在40～50ms左右, 自然QPS上不去.

## 总结

AWS DMS 和 Aliyun DTS 各有千秋,适用的场景也不尽相同.在选择时,企业应结合自身的业务需求、技术栈和地理分布,综合考虑功能、性能与成本等因素.

从产品设计上看, DMS更适用于一次性迁移任务的场景. 如果需要长期运行的同步任务, 对同步延迟/中断容忍度低, DTS目前看起来更合适.

总体来说, 各个云厂商的数据同步产品, 更关注的是将外部数据<span style="color: red;">迁移到自家的数据库产品中</span>. 如果要将数据迁移出去, 或多或少会有些问题要解决. 

随着云计算使用原来越深入, 特别是大中型互联网企业, 肯定有多云, 多区域的部署需求, 各个云厂商做好基础设施供应商的角色, 打磨自己的产品核心功能, 把自己的API做完善就很不错. 至于各个云产品间的互操作性和集成, 我觉得尽量留给三方厂商. 云计算市场这么大, 不会有绝对的垄断. 


## 参考
- [AWS DMS] (https://docs.aws.amazon.com/dms/latest/userguide/Welcome.html)
- [阿里云DTS] (https://help.aliyun.com/zh/dts/product-overview/what-is-dts)
- [Setting LOB support for source databases in an AWS DMS task
](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.LOBSupport.html)