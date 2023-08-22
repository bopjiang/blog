---
title: "AWS 踩坑记-1"
date: 2023-08-23T06:56:36+08:00
draft: true
---


在目前公司使用AWS服务已经四年多了, AWS的云主机EC2, 数据库RDS, ElasticCache Redis产品安利说使用经验已经很丰富了, 但还是难免踩坑, 为了让后来的小朋友们别再上当, 特此记录下.


## 问题1: Redis查询响应时间从1ms内增加到3s以上, CPU/内存都无波动.

