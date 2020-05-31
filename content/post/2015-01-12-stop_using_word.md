---
date: 2015-01-12
categories:
  - tech
description: stop writing technical documentation using MS Word
tags:
  - wiki
title: 停止使用MS Word撰写技术文档
---



#### 技术文档特点
- 多人参与撰写、维护
- 保留时间长
- 经常更改
- 很多人长期需要阅读
- 需要做检索
- 历史修订记录

综合下来，对我们采用的技术提出以下要求

#### 基本要求
- 轻量
- 易更改
- 易获取; 易传播,变更能及时的通知到其他所有人
- 易检索

#### 我们的文档管理软件栈
- Web服务器：Apache或Nginx
- WikiMedia：写文档
- Graphviz：写基本流程图
- PlantUML：写UML图

写文档，其他可能选择有Markdown, reStructuredText

#### 对比

|   技术项       |  MS Word            |  Wiki（WikiMedia）     |
|-------------- |---------------------|-----------------------|
|撰写难度        |容易                  | 有门槛                 |
|撰写           | WYSIWYG(所见即所得)   | WYTIWYG(所想即所得)     |
|修改难度        |好                   | 好                     |
|归档保存        |SVN, 邮件附件         | WIKI网站，网址           |
|修订历史        |有                   | 有                     |
|修改差异比较     |SVN版本差异对比困难    | 方便，WIKI系统自带       |
|检索查找        |单文档查找（借助三方索引) | 全文检索               |
|权限控制        |MS加密                | 账号/密码              |
|格式           |私有二进制,必须装有OFFICE | 开放、文本、HTML,任何平台下浏览器都能打开 |


#### 使用MediaWiki语法撰写文档
常用的语法

- 标题、段落
- 列表
- 链接
- 表格
- 图
  * 方法一：直接使用二进制的图

    画图：PowerPoint、Visio、白板+水笔+相机

    上传图片到WIKI-> 生成链接 -> 文档中嵌入链接
  * 方法二（推荐）：把图写出来
     - 流程图：graphviz
       使用graphviz 的dot语法
     - UML图： PlantUML
       使用PlantUML语法

#### 参考
- [WikiMedia](http://www.wikimedia.org/)
- [Graphviz](http://www.graphviz.org/)
- [PlantUML](http://www.plantuml.com/)
- 很多同学问为什么要学习这么多语言，参看[Domain-Specific Languages 领域特定语言](http://book.douban.com/subject/21964984/),by Martin Fowler