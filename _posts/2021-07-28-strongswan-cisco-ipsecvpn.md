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

## 相关工具移植

### openssl 交叉编译

_strongSwan 需要 openssl 作为加解密后端，来支持更多特性_

```bash
 ./config no-zlib no-asm shared  -DOPENSSL_THREADS -pthread \
 -D_REENTRANT -D_THREAD_SAFE -D_THREADSAFE --prefix=$PWD/install \
 --cross-compile-prefix=arm-none-linux-gnueabi-
# 需要手动删除Makefile中的-m64选项
```

make & make install

### iproute2 交叉编译

_需要使用 iproute2 工具查看一些 IPSec 相关的信息，busybox 提供的功能不太全，所以也移植一下_

从官网下载<https://www.kernel.org/pub/linux/utils/net/iproute2/>，我这边使用的是 4.1.0 版本，太高的版本编译器不支持

编辑 Makefile，修改`CC = arm-none-linux-gnueabi-gcc`，以及`HOSTCC = arm-none-linux-gnueabi-gcc`，只启用 ip 功能`SUBDIRS=ip`

执行 make 命令，可执行文件在 ip 目录下

### iptables 交叉编译

网关设备不带 iptables 工具，需要移植

从官网下载 1.8.7 版本，<https://www.netfilter.org/pub/iptables/>

```bash
./configure --host=arm-none-linux-gnueabi --prefix=$PWD/build --disable-nftables
```

make & make install

### tcpdump 交叉编译

_tcpdump 是 Linux 平台的抓包工具，纯命令行界面，抓到的 pcap 格式数据可以在 wireshark 中展示_

去 tcpdump 官网<https://www.tcpdump.org/>下载最新版本，我下载的是`4.99.1`，同时下载`libpcap`最新版本，我下载的是`1.10.1`

解压到同一父目录下，进入 tcpdump 目录，输入

```bash
./configure --host=arm-none-linux-gnueabi --prefix=$PWD/build
```

这里会自动找到父目录下的 libpcap 目录

make & make install

- 使用方法：

```bash
  tcpdump -i eth0 -w /var/tcpdump/eth0.pcap
```

### isc-dhcp 移植

_isc-dhcp 是一个 dhcp 工具箱，包含了 dhcp client，dhcp server 和 dhcp relay agent，支持 ipv6，可以说是功能最全面的一款 DHCP 工具了_

1. 前往官网<https://www.isc.org/dhcp/>下载最新稳定版本，我用的是 4.2.6 版本

2. 配置

```bash
./configure BUILD_CC=gcc --host=arm-none-linux-gnueabi --prefix=$PWD/build ac_cv_file__dev_random=yes
```

进入 bind 目录，解压 bind.tar.gz

```bash
cd bind
tar -zxvf bind.tar.gz
```

进入 bind-9.9.5 目录，编辑 vim lib/export/dns/Makefile.in

```bash
cd bind-9.9.5
vim lib/export/dns/Makefile.in
```

将

```makefile
gen: ${srcdir}/gen.c
        ${CC} ${ALL_CFLAGS} ${LDFLAGS} -o $@ ${srcdir}/gen.c ${LIBS}
```

改为

```makefile
gen: ${srcdir}/gen.c
        ${BUILD_CC} ${ALL_CFLAGS} ${LDFLAGS} -o $@ ${srcdir}/gen.c ${LIBS}
```

3. 回到 dhcp 目录

```bash
make & make install
```

## strongSwan 配置

移植后的 strongSwan 在/media/disk/strongswan 目录下，配置文件都在 etc 目录下，正常情况下只需修改 etc 目录下的配置即可

etc 目录结构：

```shell
.
├── ipsec.conf
├── ipsec.d
│   ├── aacerts
│   ├── acerts
│   ├── cacerts
│   ├── certs
│   ├── crls
│   ├── ocspcerts
│   ├── private
│   └── reqs
├── ipsec.secrets
├── strongswan.conf
└── strongswan.d
    ├── charon
    │   ├── attr.conf
    │   ├── cmac.conf
    │   ├── constraints.conf
    │   ├── counters.conf
    │   ├── dnskey.conf
    │   ├── drbg.conf
    │   ├── fips-prf.conf
    │   ├── kernel-netlink.conf
    │   ├── md5.conf
    │   ├── nonce.conf
    │   ├── openssl.conf
    │   ├── pem.conf
    │   ├── pgp.conf
    │   ├── pkcs8.conf
    │   ├── pubkey.conf
    │   ├── random.conf
    │   ├── resolve.conf
    │   ├── revocation.conf
    │   ├── sha1.conf
    │   ├── sha2.conf
    │   ├── socket-default.conf
    │   ├── sshkey.conf
    │   ├── stroke.conf
    │   ├── updown.conf
    │   ├── x509.conf
    │   └── xcbc.conf
    ├── charon.conf
    ├── charon-logging.conf
    ├── pki.conf
    ├── scepclient.conf
    └── starter.conf
```

### 设置环境变量

strongSwan 依赖 lib 目录下的库文件，由于网关设备使用了 ramfs 无法将库文件放入 lib 目录下，需要在运行前手动配置

```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/media/disk/strongswan/lib
export PATH=$PATH:/media/disk/strongswan/sbin
```

### ipsec.conf 配置

ipsec.conf 是老版本的配置文件，但比较直观，教程用的也比较多，还是选择用这个

关于 ipsec.conf 的详细介绍，请看官网链接：

- 配置参数<https://wiki.strongswan.org/projects/strongswan/wiki/ConfigSetupSection>
- 连接参数<https://wiki.strongswan.org/projects/strongswan/wiki/connsection>

贴一下个人配置：

```conf
config setup
    # strictcrlpolicy=yes
    uniqueids = yes
    #charondebug="ike 3, knl 3, cfg 3, chd 3, lib 3, esp 3, tls 3"
    # 调试信息等级
    charondebug="ike 3, knl 3, cfg 3, esp 1, lib 3, chd 3, net 1, enc 1"

conn %default
    ikelifetime=24h
    keylife=8h
    rekeymargin=3m
    keyingtries=1
    #authby=secret
    keyexchange=ikev2
    mobike=no

# 连接名称，host-host表示主机-主机，site-site表示子网-子网
conn host-host
    type=transport
    left=%any
    # pem格式的客户端证书
    leftcert=client.crt
    leftid=223.94.60.86
    # 使用GRE协议
    leftprotoport=47
    right=128.201.18.34
    # %any表示不指定，允许任何对端信息，一般用在right
    rightid=%any
    rightprotoport=47
    keyexchange=ikev2
    # ike握手加密算法
    ike=aes256-sha256-modp1536
    # esp加密算法
    esp=aes256-sha256
    auto=start
    # 自动重连
    #dpdaction=restart
```

### ipsec.secrets 配置

ipsec.secrets 用于配置密钥密码信息

- <https://wiki.strongswan.org/projects/strongswan/wiki/Ipsecsecrets>

```conf
# PSK密码，安全等级较低，与ipsec.conf中的leftid,rightid对应
223.94.60.86 : PSK "#*SsG@Dq^@&DCr"
128.201.18.34 : PSK "#*SsG@Dq^@&DCr"
10.230.93.19 : PSK "#*SsG@Dq^@&DCr"
# 私钥位置，在etc/ipsec.d/private目录下
: RSA client.key
```

### strongswan.conf 配置

strongswan.conf 是配置 strongSwan 这个应用相关的配置文件，包括插件启用，插件参数等

- <https://wiki.strongswan.org/projects/strongswan/wiki/strongswanconf>

```conf
# strongswan.conf - strongSwan configuration file
#
# Refer to the strongswan.conf(5) manpage for details
#
# Configuration changes should be made in the included files

charon {
        load_modular = yes
        multiple_authentication = no
        #install_routes = no
        plugins {
                include strongswan.d/charon/*.conf
                #kernel-netlink {
                        #fwmark = !0x42
                #}
                #socket-default {
                        #fwmark = 0x42
                #}
                kernel-libipsec {
                        #allow_peer_ts = yes
                        load = no
                }
                save-keys {
                        esp = yes
                        ike = yes
                        load = yes
                        wireshark_keys = /media/disk/tcpdump/keys
                }
        }
}
```

### ipsec.d 目录

ipsec.d 目录用于存放私钥与证书文件

```shell
├── ipsec.d
│   ├── aacerts
│   ├── acerts
│   ├── cacerts
│   ├── certs
│   ├── crls
│   ├── ocspcerts
│   ├── private
│   └── reqs
```

### strongswan.d 目录

strongswan.d 目录用于存放应用与插件的精细配置

## strongSwan 运行

strongSwan 的运行很简单，在完成配置后，只需在控制台运行

```bash
ipsec start
```

日志默认打印在`syslog`中

查看状态

```bash
ipsec statusall
```

连接成功应该是这样的

```shell
[root@sx sbin]# ./ipsec statusall
Status of IKE charon daemon (strongSwan 5.9.2, Linux 3.10.108, armv5tejl):
  uptime: 3 hours, since Aug 03 01:59:51 2021
  malloc: sbrk 528384, mmap 0, used 195960, free 332424
  worker threads: 11 of 16 idle, 5/0/0/0 working, job queue: 0/0/0/0, scheduled: 2
  loaded plugins: charon save-keys sha2 sha1 md5 random nonce x509 revocation constraints pubkey pkcs8 pgp dnskey sshkey pem openssl fips-prf xcbc cmac drbg attr kernel-netlink resolve socket-default stroke updown counters
Listening IP addresses:
  223.94.60.86
  2001:db8:100::1
  fd50:2000::2
  fd25::3
  fd24::3
Connections:
   host-host:  %any...128.201.18.34  IKEv2
   host-host:   local:  [C=BR, ST=MG, O=Nansen, OU=Medicao, CN=strongs-01] uses public key authentication
   host-host:    cert:  "C=BR, ST=MG, O=Nansen, OU=Medicao, CN=strongs-01"
   host-host:   remote: uses public key authentication
   host-host:   child:  dynamic[47] === dynamic[47] TRANSPORT
Security Associations (1 up, 0 connecting):
   host-host[1]: ESTABLISHED 3 hours ago, 223.94.60.86[C=BR, ST=MG, O=Nansen, OU=Medicao, CN=strongs-01]...128.201.18.34[serialNumber=918UD8IEJZU, unstructuredName=CEMIGHER01A.ami.cemig.ad]
   host-host[1]: IKEv2 SPIs: 9f30ecd4bb9d05f6_i* d9ef0a0774caacba_r, public key reauthentication in 20 hours
   host-host[1]: IKE proposal: AES_CBC_256/HMAC_SHA2_256_128/PRF_HMAC_SHA2_256/MODP_1536
   host-host{4}:  INSTALLED, TRANSPORT, reqid 1, ESP in UDP SPIs: ce0100b2_i f84857bb_o
   host-host{4}:  AES_CBC_256/HMAC_SHA2_256_128, 4350 bytes_i (51 pkts, 8s ago), 10403 bytes_o (103 pkts, 0s ago), rekeying in 7 hours
   host-host{4}:   223.94.60.86/32[47] === 128.201.18.34/32[47]
[root@sx sbin]#
```

## GRE 隧道

本项目采用的是 host-host + GRE 模式，是为了 ip 的更换更加方便，GRE 可以实现 ipv6 in ipv4 的模式，从而让只支持 ipv4 的 vpn 隧道变为 ipv6 隧道。

### GRE 介绍

`通用路由封装`（英语：Generic Routing Encapsulation，缩写：`GRE`）是一种可以在虚拟`点对点`链路中封装多种网络层协议的`隧道协议`。由思科系统开发，在[RFC 2784](https://datatracker.ietf.org/doc/html/rfc2784)中定义。

GRE tun模式协议栈:

| OSI 模型分层        | 协议       |
| :------------------ | :--------- |
| 5.会话层            | X.225      |
| 4.传输层            | UDP        |
| 3.网络层 (GRE 封装) | IPv6       |
| 封装                | GRE        |
| 3.网络层            | IPv4       |
| 2.数据链路层        | 以太网     |
| 1.物理层            | 以太物理层 |

从上面的图表可以看出，协议封装（非特指 GRE）打破了 OSI 模型中定义的分层。这可以被看成两个不同协议栈中间的分割器，一个承载另一个。

![GRE](/assets/img/2021-07-28-strongswan-cisco-ipsecvpn/gre.png)

### GRE 环境搭建

在上面搭建好 host-host 隧道的基础上创建 GRE 隧道，这里需要注意下，GRE 隧道默认是位于三层（Layer 3）网络，不带 mac 信息的，在需要用到二层网络的地方需要使用 tap 模式

![GRETAP](/assets/img/2021-07-28-strongswan-cisco-ipsecvpn/gretap.png)

1. GRE tun 模式

```bash
ip tunnel add gre1 mode gre remote 128.201.18.34 local 223.94.60.86 ttl 255
ip link set gre1 up
ip addr add fd24::3/16 dev gre1
```

2. GRE tap 模式

```bash
./ip link add gre1 type gretap remote 128.201.18.34 local 223.94.60.86 ttl 255
./ip link set gre1 up
./ip addr add fd24::3/16 dev gre1
```

由于边缘计算网关 busybox 自带的 ip 命令功能不太全，所以用了`iproute2`工具

此处的 ttl 值一定要设置，默认是根据包裹的协议的 ttl 来的，比如包的是 dhcp 协议，ttl 就变成 1 了，会导致问题

### 添加路由

默认 GRE 协议在创建的时候就配好路由，对端的路由需要配置

配置到对端地址的路由

```bash
ip -6 route add fd12::/16 dev gre1  metric 256
```

如果使用的是 GRE-TAP，需要 mac 层信息，默认在发送报文前会发送 NDP 协议查找邻居，但是在 GRE 上不可行，所以要强制配好网关，网关地址即为对端 GRE 绑定地址

```bash
ip -6 route add 2002:db8:1::/64 via fd25::1 dev gre2  metric 1024
```

## DHCPv6

后续我会专门写一篇 DHCPv6 协议的介绍

## IKE协议

## ESP协议

## 实例

[GRE-over-ipsec-tunnel 成功.zip](/assets/doc/2021-07-28-strongswan-cisco-ipsecvpn/GRE-over-ipsec-tunnel成功.zip)

## 参考

- [移植 dhcp-4.2.6 到 ARM-linux](https://www.jianshu.com/p/7a1039729d70)
- [通用路由封装 - 维基百科，自由的百科全书](https://zh.wikipedia.org/wiki/%E9%80%9A%E7%94%A8%E8%B7%AF%E7%94%B1%E5%B0%81%E8%A3%85)
- [strongSwan官网](https://www.strongswan.org/)
