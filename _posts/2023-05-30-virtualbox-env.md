---
title: "在virtualbox上搭建ubuntu开发环境"
author: Jinkai
date: 2023-05-30 09:00:00 +0800
published: true
categories: [教程]
tags: [virtual, ubuntu]
---

## 准备工具

1. [virtualbox](https://www.virtualbox.org/wiki/Downloads)
2. [ubuntu server 2204 镜像](https://ubuntu.com/download/server)

## 安装镜像

新建虚拟机，选中安装镜像，如果想在安装过程手动配置(如开启 SSH server 功能)，勾选跳过自动安装：

![virtualbox_install](/assets/img/2023-05-30-virtualbox-env/virtualbox_install.jpg)

点击下一步，配置 CPU、内存、硬盘等信息，一般默认即可，配置完如下：

![mainpanel](/assets/img/2023-05-30-virtualbox-env/virtualboxmainpanel.jpg)

之后可以直接运行虚拟机或者等配置完网卡等外设再开启。

## 配置网卡

### 桥接网卡

桥接网卡用于让虚拟机能作为独立设备连入局域网，与宿主机处于平等的网络地位(链路层)，同时可以通过 dhcp 获得局域网地址。

![mainpanel](/assets/img/2023-05-30-virtualbox-env/network1.jpg)

### NAT 网卡

NAT 网卡用于让虚拟机成为宿主机中的一个进程，能使用宿主机网络提供的传输层。如果宿主机可以连接互联网，则虚拟机通过 NAT 网卡也可以直接访问互联网。

![mainpanel](/assets/img/2023-05-30-virtualbox-env/network2.jpg)

### 双网卡配置 IP

ubuntu 18.04 之后需要手动激活双网卡

执行修改命令：

```bash
sudo vim /etc/netplan/00-installer-config.yaml
```

修改为如下内容(示例)：

```shell
# This is the network config written by 'subiquity'
network:
  ethernets:
    enp0s3:
            #dhcp4: true
            addresses: [10.9.1.8/24]
            #gateway4: 10.9.1.254
            nameservers:
              addresses: [8.8.8.8]
    enp0s8:
            dhcp4: true
  version: 2
```

其中`enp0s3`为桥接网卡，使用静态 IP 地址(或 dhcp)；`enp0s8`为 NAT 网卡，使用 dhcp 功能获取地址。注意将静态 ip 地址和 dns 服务器填写为正确的地址。

配置完后重启虚拟机，使用`ifconfig`查看网卡信息：

![mainpanel](/assets/img/2023-05-30-virtualbox-env/networkifconfig.jpg)

## 配置代理

### apt 代理

修改配置文件:

```bash
sudo vim /etc/apt/apt.conf.d/90curtin-aptproxy
```

修改代理 ip 和端口，注意代理服务器需要开放局域网访问权限和对应端口。（好像只支持**http 代理**）

```shell
Acquire::http::Proxy "http://10.9.1.123:1086";
Acquire::https::Proxy "http://10.9.1.123:1086";
```

### 通用代理

安装 proxychains：

```bash
sudo apt install proxychains
```

修改配置文件中的`ProxyList`选项，建议使用**socks5 代理**：

```config
[ProxyList]
socks5  10.9.1.122 1085
```

需要代理时直接在命令行前加上 proxychains 即可：

```bash
proxychains pip3 install requests
```

## 共享

### virtualbox 增强功能

通过安装增强功能，能实现虚拟机和宿主机直接共享文件夹、粘贴板、拖放等功能。

虚拟机运行时，点击*设备->安装增强功能*，将自动为当前运行的虚拟机挂载一个光驱：

![virtualbox_additions](/assets/img/2023-05-30-virtualbox-env/virtualbox_additions.png)

进入虚拟机内的挂载点，能看到光驱内有一些 virtulbox 提供的文件：

```console
dev@dev-PC:/$ cd /media/dev/VBox_GAs_7.0.8/
dev@dev-PC:/media/dev/VBox_GAs_7.0.8$ ls
AUTORUN.INF              VBoxDarwinAdditionsUninstall.tool
autorun.sh               VBoxLinuxAdditions.run
cert                     VBoxSolarisAdditions.pkg
NT3x                     VBoxWindowsAdditions-amd64.exe
OS2                      VBoxWindowsAdditions.exe
runasroot.sh             VBoxWindowsAdditions-x86.exe
TRANS.TBL                windows11-bypass.reg
VBoxDarwinAdditions.pkg
```

直接运行`autorun.sh`即可：

```shell
./autorun.sh
```

### 手动方法

由于增强功能不能兼容所有的 Linux 发行版，且会替换当前系统的内核，可能让运行不稳定，我并不喜欢安装增强功能。

下面提供一些替代方案：

#### 粘贴板

针对有 GUI 界面的 Linux，在宿主机上通过 ssh 工具连接虚拟机，然后在用户目录创建名为`paste`的文件，如果要往虚拟机复制文本，就用 vim 编辑这个文件，并写入需要传递的内容。然后进入虚拟机的 GUI 界面，打开该文件就能获取内容了。

![virtualbox_paste](/assets/img/2023-05-30-virtualbox-env/virtualbox_paste.png)

#### 文件共享

在虚拟机中安装 lrzsz：

```shell
sudo apt install lrzsz
```

在宿主机使用支持 Zmodem 的 ssh 工具(如 xshell):

```shell
# 上传
rz
# 下载
sz /home/dev/file
```

或者在宿主机上创建 smb 或 ftp 共享服务器，由虚拟机访问
