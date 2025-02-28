---
title: HTTPS双向认证原理与测试环境搭建
author: Jinkai
date: 2021-01-22 09:00:00 +0800
published: true
categories: [技术]
tags: [SSL, 双向认证, goahead, HTTPS]
---

## 原理
--------

`双向认证`(mutual authentication)，顾名思义，客户端和服务器端都需要验证对方的身份，在建立 HTTPS 连接的过程中，握手的流程比单向认证多了几步。单向认证的过程，客户端从服务器端下载服务器端公钥证书进行验证，然后建立安全通信通道。双向通信流程，客户端除了需要从服务器端下载服务器的公钥证书进行验证外，还需要把客户端的公钥证书上传到服务器端给服务器端进行验证，等双方都认证通过了，才开始建立安全通信通道进行数据传输。

本文所提到的认证流程都是基于`RSA`的方式，TLS1.0还支持`DH`(Diffie-Hellman)方式认证，详见《[传输层安全(TLS)相关技术详解](/posts/tls-tech)》

### 单向认证流程(RSA)

`单向认证`流程中，服务器端保存着公钥证书和私钥两个文件，整个握手过程如下：

![单向认证](/assets/img/2021-01-22-mutual-authentication/one-way-auth.png)

1. 客户端发起建立 HTTPS 连接请求，将 SSL 协议版本的信息发送给服务器端；
2. 服务器端将本机的公钥证书（server.crt）发送给客户端；
3. 客户端读取公钥证书 (server.crt)，取出了服务端公钥；
4. 客户端生成一个随机数（密钥 R），用刚才得到的服务器公钥去加密这个随机数形成密文，发送给服务端；
5. 服务端用自己的私钥 (server.key) 去解密这个密文，得到了密钥 R
6. 服务端和客户端在后续通讯过程中就使用这个密钥R进行通信了

### 双向认证流程(RSA)

![双向认证](/assets/img/2021-01-22-mutual-authentication/mutual-auth.png)

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

## 证书生成
--------

### 使用openssl生成CA自签名根证书

1. 使用以下命令生成无密码的2048位rsa密钥

    ```
    openssl genrsa -out ca.key 2048
    ```

    或加上-des3命令生成使用des3算法加密的rsa密钥

    ```
    openssl genrsa -des3 -out ca.key 2048
    ```

2. 生成x509格式的CA自签名根证书

    ```
    openssl req -new -x509 -days 365 -key ca.key -out ca.crt
    ```

3. 依次填入csr信息，Common Name表示颁发者

    ```
    Country Name (2 letter code) [AU]:CN
    State or Province Name (full name) [Some-State]:zhejiang
    Locality Name (eg, city) []:ningbo
    Organization Name (eg, company) [Internet Widgits Pty Ltd]:SX
    Organizational Unit Name (eg, section) []:tech
    Common Name (e.g. server FQDN or YOUR name) []:test
    Email Address []:
    ```

至此，CA自签名根证书已生成完成，后续需要用到CA密钥和证书签发子证书，注意密钥的保存与保密

### 签发客户端证书

1. 使用以下命令生成无密码的2048位`rsa密钥`

    ```
    openssl genrsa -out client.key 2048
    ```

    或加上`-des3`命令生成使用des3算法加密的`rsa密钥`

    ```
    openssl genrsa -des3 -out client.key 2048
    ```

2. 生成客户端`csr`文件

    ```
    openssl req -new -key client.key -out client.csr
    ```

3. 依次填入`csr`信息，`Common Name`表示使用者，不能与颁发者相同

    ```
    Country Name (2 letter code) [AU]:CN
    State or Province Name (full name) [Some-State]:zhejiang
    Locality Name (eg, city) []:ningbo
    Organization Name (eg, company) [Internet Widgits Pty Ltd]:SX
    Organizational Unit Name (eg, section) []:tech
    Common Name (e.g. server FQDN or YOUR name) []:client1
    Email Address []:

    Please enter the following 'extra' attributes
    to be sent with your certificate request
    A challenge password []:147258369
    An optional company name []:sanxing
    ```

4. 使用CA签发客户端x509证书

    ```
    openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out client.crt
    ```

5. 将客户端密钥和证书打包成`pfx`文件，用于浏览器或系统导入

    ```
    openssl pkcs12 -export -out client.pfx -inkey client.key -in client.crt
    ```

    或加上CA证书保证证书被信任

    ```
    openssl pkcs12 -export -out client.pfx -inkey client.key -in client.crt -certfile ca.crt
    ```

### 签发服务端证书

- 服务端证书生成过程与客户端相同，此处不再赘述

## 证书部署
--------

*本次配置以`GoAhead-openssl`为例，GoAhead还能使用mbedtls实现https，这里不做介绍，关于GoAhead的介绍如下：*

>GoAhead is the world's most popular, tiny embedded web server. It is compact, secure and simple to use.
>
>GoAhead is deployed in hundreds of millions of devices and is ideal for the smallest of embedded devices.

以上步骤完成后，将会生成如下文件：

```
ca.key  ca.crt  client.crt  client.key  client.pfx  server.key  server.crt
```

- (可选)`server.key`和`server.crt`部署在服务器证书路径下
- 对于GoAhead，`ca.crt`需部署在服务器证书路径下，用于验证客户端证书
- `client.pfx`安装到客户端，windows下直接下一步默认即可

## 配置GoAhead客户端证书认证功能
--------

1. 将`me.h`中的宏`ME_GOAHEAD_SSL_VERIFY_PEER`置为`1`，启用客户端证书认证
2. 将`me.h`中的宏`ME_GOAHEAD_SSL_AUTHORITY`配置为CA证书的绝对路径，用于校验客户端证书
3. 重新编译GoAhead库与服务端程序

## 测试
--------

windows客户端安装完客户端证书后访问服务端，此时浏览器会提示选择客户端证书，选择证书后能正常访问，如证书错误或未提供证书则访问失败，即测试通过

## 证书链

有时 root CA 不支持签发用户证书，而是只会签发 sub CA 证书，相当于委托 sub CA 去签发用户证书:

```bash
# 生成子CA的私钥
openssl ecparam -genkey -name prime256v1 -out subCA.key

# 创建一个 CSR（证书签名请求）用于子CA
openssl req -new -key subCA.key -out subCA.csr \
    -subj "/C=US/ST=State/L=Location/O=Organization/OU=SubCA/CN=Sub CA"

# 使用根CA签发子CA证书（basicConstraints=CA:TRUE用于表示该证书是CA证书，可以用于签发其他证书。pathlen表示子CA深度，为0表示已经是最后一层，无法用该证书再次签发sub CA证书）
openssl x509 -req -in subCA.csr -CA rootCA.crt -CAkey rootCA.key \
    -CAcreateserial -out subCA.crt -days 500 -sha256 -extfile <(printf "basicConstraints=CA:TRUE,pathlen:0")
```

此时验证流程会有些不同：

- 使用 root CA 证书验证 sub CA 证书有效性
- 使用 sub CA 证书验证用户证书的有效性

openssl 校验命令：

```bash
# untrusted 用于指定非根CA,也就是需要根CA验证的CA证书，
openssl verify -CAfile rootCA.crt -untrusted subCA.crt mycert.crt
```

上面的这个过程就像链一般，所以称为证书链，sub CA 还可以签发 sub sub CA，以此类推。

假设我们为服务端签发的一份证书，但是此时双方的**受信任证书区**都只有 root CA 证书，不知道 sub CA 的存在，且没有 sub CA 证书，因为有些设备的受信任证书区是只读的，无法添加新 CA 证书，所以不能通过更新方式添加 sub CA 证书。sub CA 证书在签发用户证书时会同时带下来，此时用户需要将其保存下来，当客户端请求服务端证书用于验证身份时，服务端需要同时提供服务端证书和 sub CA 证书。

## 参考

- [巧用 Nginx 快速实现 HTTPS 双向认证](<https://blog.csdn.net/easylife206/article/details/107776854>)
- [Using Client-Certificate based authentication with NGINX on Ubuntu](<https://www.ssltrust.com.au/help/setup-guides/client-certificate-authentication>)
