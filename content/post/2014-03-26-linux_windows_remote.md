---
date: 2014-03-26
categories:
  - tech
description: 远程访问remote
tags:
  - linux
title: Linux与Windows间相互远程访问
---



windows访问linux
-------

#### ssh访问

* putty
* xshell
* SecureCRT

#### 图形界面

* TightVNC
（linux上面要装vncserver）


linux访问windows桌面
------
* remmina, The GTK+ Remote Desktop Client
* rdesktop

~~~bash
rdesktop -a 16 172.16.13.88:3389 -u jiangjia -g 1024*768 
~~~

windows远程后，图形界面的关机按钮消失了，要关机必须命令行：

关机(等待一分钟): shutdown -s

重启: shutdown -r

30s后关机: shutdown -s -t 30

中止关机操作: shutdown – a 

遗留问题
--------
* remmina 远程没有声音问题