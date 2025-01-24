---
title: "SQL反模式"
date: 2025-01-23T16:59:58+08:00
draft: false
---

这是阅读SQL 反模式(SQL Antipatterns: Avoiding the Pitfalls of Database Programming)的一些笔记.

> 所谓专家, 就是在一个很小的领域里把所有错误都犯过的人

## 逻辑数据库设计反模式 Logical Database Design Antipatterns

### 使用分隔符存储多值属性
```sql
CREATE TABLE Products (
    product_id   SERIAL PRIMARY KEY,
    product_name VARCHAR(1000),
    account_id   VARCHAR(100)    -- comma-separated list
);

INSERT INTO Products (product_id, product_name, account_id)
VALUES (DEFAULT, 'Visual C++', '12,34');
```

带来后果:
* 查询困难, 可能需要做正则匹配, 而且用不上索引.
* 插入,更新, 删除困难, 需要读出再写入.
* 聚合操作困难
* 数据校验困难
* 字段长度限制导致列表也有个数限制, 且跟每个元素的长度相关.

解决办法:
* 增加一张交叉表(Intersection Table)

```sql
CREATE TABLE Contacts (
    product_id BIGINT UNSIGNED NOT NULL,
    account_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (product_id, account_id),
    KEY(account_id)
);

INSERT INTO Contacts (product_id, account_id)
VALUES (123, 12), (123, 34), (345, 23), (567, 12), (567, 34);
```

* PostgreSQL中有[Arrays](https://www.postgresql.org/docs/current/arrays.html)类型, 特定场景可以尝试使用.


> 对一个字符串做索引的开销会比int高得多.

### Hierarchical Structuere: Always Depend on One’s Parent

A good book that covers hierarchical queries is Joe Celko’s Trees and Hierarchies in SQL for Smarties [Cel04]. Another book that covers trees and even graphs is SQL Design Patterns [Tro06] by Vadim Tropashko.

### Primary Key: id or xx_id

### Foreign Keys Restrictions
书中观点与目前(2020s)大家的最佳实践不一样, 高并发的互联网应用往往不用外键约束.

Reason not use foreign keys, from [skeema](https://www.skeema.io/docs/options/#lint-has-fk) doc.

> Companies that restrict foreign keys typically do so for these reasons:
> - Foreign keys introduce nontrivial write latency, due to the extra locking. In a high-write-volume OLTP environment, the performance impact can be quite substantial.
> - Foreign keys are problematic when using online schema change tools. Percona’s pt-osc allows them, albeit with extra complexity and risk. Most other OSC tools – gh-ost, Spirit, fb-osc, LHM – don’t support foreign keys at all.
> - Conceptually, foreign keys simply don’t work across a sharded environment. Although they still function within a single shard, application-level checks become necessary anyway for cross-shard purposes. As a result, sharded companies tend to converge on application-level checks exclusively.

### 实体-属性-值 EAV(Entity-Attribute-Value)

### 多态关联 Polymorphic Associations
使用公共父表(Common Super-Table), 表之间的继承.

### 多列属性 Multicolumn Attributes
```sql
CREATE TABLE Bugs (
    bug_id SERIAL PRIMARY KEY, description VARCHAR(1000),
    tag1 VARCHAR(20),
    tag2 VARCHAR(20),
    tag3 VARCHAR(20)
);
```

### 元数据分裂 Metadata Tribbles

## 物理数据库设计反模式 Physical Database Design Antipatterns

### 使用浮点数
改使用`decimal` , 在MySQL, PostgreSQL中同`numeric`等价.

### 枚举值

### 幽灵文件 Phantom Files

### 乱用索引 Index Shotgun

## 查询反模式 Query Antipatterns

### NULL使用

### 模凌两可的分组 Ambiguous Groups

### 随机选择 Random Selection

### Poor Man’s Search Engine

### 复杂查询 Spaghetti Query

### Implicit Columns 隐式列

## 应用开发反模式 Application Development Antipatterns

### 明文密码

### SQL注入

### 伪键洁癖 Pseudokey Neat-Freak

### 非礼勿视 See No Evil

### Diplomatic Immunity

### Magic Beans

## 参考书目

- [BMMM98] WilliamJ.Brown,RaphaelC.Malveau,HaysW.McCormickIII,and Thomas J. Mowbray. AntiPatterns. John Wiley & Sons, New York, NY, 1998.
- [Cel04] Joe Celko. Joe Celko’s Trees and Hierarchies in SQL for Smarties. Morgan Kaufmann Publishers, San Francisco, CA, 2004.
- [Cel05] Joe Celko. Joe Celko’s SQL Programming Style. Morgan Kaufmann Publish- ers, San Francisco, CA, 2005.
- [Cod70] Edgar F. Codd. A Relational Model of Data for Large Shared Data Banks. Communications of the ACM. 13[6]:377–387, 1970, June.
- [Eva03] Eric Evans. Domain-Driven Design: Tackling Complexity in the Heart of Software. Addison-Wesley Longman, Reading, MA, First, 2003.
- [Fow03] Martin Fowler. Patterns of Enterprise Application Architecture. Addison- Wesley Longman, Reading, MA, 2003.
- [Gla92] Robert L. Glass. Facts and Fallacies of Software Engineering. Addison- Wesley Professional, Boston, MA, 1992.
- [Gol91] David Goldberg. What Every Computer Scientist Should Know About Floating-Point Arithmetic. ACM Comput. Surv.. 5–48, 1991, March.
- [GP03] Peter Gulutzan and Trudy Pelzer. SQL Performance Tuning. Addison-Wesley, Reading, MA, 2003.
- [HLV05] Michael Howard, David LeBlanc, and John Viega. 19 Deadly Sins of Soft- ware Security. McGraw-Hill, Emeryville, CA, 2005.
- [HT00] Andrew Hunt and David Thomas. The Pragmatic Programmer: From Jour- neyman to Master. Addison-Wesley, Reading, MA, 2000.
- [Lar04] Craig Larman. Applying UML and Patterns: an Introduction to Object-Oriented Analysis and Design and Iterative Development. Prentice Hall, Englewood Cliffs, NJ, Third, 2004.
- [RTH11] Sam Ruby, Dave Thomas, and David Heinemeier Hansson. Agile Web Development with Rails, 4th Edition. The Pragmatic Bookshelf, Raleigh, NC and Dallas, TX, 2011.
- [Spo02] Joel Spolsky. The Law of Leaky Abstractions. www.joelonsoftware.com, http://www.joelonsoftware.com, 2002.
- [SZTZ08] Baron Schwartz, Peter Zaitsev, Vadim Tkachenko, Jeremy Zawodny, Arjen Lentz, and Derek J. Balling. High Performance MySQL. O’Reilly & Associates, Inc., Sebastopol, CA, Second, 2008.
- [Tro06] Vadim Tropashko. SQL Design Patterns. Rampant Techpress, Kittrell, NC, USA, 2006.