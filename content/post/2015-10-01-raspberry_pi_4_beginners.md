---
date: 2015-10-01
categories:
  - tech
description: Raspberry Pi for beginners
tags:
  - Raspberry Pi
  - linux
title: 《Raspberry Pi入门指南》读书笔记
---



Raspberry Pi 入手两年了，除了装过XMBC看电视外，基本没怎么用了。偶然在图书馆发现这本[<<Raspberry Pi入门指南>>](http://book.douban.com/subject/26336217/)，作为入门读物还是不错的。

简单摘要下：

### 模块
- CSI接口(Camera Serial Interface), 摄像头
  淘宝上有大把
- DSI接口(Display Serial Interface)
- GPIO 作为单片机驱动外围设备

### 使用场景
- BT下载器
  使用aria2(http://aria2.sourceforge.net/)
  在chrome中使用Yaaw插件（Yet Another Aria2 Web）, 使用aria2提供的JSON RPC接口远程控制

- XBMC
  介绍的XBian

- 文件服务器samba

### GPIO编程
- 控制LED灯闪烁
  面包板，杜邦线(跳线), LED灯
  * SHELL/BASH控制， 操作文件
  * Python,使用RPi.GPIO包
- 温度传感器

### 图像处理
- CSI
- USB口WebCam
    罗技C270WebCam，720P
    * luvcview实时看视频流
    * uvccapeture截图
- 其他软件
   *  motion
   * python:SimpleCV
     Haar Cascade哈尔分类，面部识别
     2013-08: SimpleCV暂时还不能从CSI取视频

### Arduino开源电子原型平台
  使用USB与Pi相连， 串口通信

  python中import serial

### Raspberry Pi 2
- 新出的Raspberry Pi升级版本Raspberry Pi 2 ，可跑“官方精简版” Ubuntu Core
- 建议使用lxde图形界面（和debian类似）， 安装xrdp支持windows上使用远程桌面连接
- 听说可可运行win10