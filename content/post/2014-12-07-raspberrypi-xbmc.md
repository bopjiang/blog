---
date: 2014-12-07
categories:
  - blog
description: XBMC on Respberry Pi
tags:
  - Raspberry Pi
title: 自己动手做个机顶盒
---



不知N年后，还有人知道[机顶盒](http://en.wikipedia.org/wiki/Set-top_box)是啥东西不。

### 基础知识
- [Respberry Pi](http://www.raspberrypi.org/)
- [XBMC](www.xbmc.org/)，现在改名叫[Kodi](http://kodi.tv/)了
- [xbmc-addons-chinese](https://github.com/taxigps/xbmc-addons-chinese)
- [XBMC Remote for Android](https://code.google.com/p/android-xbmcremote/)


### 硬件准备
- Respberry Pi一个， 淘宝200-300元间
- SD卡（2G或4G），装系统和软件用
- 网线一根（我的Pi只有LAN口， 没有装WIFI模块）
- 5V micro USB电源一个(Android手机的充电器就可以用)
- Android手机一个（旧的也行，反正HTC G1能用）
- HDMI线一根(老电视没有HDMI接口，需要三色AV线1根，3.5mm一分二音频线公头转双母头1根，AV解析度只能到720×480i）

### 软件准备
- RASPBMC：raspberrypi网站上已经做好预装XBMC的镜像，直接用就可以
- ssh客户端（最好Linux系统）

### 过程
- 在SD卡上做好系统
- 修改配置文件，设置http控制端口(有raspi-config的脚本可以用)
- 手机端安装遥控程序(XBMC Remote), 使用配置的HTTP端口
- 安装中文插件xbmc-addons-chinese

### 遇到问题
- 安装插件后下载不到节目列表
  * 设置HTTP代理
  * 重启Pi
  * 打开debug，查看错误日志，一般都是网络访问不了
- 网络代理配置改后未生效，GUI上也看不到
  * 暂未解决