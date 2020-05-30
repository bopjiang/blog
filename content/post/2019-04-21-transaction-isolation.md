---
date: 2019-04-21
categories:
  - blog
description: transaction isolation
tags:
  - Database
title: MySQL和TiDB事务区别
---


我们知道, MySQL的默认隔离级别是可重复读(RR, Repeatable Read). TiDB是快照隔离 (SI, Snapshot Isolation), 虽然对外显示为Repeatable Read).

TiDB 使用 Percolator 事务模型, 冲突检测只在事务提交时才触发, 而MySQL则是通过锁等待机制(如SELECT ... FOR UPDATE)解决冲突问题.TiDB这样设计有好有坏, 在冲突小的情况下,由于没有锁等待,系统的并发性能更好. 但在冲突严重的情况下, 会造成事务失败增多,影响并发性能.

反映到应用开发中, 我们会发现, 在很多场景, MySQL事务提交成功, 但是TiDB事务提交却可能会失败.
如果应用代码有在事务执行过程中穿插业务判断逻辑, 是不能依赖TiDB自带的事务重试机制的. 这时,要显式的关闭事务重试, 重试逻辑必须放到业务层来做.

## 例子
下面三个例子, 从TiDB和MySQL执行结果和逻辑的区别, 我们可以看到两个数据库系统在事务处理上的差别.

本文中MySQL的版本是8.0.15, TiDB的版本是v2.1.7, 事务隔离级别都为默认值Repeatable Read.


### 例1: Update在事务中处理逻辑不同
创建表t1, 语句如下:
```sql
CREATE TABLE `t1` (
  `a` int(11) NOT NULL,
  `b` int(11) DEFAULT NULL,
  PRIMARY KEY (`a`)
)
```

在MySQL和TiDB中分别执行下面的两个事务, 执行时序如下:

|    Time    |   Tx1              |  Tx2      |
| ---------- | -----------------  |-----------|
|     t0     |  begin;            |           |
|     t1     |  select * from t1; |           |
|     t2     |                    |   begin;                       |
|     t3     |                    |   insert into t1 values(1,10); |
|     t4     |                    |   commit;                      |
|     t5     |  update t1 set b=b+10 where a = 1;   |           |
|     t6     |  commit;                             |           |
|     t7     |  select * from t1;                   |           |


MySQL, t7时刻,select语句的执行结果是
```bash
select * from t1;
+---+------+
| a | b    |
+---+------+
| 1 |   20 |
+---+------+
1 row in set (0.00 sec)
```


但在TiDB中执行结果却是:
```bash
mysql> select * from t1;
+---+------+
| a | b    |
+---+------+
| 1 |   10 |
+---+------+
1 row in set (0.01 sec)
```

对于MySQL,在可重复读级别下, 事务中的update操作, 为了不读到脏数据, 是当前读, 而且要加写锁. 虽然事务1的快照读是取的t1时刻的版本(MySQL默认的事务开始时间是事务执行的第一条语句), 但是在t5时刻的update操作, 是要读到当前最新版本的, 这时是能读到Tx2的insert语句的执行结果a=1这行的.

对于TiDB, update一直是快照读, t5时刻是读不到Tx2的已提交的a=1这行数据的, t5时刻的update操作自然没有修改到a=1这行数据.


### 例2 更新冲突处理逻辑不同
如果a=1这行在Tx1启动时已存在, Tx2在t3时刻更新了a=1这行的数据, 并完成提交. 同样, TiDB中,t5时刻Tx1在update时, 也是读到的过期数据, 但是在事务提交时, 才会报写冲突, 事务提交失败.

事务执行时序如下:

|    Time    |   Tx1              |  Tx2      |
| ---------- | -----------------  |-----------|
|     t0     |  begin;            |           |
|     t1     |  select * from t1; |           |
|     t2     |                    |   begin;                       |
|     t3     |                    |   update t1 set b=100 where a = 1;  |
|     t4     |                    |   commit;                      |
|     t5     |  update t1 set b=b+10 where a = 1;   |           |
|     t6     |  commit;                             |           |
|     t7     |  select * from t1;                   |           |

TiDB Tx1执行结果如下:
~~~bash
ERROR 1105 (HY000): [try again later]: WriteConflict: startTS=407855583704121345, conflictTS=407855586561228801, key={tableID=49, handle=1} primary={tableID=49, handle=1}
~~~

在MySQL中, 事务会提交成功, t7时刻select查询返回为:
~~~bash
mysql> select * from t1;
+---+------+
| a | b    |
+---+------+
| 1 |  110 |
+---+------+
1 row in set (0.00 sec)

~~~

### 例3 Select ... For Update的执行区别

假设表t1中有(2,1)这行数据,事务执行时序如下:

|    Time    |   Tx1              |  Tx2      |
| ---------- | -----------------  |-----------|
|     t0     |  begin;            |           |
|     t1     |  select * from t1 where a = 2 for update; |         |
|     t2     |                    |                        |
|     t3     |                    |   update t1 set b=b+20 where a = 2;  |
|     t4     |                    |                         |
|     t5     |  update t1 set b=b*2 where a = 2;   |          |
|     t6     |  commit;           |   (MySQL: Tx2 BLOCK UNTIL Tx1 commited)       |
|     t7     |  select * from t1 where a = 2; |       |

MySQL,Tx1和Tx2都可以成功提交, t7时刻, select执行结果为:
~~~bash
select * from t1 where a = 2;
+---+------+
| a | b    |
+---+------+
| 2 |   22 |
+---+------+
~~~
但Tx2从t3时刻开始,会被阻塞,一直到t6时刻, Tx1完成提交后, Tx2才能提交.

TiDB中, Tx1提交会失败(WriteConflict).  t7时刻, select执行结果为:
~~~bash
mysql> select * from t1 where a=2;
+---+------+
| a | b    |
+---+------+
| 2 |   21 |
+---+------+
1 row in set (0.00 sec)
~~~


## 小结

TiDB在事务提交时,检测冲突. 有冲突时,后提交事务的失败.

TiDB使用Percolator事务模型, 并发控制模型感觉像是Timestamp-Base + MutliVersion的综合, 是无锁的并发控制方案.

但是TiDB这样的分布式数据库系统, 如果像MySQL使用的锁机制解决冲突的话, 光分布式锁的开销将会非常大.