---
title: "Linux Home Lab Tips"
date: 2020-06-28T06:43:06+08:00
draft: true
---

command collection use in Linux home lab.

## OPS command
### turn off screen
```bash
#turn off server screen.
vbetool dpms off

#turn on server screen.
vbetool dpms on
```


### reclaim disk space
* apt cache (9 GiB).

```bash
$ sudo du -sh /var/cache/apt
9.0G    /var/cache/apt

$ sudo apt-get clean

$ sudo du -sh /var/cache/apt
476K    /var/cache/apt
```

* systemd logs
https://ma.ttias.be/clear-systemd-journal/


```
$ du -sh /var/log/journal
1.9G    /var/log/journal

$ sudo journalctl --vacuum-time=16d
$ sudo du -sh /var/log/journal
73M     /var/log/journal
```

### only upgrade a single package

```bash
$ sudo apt-get install --only-upgrade
```

### iptables

```bash
# for mosh use
sudo iptables -I INPUT -p udp -m udp --dport 60002 -j ACCEPT
```


## docker
```
$ sudo du -sh /var/lib/docker
6.9G    /var/lib/docker
```
