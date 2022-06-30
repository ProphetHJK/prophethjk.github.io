---
title: "DLMS/COSEM设计方案"
author: Jinkai
date: 2022-06-20 09:00:00 +0800
published: false
categories: []
tags: []
---

## 接口介绍

```c
// 接收一个字节
int svr_handleRequest3(
    dlmsServerSettings* settings,
    unsigned char data,
    gxByteBuffer* reply)
// 处理固定长度的接收字符串
int svr_handleRequest2(
    dlmsServerSettings* settings,
    unsigned char* buff,
    uint16_t size,
    gxByteBuffer* reply)

// 解析dlms字符串，解各种包装协议，负责完整性校验
int dlms_getData2(
    dlmsSettings* settings,
    gxByteBuffer* reply,
    gxReplyData* data,
    unsigned char first)

// 获取明文pdu，包括解密
int dlms_getPdu(
    dlmsSettings* settings,
    gxReplyData* data,
    unsigned char first)
```

```c
struct dlmsSettings // 应该就是AA有关信息，每个客户端需要一个对应的setting。根据示例这样设计每个接口只允许一个AA(应该可以实现多个)。每个setting中global key信息单独保存。

```

## 问题

- 不支持suite2
- 不支持GBT响应
- 未提供自动化代码生成工具（如对象初始化函数生成，参考gsoap）
- object list压缩（存在内存里太大，且检索复杂）
- object初始化、持久化未实现（参数一般存在EE中，启动全加载较慢，可选择懒惰加载）
- 序列化使用了固定格式读取写入，代码修改起来较为繁琐loadObjects（如果能够有自动生成代码工具，EE和flash的对象读取写入接口也能用这个工具生成，固定格式也可以）
- asn.1编解码工具(嵌套类型编解码，单独一份的xml或asn.1格式的说明文档，存于rom中，通过解析方式获取对象的结构)
- 对象列表不应该用C语言来表示，比如用asn.1或xml，可以通过工具转换成C语言表示
- 数据与DLMS/COSEM分离，通过适配层映射(想象成数据用数据库形式保存，根据数据使用频次决定是否放入内存。同时也能支持不同的通信协议)

## 优点

- 支持malloc和非malloc方式分配变量
- 
