---
title: "在deepin中使用新版本GCC"
author: Jinkai
date: 2023-10-11 09:00:00 +0800
published: true
categories: [教程]
tags: [GCC, deepin]
---

## 问题

deepin 的官方仓库更新较慢，最新 deepin V20 版本的默认 GCC 居然还是 GCC8，很多特性都不支持。

下面介绍下如何在不使用容器的情况下安装使用 GCC12，同时不影响系统自带的 GCC。

## 安装 debian 的 rootfs

安装 debian 的 rootfs 是为了使用 debian 的仓库下载 GCC。

1. 前往[清华大学镜像站](https://mirrors.tuna.tsinghua.edu.cn/lxc-images/images/debian/bookworm/amd64/default)下载 debian 的 rootfs.tar.gz
2. 将 rootfs.tar.gz 解压到数据盘的个人目录中。
3. 进入目录，在该目录执行 chroot：

   ```shell
   sudo chroot ./
   ```

4. (可选)为 apt 添加代理
5. 执行`apt install gcc g++`来安装最新的 GCC 版本，目前是 GCC12。
6. 如果遇到包不存在错误，说明 apt 的包 cache 过时了，不过`apt update`命令好像不能执行，解决方法是按提示去手动下载该 deb 包的最新版，并用 dpkg 安装。

   ```console
   E: Failed to fetch http://deb.debian.org/debian-security/pool/updates/main/l/linux/linux-libc-dev_6.1.38-4_amd64.deb  404  Not Found
   ```

7. 检查 GCC 版本

   ```console
   root@dev-PC:~# gcc -v
   Using built-in specs.
   COLLECT_GCC=gcc
   COLLECT_LTO_WRAPPER=/usr/lib/gcc/x86_64-linux-gnu/12/lto-wrapper
   OFFLOAD_TARGET_NAMES=nvptx-none:amdgcn-amdhsa
   OFFLOAD_TARGET_DEFAULT=1
   Target: x86_64-linux-gnu
   Configured with: ../src/configure -v --with-pkgversion='Debian 12.2.0-14' --with-bugurl=file:///usr/share/doc/gcc-12/README.Bugs --enable-languages=c,ada,c++,go,d,fortran,objc,obj-c++,m2 --prefix=/usr --with-gcc-major-version-only --program-suffix=-12 --program-prefix=x86_64-linux-gnu- --enable-shared --enable-linker-build-id --libexecdir=/usr/lib --without-included-gettext --enable-threads=posix --libdir=/usr/lib --enable-nls --enable-clocale=gnu --enable-libstdcxx-debug --enable-libstdcxx-time=yes --with-default-libstdcxx-abi=new --enable-gnu-unique-object --disable-vtable-verify --enable-plugin --enable-default-pie --with-system-zlib --enable-libphobos-checking=release --with-target-system-zlib=auto --enable-objc-gc=auto --enable-multiarch --disable-werror --enable-cet --with-arch-32=i686 --with-abi=m64 --with-multilib-list=m32,m64,mx32 --enable-multilib --with-tune=generic --enable-offload-targets=nvptx-none=/build/gcc-12-bTRWOB/gcc-12-12.2.0/debian/tmp-nvptx/usr,amdgcn-amdhsa=/build/gcc-12-bTRWOB/gcc-12-12.2.0/debian/tmp-gcn/usr --enable-offload-defaulted --without-cuda-driver --enable-checking=release --build=x86_64-linux-gnu --host=x86_64-linux-gnu --target=x86_64-linux-gnu
   Thread model: posix
   Supported LTO compression algorithms: zlib zstd
   gcc version 12.2.0 (Debian 12.2.0-14)
   ```

## 使用

使用的话暂时只能想到将要编译的项目放入上一步生成的 rootfs 中，然后在 chroot 到该 rootfs 的情况下编译，防止使用到系统自带的 libc 库。

这个方式的优势是不需要安装额外的容器服务(如 lxc,docker)，直接使用内核自带的 chroot 即可，当然如果系统中已经安装了容器服务，可以直接用容器的方式，可能效果会更好。
