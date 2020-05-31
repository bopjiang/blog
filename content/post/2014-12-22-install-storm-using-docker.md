---
date: 2014-12-22
categories:
  - tech
description: install storm cluster using docker
tags:
  - docker
  - Database
title: 使用docker安装storm集群
---



#### 基础
* [storm](https://storm.apache.org/)
* [storm-docker](https://github.com/wurstmeister/storm-docker)
* [docker](https://www.docker.com/)
* [fig](http://www.fig.sh/)
* pip, python

#### 步骤
* 升级内核

  由于是CentOS 6.3环境，内核不满足版本要求。升级内核版本至3.10.63

  >In general, a 3.8 Linux kernel is the minimum requirement for Docker, as some of the prior versions have known issues that are triggered by Docker. Linux kernel versions older than 3.8 are known to cause kernel panics and to break Docker.

  >The latest minor version (3.x.y) of the 3.10 (or a newer maintained version) Linux kernel is recommended. Keeping the kernel up to date with the latest minor version will ensure critical kernel bugs get fixed.

* 安装fig

  首先安装pip 

~~~bash
$ sudo apt-get install python-pip 
$ sudo pip install fig
~~~

* 安装storm-docker

~~~bash
$ mkdir storm && cd storm
$ git clone https://github.com/wurstmeister/storm-docker.git
$ cd storm-docker
$ 
$ sudo fig up -d
$ ## 第一次会拉取镜像, 时间较长, 随后集群将启动
~~~

* storm集群UI: 

  可以看到cluster, topology一系列信息

  <http://172.16.12.31:49080/index.html>

#### 加入topology
* 新增一个topopogy到cluster: call-perf-topology

~~~bash
$storm jar target/call-perf-0.1.0-jar-with-dependencies.jar com.uxin.storm.RollingTopWords call-perf-topology  remote -c nimbus.host=172.16.12.31 -c nimbus.thrift.port=49627
~~~