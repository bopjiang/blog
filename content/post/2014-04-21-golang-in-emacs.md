---
date: 2014-04-21
categories:
  - blog
description: golang programming in emacs
tags:
  - linux
  - emacs
  - Golang
title: 使用emacs进行golang编程
---



### 环境
Ubuntu 12.04， Emacs 23, 中文输入法fcitx

### Emacs配置

使用el-get管理Emacs插件甚是方便，具体见[1]

Emacs需要安装的插件  

* el-get （下面的emacs插件都使用el-get-install安装）
* cscope (安装前要在系统安装cscope)
* go-mode
* ibus

### 中文输入法问题
除了安装ibus，下面两个要注意： 

* apt-get安装python-xlib插件
* 快捷键冲突：

### 建立代码索引
用下面的脚本：
<script src="https://gist.github.com/bopjiang/11146574.js"></script>

### 参考
1. <http://www.cnblogs.com/A-Song/archive/2013/03/09/2951951.html>
2. <http://www.ibm.com/developerworks/cn/aix/library/au-sudo/index.html>

