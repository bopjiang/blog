---
title: "CTE & Window Function: MySQL 8.0的新特性"
date: 2026-04-26T12:00:00+08:00
draft: false
categories:
  - tech
---

MySQL 8.0补齐了不少现代SQL能力, 其中最常用的两个是:

* CTE(Common Table Expression), 也就是`WITH ... AS (...)`
* Window Function, 也就是`xxx() OVER (PARTITION BY ... ORDER BY ...)`

以前在MySQL 5.7里写Top N, 分组排名, 中位数这类题目, 经常需要用户变量或多层子查询. 到了MySQL 8.0, 写法终于接近PostgreSQL这类数据库.

这篇用LeetCode的[Median Employee Salary](https://leetcode.cn/problems/median-employee-salary/)作为例子.

## 测试数据

```sql
CREATE TABLE IF NOT EXISTS Employee (
    id INT PRIMARY KEY,
    company VARCHAR(255),
    salary INT
);

TRUNCATE TABLE Employee;

INSERT INTO Employee (id, company, salary) VALUES (1, 'A', 2341);
INSERT INTO Employee (id, company, salary) VALUES (2, 'A', 341);
INSERT INTO Employee (id, company, salary) VALUES (3, 'A', 15);
INSERT INTO Employee (id, company, salary) VALUES (4, 'A', 15314);
INSERT INTO Employee (id, company, salary) VALUES (5, 'A', 451);
INSERT INTO Employee (id, company, salary) VALUES (6, 'A', 513);
INSERT INTO Employee (id, company, salary) VALUES (7, 'B', 15);
INSERT INTO Employee (id, company, salary) VALUES (8, 'B', 13);
INSERT INTO Employee (id, company, salary) VALUES (9, 'B', 1154);
INSERT INTO Employee (id, company, salary) VALUES (10, 'B', 1345);
INSERT INTO Employee (id, company, salary) VALUES (11, 'B', 1221);
INSERT INTO Employee (id, company, salary) VALUES (12, 'B', 234);
INSERT INTO Employee (id, company, salary) VALUES (13, 'C', 2345);
INSERT INTO Employee (id, company, salary) VALUES (14, 'C', 2645);
INSERT INTO Employee (id, company, salary) VALUES (15, 'C', 2645);
INSERT INTO Employee (id, company, salary) VALUES (16, 'C', 2652);
INSERT INTO Employee (id, company, salary) VALUES (17, 'C', 65);
```

## CTE是什么

CTE可以理解为"只在当前SQL语句里可见的临时命名结果集".

```sql
WITH ranked_employee AS (
    SELECT
        id,
        company,
        salary,
        ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) AS rn
    FROM Employee
)
SELECT *
FROM ranked_employee
WHERE company = 'A';
```

CTE不一定等价于临时表, 优化器可能会选择合并、物化或重写. 日常写SQL时, 它最大的价值是把复杂查询拆成几个可读的步骤.

递归CTE也很有用, 例如生成序列、处理树形结构. 本文先只讨论非递归CTE.

## Window Function是什么

窗口函数和`GROUP BY`的差异在于:

* `GROUP BY`会把多行聚合成一行.
* Window Function保留原始行, 只是在每一行旁边算出一个窗口内的值.

例如按公司排序员工工资:

```sql
SELECT
    id,
    company,
    salary,
    ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) AS rn
FROM Employee
ORDER BY company, rn;
```

`PARTITION BY company`表示每个公司单独计算, `ORDER BY salary, id`表示公司内部先按工资排序, 工资相同再按`id`排序.

这里的`id`很重要. 如果只写`ORDER BY salary`, C公司有两个人工资都是`2645`, 它们的先后顺序在SQL语义上是不稳定的.

## 三个排名函数

排名函数里最常用的是`ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`.

用C公司数据看最清楚:

```sql
SELECT
    id,
    company,
    salary,
    ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) AS row_number_,
    RANK() OVER (PARTITION BY company ORDER BY salary) AS rank_,
    DENSE_RANK() OVER (PARTITION BY company ORDER BY salary) AS dense_rank_
FROM Employee
WHERE company = 'C'
ORDER BY salary, id;
```

结果:

```text
+----+---------+--------+-------------+-------+-------------+
| id | company | salary | row_number_ | rank_ | dense_rank_ |
+----+---------+--------+-------------+-------+-------------+
| 17 | C       |     65 |           1 |     1 |           1 |
| 13 | C       |   2345 |           2 |     2 |           2 |
| 14 | C       |   2645 |           3 |     3 |           3 |
| 15 | C       |   2645 |           4 |     3 |           3 |
| 16 | C       |   2652 |           5 |     5 |           4 |
+----+---------+--------+-------------+-------+-------------+
```

区别:

* `ROW_NUMBER()`不关心并列, 每一行都有唯一序号: `1, 2, 3, 4, 5`.
* `RANK()`有并列, 并且跳号: `1, 2, 3, 3, 5`.
* `DENSE_RANK()`有并列, 但不跳号: `1, 2, 3, 3, 4`.

如果要"每组取前3行", 用`ROW_NUMBER()`. 如果要"工资前三名, 并列也算", 用`RANK()`或`DENSE_RANK()`, 取决于是否允许跳号.

中位数这题要取排序后第`N/2`附近的行, 所以用`ROW_NUMBER()`最直接.

## 解法

每个公司内部按工资升序排序, 同时算出公司总人数:

```sql
WITH ordered_employee AS (
    SELECT
        id,
        company,
        salary,
        ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) AS rn,
        COUNT(*) OVER (PARTITION BY company) AS cnt
    FROM Employee
)
SELECT
    id,
    company,
    salary
FROM ordered_employee
WHERE rn >= cnt / 2
  AND rn <= cnt / 2 + 1
ORDER BY company, salary, id;
```

为什么这个条件能处理奇偶?

* `cnt = 6`, `cnt / 2 = 3`, 选`rn >= 3 AND rn <= 4`, 也就是第3和第4行.
* `cnt = 5`, `cnt / 2 = 2.5`, 选`rn >= 2.5 AND rn <= 3.5`, 整数`rn`只有第3行满足.

输出:

```text
+----+---------+--------+
| id | company | salary |
+----+---------+--------+
|  5 | A       |    451 |
|  6 | A       |    513 |
| 12 | B       |    234 |
|  9 | B       |   1154 |
| 14 | C       |   2645 |
+----+---------+--------+
```

注意C公司有两条`2645`. 因为SQL里写了`ORDER BY salary, id`, 所以中位数员工稳定为`id = 14`. 如果只按`salary`排序, MySQL, PostgreSQL, TiDB都不承诺两条`2645`的内部顺序, 结果可能变成`id = 15`.

## 另一种写法

也可以把中位数位置直接算出来:

```sql
WITH ordered_employee AS (
    SELECT
        id,
        company,
        salary,
        ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) AS rn,
        COUNT(*) OVER (PARTITION BY company) AS cnt
    FROM Employee
),
median_pos AS (
    SELECT
        id,
        company,
        salary,
        rn,
        FLOOR((cnt + 1) / 2) AS left_pos,
        FLOOR((cnt + 2) / 2) AS right_pos
    FROM ordered_employee
)
SELECT
    id,
    company,
    salary
FROM median_pos
WHERE rn IN (left_pos, right_pos)
ORDER BY company, salary, id;
```

这种写法更直观:

* `cnt = 6`, 位置是`3`和`4`.
* `cnt = 5`, 位置是`3`和`3`.

## MySQL 8.0, PostgreSQL, TiDB的差异

这道题的核心SQL在三者上都能跑:

```sql
WITH ordered_employee AS (
    SELECT
        id,
        company,
        salary,
        ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) AS rn,
        COUNT(*) OVER (PARTITION BY company) AS cnt
    FROM Employee
)
SELECT id, company, salary
FROM ordered_employee
WHERE rn >= cnt / 2
  AND rn <= cnt / 2 + 1
ORDER BY company, salary, id;
```

但有几个细节值得注意.

### 1. MySQL 5.7不能这样写

CTE和窗口函数都是MySQL 8.0时代才正式进入MySQL主线的常用能力. MySQL 5.7没有`WITH`, 也没有`ROW_NUMBER() OVER (...)`.

在MySQL 5.7里, 通常要用用户变量模拟排名:

```sql
SELECT
    id,
    company,
    salary
FROM (
    SELECT
        e.*,
        @rn := IF(@company = company, @rn + 1, 1) AS rn,
        @company := company
    FROM Employee e
    CROSS JOIN (SELECT @rn := 0, @company := '') vars
    ORDER BY company, salary, id
) ranked;
```

这类写法依赖MySQL用户变量求值顺序, 可读性和可移植性都差很多.

### 2. 窗口函数不能直接写在WHERE里

下面这个SQL不应该写:

```sql
SELECT
    id,
    company,
    salary
FROM Employee
WHERE ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) = 1;
```

原因是SQL的逻辑执行顺序里, `WHERE`早于窗口函数计算. MySQL官方文档也明确说窗口函数只能出现在select list和`ORDER BY`里.

所以通常做法是:

```sql
WITH ranked AS (
    SELECT
        id,
        company,
        salary,
        ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) AS rn
    FROM Employee
)
SELECT *
FROM ranked
WHERE rn = 1;
```

PostgreSQL和TiDB也是同样的思路. 如果用的是支持`QUALIFY`的数据库, 可以少一层CTE, 但MySQL 8.0和PostgreSQL原生语法里没有`QUALIFY`.

### 3. CTE物化行为不同

CTE主要是可读性工具, 不要天然假设它一定更快.

* MySQL 8.0会对CTE做合并或物化等优化, 行为要看具体SQL和版本.
* PostgreSQL 12之前, CTE经常被当成优化屏障; PostgreSQL 12之后, 简单CTE可以被内联, 也支持`MATERIALIZED`和`NOT MATERIALIZED`提示.
* TiDB支持CTE和递归CTE, 执行计划还会受分布式执行、TiFlash下推等因素影响.

真实业务里, 复杂SQL写完后还是应该看`EXPLAIN`.

### 4. 返回类型可能不一样

PostgreSQL文档里`row_number()`, `rank()`, `dense_rank()`返回`bigint`.

MySQL和TiDB里一般也会把窗口函数结果当作整数列来处理, 但客户端驱动展示的类型细节可能不同. 如果应用层强依赖字段类型, 最好显式转换:

```sql
CAST(ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) AS SIGNED) AS rn
```

PostgreSQL里对应写法是:

```sql
CAST(ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) AS INTEGER) AS rn
```

### 5. 排序必须写完整

这是跨数据库最容易忽略的问题.

`ROW_NUMBER()`遇到并列值时, 如果`ORDER BY`不能唯一决定顺序, 数据库可以用任意顺序返回这些peer rows. 同一条SQL在不同数据库, 不同执行计划, 甚至同一数据库不同版本下, 都可能返回不同的`ROW_NUMBER()`.

所以中位数员工这题应该写:

```sql
ORDER BY salary, id
```

而不是:

```sql
ORDER BY salary
```

这不是为了好看, 是为了结果稳定.

### 6. 这道题的输出没有本质差异

如果使用本文这条带`ORDER BY salary, id`的SQL, MySQL 8.0, PostgreSQL, TiDB的结果行应该一致:

```text
+----+---------+--------+
| id | company | salary |
+----+---------+--------+
|  5 | A       |    451 |
|  6 | A       |    513 |
| 12 | B       |    234 |
|  9 | B       |   1154 |
| 14 | C       |   2645 |
+----+---------+--------+
```

差异主要在客户端展示格式和执行计划上. MySQL/TiDB命令行默认是上面这种表格样式, PostgreSQL的`psql`默认也是表格, 但边框样式不同. 真正影响结果的是排序条件是否完整, 而不是这三个数据库对`ROW_NUMBER()`语义的差异.

## 小结

CTE和Window Function让MySQL 8.0的SQL表达能力提升很多. 对应用开发来说, 最常见的收益是:

* 复杂查询可以拆成可读步骤.
* 分组排序、Top N、中位数、去重保留第一行等问题, 不再需要MySQL用户变量.
* 同一套SQL更容易迁移到PostgreSQL和TiDB.

排名函数的选择可以简单记:

* 要每行唯一序号: `ROW_NUMBER()`
* 要排名, 并列后跳号: `RANK()`
* 要排名, 并列后不跳号: `DENSE_RANK()`

这道中位数题的关键是`ROW_NUMBER()`加`COUNT(*) OVER`, 再用CTE在外层过滤目标行.

## 参考资料

* [MySQL 8.0 Reference Manual: WITH (Common Table Expressions)](https://dev.mysql.com/doc/refman/8.0/en/with.html)
* [MySQL 8.0 Reference Manual: Window Function Concepts and Syntax](https://dev.mysql.com/doc/refman/8.0/en/window-functions-usage.html)
* [MySQL 8.0 Reference Manual: Window Function Descriptions](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html)
* [PostgreSQL Documentation: Window Functions](https://www.postgresql.org/docs/current/functions-window.html)
* [PostgreSQL Documentation: WITH Queries](https://www.postgresql.org/docs/current/queries-with.html)
* [TiDB Docs: Window Functions](https://docs.pingcap.com/tidb/stable/window-functions/)
* [TiDB Docs: WITH](https://docs.pingcap.com/tidb/stable/sql-statement-with)
