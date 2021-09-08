---
title: "DHCPv6 relay的使用"
author: Jinkai
date: 2021-09-08 09:00:00 +0800
published: true
categories: [技术]
tags: [dhcp, dhcpv6, relay]
---

本文将介绍如何使用DHCPv6 relay技术转发DHCPv6请求，包括widedhcpv6的交叉编译和配置

## DHCPv6简介

在[DHCPv6基础-曹世宏的博客](https://cshihong.github.io/2018/02/01/DHCPv6%E5%9F%BA%E7%A1%80/)一文对于DHCPv6协议做了详细的介绍，另可查看DHCPv6 IETF标准文档[RFC8415](https://datatracker.ietf.org/doc/html/rfc8415)，本文不再赘述。

DHCPv6 relay(中继代理)的作用就是将原来的DHCPv6`多播`(multicast)方式转化为`单播`(unicast)报文，从而可以跨网关传输DHCPv6的请求响应，一般的使用场景是DHCPv6客户端与服务器不在同一个链路的情况

## 工具

- [WIDE-DHCPv6](https://sourceforge.net/projects/wide-dhcpv6/)

- arm-none-linux-gnueabi-gcc(Sourcery CodeBench Lite 2014.05-29)

## 编译

实现DHCPv6 relay功能的开源工具并不多，而且很多已经长时间没维护了，试了好几个工具后，最后选择了`WIDE-DHCPv6`作为项目中使用的工具。

### 编辑configure

修改configure文件

```bash
echo "$as_me: error: cannot check setpgrp when cross compiling" >&2;}
{ (exit 1); exit 1; };}
```

为

```bash
echo "$as_me: error: cannot check setpgrp when cross compiling" >&2;}
#{ (exit 1); exit 1; };
}
```

### 执行配置脚本

```bash
CFLAGS="-D_GNU_SOURCE" ./configure  --host=arm-none-linux-gnueabi --prefix=$PWD/build
```

### 编辑cftoken.c

添加

``` c
int yywrap() {return 1;}
```

### 执行编译与安装

WIDE-DHCPv6不需要额外依赖，可直接编译，生成的目标文件为单独的二进制文件。执行以下命令即可：

```bash
make & make install
```

## 使用

WIDE-DHCPv6的使用非常简单，甚至不需要配置文件，参数说明如下：

```manual
NAME
     dhcp6relay — DHCPv6 relay agent

SYNOPSIS
     dhcp6relay [-Ddf] [-b boundaddr] [-H hoplim] [-r relay-IF] [-s serveraddr] [-S script-file]
                [-p pid-file] interface ...

DESCRIPTION
     dhcp6relay acts as an intermediary to deliver DHCPv6 messages between clients and servers,
     and is on the same link as a client.  dhcp6relay needs command line arguments interface ...,
     which specifies the list of links accommodating clients.

     Options supported by dhcp6relay are:

     -d      Print debugging messages.

     -D      Even more debugging information is printed.

     -f      Foreground mode (useful when debugging).  Although dhcp6relay usually prints
             warning, debugging, or error messages to syslog(8), it prints the messages to
             standard error if this option is specified.

     -b boundaddr
             Specifies the source address to relay packets to servers (or other agents).

     -H hoplim
             Specifies the hop limit of DHCPv6 Solicit messages forwarded to servers.

     -r relay-IF
             Specifies the interface on which messages to servers are sent.  When omitted, the
             same interface as interface will be used.  When multiple interface are specified,
             this option cannot be omitted.

     -s serveraddr
             Specifies the DHCPv6 server address to relay packets to.  If not specified, packets
             are relayed to ff05::1:3 (All DHCPv6 servers).

     -S script-file
             Specifies the script file to be executed when dhcp6relay receives a RELAY-REPLY
             message from a DHCPv6 server.  Further detail of the script file syntax is available
             in dhcp6c(8)

     -p pid-file
             Use pid-file to dump the process ID of dhcp6relay.

FILES
     /var/run/dhcp6relay.pid  is the default file that contains pid of the currently running
                              dhcp6relay.

SEE ALSO
     dhcp6c(8), dhcp6s(8)

     Ralph Droms, Editor, Dynamic Host Configuration Protocol for IPv6 (DHCPv6), RFC 3315, 2003.

HISTORY
     The dhcp6relay command first appeared in WIDE/KAME IPv6 protocol stack kit.
```

根据该配置说明进行配置即可，其中`-s`参数比较重要，用于指定服务端的地址；最后需要加上网口用于监听客户端DHCPv6请求

### 示例

```bash
./dhcp6relay -dD -s fd12::58 tun0
```

## 参考

- [DHCPv6基础-曹世宏的博客](https://cshihong.github.io/2018/02/01/DHCPv6%E5%9F%BA%E7%A1%80/)
- [RFC3315](https://datatracker.ietf.org/doc/html/rfc3315)
- [RFC8415](https://datatracker.ietf.org/doc/html/rfc8415)
- [Ubuntu Manpage:dhcp6relay—DHCPv6 relay agent](https://manpages.ubuntu.com/manpages/bionic/man8/dhcp6relay.8.html)
