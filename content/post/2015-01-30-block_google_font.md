---
date: 2015-01-30
categories:
  - tech
description: website cannot open because font.google blocked
tags:
  - gwf
title: fonts.googleapi导致网页打不开问题
---



经常打开[readthedocs.org](https://readthedocs.org)网站时，页面崩溃或很长时间才打开，看了下基本都用到fonts.googleapis提供的字体的服务。

解决办法：

安装Adblock Plus插件（chrome和firefox都有）， 增加自定义过滤规则：

~~~
fonts.googleapis.com$stylesheet,match-case
use.typekit.net$script,match-case
~~~