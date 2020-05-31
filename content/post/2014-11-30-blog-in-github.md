---
date: 2014-11-30
categories:
  - tech
description: blog
tags: []
title: 使用jekyll-bootstrap和github建立个人博客
---



注意：仅在Ubuntu 14.04环境下测试过。

### 安装jekyll-bootstrap
<http://www.ithans.com/blog/2013/02/18/jekyll-bootstrap-install/>

### 本地测试环境

~~~bash
jekyll b          ## 编译
jekyll s --watch  ## 运行服务（有变动时实时编译）
~~~

### 出错处理
1. jekyll serve启动服务的时候报错：

~~~bash
/var/lib/gems/1.9.1/gems/execjs-1.4.0/lib/execjs/runtimes.rb:51:in `autodetect': Could not find a JavaScript runtime.
See https://github.com/sstephenson/execjs for a list of available runtimes. (ExecJS::RuntimeUnavailable)
~~~

- 原因: 没有js运行时环境
- 解决办法: 安装js运行时环境

~~~bash
sudo apt-get install nodejs
~~~


2. 错误

~~~bash
ERROR:  Could not find a valid gem 'jekyll' (>= 0) in any repository
ERROR:  Possible alternatives: jekyll`
~~~

- 原因: 国内网络的原因。
- 解决办法: 只用taobao源

~~~bash
gem sources --remove http://rubygems.org/
gem sources -a http://ruby.taobao.org/
gem sources -l ## 确保只有taobao源
sudo gem install rack
sudo gem install jekyll
~~~

- 参考: <http://blog.ownlinux.net/2012/08/fix-gem-install-jekyll-problem.html>