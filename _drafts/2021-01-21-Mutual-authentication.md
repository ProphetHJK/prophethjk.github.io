---
title: HTTPS双向认证原理与测试环境搭建
author: Jinkai
date: 2021-01-20 14:40:00 +0800
image: 
categories: [技术]
tags: [SSL, 双向认证, goahead]
---

## 1.原理

双向认证，顾名思义，客户端和服务器端都需要验证对方的身份，在建立 HTTPS 连接的过程中，握手的流程比单向认证多了几步。单向认证的过程，客户端从服务器端下载服务器端公钥证书进行验证，然后建立安全通信通道。双向通信流程，客户端除了需要从服务器端下载服务器的公钥证书进行验证外，还需要把客户端的公钥证书上传到服务器端给服务器端进行验证，等双方都认证通过了，才开始建立安全通信通道进行数据传输。

### 1.1  单向认证流程

单向认证流程中，服务器端保存着公钥证书和私钥两个文件，整个握手过程如下：

![单向认证](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9tbWJpei5xcGljLmNuL21tYml6X3BuZy84WkZ6clJqcWF0cTZVREN5MjlTQjMyZXB4YTJnUmNTMWZtZHlvSFA3RTFhSjhKZXJ2Z0lMUDZoSjN3WnFxZ3NoaHpZR3ZpY2hUZjZtcUpRcXp2YldPUFEvNjQw?x-oss-process=image/format,png)

1. 客户端发起建立 HTTPS 连接请求，将 SSL 协议版本的信息发送给服务器端；
2. 服务器端将本机的公钥证书（server.crt）发送给客户端；
3. 客户端读取公钥证书 (server.crt)，取出了服务端公钥；
4. 客户端生成一个随机数（密钥 R），用刚才得到的服务器公钥去加密这个随机数形成密文，发送给服务端；
5. 服务端用自己的私钥 (server.key) 去解密这个密文，得到了密钥 R
6. 服务端和客户端在后续通讯过程中就使用这个密钥R进行通信了

### 1.2 双向认证流程

![双向认证](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9tbWJpei5xcGljLmNuL21tYml6X3BuZy84WkZ6clJqcWF0cTZVREN5MjlTQjMyZXB4YTJnUmNTMW5Xa0hxa0YxT1BmMFRwbXZmVkp6eTBDWXo1OENEY1k3VEJ1Tll1ZDhDblhpY2dBMU9wSmZZb2cvNjQw?x-oss-process=image/format,png)

1. 客户端发起建立 HTTPS 连接请求，将 SSL 协议版本的信息发送给服务端；
2. 服务器端将本机的公钥证书 (server.crt) 发送给客户端；
3. 客户端读取公钥证书 (server.crt)，取出了服务端公钥；
4. 客户端将客户端公钥证书 (client.crt) 发送给服务器端；
5. 服务器端解密客户端公钥证书，拿到客户端公钥；
6. 客户端发送自己支持的加密方案给服务器端；
7. 服务器端根据自己和客户端的能力，选择一个双方都能接受的加密方案，使用客户端的公钥加密后发送给客户端；
8. 客户端使用自己的私钥解密加密方案，生成一个随机数 R，使用服务器公钥加密后传给服务器端；
9. 服务端用自己的私钥去解密这个密文，得到了密钥 R
10. 服务端和客户端在后续通讯过程中就使用这个密钥R进行通信了。

