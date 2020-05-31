---
date: 2017-10-31
categories:
  - tech
description: debug go program
tags:
  - Golang
title: Golang程序问题定位方法
---


本文总结的方法对Go1.6及以后版本有效。

## 运行时问题
通过暴露http接口把运行栈打出来：
~~~Go
import _ "net/http/pprof"
~~~

命令如下:
~~~bash
curl http://server:port/debug/pprof/goroutine?debug=1
~~~

参数debug=1时输出按照goroutine的当前栈位置汇总过的栈信息。 譬如可以看到某类goroutine运行了多少个，在遇到goroutine泄露的问题时比较有用。

~~~
goroutine profile: total 104
100 @ 0x102ebdc 0x102ecce 0x10065a4 0x100624b 0x12e3683 0x105cbd1
#	0x12e3682	main.foo+0x42	/Users/bopjiang/code/test/go/stackdump.go:18

1 @ 0x102ebdc 0x1029b8a 0x1029187 0x108f55e 0x108f5dd 0x109037a 0x10f1242 0x110264d 0x1258052 0x105cbd1
#	0x1029186	internal/poll.runtime_pollWait+0x56		/usr/local/go/src/runtime/netpoll.go:173
#	0x108f55d	internal/poll.(*pollDesc).wait+0xad		/usr/local/go/src/internal/poll/fd_poll_runtime.go:85
#	0x108f5dc	internal/poll.(*pollDesc).waitRead+0x3c		/usr/local/go/src/internal/poll/fd_poll_runtime.go:90
#	0x1090379	internal/poll.(*FD).Read+0x189			/usr/local/go/src/internal/poll/fd_unix.go:125
#	0x10f1241	net.(*netFD).Read+0x51				/usr/local/go/src/net/fd_unix.go:202
#	0x110264c	net.(*conn).Read+0x6c				/usr/local/go/src/net/net.go:176
#	0x1258051	net/http.(*connReader).backgroundRead+0x61	/usr/local/go/src/net/http/server.go:660
~~~


~~~bash
curl http://server:port/debug/pprof/goroutine?debug=2
~~~
参数debug=2时输出的是详细每个goroutine的运行状态：调用栈信息，传入参数值，阻塞事件等待时间
最后的等待时间对定位程序挂起的问题很有用。譬如某个goroutine的channel写入阻塞了1个小时，那很有可能此channel的消费端出了问题。

~~~bash
goroutine 47 [chan receive, 3 minutes]:
main.foo(0x1d)
	/Users/bopjiang/code/test/go/stackdump.go:23 +0x7c
created by main.main
	/Users/bopjiang/code/test/go/stackdump.go:33 +0xae
        
goroutine 48 [chan receive, 3 minutes]:
main.foo(0x0)
	/Users/bopjiang/code/test/go/stackdump.go:18 +0x43
created by main.main
	/Users/bopjiang/code/test/go/stackdump.go:28 +0xae

goroutine 118 [running]:
runtime/pprof.writeGoroutineStacks(0x154b720, 0xc4201901c0, 0x0, 0xc42004fad0)
	/usr/local/go/src/runtime/pprof/pprof.go:608 +0xa7
runtime/pprof.writeGoroutine(0x154b720, 0xc4201901c0, 0x2, 0x30, 0x135ff20)
	/usr/local/go/src/runtime/pprof/pprof.go:597 +0x44
runtime/pprof.(*Profile).WriteTo(0x157d720, 0x154b720, 0xc4201901c0, 0x2, 0xc4201901c0, 0x15893e0)
	/usr/local/go/src/runtime/pprof/pprof.go:310 +0x3ab
net/http/pprof.handler.ServeHTTP(0xc42001ea31, 0x9, 0x154fb20, 0xc4201901c0, 0xc420112400)
	/usr/local/go/src/net/http/pprof/pprof.go:237 +0x1b8
net/http/pprof.Index(0x154fb20, 0xc4201901c0, 0xc420112400)
	/usr/local/go/src/net/http/pprof/pprof.go:248 +0x1db
net/http.HandlerFunc.ServeHTTP(0x13b54d0, 0x154fb20, 0xc4201901c0, 0xc420112400)
	/usr/local/go/src/net/http/server.go:1918 +0x44
net/http.(*ServeMux).ServeHTTP(0x15893e0, 0x154fb20, 0xc4201901c0, 0xc420112400)
	/usr/local/go/src/net/http/server.go:2254 +0x130
net/http.serverHandler.ServeHTTP(0xc4201281a0, 0x154fb20, 0xc4201901c0, 0xc420112400)
	/usr/local/go/src/net/http/server.go:2619 +0xb4
net/http.(*conn).serve(0xc420184000, 0x15501e0, 0xc420126100)
	/usr/local/go/src/net/http/server.go:1801 +0x71d
created by net/http.(*Server).Serve
	/usr/local/go/src/net/http/server.go:2720 +0x288
~~~

## 崩溃问题
找崩溃原因，遇到大部分都是nil reference。
输出跟debug=2一样格式的栈信息（只不过只有崩溃goroutine一个栈的）。

### race detector
在程序出现race condition的情况下（通常都是并发对map进行读写），崩溃的地点可能在runtime里面， 这时候就不太好定位了。

~~~bash
fatal error: concurrent map writes

goroutine 19 [running]:
runtime.throw(0x13a3caf, 0x15)
	/usr/local/go/src/runtime/panic.go:605 +0x95 fp=0xc420028f08 sp=0xc420028ee8 pc=0x102d065
runtime.mapassign_faststr(0x1339020, 0xc420130060, 0x139dd66, 0x8, 0x0)
	/usr/local/go/src/runtime/hashmap_fast.go:607 +0x4f5 fp=0xc420028f88 sp=0xc420028f08 pc=0x100ea85
main.foo(0x1)
	/Users/bopjiang/code/test/go/stackdump.go:20 +0x52 fp=0xc420028fd8 sp=0xc420028f88 pc=0x12e3692
runtime.goexit()
	/usr/local/go/src/runtime/asm_amd64.s:2337 +0x1 fp=0xc420028fe0 sp=0xc420028fd8 pc=0x105cbd1
created by main.main
	/Users/bopjiang/code/test/go/stackdump.go:33 +0xae
~~~

此时可以依靠[Race Detector](https://blog.golang.org/race-detector)。写测试用例做race检查是一个办法。还可以将线上的某台机器运行race版本，等待问题，或者复制客户端请求重现。race detector对性能影响非常大，这点上线时要注意。

## core dump
最后还有一个办法就是看core dump，可以看到程序的完整状态。这篇文章[Debugging Go core dumps](https://rakyll.org/coredumps/)总结得很好。


## 性能分析
除了崩溃，挂死问题，很多性能方面问题必须依赖profile和指标监控：
- [Profiling Go Programs](https://blog.golang.org/profiling-go-programs)

~~~bash
# CPU Profile
$ curl -s -o cpu.pprof ./server http://server:port/debug/pprof/profile # 30-second CPU profile
$ go tool pprof cpu.pprof
Type: cpu
Time: Nov 14, 2017 at 7:43pm (CST)
Duration: 30s, Total samples = 0
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) web       
# 会生成SVG图(需要安装graphviz)

# Heap Profile
go tool pprof ./server http://server:port/debug/pprof/heap    
# goroutine blocking profile
go tool pprof ./server http://server:port/debug/pprof/block  
~~~

- 通过程序自己上报指标，在TSDB中做回溯分析。程序中buffered channel的长度最好都做下监控。 这块一般都是[Promethues](https://prometheus.io/) 搭配[Grafana](https://grafana.com/)使用。

## UPDATE 2018-09-21

### flame graphs 火焰图

Go 1.11已经在tool中集成了火焰图。

~~~bash
go tool pprof -http=:8080 /path/to/profile
~~~