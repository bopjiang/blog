---
title: "云原生关系型数据库的架构取舍: Spanner, F1, Aurora, AWS RDS, AlloyDB, GCP Cloud SQL和TiDB"
date: 2026-04-26T15:35:00+08:00
draft: false
slug: "cloud-native-relational-database-architecture"
aliases:
  - /post/2026/04/26/云原生关系型数据库的架构取舍-spanner-f1-aurora-alloydb-cloud-sql和tidb/
  - /post/2026/04/26/云原生关系型数据库的架构取舍-spanner-f1-aurora-rds-alloydb-cloud-sql和tidb/
  - /post/2026/04/26/云原生关系型数据库的架构取舍-spanner-f1-aurora-rds-alloydb-gcp-cloud-sql和tidb/
  - /post/2026/04/26/云原生关系型数据库的架构取舍-spanner-f1-aurora-aws-rds-alloydb-gcp-cloud-sql和tidb/
categories:
  - tech
---

## Introduction

云时代怎么构建一个关系型数据库?

这个问题看起来像是"把MySQL/PostgreSQL放到云上", 但真正做起来会很快碰到几个硬约束:

* 单机数据库的故障域太大, 云上必须默认跨机架、跨可用区, 甚至跨地域.
* 存储和计算资源要弹性伸缩, 不能像传统数据库那样强绑定在一台机器上.
* 用户仍然想要SQL, 事务, 索引, 二级索引, 约束, 备份恢复, 低延迟.
* 网络成为新的磁盘. 分布式系统里一次额外RPC, 可能比本机一次内存访问贵几个数量级.

所以云原生关系型数据库不是单一方向, 而是一条光谱:

```text
强一致 / 全球事务 / 分布式复杂度高
        Spanner + F1
              TiDB
                    Aurora / AlloyDB
                          AWS RDS / GCP Cloud SQL
低延迟 / 兼容性优先 / 单机语义保留
```

这条线不是优劣排序. 它表达的是: 系统把复杂度放在哪里.

Spanner把复杂度放在分布式复制、时间和事务协议里. Aurora把复杂度放在存储层, 尽量保留单主数据库的执行模型. AlloyDB试图在PostgreSQL兼容边界内增强存储、缓存和管理能力. TiDB把复杂度放在SQL层、事务层和分布式执行引擎里. AWS RDS和GCP Cloud SQL则基本选择"托管传统数据库", 把主要价值放在运维自动化上.

理解这些系统, 不能只看功能表. 更重要的是看它们选择不做什么.

## AWS和GCP产品对照

先给一个粗略定位表, 避免把"托管数据库", "云原生重构", "分布式SQL"混在一起.

| Category | AWS | GCP |
|---|---|---|
| Managed traditional DB | AWS RDS | GCP Cloud SQL |
| HA traditional DB | AWS RDS Multi-AZ DB instance | GCP Cloud SQL HA |
| HA cluster for MySQL/PG | AWS RDS Multi-AZ DB cluster | - |
| Cloud-native MySQL/PG | Amazon Aurora | AlloyDB for PostgreSQL |
| Distributed SQL | - | Cloud Spanner |
| Open-source distributed SQL | TiDB on AWS / self-managed | TiDB on GCP / self-managed |
| Analytics warehouse | Redshift | BigQuery |

这个表不是一一等价关系. 例如Aurora和AlloyDB都属于"兼容传统生态但重构云上执行环境", 但Aurora公开论文强调redo/WAL下沉到存储层, AlloyDB则强调PostgreSQL兼容、云化多节点架构、缓存和分析加速. AWS RDS Multi-AZ DB cluster也不要和Aurora cluster混为一谈, 前者仍是AWS RDS for MySQL/PostgreSQL的高可用部署形态.

## SLA, RPO, RTO

下面这个表只列公开文档能确认的承诺或典型行为. 需要特别注意: SLA通常是赔付口径的可用性承诺, RPO/RTO更多是架构目标或产品文档里的典型恢复行为, 两者不是同一种合同语言.

| 产品/部署形态 | SLA | RPO | RTO / failover |
|---|---:|---|---|
| AWS RDS Single-DB Instance | >= 99.5% | 依赖备份/PITR | 手工恢复或实例恢复 |
| AWS RDS Multi-AZ DB instance | >= 99.95% | AZ failover为0 | 通常60-120秒 |
| AWS RDS Multi-AZ DB cluster | >= 99.95% | 已提交复制为0 | 通常小于35秒, 受replica lag影响 |
| Amazon Aurora Single-AZ cluster | >= 99.9% | 存储仍跨AZ复制 | 依赖实例恢复 |
| Amazon Aurora Multi-AZ cluster | >= 99.99% | Region内已提交写入为0 | 有Aurora Replica时通常小于30秒 |
| GCP Cloud SQL Enterprise HA | >= 99.95% | HA写入为0 | 约60秒 |
| GCP Cloud SQL Enterprise Plus HA | >= 99.99% | HA写入为0 | 约60秒 |
| AlloyDB HA | 99.99% (*) | 未作为合同RPO声明 | 多数数据库故障60秒内 |
| Cloud Spanner Regional | >= 99.99% (**) | 强一致复制 | 未公开具体RTO |
| Cloud Spanner Dual/Multi-Regional | >= 99.999% | 强一致复制 | 未公开具体RTO |
| TiDB Cloud Dedicated/Essential | >= 99.99% | HA模式文档为0 | Zonal近0秒; Regional小于600秒 |
| TiDB Cloud Starter | >= 99.9% | Zonal HA文档为0 | 近0秒 |

(*) AlloyDB SLA在大多数Cloud Regions为99.99%, Mexico和Stockholm为99.95%.

(**) Spanner Regional在大多数Cloud Regions为99.99%, Mexico和Stockholm为99.95%; Dual/Multi-Regional为99.999%.

几个解读:

* AWS RDS Multi-AZ DB instance的"RPO 0"来自同步主备: primary确认提交前, 变更已经同步到standby. 它的RTO不是0, 因为还要检测故障、提升standby、切换DNS/连接.
* AWS RDS Multi-AZ DB cluster比传统Multi-AZ DB instance恢复更快, 但它使用数据库引擎native replication, failover仍可能受replica lag影响.
* Aurora的SLA比AWS RDS Multi-AZ更高, 核心原因是存储层已经跨AZ复制到多个storage nodes. 如果集群里有Aurora Replica, writer故障时通常可以在几十秒内完成提升.
* GCP Cloud SQL HA用regional persistent disk做跨zone同步复制. 文档明确说写入会复制到两个zone的磁盘后才报告事务提交, 因此HA场景的数据丢失目标可以看成0; 但failover期间连接会中断, 文档给出的恢复感知时间约60秒.
* AlloyDB公开SLA是可用性, RPO没有像TiDB Cloud文档那样直接列成表. 官方博客强调多zone冗余存储和自动failover, 并给出多数数据库故障60秒内恢复的描述.
* Spanner的公开SLA是可用性. 它的事务语义是强一致/外部一致, 但Google的SLA页没有把RPO/RTO写成一组可赔付数字. 对业务连续性仍然需要自己定义应用层RTO/RPO.
* TiDB Cloud表里的zonal HA near 0 seconds不是跨AZ容灾. 官方文档也明确说zonal setup不能处理整个zone failure; regional HA才是跨AZ容灾, 但RTO通常小于600秒.

## System Positioning

先把几个系统放到正确位置.

### Spanner

Spanner是Google的全球分布式关系型数据库. 它不是"更快的MySQL", 而是从一开始就假设数据会被切成很多split, 分布在多个replica上, 每个replica group用Paxos复制, 再用TrueTime给事务分配满足外部一致性的时间戳.

Spanner的核心定位是: 在分布式环境里提供SQL、强一致事务和自动分片. 它适合愿意为了正确性、可扩展性和跨地域可用性付出延迟和建模成本的系统.

### F1

F1是Google广告系统使用的分布式SQL数据库, 构建在Spanner之上. Spanner提供分布式存储、复制和事务; F1提供更完整的SQL层、分布式查询执行、schema设计约束和面向业务的访问模式.

可以把F1理解为"在Spanner这个分布式KV/事务底座上构建的SQL数据库系统". 它的价值不只是把SQL parser接到Spanner, 而是把应用的层次化数据模型显式暴露给数据库, 让数据库能利用数据局部性.

### Aurora

Aurora是AWS对MySQL/PostgreSQL兼容数据库的云原生重构. 它保留单主数据库的核心执行模型, 但重写了存储层: 计算节点不再把完整数据页刷到远端存储, 而是把redo/WAL日志发送到一个多AZ复制的分布式存储服务.

Aurora的定位很清晰: 不追求全球分布式事务, 而是在一个Region内用共享存储、quorum写入和快速恢复, 提升传统数据库的吞吐、可用性和故障恢复速度.

### AWS RDS Multi-AZ

AWS RDS还有两种经常和Aurora混淆的高可用架构:

* Multi-AZ DB instance deployment: 一个primary DB instance加一个不同AZ里的standby DB instance. standby用于故障切换, 不承担读流量.
* Multi-AZ DB cluster deployment: 一个writer DB instance加两个readable standby DB instances, 三个实例分别位于同一Region的三个AZ中. standby既用于故障切换, 也可以承担读请求.

它们都属于"托管传统数据库"路线, 不是Aurora那种专门重写过的分布式共享存储架构, 也不是Spanner/TiDB那种shared-nothing分布式SQL. AWS RDS Multi-AZ的核心目标是提高可用性和降低故障切换风险, 而不是把一个数据库自动变成水平写扩展系统.

底层同步方式放到后面的Storage Engine Design里单独讲. 简单说, Multi-AZ DB instance更像同步块复制主备, Multi-AZ DB cluster更像数据库引擎复制集群.

### AlloyDB

AlloyDB是Google Cloud的PostgreSQL兼容数据库. 它不是GCP Cloud SQL PostgreSQL的简单升级版, 而是在PostgreSQL兼容协议和语义之下, 引入云化存储、自动管理、缓存、读池和分析加速.

公开资料没有像Aurora论文那样完整披露AlloyDB存储协议. 但从产品定位看, 它选择的是"增强PostgreSQL, 尽量不破坏PostgreSQL生态". 这意味着它不能像Spanner那样要求用户重新理解全局主键、interleaving和跨分片事务; 也不能像一个全新数据库那样随意改变SQL语义和扩展兼容性.

### GCP Cloud SQL

GCP Cloud SQL是Google Cloud上的托管MySQL/PostgreSQL/SQL Server. 它的本质不是重新设计数据库, 而是托管传统数据库: 自动备份、补丁、监控、故障切换、存储扩容、安全集成.

GCP Cloud SQL的价值在于降低运维成本. 它不是用来解决"单机数据库架构上限"的, 而是让大量普通OLTP系统不用自己维护数据库服务器.

GCP Cloud SQL HA的底层存储复制也放到后面的Storage Engine Design里讨论. 它和AWS RDS Multi-AZ DB instance在直觉上很像: 都是在传统数据库实例之外, 依赖云厂商托管的同步块存储复制来提高可用性.

### TiDB

TiDB是开源分布式SQL数据库, MySQL协议兼容, 底层通常由TiDB Server, TiKV, PD, TiFlash组成. TiDB Server是无状态SQL层; TiKV是基于Raft复制的分布式KV; PD负责元数据、调度和时间戳; TiFlash提供列式副本和MPP分析能力.

TiDB的定位介于Spanner和Aurora之间. 它是分布式系统, 但没有TrueTime. 它支持分布式事务和水平扩展, 但通过Percolator风格的2PC, MVCC和时间戳服务来完成, 而不是把外部一致性建立在全球同步时钟上.

## Architecture Comparison

### Shared-nothing vs Shared-storage

Spanner更接近shared-nothing模型. 数据被切成split, split有自己的副本组, 每个副本组内部用Paxos维护一致状态. 计算和数据放置强相关: 查询一个key range时, 请求会路由到拥有这个range的server/replica group.

Aurora和AlloyDB更接近shared-storage模型. 数据库计算节点和存储层分离, 多个数据库实例可以连接到同一个底层集群卷或云化存储服务. 写入路径仍然有主写节点, 但底层数据已经不再属于某一台数据库机器的本地磁盘.

AWS RDS Multi-AZ DB instance deployment更接近传统主备数据库: primary对外服务, standby通过底层同步物理复制保持一致并等待故障切换, 但不服务读流量.

AWS RDS Multi-AZ DB cluster deployment向Aurora的"cluster使用体验"靠近一步: 有writer endpoint和可读standby, 读能力更强, failover也更快; 但它仍然是AWS RDS for MySQL/PostgreSQL的高可用部署形态, 不是Aurora存储引擎.

简化图:

```text
Spanner / TiDB:

SQL/Txn Layer
    |
    +--> Range A -> Replica group A
    +--> Range B -> Replica group B
    +--> Range C -> Replica group C

Aurora / AlloyDB:

Writer / Readers
    |
    +--> Shared distributed storage

AWS RDS Multi-AZ DB instance:

Primary DB instance
    |
    +--> Synchronous physical/block-level standby, not readable

AWS RDS Multi-AZ DB cluster:

Writer DB instance
    |
    +--> Native replication to two readable standby DB instances

GCP Cloud SQL HA:

Primary instance
    |
    +--> Regional Persistent Disk, synchronously replicated across two zones
```

这两个模型的差异很大.

shared-nothing的优势是天然水平扩展. 数据所有权分散在很多range上, 每个range可以独立迁移、复制、调度. 代价是跨range事务和跨range join会变成分布式问题.

shared-storage的优势是兼容单机数据库执行模型. Buffer pool, lock manager, SQL optimizer, executor可以保留更多传统形态. 代价是写扩展通常受主节点限制, 系统的上限更多来自单writer、缓存一致性和共享存储访问路径.

AWS RDS Multi-AZ的优势更朴素: 让传统数据库具备托管主备或一主两备能力. 它没有改变关系数据库的基本执行模型, 也没有让所有节点都能同时写入. 传统Multi-AZ DB instance把复杂度放在块设备/存储复制和故障切换编排里; Multi-AZ DB cluster则把复杂度更多放在数据库引擎复制和集群管理里.

### Compute-storage separation

所有这些系统都在谈计算存储分离, 但含义不同.

Aurora的分离是数据库进程和持久化存储服务的分离. 计算节点负责SQL执行、事务管理、buffer cache和锁; 存储节点负责持久化日志、复制、恢复页面.

AlloyDB也是计算和存储解耦, 但它保留PostgreSQL兼容性更强. 对用户来说, 它仍然像PostgreSQL: SQL语法、协议、扩展生态和很多运维概念仍然围绕PostgreSQL展开.

Spanner的分离不是"一个PostgreSQL计算节点接一个远端盘", 而是数据天然分布在很多replica group中. SQL层必须理解数据分片, 查询计划也必须理解远端执行和分布式join.

TiDB更显式: TiDB Server无状态, TiKV负责行存KV和Raft复制, TiFlash负责列存分析副本. 计算和存储分离的结果是SQL层可以横向扩展, 但优化器和执行器必须承担更多跨节点代价估算.

### Data ownership and placement

云数据库最关键的问题之一是: 一行数据到底属于谁?

在Aurora里, 一行数据逻辑上仍然属于一个数据库实例管理的表和页. 物理持久化在分布式存储里, 但数据所有权没有暴露为"这个key range归这个Raft group".

在Spanner/TiDB里, 数据所有权更接近key range. 主键设计直接决定数据切分、热点和事务路径. 一个糟糕的递增主键可能把写流量打到少数split/region上; 一个好的业务主键或shard key可以让数据自然分散.

这也是为什么Spanner文档反复强调primary key和interleaved table设计. 在分布式数据库里, schema不只是逻辑模型, 它也是物理拓扑的一部分.

## Consistency and Transactions

### Spanner: Paxos + TrueTime + external consistency

Spanner的事务设计有三个关键部件:

* Paxos负责每个replica group内部复制.
* 2PC负责跨多个Paxos group的写事务提交.
* TrueTime提供有界时间不确定性, 用来分配满足外部一致性的commit timestamp.

外部一致性比普通serializability更强. 如果客户端观察到事务T1已经提交, 然后才开始T2, 系统必须保证T2的序列化顺序在T1之后. Spanner通过TrueTime的时间边界和commit wait来保证这个性质.

代价也很直接: 跨地域写入需要等待复制和时间不确定窗口. Spanner不是在魔法般消除CAP, 而是在工程上把时间、复制和事务协议组合起来, 给用户一个清晰的一致性模型.

### Aurora: quorum commit without distributed consensus

Aurora的提交路径不是Spanner式的每个数据分片Paxos共识. 它把数据库写入转化为日志记录, 发往分布式存储层. 存储层跨3个AZ维护多份副本, 通过quorum确认日志持久化. 论文里经典设计是6份副本, 写quorum为4, 读quorum为3.

这套设计绕开了一个问题: 如果目标不是"任意key range都能独立接受写入并参与全球事务", 那就不必为每个事务支付分布式共识和跨分片提交的成本.

Aurora的正确性边界更多来自单writer数据库引擎的事务语义, 加上存储层对日志持久性的保证. 它适合Region内的高性能OLTP, 不适合把多个Region当成一个强一致写入域.

### TiDB: Percolator-style 2PC + MVCC

TiDB的事务模型借鉴Google Percolator. 事务开始时从PD获取全局单调时间戳`start_ts`, 读路径基于MVCC读取对应快照. 提交时进入2PC流程, 选择primary key, prewrite锁和数据, 再提交commit timestamp.

TiDB后来默认使用悲观事务模式, 更接近MySQL使用体验: DML执行阶段就加锁, 减少提交阶段冲突失败. 但底层提交逻辑仍然是分布式2PC.

TiDB的优势是通用性: MySQL协议, 分布式事务, 横向扩展, 还可以通过TiFlash做HTAP. 代价是事务路径比单机MySQL长, 热点写和大事务需要更谨慎的设计.

### Latency vs correctness

一致性不是免费的.

如果一个事务只写单机MySQL的一行, 提交路径可以非常短. 如果写Aurora, 它要把日志发到远端存储并等quorum. 如果写TiDB跨多个Region/Region group, 它要走分布式事务协议和Raft复制. 如果写Spanner跨多个Paxos group和地域, 它还要考虑TrueTime和外部一致性.

简化路径:

```text
GCP Cloud SQL:
client -> DB process -> local/managed storage

Aurora:
client -> writer -> redo/WAL to storage quorum

TiDB:
client -> TiDB -> TiKV prewrite -> TiKV commit -> Raft replication

Spanner:
client -> coordinator -> Paxos groups + 2PC -> TrueTime commit wait
```

这不是说后者一定慢. 后者解决的是更大的问题. 但如果业务问题本身不需要分布式写入域, 强行使用全球分布式事务数据库, 通常只是把简单问题复杂化.

## Storage Engine Design

这是理解Aurora, AlloyDB和Spanner差异的关键.

### AWS RDS和GCP Cloud SQL: managed block storage

先看最保守的托管数据库路线: AWS RDS和GCP Cloud SQL. 它们没有把数据库重写成分布式KV, 也没有像Aurora那样让存储层理解数据库redo/WAL. 它们更接近"传统数据库进程 + 云厂商托管块存储".

AWS RDS for MySQL/PostgreSQL这类传统实例底层使用Amazon EBS存放数据库和日志. EBS volume属于某个具体AZ, 并在该AZ内部做冗余复制来防单组件故障. 所以Single-AZ AWS RDS的磁盘可以粗略理解为"一个AZ内的RAID1-like网络块设备". 它不是本地盘, 也不是跨AZ磁盘, 而是一个AZ内的托管网络块设备.

AWS RDS Multi-AZ DB instance在这个基础上再做跨AZ同步物理主备. 这个模型可以类比DRBD: primary写入时, 变更需要同步到另一个AZ的standby存储侧, standby数据库实例平时不对外服务. 它不是MySQL binlog或PostgreSQL logical replication这类数据库层复制, 重点是故障时接管同一份物理状态.

AWS RDS Multi-AZ DB cluster则不同. AWS文档说明它使用数据库引擎的native replication能力, 从writer复制到两个reader DB instances, 语义上更接近一主两备的数据库复制集群, standby可以承担读流量.

GCP这边对应的块存储是Persistent Disk. Zonal Persistent Disk只在一个zone内可用, 底层基于Google的Colossus分布式块存储; Regional Persistent Disk会在同一个region的两个zones之间同步复制. GCP Cloud SQL HA使用regional persistent disk, 因此它和AWS RDS Multi-AZ DB instance在直觉上很像: 都是在传统数据库实例之外, 依赖云厂商托管的同步块存储复制来提高可用性.

```text
Single-AZ AWS RDS:
DB process -> EBS volume, replicated inside one AZ

AWS RDS Multi-AZ DB instance:
DB process -> EBS volume -> synchronous physical standby in another AZ

GCP Cloud SQL HA:
DB process -> Regional Persistent Disk, synchronously replicated across two zones

Aurora:
DB process -> redo/WAL records -> database-aware distributed storage
```

这个对比解释了为什么Aurora不是"AWS RDS加更好的磁盘". AWS RDS/GCP Cloud SQL HA的存储层主要提供块设备语义; Aurora的存储层理解数据库日志, 可以参与页面重建、恢复和修复.

### Aurora: log is the database

Aurora论文最重要的观点是: 在云环境中, 瓶颈从磁盘变成网络. 传统数据库会产生大量写放大: redo log, binlog, data page, double write, replication log, backup stream. 如果这些都跨网络传输, 网络会成为瓶颈.

Aurora的选择是只把redo/WAL日志作为主要写入内容发送到存储层. 存储层接收日志后, 自己负责把日志应用到页面, 进行恢复、修复和后台整理.

这就是"Log is the database"的工程含义: 数据库计算节点不再是唯一能重建页面状态的地方. 存储层也理解日志, 并能根据日志重建页面.

```text
Traditional:
DB compute reconstructs page
DB compute flushes dirty page
Storage stores blocks

Aurora:
DB compute sends redo/WAL
Storage reconstructs page
Storage repairs and catches up by log
```

这个设计带来几个结果:

* 写网络流量下降.
* crash recovery更快, 因为很多redo apply已经在存储层完成.
* replica failover更快, 因为新writer不需要重新拷贝全量数据.
* 存储层变复杂, 数据库引擎和存储服务深度耦合.

Aurora不是简单的"远端磁盘". 如果只是把InnoDB数据文件放到网络盘上, 不会得到Aurora的效果.

### AlloyDB: PostgreSQL WAL + accelerated storage, page still central

AlloyDB的公开叙述是PostgreSQL兼容的数据库服务, 使用Google构建的数据库引擎和云化多节点架构, 支持计算存储分离、读池、自动管理和分析加速.

它与Aurora最大的共同点是: 都试图在PostgreSQL/MySQL兼容边界内重构云上数据库. 但AlloyDB的取舍更偏"增强PostgreSQL", 而不是公开强调"日志就是数据库"这种存储协议重写.

因此从用户和兼容性边界看, AlloyDB仍然围绕PostgreSQL的WAL、page、buffer/cache、VACUUM、extension生态展开. Google可以在存储、缓存、预取、列式加速、自动内存管理上做大量优化, 但它不能轻易把PostgreSQL语义改造成Spanner式的全局分片事务模型.

换句话说, AlloyDB优化的是PostgreSQL在云上的执行环境; Spanner改变的是关系数据库在分布式系统中的基本假设.

### Spanner: distributed KV + replication

Spanner的存储模型更接近分布式有序KV. 表和索引最终映射到key-value空间, 数据按key range切分成split, split被复制到多个副本. 关系模型建立在这个分布式KV和事务层之上.

状态由谁重建?

Spanner里, 每个replica group通过Paxos日志维护自己的状态. SQL层不是拿一个远端page回来执行传统buffer pool逻辑, 而是把读写请求路由到拥有数据的分片. 分布式事务协调多个分片的一致提交.

这与Aurora完全不同. Aurora的核心是"保留单writer数据库, 让存储层更聪明"; Spanner的核心是"让数据本身分布式, 再在上面构造关系语义".

### 谁负责重建状态

可以用一个表概括:

```text
System      Durable input        Reconstructs state           User-visible model
GCP Cloud SQL   DB engine files/WAL   DB engine                   Traditional DB
Aurora      Redo/WAL records      Storage layer + DB cache     MySQL/PostgreSQL compatible
AlloyDB     PostgreSQL WAL/page   Enhanced PG engine/storage   PostgreSQL compatible
TiDB        KV writes + Raft log   TiKV raftstore/MVCC          MySQL-compatible distributed SQL
Spanner     Paxos log + KV state   Replica group                Distributed SQL
```

真正的设计分歧在这里: 是让存储层理解数据库日志, 还是让数据库本身变成分布式KV上的事务SQL系统.

## Schema and Data Locality

分布式数据库里, schema设计不是纯逻辑问题.

### Spanner interleaved tables

Spanner支持interleaved tables. 子表的主键包含父表主键, 物理上把子表行和父表行放在相邻key range里.

例如:

```sql
CREATE TABLE Customers (
    CustomerId INT64 NOT NULL,
    Name STRING(MAX)
) PRIMARY KEY (CustomerId);

CREATE TABLE Orders (
    CustomerId INT64 NOT NULL,
    OrderId INT64 NOT NULL,
    Amount NUMERIC
) PRIMARY KEY (CustomerId, OrderId),
  INTERLEAVE IN PARENT Customers ON DELETE CASCADE;
```

如果常见访问模式是"读取一个客户和他的订单", interleaving可以让相关数据落在同一局部范围里, 减少跨split访问.

代价是它把物理局部性写进schema. 如果访问模式变了, 或者某个父实体下子数据爆炸, interleaving可能制造热点或大split.

### F1 hierarchical schema

F1论文强调hierarchical schema. 这不是数据库设计课里的普通ER模型, 而是为了减少跨分布式事务和跨节点join而做的物理建模.

广告系统天然有层级: customer, campaign, ad group, ad, keyword. 如果这些数据按业务层次共址, 很多事务和查询都可以落在一个较小的数据范围里. F1的核心经验是: 分布式SQL不能只靠优化器救场, schema必须表达业务局部性.

这点很反直觉. 单机数据库时代, 我们会说"先做规范化, 性能问题交给索引和优化器". 分布式数据库时代, 数据模型如果完全无视局部性, 后面每个事务都可能变成跨网络协议.

### TiDB lack of interleaving

TiDB没有Spanner/F1那种interleaved table语义. 它依赖主键、索引、Region切分、调度和执行引擎来处理数据分布. 表数据和索引数据会映射到TiKV key space, 但用户不能用interleaving显式声明"这张子表必须跟父表共址".

结果是TiDB对MySQL迁移更友好, schema约束更少. 但代价是数据库不一定知道业务对象边界. 如果一个事务频繁同时更新`orders`, `order_items`, `payments`, `inventory`, 它可能跨多个Region, 需要2PC协调.

在TiDB里做分布式建模, 重点不是interleaving, 而是:

* 避免热点主键.
* 控制事务大小.
* 让高频事务尽量命中少量Region.
* 对分析查询使用TiFlash/MPP, 不要让OLTP路径承担所有事情.

### Impact on distributed transactions

数据局部性决定事务成本.

如果一个订单事务只触碰同一客户下的几行, Spanner/F1可以通过层次化schema提高局部提交概率. 如果一个事务触碰多个无关实体, 那就必须跨分片协调.

Aurora/AlloyDB/GCP Cloud SQL里, 只要还在单writer实例内, "跨表事务"通常不是分布式事务. 它可能有锁竞争、索引维护、WAL写入, 但不会因为两张表在不同分片上而触发2PC.

这也是为什么很多业务在相当长时间内不需要分布式SQL. 单机事务的简单性本身就是巨大的工程优势.

## Query Execution Model

### F1 distributed query execution

F1需要支持广告业务里的复杂查询, 包括跨大量数据的join, aggregation和报表类访问. 它建立在Spanner之上, 因此查询执行不能假设数据在本机.

F1的查询执行更像一个分布式SQL引擎: 把查询计划拆成多个阶段, 下推过滤和扫描, 在不同节点并行执行, 再汇总结果. 它的难点是既要服务OLTP, 又要支持足够复杂的SQL.

### TiDB MPP and distributed joins

TiDB早期主要依赖TiDB Server聚合TiKV coprocessor结果. 引入TiFlash和MPP后, 分析查询可以在列式副本上做分布式join和aggregation.

这让TiDB具有HTAP特征: 行存TiKV服务事务, 列存TiFlash服务分析. 但HTAP不是免费午餐. 复制延迟、资源隔离、优化器选择、join重排和统计信息都会影响实际效果.

TiDB的设计哲学是把更多复杂度推给执行层: 存储层提供分布式KV和列式副本, SQL层决定如何把查询拆开、下推、并行化.

### Spanner OLTP-oriented execution

Spanner当然也有查询优化器和分布式执行计划, 但它的核心场景仍然是强一致OLTP和可扩展事务. 如果把Spanner当成通用大数据分析引擎, 往往会失望.

Spanner的查询优化重点是利用主键、索引、interleaving和split locality, 尽量避免昂贵的全局shuffle. 它可以执行分布式查询, 但最舒服的姿势还是让访问模式贴近数据布局.

### Aurora/AlloyDB mostly single-node execution

Aurora和AlloyDB的SQL执行大体仍是单数据库实例模型. 读扩展可以通过read replica/read pool, 但单个复杂查询通常不是像F1/TiDB MPP那样天然拆到大量节点做分布式执行.

这带来的好处是成熟、兼容、可预期. PostgreSQL/MySQL生态里的优化经验仍然有效. 代价是单查询的横向扩展能力有限. 如果你要跑重分析, 通常应该把数据同步到Redshift, BigQuery, Snowflake, ClickHouse, Doris, TiFlash等系统, 而不是期待OLTP数据库无限扩展.

## Design Philosophies

### Google: embrace distributed complexity

Spanner和F1的思路是直面分布式复杂度. 既然Google内部业务需要全球规模、强一致和SQL, 那就构造TrueTime, Paxos复制, 分布式事务, 层次化schema和分布式查询执行.

这套设计很强, 但也很贵. 贵不只是价格, 还包括认知成本. 用户必须理解主键设计、热点、事务边界、跨地域延迟和数据局部性.

Google路线的核心信念是: 如果问题本质是分布式的, 就应该把分布式语义纳入数据库设计, 而不是隐藏在传统单机抽象后面.

### AWS: avoid distributed consensus

Aurora代表另一种路线: 不把关系数据库整体改造成Spanner, 而是在保留单主执行模型的前提下, 重构最影响云上性能和可用性的部分, 也就是存储和恢复.

Aurora避开了"每个事务都要分布式共识"这条路. 它用quorum持久化日志, 但不提供任意分片多主写入和全球外部一致性事务.

这是非常务实的设计. 绝大多数OLTP应用需要的是"比自建MySQL更可靠、更快恢复、更少运维", 而不是"全球分布式serializable事务".

AWS RDS Multi-AZ则是这条路线里更保守的一端. Multi-AZ DB instance deployment解决的是"主库挂了怎么办", 底层更像同步块复制加自动提升standby; Multi-AZ DB cluster deployment进一步解决"能不能让standby也承担读, 并降低写延迟和故障切换时间", 底层使用数据库引擎native replication. 它们的共同点是尽量不改变数据库内核哲学, 把复杂度放在托管、复制和故障切换编排里.

### TiDB: push complexity into execution layer

TiDB的路线是开源分布式SQL: 保持MySQL协议和生态亲和力, 底层用Raft和MVCC提供水平扩展, 上层用SQL优化器和MPP执行引擎处理复杂查询.

它没有TrueTime, 所以不会走Spanner的外部一致性路线. 它也不是Aurora式共享存储, 因为数据切分和Raft group是真实暴露在系统行为里的.

TiDB的挑战是平衡"像MySQL"和"是分布式数据库". 用户越把它当透明MySQL, 越容易踩到热点、大事务、执行计划和跨Region延迟的问题. 用户越理解分布式代价, 越能用好它.

### AlloyDB: enhance PostgreSQL without breaking compatibility

AlloyDB的哲学是: PostgreSQL生态很强, 不要轻易打破它. 云厂商可以在存储、缓存、自动调优、读池、可用性、备份恢复、分析加速上做大量工程, 但用户看到的仍然应该是PostgreSQL.

这条路线对企业迁移非常友好. 它没有Spanner那样的建模成本, 也比GCP Cloud SQL PostgreSQL更激进. 但它的边界也很清楚: PostgreSQL兼容性既是资产, 也是约束.

## Trade-off Spectrum

可以从三个轴看这些系统.

### Consistency vs latency

```text
更强一致/更高延迟倾向
Spanner -> TiDB -> Aurora/AlloyDB -> GCP Cloud SQL
更低延迟/更少分布式协调倾向
```

这个排序不是绝对性能排序, 而是提交路径复杂度排序. GCP Cloud SQL单机事务路径最短. Aurora多了存储quorum. TiDB多了分布式KV和2PC. Spanner多了Paxos group, TrueTime和外部一致性语义.

### Generality vs specialization

| 定位 | 代表系统 |
|---|---|
| 通用分布式SQL | Spanner, TiDB |
| PostgreSQL/MySQL增强 | Aurora, AlloyDB |
| 托管传统数据库 | AWS RDS, GCP Cloud SQL |
| 托管高可用传统数据库 | AWS RDS Multi-AZ, GCP Cloud SQL HA |
| 业务定制SQL层 | F1 |

F1很有意思. 它不是最通用的系统, 但在Google广告业务里非常有效. 它说明一件事: 数据库越理解业务局部性, 越能优化分布式代价.

### System complexity vs user responsibility

Spanner系统内部极其复杂, 但用户也要承担schema和事务建模责任. Aurora系统内部复杂, 但用户责任更接近传统MySQL/PostgreSQL. GCP Cloud SQL内部复杂度对用户最透明, 但它也不替用户解决架构上限.

| System | Internal complexity | User modeling responsibility |
|---|---|---|
| GCP Cloud SQL | Medium | Low |
| AWS RDS Multi-AZ | High | Low |
| Aurora | High | Low-Medium |
| AlloyDB | High | Low-Medium |
| TiDB | High | Medium-High |
| Spanner | Very High | High |
| F1 | Very High | High, often domain-specific |

## Practical Guidance

### 选择GCP Cloud SQL

如果系统规模还没有超过单机数据库边界, GCP Cloud SQL通常是最务实的选择.

适合:

* 普通Web应用.
* 中小型SaaS.
* 成本敏感系统.
* 团队更熟悉MySQL/PostgreSQL/SQL Server.
* 主要需求是托管、备份、补丁和故障切换.

不要因为"云原生"四个字过早选择分布式数据库. 单机数据库的事务语义、调试工具和运维经验仍然非常有价值.

### 选择Aurora

如果你在AWS上, 已经接近传统AWS RDS for MySQL/PostgreSQL的性能、可用性或恢复边界, Aurora是自然升级路径.

适合:

* Region内高吞吐OLTP.
* 希望兼容MySQL/PostgreSQL生态.
* 需要更快failover和更强存储可靠性.
* 读多写少, 可以利用read replica扩展读.

不适合:

* 多Region强一致写入.
* 需要自动水平写扩展.
* 大规模分布式分析查询.

### 选择AWS RDS Multi-AZ DB instance

如果你需要的是传统数据库的高可用, 而不是读扩展或云原生存储重构, AWS RDS Multi-AZ DB instance是最直接的选择.

适合:

* 普通生产OLTP.
* 希望故障时自动切换到standby.
* 不希望应用读写分离.
* 成本和复杂度都要低于cluster形态.
* 想要类似DRBD的同步物理主备, 而不是数据库层读副本.

注意:

* standby不承担读流量.
* 它提升可用性, 不提升写扩展能力.
* 性能模型仍然接近传统单主数据库.
* 因为提交路径要等待跨AZ同步, 写延迟可能高于Single-AZ.

### 选择AWS RDS Multi-AZ DB cluster

如果你希望继续使用AWS RDS for MySQL/PostgreSQL, 但需要更高可用性、更快failover和一定读扩展, 可以考虑Multi-AZ DB cluster.

适合:

* 读流量较多, 希望两个standby承担读.
* 希望比传统Multi-AZ DB instance有更低写延迟和更短故障切换时间.
* 不想迁移到Aurora, 仍希望保留AWS RDS数据库形态.

边界:

* 目前主要面向AWS RDS for MySQL和AWS RDS for PostgreSQL.
* 仍然是单writer, 不是多主分布式SQL.
* 不等价于Aurora cluster, 底层存储架构不同.

### 选择AlloyDB

如果你在Google Cloud上, 想要PostgreSQL兼容, 但GCP Cloud SQL PostgreSQL不够用, AlloyDB值得考虑.

适合:

* PostgreSQL重度用户.
* 企业迁移, 不想重写应用.
* 需要更好的读扩展、自动管理和性能优化.
* 有一定HTAP需求, 但不想直接上Spanner或BigQuery作为主库.

边界:

* 它不是Spanner.
* PostgreSQL兼容性意味着它不会把你的schema自动变成全球分布式数据模型.

### 选择Spanner

如果业务真的需要跨地域强一致、水平写扩展和高可用, Spanner是少数成熟选择之一.

适合:

* 全球账户系统.
* 金融账本类强一致系统.
* 多Region active-active需求.
* 数据规模和可用性要求超过单机/单Region数据库.

前提:

* 团队愿意为schema设计付出成本.
* 能接受写延迟和成本.
* 事务边界清晰, 访问模式能围绕主键和局部性设计.

### 选择TiDB

如果你需要MySQL协议兼容、水平扩展、开源可控和HTAP能力, TiDB很有吸引力.

适合:

* MySQL分库分表后想收敛到分布式SQL.
* 单表/总数据量超过单机舒适区.
* 需要在线扩容.
* 同一份数据既服务OLTP, 又有近实时分析需求.

注意:

* 热点写不是自动消失.
* 大事务仍然危险.
* 执行计划和统计信息很重要.
* 分布式数据库不是MySQL的无限加强版.

## 为什么Aurora不能轻易演化成Spanner

Aurora和Spanner都很优秀, 但它们不是同一条路上的前后版本.

Aurora的基本假设是单writer数据库引擎加分布式共享存储. 它的兼容性、性能和可用性都围绕这个假设优化. 要把Aurora变成Spanner式系统, 至少要改变:

* 数据所有权: 从页面/表空间变成key range/replica group.
* 写入模型: 从单writer变成多分片协调提交.
* 复制协议: 从日志quorum持久化变成每个分片的共识复制.
* 时间模型: 需要全局事务顺序, 甚至类似TrueTime的时间边界或等价机制.
* SQL执行: 从单节点执行模型变成分布式计划、shuffle、下推和跨分片代价模型.
* schema设计: 用户必须理解数据局部性和热点.

这不是"加一个功能"的问题, 而是重写系统哲学.

反过来也一样. Spanner很难变成Aurora那样低迁移成本的MySQL/PostgreSQL兼容数据库, 因为它从底层就要求用户接受分布式数据模型.

## 为什么Spanner-like系统仍然少

Spanner论文已经很多年了, 但真正成熟的Spanner-like系统仍然少. 原因很现实:

* TrueTime这类基础设施很难复制. GPS/原子钟不是买几台机器就能得到的能力, 更难的是把它变成全公司可依赖的服务.
* 分布式事务数据库的测试难度极高. 网络分区、时钟漂移、leader切换、事务恢复、schema变更都可能组合出复杂故障.
* 成本高. 为了强一致和高可用, 系统要复制更多数据, 等待更多网络往返, 保留更多版本.
* 市场需求没有想象中大. 大量业务用单Region Aurora/GCP Cloud SQL/PostgreSQL已经足够.
* 用户建模成本高. 很多团队并不想为了数据库学习新的数据局部性模型.

所以Aurora路线会更普及, Spanner路线会更稀缺. 这不是因为Spanner不够好, 而是它解决的是更难、更窄、更昂贵的问题.

## Conclusion

云原生关系型数据库没有唯一正确架构.

Spanner/F1回答的是: 如果关系数据库必须全球分布式, 怎么把一致性、SQL和数据局部性统一起来?

Aurora回答的是: 如果大多数应用仍然想要MySQL/PostgreSQL语义, 能不能重写存储层, 让它在云上更快、更可靠?

AlloyDB回答的是: 能不能在PostgreSQL兼容边界内, 尽量利用云基础设施提升性能、可用性和管理效率?

GCP Cloud SQL回答的是: 能不能让用户少管数据库机器?

TiDB回答的是: 能不能用开源方式提供MySQL兼容的分布式SQL和HTAP能力?

统一的洞察是: 云数据库设计的本质不是"分布式越多越先进", 而是选择一个复杂度边界.

复杂度可以在数据库内核里, 在存储层里, 在SQL执行层里, 在schema设计里, 或者在应用架构里. 没有系统能消灭复杂度, 好系统只是把复杂度放在最值得放的位置.

## 参考资料

* [Spanner: TrueTime and external consistency](https://cloud.google.com/spanner/docs/true-time-external-consistency)
* [Cloud Spanner Service Level Agreement](https://cloud.google.com/spanner/sla)
* [Spanner: Google's Globally-Distributed Database](https://research.google.com/archive/spanner.html)
* [F1: A Distributed SQL Database That Scales](https://research.google.com/pubs/archive/41344.pdf)
* [Spanner schema and data model](https://cloud.google.com/spanner/docs/schema-and-data-model)
* [Spanner query optimizer overview](https://cloud.google.com/spanner/docs/query-optimizer/overview)
* [Amazon Aurora: Design considerations for high throughput cloud-native relational databases](https://www.amazon.science/publications/amazon-aurora-design-considerations-for-high-throughput-cloud-native-relational-databases)
* [Amazon Aurora Service Level Agreement](https://aws.amazon.com/rds/aurora/sla/)
* [Amazon Aurora storage](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Overview.StorageReliability.html)
* [High availability for Amazon Aurora](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.AuroraHighAvailability.html)
* [Amazon RDS Service Level Agreement](https://aws.amazon.com/rds/sla/)
* [Amazon RDS Multi-AZ deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html)
* [Amazon RDS Multi-AZ DB instance deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html)
* [Failing over a Multi-AZ DB instance for Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.Failover.html)
* [Amazon RDS Multi-AZ DB cluster deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html)
* [AlloyDB overview](https://cloud.google.com/alloydb/docs/overview)
* [AlloyDB Service Level Agreement](https://cloud.google.com/alloydb/sla)
* [AlloyDB business continuity capabilities](https://cloud.google.com/blog/products/databases/understanding-alloydb-business-continuity-capabilities)
* [GCP Cloud SQL overview](https://cloud.google.com/sql/docs/introduction)
* [GCP Cloud SQL Service Level Agreement](https://cloud.google.com/sql/sla)
* [GCP Cloud SQL high availability](https://cloud.google.com/sql/docs/mysql/high-availability)
* [Google Cloud Persistent Disk](https://cloud.google.com/compute/docs/disks/persistent-disks)
* [Google Cloud regional disk synchronous replication](https://cloud.google.com/compute/docs/disks/about-regional-persistent-disk)
* [TiDB Cloud Service Level Agreement](https://www.pingcap.com/legal/service-level-agreement-for-tidb-cloud-services/)
* [High Availability in TiDB Cloud](https://docs.pingcap.com/tidbcloud/serverless-high-availability/)
* [TiDB Optimistic Transaction Model](https://docs.pingcap.com/tidb/stable/optimistic-transaction/)
* [TiDB Pessimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction/)
* [TiDB: A Raft-based HTAP Database](https://www.vldb.org/pvldb/vol13/p3072-huang.pdf)
