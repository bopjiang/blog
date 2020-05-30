---
date: 2014-03-20
categories:
  - blog
description: ip地址统计
tags:
  - linux
  - network
title: 分配给中国的IP有多少个
---



获取全球IP地址分配列表
-------
-------
```bash
curl http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest -o iplist.txt
```

统计
------
------
```bash
[jiangjia@houtaiceshi1 ipaddr]$ cat  iplist.txt  |grep ipv4 |grep \|CN\| | cut -d \| -f 5 | awk '// {sum += $1};END {print sum}'
330410496
```

IP v4才3.3亿，难怪深圳联通ADSL宽带分配给我是个私网IP了，合同到期坚决换掉。