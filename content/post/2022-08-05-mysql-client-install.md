---
title: "MySQL Client Install"
date: 2022-08-05T06:50:37Z
draft: false
---

## CentOS

check CentOS version

```bash
$ sudo yum install redhat-lsb-core
$ lsb_release -d
Description:    CentOS Linux release 7.9.2009 (Core)

$ hostnamectl
   Static hostname: tidb-dm-1
         Icon name: computer-vm
           Chassis: vm
        Machine ID: xxxx
           Boot ID: xxxx
    Virtualization: kvm
  Operating System: CentOS Linux 7 (Core)
       CPE OS Name: cpe:/o:centos:centos:7
            Kernel: Linux 3.10.0-1160.71.1.el7.x86_64
      Architecture: x86-64
```

purge existing installation

```bash
$ rpm -qa|grep -E "(mariadb|mysql)"
mysql57-community-release-el7-11.noarch
mariadb-libs-5.5.68-1.el7.x86_64

$ yum remove mysql57-community-release-el7-11.noarch  mariadb-libs-5.5.68-1.el7.x86_64

```

install MySQL 5.7.38 client

get packages from MySQL site: [https://downloads.mysql.com/archives/community/](https://downloads.mysql.com/archives/community/)

```bash
wget https://downloads.mysql.com/archives/get/p/23/file/mysql-community-client-5.7.38-1.el7.x86_64.rpm
wget https://downloads.mysql.com/archives/get/p/23/file/mysql-community-libs-5.7.38-1.el7.x86_64.rpm
wget https://downloads.mysql.com/archives/get/p/23/file/mysql-community-common-5.7.38-1.el7.x86_64.rpm

rpm -ivh ./mysql-community-common-5.7.38-1.el7.x86_64.rpm ./mysql-community-libs-5.7.38-1.el7.x86_64.rpm ./mysql-community-client-5.7.38-1.el7.x86_64.rpm
```

## MySQL Client for Python

MacOS:

```
brew install mysql-client
```
Linux:

```bash
apt install libmysqlclient-dev
```

install Python MySQL package

```
pip install --user mysql-connector-python

pip install --user mysqlclient
# if OSError: mysql_config not found, run `export PATH=/usr/local/mysql/bin:$PATH` fisrt

pip install --user records
```
