---
title: vscode远程SSH连接方法
author: Jinkai
date: 2021-03-01 09:00:00 +0800
published: true
categories: [技术]
tags: [vscode, ssh]
---

>参考：
>
>- [【工程调试记录】vscode远程连接卡顿、频繁掉线的一个解决方法](<https://blog.csdn.net/jyhongjax/article/details/106075493>)

## 安装Remote-SSH

-------

在商店搜索Remote-SSH，并安装

如需要连接windows自带的wsl虚拟机，可以使用Remote-WSL插件

![remote-ssh](/assets/img/2021-03-01-vscode-ssh-remote/vscode-remote-ssh.png)

## 修改配置文件

-------

1. 打开`远程资源管理器`标签
2. 选择`设置`图标
3. 编辑ssh config文件

![open-config](/assets/img/2021-03-01-vscode-ssh-remote/open-config.png)

![config-file](/assets/img/2021-03-01-vscode-ssh-remote/config-file.jpg)

## 使用私钥登录

-------

使用`ssh-keygen`生成公私钥对:

- 私钥`id_rsa`放置在Windows(SSH客户端)的用户`.ssh`目录下
- 公钥`id_rsa.pub`放置在ssh服务器的`.ssh`目录下，Linux下需重命名为`authorized_keys`

完成后可直接登录，无需输入密码

## SSH频繁断开问题

-------

连接成功后会发现SSH频繁断开，且速度很慢

### 原因

Windows自带openSSH版本较老，与Linux中的版本不兼容

使用`ssh -V`查看版本:

![openssh-version](/assets/img/2021-03-01-vscode-ssh-remote/openssh-version.jpg)

### 解决方法

使用git中自带的openSSH

编辑环境变量，将`C:\Program Files\Git\usr\bin`添加至`Path`环境变量，并置于上层

![system-env](/assets/img/2021-03-01-vscode-ssh-remote/system-env.png)

重新查看版本号,如显示版本为新版，则设置成功

```console
C:\Users\huangjinkai>ssh -V
OpenSSH_8.3p1, OpenSSL 1.1.1g  21 Apr 2020
```

关闭所有vscode窗口后，重新打开，可以发现SSH使用流畅，不会有掉线现象