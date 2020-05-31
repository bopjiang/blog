---
date: 2019-03-02
categories:
  - tech
description: http go program
tags:
  - Golang
title: 关于Go HTTP Timeout
---


上周碰到一个使用Traefik反向代理的问题, 正好跟HTTP Timeout相关，现将分析过程总结如下。

## 问题现象

客户端的一个文件请求，先经过反向代理， 再经过Server，最后数据从Storage中获取（类似S3）。 基本架构如下：
~~~txt

+----------------------+
|  Client              |
+----------------------+
        |
  GET /FileA HTTP/1.1
        |
        |
 +-----------------------+        +-----------------+       +-----------------+
 | Nginx/Traefik         |--------|  Server         |-------|  Storage        |
 +-----------------------+        +-----------------+       +-----------------+

~~~

反向代理最开始是使用的Nginx， 后来因为服务都在Docker部署，切换到Traefik。

开始还没有问题, 直到有一天, 测试同学反馈客户端偶尔`GET /AFile`请求老是被异常关闭， 请求响应越大概率失败概率越大， 网速不好的时候更容易出现。最开始还以为是客户端的锅。


## 问题定位

后面试了好几个客户端版本， 问题依然存在， 看来跟客户端最近的更新无关。

排除了客户端后，开始怀疑Traefik这块配置有问题。查看服务端日志， 果然失败时Taefik有日志打印：

        2018/12/19 09:16:54 reverseproxy.go:395: httputil: ReverseProxy read error during body copy: unexpected EOF

traefik 上有个issue [#2903](https://github.com/containous/traefik/issues/2903) Truncated body when unexpected EOF，跟我们看到的现象是一样的。切换到Nginx后，问题不出现了, 更加证实了我们的判断。

运气这么好， 一下就踩到了traefik的BUG？直觉告诉我， 问题可能不是这样。 又试了用curl命令行模拟Client请求， 没有出错。其间抓包发现EOF(FIN)确实是服务端发起，主动关闭的。

最后当用`--limit-rate`参数限制curl请求速率到1MBps, 问题可以重现了， 而且都是在10s时出问题。联想到这个问题只在大响应报文才出现， 肯定跟我们设置的超时时间相关了。查看Server代码，果然`GET /AFile`请求设置了默认超时时间10秒， 增加到1分钟后， 问题解决。


### 思考

问题是定位出来了，这个错误一直就有， 为什么之前使用Nginx的时候没有暴露出来呢？

#### Nginx和Traefik做反向代理的区别
查看Nginx文档， 反向代理缓存这块， Nginx有三个参数控制
* [proxy_buffering](http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_buffering) 控制是否缓存后台响应，默认开
* [proxy_buffer_size](http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_buffer_size) 控制读取后台响应时的内存缓存， 默认大小4K
* [proxy_max_temp_file_size](http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_max_temp_file_size)， 控制磁盘缓存大小， 如果内存缓存放不下，就会写入磁盘。默认大小1024M

之前没有出问题，是因为10s内Nginx早就将响应报文从后台读完了，缓存在磁盘， 直到客户端读取完毕。

这么看， 在大响应的场景，Server上统计的请求处理时间和实际客户端的请求处理时间是较大有差别的。Server可能几秒就处理完了，但数据还缓存在Nginx，客户端迟迟还未读取完。

Traefik的行为不太一样， 默认是不开启缓存的。 客户端读取多少， Traefik才去Backend读取， 中间只有net/http模块内部默认的4K buffer。  参见Traefik中[Buffer的定义](https://github.com/containous/traefik/blob/fb617044e0221b7f9f0665d4c8adaa3736335cf4/config/middlewares.go#L26)


~~~go
// Middleware holds the Middleware configuration.
type Middleware struct {
        ForwardAuth       *ForwardAuth       `json:"forwardAuth,omitempty"`
        IPWhiteList       *IPWhiteList       `json:"ipWhiteList,omitempty"`
        RateLimit         *RateLimit         `json:"rateLimit,omitempty"`
	MaxConn           *MaxConn           `json:"maxConn,omitempty"`
        Buffering         *Buffering         `json:"buffering,omitempty"`
        //...

// Buffering holds the request/response buffering configuration.
type Buffering struct {
	MaxRequestBodyBytes  int64  `json:"maxRequestBodyBytes,omitempty"`
	MemRequestBodyBytes  int64  `json:"memRequestBodyBytes,omitempty"`
	MaxResponseBodyBytes int64  `json:"maxResponseBodyBytes,omitempty"`
	MemResponseBodyBytes int64  `json:"memResponseBodyBytes,omitempty"`
	RetryExpression      string `json:"retryExpression,omitempty"`
}

// server/middleware/middlewares.go
func (b *Builder) buildConstructor(ctx context.Context, middlewareName string, config config.Middleware) (alice.Constructor, error) {
        // ... 

	// Buffering
	if config.Buffering != nil && config.MaxConn.Amount != 0 {
		if middleware == nil {
			middleware = func(next http.Handler) (http.Handler, error) {
				return buffering.New(ctx, next, *config.Buffering, middlewareName)
			}
		} else {
			return nil, badConf
		}
	}
~~~


## 优化

对于这种连接关闭问题， 第一反应改是确认谁主动发起了关闭行为。
其实很多办法可以判断的：

### 分析日志：
  Traefik上的read error， unexpected EOF日志， 表明是读出错， 作为反向代理， 它有两处读行为：
  * 读客户端的请求
  * 读后台的响应

  我们的场景中，是请求报文小，响应报文大， 显然基本可以是读后台的响应出问题了， 根源在Traefik上游。

  `Server上请求处理超时没有打印日志， 是这个问题没有一下就定位到的主要原因`， 之前的代码如下：
~~~go
ctx, cancel := context.WithTimeout(context.Background(), time.Minute) 
defer cancel()

rs, err := GetFileA(ctx, "FileA")
if err != nil{
        // Write 500, server side error
        return
}

http.ServeConent(w, req, "FileA", fileATs, rs)

```

~~~
 
  http.ServeConent开始处理后， 就进入了阻塞状态， 一直到客户端将response读取完。ServeConent也没有返回值能告诉我们处理是否正常结束。
  优化后， 我们在超时时， 可以加上日志， 优化后代码如下：

~~~go
ctx, cancel := context.WithCancel(context.TODO())
timer := time.AfterFunc(time.Minute, func() {
        // 在此处可以记录超时日志！！！！
        log.Errorf("get FileA timeout")
	cancel()
})

rs, err := GetFileA(ctx, "FileA")
if err != nil{
        // Write 500, server side error
        return
}

http.ServeConent(w, req, "FileA", fileATs, rs)
~~~



### 通过抓包分析

不过上面问题中，看到的现象是四个模块间的三个TCP连接都中断， 一开始就抓包可能找不到头绪。而且在容器网络抓包， 方法和宿主机还有点不一样。


## 总结

最后看来， 这个还算是个比较简单的问题。 完全是开发过程中，对超时时间的设置没有把控好导致的。 HTTP 客户端、服务端处理超时这块常常被大家忽视。


## 后记

### unexpected EOF 究竟是怎么产生的

在我们的例子中，反向代理作为HTTP客户端， 从后台请求数据。 如果HTTP请求是有Content-Length的， HTTP客户端将会一直读，直到读满Content-Length长度的数据时，才算请求结束。如果中途TCP连接断开， Read返回EOF， 就是unexpected EOF错误。

代码逻辑在net/http模块Response.Body的Read()函数中：
~~~go
func (b *body) Read(p []byte) (n int, err error) {
        // ... 
	return b.readLocked(p)
}

// Must hold b.mu.
func (b *body) readLocked(p []byte) (n int, err error) {
        // ...
	n, err = b.src.Read(p)
	if err == io.EOF {
			// If the server declared the Content-Length, our body is a LimitedReader
			// and we need to check whether this EOF arrived early.
			if lr, ok := b.src.(*io.LimitedReader); ok && lr.N > 0 {
				err = io.ErrUnexpectedEOF
			}
	}
~~~


## 参考

cloudflare 讲Go http超时的文章 [The complete guide to Go net/http timeouts](https://blog.cloudflare.com/the-complete-guide-to-golang-net-http-timeouts/)

关于超时， 有个很长的issue讨论 [go #16100](https://github.com/golang/go/issues/16100)

容器网络的抓包可以参考这篇文章 [Inspecting Docker container network traffic](https://byteplumbing.net/2018/01/inspecting-docker-container-network-traffic/)