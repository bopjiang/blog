---
title: "A Brief History of Database History"
date: 2025-01-02T10:31:07+08:00
draft: false
---

去年读了《数据库简史》, 发现每个技术方向都有一些有趣的事情, 我们每个人其实都在历史浪潮中.

以古鉴今, 多读读历史能让我们少走很多弯路.

Snowflake的创始人Marcin Żukowski在一个[采访](https://www.youtube.com/clip/UgkxPjf-NvN0kNaj2QV-V534SLNN4iToricC)中说得很好
> I mean our field (database), especially computer science, has been around for you know decades, like 60, 70 years. The new generations often forget things, or don't really know that somethings has been tried or tested, and there is a lot of depth and wisdom in old research. Maybe that's something I would encourage everybody to at least look into, because we focus on the brand new things over and over, but we don't realize how much we can learn from the old things.

所以, 2025年一开始, 便以`A Brief History of Database History`为题, 在[SZDIY](https://szdiy.org/)社区开了一个小讲座, 想不到反响还不错, 私信问我要Slides的小伙伴不下10位.

### 讨论
其实分享的大部分内容都是来自看过的几本书, 加上同业内人士的聊天中得到的一些八卦. 我觉得做分享, 对主讲人来说, 最大收获的是接收到大家的反馈(提问和讨论)

首先, 大家最关心的还是NoSQL, 看起来这些年MongoDB的营销产生了一些效果.
> NoSQL不是一个新技术, 在关系模型出现前的1970年代就有了, 譬如存储认证/授权信息的层级目录(hierarchical directories for storing authentication and authorization credentials).

>最近20年, NoSQL出现的本质是大家对互联网产生的大量数据的存储需求, 对数据存储有水平扩展的巨大需求. 讽刺的是, 在NoSQL数据库中大家最希望的特性往往是SQL!

其次, 怎么选择数据库?
> 选择我们最熟悉和易于维护的数据库. 分布式数据库在大部分场景都不是第一选择. 国外网友经验, 使用PostgreSQL一般不是最差的选择.

> 有了S3之类的稳定存储系统后, 不是所有东西都必须往数据库扔的.
> 我之前做过最愚蠢的设计是将图片的缩略图放入MySQL数据库, 导致存放缩略图的表急剧膨胀.

有小伙伴问Redis是不是数据库?
> `It's data structure server!` 得看你怎么使用, 当cache还是存储.
并且现在云厂商已经提供了具有Redis接口, 数据可持久化的数据库, 如[AWS MemoryDB](https://aws.amazon.com/memorydb/).

有个配置信息存储的问题, 有人说他们目前存储在Redis上的, 问是不是个好主意?
> 得看你的Redis怎么用, 持久化怎么做的, 配置的数据量有多大(Redis有单机内存限制, 如果一开始未考虑集群模式, 后面从单机切换为集群模式, 很可能涉及代码改造). 如果数据量不大, 存储在MySQL/PostgreSQL的一张表就可以了. 这是典型的EVA(Entity-Attribute-Value)反模式, 一般不推荐使用. 不过还是那句话, 方案跟你的数据规模相关. 至于用MongoDB存储一点点配置信息, 还是算了吧😓.

SQLite的使用上, 有小伙伴提到在嵌入式设备上, 他们使用SQLite替代文件系统, 在大量小文件IO的场景, 效率提升N倍. 算是数据库另辟蹊径的一种用法.

还有个人问到, PostgreSQL的吉祥物为什么是大象, 问了下ChatGTP
> PostgreSQL 的标志使用大象，是因为“大象”代表了 PostgreSQL 的强大、稳定和灵活的特性。这个符号最早由 PostgreSQL 项目的创始人之一、数据库设计师 Michael Stonebraker 提出，他认为大象是个合适的象征，因为大象在自然界中是强大且持久的，而这也恰如 PostgreSQL 作为一个数据库系统的特点。
>
>
> 具体来说，有几个原因与大象的象征性有关：
>
> 1. **强大与稳健**：大象是一种体型庞大、强壮且耐力极强的动物，象征着 PostgreSQL 作为一个具有强大处理能力和高可扩展性的数据库系统。
> 2. **象征“重量级”功能**：PostgreSQL 是一个功能丰富的数据库，支持复杂的数据类型、事务管理、完整性约束等高级功能。这种“重量级”特性与大象的体型非常契合。
> 3. **持久性和稳定性**：大象可以活几十年，体现了 PostgreSQL 作为一个长期可靠的数据库系统的特点。
> 4. **社区精神**：PostgreSQL 是一个开源项目，许多开发者和贡献者都积极参与其发展。大象的形象也可能象征着数据库的开源社区有着“团结”和“稳固”的基础。
>
> 因此，大象的形象通过其自然界中的特性，向外界传达了 PostgreSQL 的强大、可靠和持久的印象。


### 国产化

最后谈谈数据库国产化替代, 最近一次聊天中, 某位大佬预判关系型数据库这块, 国内能存活下来的只有三家: 
* 阿里云PolarDB (蚂蚁Oceanbase没说)
* TiDB
* GaussDB

我说光在深圳, 不是还有TD-SQL, 崖山(~~Gauss 100?~~), 昆仑,  GoldenDB? 大佬笑而不语.

下一个十年, 我们拭目以待.

## 数据库相关书籍
推荐几本由浅入深的书和教材
- Avi Silberschatz, Henry F. Korth, S. Sudarshan.Database System Concepts, Seventh Edition. 2019.
- Peter Bailis, Joseph M. Hellerstein, Michael Stonebraker. Readings in Database Systems, 5th Edition](http://www.redbook.io/). 2015.
- Jim Gray, Andreas Reuter. Transaction Processing: Concepts and Techniques. 1992.

基本上第一本已经可以应付数据库相关的应用开发和面试了.

Gray的Transaction Processing, 涉及的知识领域已经远远不只数据库了. 有个朋友说, 他要是早看这本书, 说不定就去AWS搞云计算了.

如果要探究数据库内核, 数据结构、编译原理基础知识肯定必不可少.

现在数据库都是C-S架构, 如果做些接入层方面的工作(如数据库驱动, 数据库中间件), 计算机网络TCP/IP方面的知识肯定得扎实.

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
- 徐飞. 2019. 大数据浪潮之巅. 公众号: 飞总聊IT
- 盖国强. 2024. 《数据库简史》, 墨天轮社区
- 吴军. 浪潮之巅, 第四版. 2019. 里面专门一章讲了Oracle的故事.

### 其他
- Marcin Żukowski获得CWI Dijkstra Fellowship的采访
{{< youtube id="moQY_eiHCTs" >}}