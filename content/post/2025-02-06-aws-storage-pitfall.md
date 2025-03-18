---
title: "AWS存储的坑"
date: 2025-02-06T11:18:10+08:00
draft: false
---

在最近5年使用AWS的历程中, 出现的最严重的两次故障, 都跟存储有关.

## Aurora Instance Local Storage Full导致数据库宕机

这个问题的起因是有DBA同事想定位某个生产环境Aurora数据库CPU毛刺问题, 想查看下CPU上升时有哪些SQL正在执行.
初衷是好的, 按照他之前的运维经验, 打开General Log, 如果系统性能没有明显下降, 在产线采集一段时间应该不会有什么问题.

偏偏就在打开General Log的那天凌晨, Aurora数据库宕机了, 数据库突然连不上, 没有任何提示.紧急联系AWS的最高级别技术支持, 5分钟左右就有人介入处理了(好像要买专门的support服务才有这个待遇). 当时给的建议是, 实例规格不够, 让我们升级实例规格. DBA同学听从了建议, 升级了一倍实例规格(从db.r5.xlarge到db.r5.2xlarge).

可惜, 扛了几天, 数据库又跪了! 这次Support才分析到数据库宕机的本质原因是Instance Local Storage Full, 给出的建议还是我们升级规格, 到db.r5.4xlarge.

这时候老板们就怒了, 发出了灵魂拷问:
* 升级到db.r5.2xlarge后, 数据库负载很低, 1分钟级别的CPU占有率P99值已经不到10%, 再升级一倍不是浪费钱吗?
* Aurora不是号称存算分离吗? 为什么一个小小的Instance Local Storage模块会导致数据库崩溃.
* 到底是什么原因导致Local Storage Full?

这时候DBA同学才小心翼翼的道出, 前几天为了配合开发定位问题, 打开了General Log.关闭General Log后, Local Storage没有再继续下降, 问题解决. 

至于后续AWS内部怎么定性这个问题, 就不得而知了.

### 教训
AWS Aurora不是完全的Serverless服务, 计算节点也是EC2 Instance.

* Aurora的计算节点, 不光CPU/内存, 本地磁盘/网络都需要监控.
* Aurora不要开启General Log. 可以使用Audit Log替代General Log功能. <br/>
  Aurora的Audit Log貌似没有写Instance Local Storage.
* 数据库系统级别的变更操作, 需要有统一记录. <br/>
  出现问题时, 可以根据变更历史分析潜在的原因, 毕竟绝大部分生产环境问题都是变更导致的.


<!---
## Amazon MQ for RabbitMQ的Broker EBS磁盘空间满, 导致MQ不可用
-->

## 参考

* AWS Knowledge Center: [How can I troubleshoot local storage issues in Aurora PostgreSQL-Compatible instances?](https://repost.aws/knowledge-center/postgresql-aurora-storage-issue)