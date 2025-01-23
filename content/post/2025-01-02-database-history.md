---
title: "A Brief History of Database History"
date: 2025-01-23T10:31:07+08:00
draft: false
---

去年读了《数据库简史》, 发现每个技术方向都有一些有趣的事情, 我们每个人其实都在历史浪潮中.

以古鉴今, 多读读历史能让我们少走很多弯路.

Snowflake的创始人Marcin Żukowski有个[采访](https://www.youtube.com/clip/UgkxPjf-NvN0kNaj2QV-V534SLNN4iToricC)中说得很好
> I mean our field (database), especially computer science, has been around for you know decades, like 60, 70 years. The new generations often forget things, or don't really know that someths has been tried or tested, and there is a lot of depth and wisdom in old research. Maybe that's something I would encourage everybody to at least look into, because we focus on the brand new things over and over, but we don't realize how much we can learn from the old things.

所以, 以`A Brief History of Database History`为题, 在[SZDIY](https://szdiy.org/)社区开了一个小讲座, 想不到反响还不错, 私信问我要Slides的小伙伴不下10位.

大家最关心的还是NoSQL, 看起来最近MongoDB的营销产生了一些效果.

至于Redis是不是数据库的问题, 也有小伙伴问到.

## 数据库相关书籍
从入门到深入, 基本上第一本已经可以应付数据库相关的应用开发和面试了.
- Avi Silberschatz, Henry F. Korth, S. Sudarshan.Database System Concepts, Seventh Edition. 2019. 
- Peter Bailis, Joseph M. Hellerstein, Michael Stonebraker. Readings in Database Systems, 5th Edition](http://www.redbook.io/). 2015. 
- Jim Gray, Andreas Reuter. Transaction Processing: Concepts and Techniques. 1992.

如果要探究数据库内核, 数据结构、编译原理基础知识肯定必不可少. 

现在数据库都是C-S架构, 如果做些接入层方面的工作(如数据库驱动, 数据库中间件), 计算机网络TCP/IP方面的知识必不可少.

## 参考资料
### 英文
- [CMU 15-721 Advanced Database Systems](https://15721.courses.cs.cmu.edu/spring2023/schedule.html). 2023.
- Michael Stonebraker, Andrew Pavlo. [What Goes Around Comes Around... And Around...](https://db.cs.cmu.edu/papers/2024/whatgoesaround-sigmodrec2024.pdf). 2024.
- Andy Pavlo. [Databases in 2023: A Year in Review](https://www.cs.cmu.edu/~pavlo/blog/2024/01/2023-databases-retrospective.html). 2024.
- Richard Hipp. [The Untold Story of SQLite](https://open.spotify.com/episode/3AVbDpEiZqgYyqJSq9FXCY). 2021.
- Alex Petrov. Database Internals. 2020.
- Diego Ongaro. [In Search of an Understandable Consensus Algorithm](https://raft.github.io/raft.pdf). 2014.
- [Bytebytego Newsletter](https://blog.bytebytego.com/).

### 中文
- 徐飞. 2019.大数据 浪潮之巅. 公众号： 飞总聊IT
- 盖国强. 2024. 《数据库简史》, 墨天轮社区
- 吴军. 浪潮之巅, 第四版. 2019. 里面专门一章讲了Oracle的故事.

### 其他
- Marcin Żukowski获得CWI Dijkstra Fellowship的采访
{{< youtube id="moQY_eiHCTs" >}}