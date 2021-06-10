---
title: "手动安装Linux网卡驱动"
date: 2021-06-10T12:16:07+08:00
draft: false
categories:
  - tech
---


今天偶然间发现一台Linux机器的网卡峰值速度只有100Mbps了, 奇怪.

虽说是台旧电脑(Thinkpad X61s), 但明明规格是1000Mbps啊.

查询了下interface信息, 网卡类型`Intel(R) PRO/1000`,`eth0: NIC Link is Up 100 Mbps Full Duplex`, 果然是100Mbps.
```bash
sudo dmesg | grep -i duplex
[   15.928542] e1000e 0000:00:19.0 eth0: NIC Link is Up 100 Mbps Full Duplex, Flow Control: Rx/Tx
(dev2)➜  ~ sudo dmesg | grep -i eth
[    3.568102] e1000e 0000:00:19.0 eth0: (PCI Express:2.5GT/s:Width x1) 00:16:d3:3e:0d:74
[    3.568105] e1000e 0000:00:19.0 eth0: Intel(R) PRO/1000 Network Connection
[    3.568144] e1000e 0000:00:19.0 eth0: MAC: 6, PHY: 6, PBA No: FFFFFF-0FF
[    7.716045] Bluetooth: BNEP (Ethernet Emulation) ver 1.3
[   15.928542] e1000e 0000:00:19.0 eth0: NIC Link is Up 100 Mbps Full Duplex, Flow Control: Rx/Tx
[   15.928653] e1000e 0000:00:19.0 eth0: Link Speed was downgraded by SmartSpeed
[   15.928656] e1000e 0000:00:19.0 eth0: 10/100 speed: disabling TSO
```

怎么回事?想想做过什么操作吗?

哦, 手动编译升级过内核到5.6版本.

默认kernel source tree中的驱动有问题.

从上面dmesg信息中, 可以看到驱动是`e1000e`, 查了下驱动版本, 是3.2
```bash
sudo modinfo e1000e |less
version:        3.2
```

在Intel的[网站](https://www.intel.com/content/www/us/en/support/articles/000005480/ethernet-products.html)查了下, PRO/1000最新的驱动已经是3.8.*

下载最新的驱动(是源代码发布的), 按照README `make install`, 提示没有kernel-devel.

```bash
$ sudo make install
common.mk:85: *** Kernel header files not in any of the expected locations.
common.mk:86: *** Install the appropriate kernel development package, e.g.
common.mk:87: *** kernel-devel, for building kernel modules and try again.  Stop.
```

apt里面搜索了下, 什么鬼, 没有5.6版本的...
```bash
$ apt search linux-headers
linux-headers-4.19.0-10-amd64/now 4.19.132-1 amd64 [installed,local]
  Header files for Linux 4.19.0-10-amd64
```

想了下, 是使用源代码编译的, 其实编译驱动需要的只是kernel代码而已

把/usr/src/linux指向代码目录后, make install OK

```bash
sudo ln -s /data/linux_src /usr/src/linux
```
检查驱动版本, OK, 已经是3.8版本.
```bash
$ sudo modinfo e1000e
version:        3.8.4-NAPI
license:        GPL
description:    Intel(R) PRO/1000 Network Driver
...
```
但...iperf3测速还是100Mbps.


重启下网卡后, 终于恢复1000Mbps.
```bash
sudo ip link set eth0 down && sudo ip link set eth0 up

sudo dmesg | grep -i duplex
[ 3449.405283] e1000e 0000:00:19.0 eth0: NIC Link is Up 1000 Mbps Full Duplex, Flow Control: Rx/Tx
```

Done.

看来以后从kernel source编译内核, 驱动得多留意.
