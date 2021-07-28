---
title: "strongSwan与Cisco CSR 1000V建立IPSec vpn调试记录"
author: Jinkai
date: 2021-07-28 09:00:00 +0800
published: true
categories: [技术]
tags: [strongSwan, Cisco, IPSec, VPN]
---

因项目需要，要让边缘计算网关与 Cisco CSR 1000V 连接，连接方式为 IPSec VPN，在本文记录下调试过程

## 环境介绍

### 客户端信息

本次使用的客户端设备为一台边缘计算网关设备，运行 Linux 系统，使用 strongSwan 工具进行 vpn 连接

| 参数       | 值                               |
| :--------- | :------------------------------- |
| MCU        | SCM601L216UE                     |
| model      | ARM926EJ-S rev 5 (v5l)           |
| flash      | 256MB                            |
| RAM        | 64MB                             |
| OS         | Linux 3.10.108                   |
| strongswan | 5.9.2                            |
| busybox    | 1.29.3                           |
| toolchain  | arm-none-linux-gnueabi-gcc 4.8.3 |
| ip         | 公网 ipv4                        |

### 服务端信息

本次使用的服务端设备为一台服务器，运行 Cisco Cloud Services Router (CSR) 1000V 路由软件，部署在巴西，网络环境为 IPv4 NAT

_Cisco Cloud Services Router (CSR) 1000V 是一款软件路由器，企业或云提供商可将其作为虚拟机 (VM) 部署在提供商托管云中，提供路由器相关功能等。_

### IPSec VPN 软件

有几个开源项目支持互联网密钥交换 （IKE） 和 IPSec 协议来构建安全的 L2L 隧道：

- **Free Secure Wide-Area Networking (freeS/WAN):**
  版本较老，未积极维护
- **ipsec-tools:**
  racoon - 不支持 Ikev2， 旧的 Linux kernel 2.6
- **Openswan:**
  非常基本的 IKEv2 支持，旧的 Linux kernel 2.6 和更早的 API，不积极维护
- **strongSwan:**
  支持 IKEv2 和 EAP/mobility，新的 Linux kernel 3.x 及之后的版本，使用 NETKEY API（这是 kernel 2.6 及以后的原生 IPSec 实现名称），积极维护，记录良好

目前，最好的选择通常是 strongSwan。

## strongSwan 移植

由于网关设备上并不包含 strongSwan 工具，需要从源码执行交叉编译，并移植

### strongSwan 下载

从官网下载界面下载最新版本，当前最新版本为 5.9.2，<https://download.strongswan.org/strongswan-5.9.2.tar.gz>

### strongSwan 交叉编译

1. 解压下载的文件，进入 strongswan 目录，输入配置命令

```bash
./configure --host=arm-none-linux-gnueabi --prefix=/media/disk/strongswan \
LDFLAGS="-Wl,-rpath,/root/repo/openssl/lib -L/root/repo/openssl/lib/" \
CFLAGS=-I/root/repo/openssl-1.0.2l/include --disable-gmp --disable-aes \
--disable-hmac --enable-openssl --disable-ikev1 --disable-des \
--disable-vici  --disable-swanctl --disable-curve25519 --disable-pkcs1 \
--disable-pkcs7 --disable-pkcs12 --disable-rc2 --enable-save-keys
```

- --host: 指定交叉编译工具的 prefix
- --prefix: 指定 install 目录
- LDFLAGS: 指定 openssl 的库目录
- CFLAGS: 指定 openssl 的头文件目录
- --disable-gmp: 关闭 gmp 插件，gmp 提供 RSA/DH 加解密后端
- --disable-aes：关闭自带的 aes 功能，使用 openssl 提供的 aes 功能
- --disable-hmac: 关闭自带的 hmac 功能，使用 openssl 提供的 hmac 功能
- --enable-openssl: 启用 openssl 插件，提供 RSA/ECDSA/DH/ECDH/ciphers/hashers/HMAC/X.509/CRL/RNG 加解密后端
- --enable-save-keys: 启用密钥保存功能，能够在 esp 建立时保存密钥，仅作为调试使用

_有关 strongSwan 插件的相关信息，可在<https://wiki.strongswan.org/projects/strongswan/wiki/Pluginlist>查看_

执行后会显示如下内容

```console
 strongSwan will be built with the following plugins
-----------------------------------------------------
libstrongswan: sha2 sha1 md5 random nonce x509 revocation constraints pubkey pkcs8 pgp dnskey sshkey pem openssl fips-prf xcbc cmac drbg
libcharon:     attr kernel-netlink resolve save-keys socket-default stroke updown counters
libtnccs:
libtpmtss:
```

2. 输入 make & make install，程序文件会放在 prefix 对应的目录下

`注意`：程序运行时的环境地址就是 prefix 指定的地址，程序会从该地址读取配置文件，所以移植程序时，需要放在和 prefix 相同的目录下

### 启用内核功能

需要的内核组件已在官网给出<https://wiki.strongswan.org/projects/strongswan/wiki/KernelModules>

由于网关设备是嵌入式设备，就不使用模块化编译了，直接编译进内核就行

Include the following modules:

```console
 Networking  --->
  Networking options  --->
    Transformation user configuration interface [CONFIG_XFRM_USER]
    TCP/IP networking [CONFIG_INET]
      IP: advanced router [CONFIG_IP_ADVANCED_ROUTER]
      IP: policy routing [CONFIG_IP_MULTIPLE_TABLES]
      IP: AH transformation [CONFIG_INET_AH]
      IP: ESP transformation [CONFIG_INET_ESP]
      IP: IPComp transformation [CONFIG_INET_IPCOMP]
    The IPv6 protocol ---> [CONFIG_IPV6]
      IPv6: AH transformation [CONFIG_INET6_AH]
      IPv6: ESP transformation [CONFIG_INET6_ESP]
      IPv6: IPComp transformation [CONFIG_INET6_IPCOMP]
      IPv6: Multiple Routing Tables  [CONFIG_IPV6_MULTIPLE_TABLES]
    Network packet filtering framework (Netfilter) ---> [CONFIG_NETFILTER]
      Core Netfilter Configuration --->
        Netfilter Xtables support [CONFIG_NETFILTER_XTABLES]
          IPsec "policy" match support [CONFIG_NETFILTER_XT_MATCH_POLICY]
```

`Note:` For kernel versions `before 5.2`, the required IPsec modes have to be enabled explicitly (they are built-in for newer kernels).

```console
 Networking  --->
  Networking options  --->
    TCP/IP networking [CONFIG_INET]
      IP: IPsec transport mode [CONFIG_INET_XFRM_MODE_TRANSPORT]
      IP: IPsec tunnel mode [CONFIG_INET_XFRM_MODE_TUNNEL]
      IP: IPsec BEET mode [CONFIG_INET_XFRM_MODE_BEET]
    The IPv6 protocol ---> [CONFIG_IPV6]
      IPv6: IPsec transport mode [CONFIG_INET6_XFRM_MODE_TRANSPORT]
      IPv6: IPsec tunnel mode [CONFIG_INET6_XFRM_MODE_TUNNEL]
      IPv6: IPsec BEET mode [CONFIG_INET6_XFRM_MODE_BEET]
```

`Note:` For kernel versions `4.2-4.5`, you will have to select Encrypted Chain IV Generator manually in order to use any encryption algorithm in CBC mode.

```console
 Cryptographic API
   Select algorithms you want to use...
   Encrypted Chain IV Generator [CRYPTO_ECHAINIV]
```

### openssl 交叉编译

```shell
 ./config no-zlib no-asm shared  -DOPENSSL_THREADS -pthread \
 -D_REENTRANT -D_THREAD_SAFE -D_THREADSAFE --prefix=$PWD/install \
 --cross-compile-prefix=arm-none-linux-gnueabi-
# 需要手动删除Makefile中的-m64选项
```

make & make install

### iproute2 交叉编译

需要使用 iproute2 工具查看一些 IPSec 相关的信息，busybox 提供的功能不太全，所以也移植一下

从官网下载<https://www.kernel.org/pub/linux/utils/net/iproute2/>，我这边使用的是 4.1.0 版本，太高的版本编译器不支持

编辑 Makefile，修改`CC = arm-none-linux-gnueabi-gcc`，以及`HOSTCC = arm-none-linux-gnueabi-gcc`，只启用 ip 功能`SUBDIRS=ip`

执行 make 命令，可执行文件在 ip 目录下

### iptables 交叉编译

网关设备不带iptables工具，需要移植

从官网下载1.8.7版本，<https://www.netfilter.org/pub/iptables/>

```shell
./configure --host=arm-none-linux-gnueabi --prefix=$PWD/build --disable-nftables
```

make & make install

## strongSwan 配置

移植后的strongSwan在/media/disk/strongswan目录下，配置文件都在etc目录下，正常情况下只需修改etc目录下的配置即可

### 设置环境变量

strongSwan依赖lib目录下的库文件，由于网关设备使用了ramfs需要手动指定，