---
date: 2019-05-05
categories:
  - blog
description: protocol design
tags:
  - API
title: 关于API、协议设计的一点思考
---


最近几年有幸在两家公司从零开始主导了两个系统对外API、协议的的设计, 最近也在反思在协议设计中的问题(自己埋下的坑).

## 自定义二进制协议
先讲第一家ToC的互联网公司, 客户端是手机APP. 因为涉及到VOIP相关业务, 客户端-服务端必须具备双工通信能力, 同时为了节省流量, 选择了基于TCP的二进制协议.(当然也跟我当时从传统通信行业出来有关)

一个系统当然不是凭空设计出来的, 从中一定能看出组织架构的影子.当时我这边主要负责接入层这块, VoIP SIP信令是另一个团队在负责, 本着两个团队间代码最小耦合的原则, 于是乎, 协议就分为了两层, 一层负责消息路由(报文头), 一层负责业务数据(报文体).
具体到字段设计

| 字段名称      |   宽度(Byte)   |  
---------------|----------------
|  报文头长度    |   2      |  
|  报文体长度    |   2      |  
|  报文头       |   变长    |   
|  报文体       |   变长    |   

为了保证版本向后扩展, 在TCP三次握手完成后, 客户端必须主动发送一个版本号消息.

因为是TCP长连接,所以必须要有应用层心跳消息进行连接保活, 4个Bytes的全0就行了(报文头长度和报文体长度都设置为0)

这里的版本号在后来还真起到了很大的用处, 报文头最开始用的是JSON编码, 后面改为Protocol Buffers, 版本号在这块帮助了协议的平滑升级.

### 遇到的坑
由于我们的二进制协议没有特殊的边界字符(magic number), 导致客户端处理异常时, 没有很快的检测到报文错误(`Fail Fast`), 会导致服务端一致读阻塞(读到错误的报文头或报文体长度字段). 

报文体长度的宽度, 2个字节一般是够用了, 设计4字节大小的报文体, 也不太合适,万一谁不小心发个几百M的巨包, 岂不是把整条TCP连接都阻塞住了? 
但是大报文的场景总是存在的, 预先设计好`分帧协议`是很有必要的.

二进制协议调试定位上会有一定难度, 特别是协议开发初期, 数据结构不稳定时.想到在Wireshark里看一堆二进制符号现在都有些头疼, 如果是PB协议, 更是令人抓狂. 相比而言, HTTP明文协议调试起来就简单多了.

## REST API
第二家是硬件独角兽, 我从事的是ToB系统的设计. API主要提供给外部用户使用, HTTP看上去是不错选择. 这个API设计的时候, 严格遵循了REST风格, 每个请求都包含:
- 动词(HTTP Method: GET POST PUT PATCH DELETE)
- 资源属性

其中, GET、PUT、DELETE请求都是幂等的. PUT用来整体更新或覆盖, PATCH是做部分修改.

响应报文, HTTP状态码的定义:
- 200: 正常
- 4**: 客户端错误
- 5**: 服务端错误

API在内部用户使用时还好, 一旦提供给第三方用户客户使用, 各种问题就来了.

第一是API的签名计算, 使用了类似[AWS](https://docs.aws.amazon.com/general/latest/gr/sigv4-calculate-signature.html)的多次循环HMAC Hash. 一开始只提供了Golang的示例代码, 于是每次有外部用户对接,都要花时间指导怎么写签名算法. 

API接口文档是用Swagger手写的, 这意味着, 一个接口必须同时维护业务逻辑代码和API代码, 还得保证二者间的一致.

由Swagger生成数据结构定义还行, 但生成客户端代码还不是很成熟, 特别是go target, 生成可执行的库还需要额外hack.

## 如果还有下一次:)

业务层的代码一般来说写几个月就乏味了, 可以明显感觉到, 大部分CRUD的场景, 接口层、数据访问层的代码都是简单的重复. 最重要的是数据结构, 数据结构定义好了, API接口的请求、响应结构也基本就定了, 数据库的结构也就可以确定.

数据访问层有ORM可以释放部分生产力(当然sqlx,dbr也都很顺手),接口层呢? 这部分的代码是否完全可以自动生成?个人理想中的API开发的状态应该做到:
- 有强类型、规范化的IDL语言定义接口
- 可自动生层服务端的接口定义和消息路由
- 可自动生成API客户端代码
- 可自动生成API文档

目前看, gRPC+[gRPC Gateway](https://github.com/grpc-ecosystem/grpc-gateway),一定程度上达到了这些要求.
但是这个方案一个HTTP请求过来, 要经过Gateway转换后再到gRPC服务, 如果能同时生成gRPC和HTTP两套代码, 不用Gateway转发就完美了,不仅效率更高, 还可以减少一个服务的部署成本.

![gRPC+gRPC Gateway](https://camo.githubusercontent.com/e75a8b46b078a3c1df0ed9966a16c24add9ccb83/68747470733a2f2f646f63732e676f6f676c652e636f6d2f64726177696e67732f642f3132687034435071724e5046686174744c5f63496f4a707446766c41716d35774c513067677149356d6b43672f7075623f773d37343926683d333730)

### 做得比较好的API接口
写了怎么多, 其实很多想法也是从别人的API设计中学习到的, 特别是下面两家的API接口设计:
- twilio API (其实判断一个ToB公司技术能力怎样,API文档拿出来就可以看出些. 说到这儿, 2018年没有成为twilio股东是不是后悔了?)
- Google API: 把Protocol Buffer文件都开放了

## WebSocket
最后讲下WebSocket, 其实二进制协议走WebSocket也是可以的, 但WebSocket本质上只是一个传输通道, 就算用了WebSocket, 你自己还是需要定义应用层的封包协议. 上面说的TCP二进制协议, 后来我们确实做到了TCP和WebSocket两种接入方式同时兼容, 代码改动很小, 在WebSocket层上再做一次包装即可, 二进制协议本身都不用改动.

WebSocket的设计本质上存在一个问题: 它底层的TCP是一个流式协议, 但WebSocket对外提供却是一个Packet协议, 它迫使你的应用层也只能使用Packet协议, 而且要遵循WebSocket的封包规则.

基于WebSocket Binary类型, 一个WebSocket packet就是一个JSON, 也有这样设计RPC协议的. 当然也是可以的, 不过大包场景,WebSocket分帧这块还是需要特别注意.

前端还比较流行一个socket.io的WebSocket协议封装, 说实话, 相当的蛋疼, 竟然找不到这个协议的准确描述, 只是一个js库, 后面果断地放弃了.


## 参考

1. [apigee API design](https://pages.apigee.com/rs/apigee/images/api-design-ebook-2012-03.pdf)

2. [Wowza Streaming Cloud REST API Documentation](https://sandbox.cloud.wowza.com/api/current/docs)

3. [Google APIs](https://github.com/googleapis/googleapis)

4. [Twilio API doc](https://www.twilio.com/docs/usage/api)

5. [go-restful](https://github.com/emicklei/go-restful), K8S在使用, 可由代码生成Swagger.