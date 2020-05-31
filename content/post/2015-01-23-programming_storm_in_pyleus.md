---
date: 2015-01-23
categories:
  - tech
description: Programming Storm using Pyleus
tags:
  - Database
  - python
title: 使用Pyleus开发Storm应用
---



### Storm

- 什么是Storm(https://storm.apache.org/)
  解决的问题：实时数据分析

### Pyleus

- 用Python写Storm topolopgy
  Storm是在JVM平台上开发的，要使用非JVM平台语言（如Python，Go),需要使用ShellBolt，但是top仍然要使用Java定义
  Pyleus是全部使用Python开发spout,bolt,top的一整套框架，可以完全不使用Java。

  Pyleus由Yelp开发


### 遇到的坑

#### 定义muti-stream时的语法

注意，当只有一个stream时，[文档](http://yelp.github.io/pyleus/grouping.html#groupings)中定义muti-stream的语法有有问题，运行提交topoplogy时会报错

    Topology submission exception. (topology name='top_name') #<InvalidTopologyException InvalidTopologyException(msg:Component: [my_bolt] subscribes from non-existent stream:

~~~python
class MultipleBolt(Bolt):
    OUTPUT_FIELDS = {
        "stream-id": ["id", "value"],
        "stream-fake": ["fake"], ##只有一个stream时，记得加个假的，不然会出错
    }
~~~