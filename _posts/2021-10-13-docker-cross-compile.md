---
title: "移植Docker到ARM嵌入式设备"
author: Jinkai
date: 2021-10-13 09:00:00 +0800
published: true
categories: [技术]
tags: [Docker, OS-level virtualization, container]
---

本文将会介绍如何对 Docker 源码进行交叉编译并将 Docker 相关组件移植到 arm 嵌入式设备上

## Docker 源码下载

Docker 相关组件的源码已经移动到了 moby 库，在[https://github.com/moby/moby](https://github.com/moby/moby)获取源码，我这边使用的是[moby-17.05.0-ce](https://github.com/moby/moby/releases/tag/v17.05.0-ce)这个 tag，因为嵌入式设备的资源空间有限，而新版本的 Docker 由于集成了大量功能，导致耗费资源较多，可能跑不起来。

下载[Source code](https://github.com/moby/moby/archive/refs/tags/v17.05.0-ce.tar.gz)：

```shell
wget https://github.com/moby/moby/archive/refs/tags/v17.05.0-ce.tar.gz
```

解压到合适位置：

```shell
tar -zxvf v17.05.0-ce.tar.gz
```

解压后目录如下图：

![docker-dir](/assets/img/2021-10-13-docker-cross-compile/docker-dir.jpg)

## 准备编译环境

Docker 编译需要在专用的 Docker 容器内进行，官方已经提供了完整的编译脚本，不过对于交叉编译的适配并不好，这里不使用自带的编译脚本，而是通过手动配置的办法进行编译

### 进入 Docker bash

通过 vim 编辑 Makefile 脚本，找到`cross:`这个编译选项，将 Makefile 脚本修改为:

```makefile
cross: build ## cross build the binaries for darwin, freebsd and\nwindows
        $(DOCKER_RUN_DOCKER) /bin/bash
```

![makefile-cross](/assets/img/2021-10-13-docker-cross-compile/makefile-cross.jpg)

以上操作表示进入 Docker 容器的 bash，而不是通过脚本直接编译

使用 make 命令（`DOCKER_CROSSPLATFORMS`这个编译参数好像不加也没事）：

```bash
DOCKER_CROSSPLATFORMS="linux/arm" make cross
```

之后容器构建脚本会开始执行构建命令，国内的网络环境可能下载不了某些库，如果有必要，自行修改源码目录下的`Dockerfile`。

构建完成后就会进入容器的 bash：

![docker-bash](/assets/img/2021-10-13-docker-cross-compile/docker-bash.jpg)

### 安装交叉编译工具链

使用 golang 交叉编译还是比较方便的，可惜只支持静态链接，二进制文件较大，动态链接还没试成功过

对于`armv5el`平台，需要对应的交叉编译工具链`arm-linux-gnueabi-gcc`，当前容器默认是没安装的，需要手动安装

安装交叉编译工具链：

```shell
echo "deb http://ftp.de.debian.org/debian sid main" >> /etc/apt/sources.list
apt-get update
apt-get install gcc-arm-linux-gnueabi
```

### 交叉编译依赖库

docker 编译会有两个选择，`binary/dynbinary`即静态编译与动态编译（dynbinary 好像不支持交叉编译，反正我没试成功），因此须要提供的 arm 库的数量也不一样：

```console
# 静态编译提供的dev如下：
  libapparmor-dev
  libdevmapper-dev
  libseccomp-dev
# 动态编译提供的dev如下：
  libapparmor-dev
  libdevmapper-dev
  libseccomp-dev
  libltdl-dev
  libattr1-dev
  libcap-dev
  intltool
  libtinfo-dev
  util-linux
  expat
  dbus
  ffi
  zlib
  glib-2.0
  libsystemd-dev
```

不过每个库都交叉编译比较麻烦，这里提供两种更简单的方法：

1. 直接通过 apt 安装

   如过当前的 debian 版本较新，可以直接通过 apt 安装，安装时指定对应的平台即可，armv5 对应是`armel`

   ```shell
   apt install libapparmor-dev:armel
   apt install libdevmapper-dev:armel
   apt install libseccomp-dev:armel
   ```

2. 去 debian 仓库网页下载

   部分 debian 的版本较老，仓库内可能没有对应的库，这时就要去手动下载，下面是部分库的地址：

   - <https://packages.debian.org/buster/libdevmapper-dev> (注意依赖)
   - <https://packages.debian.org/buster/libseccomp-dev>
   - <https://packages.debian.org/buster/libapparmor-dev>

   下载完是 deb 包，传到容器里，安装即可。如果无法安装就解压后覆盖到根目录

   ```shell
   dpkg --force-architecture -i libdevmapper-dev_1.02.155-3_armel.deb
   ```

   _注意：交叉编译时可能优先使用容器内自带的 x86 的库做链接，如果报了链接出错就把原来的库删了:_

   ```console
   /usr/local/lib/libseccomp.so: file not recognized: file format not recognized
   collect2: error: ld returned 1 exit status
   ```

   ```shell
   rm /usr/local/lib/libseccomp.a
   rm /usr/local/lib/libseccomp.so
   rm /usr/lib/libdevmapper.so
   rm /usr/lib/libdevmapper.a
   ```

### 设置编译相关环境变量

```shell
#由于docker是golang进行编译的因此直接声明目标平台架构
export GOARCH=arm
#打开CGO支持
export CGO_ENABLED=1
#声明目标平台系统
export GOOS=linux
#声明编译工具
export CC=arm-linux-gnueabi-gcc
#声明编译docker的版本
export DOCKER_GITCOMMIT=89658be
#Docker编译参数，这里禁用了一些组件
export DOCKER_BUILDTAGS='no_btrfs no_cri no_zfs exclude_disk_quota exclude_graphdriver_btrfs exclude_graphdriver_zfs no_buildkit'
```

## 编译 docker 依赖组件

`moby`项目只包含了`docker-client`和`docker-daemon`，其他的组件需要通过脚本单独下载编译：

```shell
#清理x64环境下的执行程序
rm -rf /usr/local/bin/docker-*
#编译执行程序
sh /go/src/github.com/docker/docker/hack/dockerfile/install-binaries.sh runc tini proxy containerd
```

![containerd-compile](/assets/img/2021-10-13-docker-cross-compile/containerd-compile.jpg)

编译完的文件自动部署在容器的`/usr/local/bin/`目录，需要自行拷贝出来。当然也可以自行修改`install-binaries.sh`脚本把二进制文件保存到自己希望的目录

## 编译 docker

使用 hack/make.sh 脚本进行编译 docker 与 dockerd 执行程序。

```shell
#编译静态包（成功）
hack/make.sh binary
#编译动态包（失败）
hack/make.sh dynbinary
```

![docker-build](/assets/img/2021-10-13-docker-cross-compile/docker-build.jpg)

编译完的二进制文件在/go/src/github.com/docker/docker/bundles/17.05.0-ce 目录，该目录是宿主机目录的映射，可以在宿主机目录/repo/moby-17.05.0-ce/bundles/17.05.0-ce 提取文件。别忘了上一节的依赖组件

```console
root@racknerd-ae2d96:~/repo/moby-17.05.0-ce/bundles/17.05.0-ce/binary-client# file docker-17.05.0-ce
docker-17.05.0-ce: ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), statically linked, Go BuildID=78906b998b797bc6afd511082f0928b0bd4c70a0, BuildID[sha1]=a1da4f0f805fc199891bba9ccc22d5b697186994, for GNU/Linux 3.2.0, with debug_info, not stripped
```

## 移植程序

把所有文件打包放入目标设备合适的目录

```console
17.05.0-ce
├── binary-client
│ ├── docker -> docker-17.05.0-ce
│ ├── docker-17.05.0-ce
│ ├── docker-17.05.0-ce.md5
│ └── docker-17.05.0-ce.sha256
└── binary-daemon
├── docker-containerd
├── docker-containerd-ctr
├── docker-containerd-ctr.md5
├── docker-containerd-ctr.sha256
├── docker-containerd.md5
├── docker-containerd.sha256
├── docker-containerd-shim
├── docker-containerd-shim.md5
├── docker-containerd-shim.sha256
├── dockerd -> dockerd-17.05.0-ce
├── dockerd-17.05.0-ce
├── dockerd-17.05.0-ce.md5
├── dockerd-17.05.0-ce.sha256
├── docker-init
├── docker-init.md5
├── docker-init.sha256
├── docker-proxy
├── docker-proxy.md5
├── docker-proxy.sha256
├── docker-runc
├── docker-runc.md5
└── docker-runc.sha256
```

## 扩展：balena-engine

介绍：_An engine purpose-built for embedded and IoT use cases, based on Moby Project technology from Docker_

官网：<https://www.balena.io/engine/>

移植 docker 的过程中无意中发现了 balena-engine，根据官网介绍这个软件是专门为 IoT 定制的精简版 docker，比 docker 更快更小。

整体的编译方法和 docker 相同，编译时使用`hack/make.sh binary-balena`就行，二进制文件只有一个，其他都是软链接。

![balena-engine](/assets/img/2021-10-13-docker-cross-compile/balena-engine.jpg)

## 运行 Docker

后面的介绍以 balena-engine 为例，Docker 也是一样的

### 运行环境检查

先下载检测脚本<https://github.com/moby/moby/blob/master/contrib/check-config.sh>

找到内核编译时的`.config`文件，使用`check-config.sh`对.config 进行检测，该操作可以不在目标机运行。

`Generally Necessary`表示必须满足的，如果有`missing`项一定要把功能启用了，重新编译内核

```console
$ ./check-config.sh
info: reading kernel config from ./.config ...

Generally Necessary:
- cgroup hierarchy: nonexistent??
    (see https://github.com/tianon/cgroupfs-mount)
- CONFIG_NAMESPACES: enabled
- CONFIG_NET_NS: enabled
- CONFIG_PID_NS: enabled
- CONFIG_IPC_NS: enabled
- CONFIG_UTS_NS: enabled
- CONFIG_CGROUPS: enabled
- CONFIG_CGROUP_CPUACCT: enabled
- CONFIG_CGROUP_DEVICE: enabled
- CONFIG_CGROUP_FREEZER: enabled
- CONFIG_CGROUP_SCHED: enabled
- CONFIG_CPUSETS: enabled
- CONFIG_MEMCG: enabled
- CONFIG_KEYS: enabled
- CONFIG_VETH: enabled
- CONFIG_BRIDGE: enabled
- CONFIG_BRIDGE_NETFILTER: enabled
- CONFIG_NF_NAT_IPV4: enabled
- CONFIG_IP_NF_FILTER: enabled
- CONFIG_IP_NF_TARGET_MASQUERADE: enabled
- CONFIG_NETFILTER_XT_MATCH_ADDRTYPE: enabled
- CONFIG_NETFILTER_XT_MATCH_CONNTRACK: enabled
- CONFIG_NETFILTER_XT_MATCH_IPVS: enabled
- CONFIG_IP_NF_NAT: enabled
- CONFIG_NF_NAT: enabled
- CONFIG_NF_NAT_NEEDED: enabled
- CONFIG_POSIX_MQUEUE: enabled
- CONFIG_DEVPTS_MULTIPLE_INSTANCES: enabled

Optional Features:
- CONFIG_USER_NS: missing
- CONFIG_SECCOMP: missing
- CONFIG_CGROUP_PIDS: missing
- CONFIG_MEMCG_SWAP: missing
- CONFIG_MEMCG_SWAP_ENABLED: missing
- CONFIG_MEMCG_KMEM: missing
- CONFIG_RESOURCE_COUNTERS: enabled
- CONFIG_BLK_CGROUP: missing
- CONFIG_BLK_DEV_THROTTLING: missing
- CONFIG_IOSCHED_CFQ: enabled
- CONFIG_CFQ_GROUP_IOSCHED: missing
- CONFIG_CGROUP_PERF: enabled
- CONFIG_CGROUP_HUGETLB: missing
- CONFIG_NET_CLS_CGROUP: missing
- CONFIG_NETPRIO_CGROUP: missing
- CONFIG_CFS_BANDWIDTH: missing
- CONFIG_FAIR_GROUP_SCHED: enabled
- CONFIG_RT_GROUP_SCHED: enabled
- CONFIG_IP_NF_TARGET_REDIRECT: enabled
- CONFIG_IP_VS: missing
- CONFIG_IP_VS_NFCT: missing
- CONFIG_IP_VS_PROTO_TCP: missing
- CONFIG_IP_VS_PROTO_UDP: missing
- CONFIG_IP_VS_RR: missing
- CONFIG_EXT3_FS: missing
- CONFIG_EXT3_FS_XATTR: missing
- CONFIG_EXT3_FS_POSIX_ACL: missing
- CONFIG_EXT3_FS_SECURITY: missing
    (enable these ext3 configs if you are using ext3 as backing filesystem)
- CONFIG_EXT4_FS: missing
- CONFIG_EXT4_FS_POSIX_ACL: missing
- CONFIG_EXT4_FS_SECURITY: missing
    enable these ext4 configs if you are using ext4 as backing filesystem
- Network Drivers:
  - "overlay":
    - CONFIG_VXLAN: missing
      Optional (for encrypted networks):
      - CONFIG_CRYPTO: enabled
      - CONFIG_CRYPTO_AEAD: enabled
      - CONFIG_CRYPTO_GCM: enabled
      - CONFIG_CRYPTO_SEQIV: enabled
      - CONFIG_CRYPTO_GHASH: enabled
      - CONFIG_XFRM: enabled
      - CONFIG_XFRM_USER: missing
      - CONFIG_XFRM_ALGO: missing
      - CONFIG_INET_ESP: missing
      - CONFIG_INET_XFRM_MODE_TRANSPORT: missing
  - "ipvlan":
    - CONFIG_IPVLAN: missing
  - "macvlan":
    - CONFIG_MACVLAN: missing
    - CONFIG_DUMMY: enabled
  - "ftp,tftp client in container":
    - CONFIG_NF_NAT_FTP: enabled
    - CONFIG_NF_CONNTRACK_FTP: enabled
    - CONFIG_NF_NAT_TFTP: enabled
    - CONFIG_NF_CONNTRACK_TFTP: enabled
- Storage Drivers:
  - "aufs":
    - CONFIG_AUFS_FS: missing
  - "btrfs":
    - CONFIG_BTRFS_FS: missing
    - CONFIG_BTRFS_FS_POSIX_ACL: missing
  - "devicemapper":
    - CONFIG_BLK_DEV_DM: missing
    - CONFIG_DM_THIN_PROVISIONING: missing
  - "overlay":
    - CONFIG_OVERLAY_FS: missing
  - "zfs":
    - /dev/zfs: missing
    - zfs command: missing
    - zpool command: missing

Limits:
cat: /proc/sys/kernel/keys/root_maxkeys: No such file or directory
./check-config.sh: line 351: [: -le: unary operator expected
cat: /proc/sys/kernel/keys/root_maxkeys: No such file or directory
- /proc/sys/kernel/keys/root_maxkeys:
```

### 挂载 cgroup

Docker 使用依赖于 cgroup，通过以下 shell 脚本挂载 cgroup：

```shell
#!/bin/bash
set -e

if grep -v '^#' /etc/fstab | grep -q cgroup; then
  echo 'cgroups mounted from fstab, not mounting /sys/fs/cgroup'
  exit 0
fi

# kernel provides cgroups?
if [ ! -e /proc/cgroups ]; then
  exit 0
fi

# 确保目录存在
if [ ! -d /sys/fs/cgroup ]; then
  exit 0
fi

# mount /sys/fs/cgroup if not already done
if ! mountpoint -q /sys/fs/cgroup; then
  mount -t tmpfs -o uid=0,gid=0,mode=0755 cgroup /sys/fs/cgroup
fi

cd /sys/fs/cgroup

# get/mount list of enabled cgroup controllers
for sys in $(awk '!/^#/ { if ($4 == 1) print $1 }' /proc/cgroups); do
  mkdir -p $sys
  if ! mountpoint -q $sys; then
    if ! mount -n -t cgroup -o $sys cgroup $sys; then rmdir $sys || true
    fi
  fi
done
exit 0
```

cgroup 挂载成功：

![cgroup-mount](/assets/img/2021-10-13-docker-cross-compile/cgroup-mount.jpg)

### 安装 iptables

Docker 需要 iptables 配置网络，关于 iptables 的交叉编译，在我之前写的文章《[strongSwan 与 Cisco CSR 1000V 建立 IPSec vpn 调试记录](https://hjk.life/posts/strongswan-cisco-ipsecvpn/#iptables-%E4%BA%A4%E5%8F%89%E7%BC%96%E8%AF%91)》里有提到

### 配置环境变量

需要配置 iptables 和 Docker 的运行环境变量

关于 XTABLES_LIBDIR 的信息，见这篇文章《[移植 iptables 扩展依赖问题](https://zhuanlan.zhihu.com/p/159638436)》

```shell
export PATH=$PATH:/media/disk/iptables/sbin:/media/disk/balena-engine
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/media/disk/iptables/lib
export XTABLES_LIBDIR=/media/disk/iptables/lib/xtables
```

### 修改 Docker 配置文件

Docker 的配置文件名为`daemon.json`，主要是配置 storage-driver 和 data-root，分别是文件系统驱动和数据根目录

daemon.json：

```json
{
  "storage-driver": "devicemapper",
  "data-root": "/media/disk/balena-engine/lib/docker",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3",
    "labels": "production_status",
    "env": "os,customer"
  }
}
```

### 运行 containerd 和 dockerd

运行 dockerd 会自动拉起 containerd：

```shell
balena-engine-daemon --config-file /media/disk/balena-engine/daemon.json
```

编写 start-docker.sh 脚本：

```shell
#/bin/sh
./mountcgroup.sh
export PATH=$PATH:/media/disk/iptables/sbin:/media/disk/balena-engine
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/media/disk/iptables/lib
export XTABLES_LIBDIR=/media/disk/iptables/lib/xtables
balena-engine-daemon --config-file /media/disk/balena-engine/daemon.json
```

启动日志：

```console
[root@sx binary-balena]# ./start-docker.sh
WARN[2021-10-13T06:56:16.290000000Z] could not change group /var/run/balena-engine.sock to balena-engine: group balena-engine not found
INFO[2021-10-13T06:56:16.310000000Z] libcontainerd: started new balena-engine-containerd process  pid=1351
INFO[0000] starting containerd                           module=containerd revision= version=1.0.0+unknown
INFO[0000] setting subreaper...                          module=containerd
INFO[0000] changing OOM score to -500                    module=containerd
INFO[0000] loading plugin "io.containerd.content.v1.content"...  module=containerd type=io.containerd.content.v1
INFO[0000] loading plugin "io.containerd.snapshotter.v1.overlayfs"...  module=containerd type=io.containerd.snapshotter.v1
INFO[0000] loading plugin "io.containerd.metadata.v1.bolt"...  module=containerd type=io.containerd.metadata.v1
INFO[0000] loading plugin "io.containerd.differ.v1.walking"...  module=containerd type=io.containerd.differ.v1
INFO[0000] loading plugin "io.containerd.gc.v1.scheduler"...  module=containerd type=io.containerd.gc.v1
INFO[0000] loading plugin "io.containerd.grpc.v1.containers"...  module=containerd type=io.containerd.grpc.v1
INFO[0000] loading plugin "io.containerd.grpc.v1.content"...  module=containerd type=io.containerd.grpc.v1
INFO[0000] loading plugin "io.containerd.grpc.v1.diff"...  module=containerd type=io.containerd.grpc.v1
INFO[0000] loading plugin "io.containerd.grpc.v1.events"...  module=containerd type=io.containerd.grpc.v1
INFO[0000] loading plugin "io.containerd.grpc.v1.healthcheck"...  module=containerd type=io.containerd.grpc.v1
INFO[0000] loading plugin "io.containerd.grpc.v1.images"...  module=containerd type=io.containerd.grpc.v1
INFO[0000] loading plugin "io.containerd.grpc.v1.leases"...  module=containerd type=io.containerd.grpc.v1
INFO[0000] loading plugin "io.containerd.grpc.v1.namespaces"...  module=containerd type=io.containerd.grpc.v1
INFO[0000] loading plugin "io.containerd.grpc.v1.snapshots"...  module=containerd type=io.containerd.grpc.v1
INFO[0000] loading plugin "io.containerd.monitor.v1.cgroups"...  module=containerd type=io.containerd.monitor.v1
INFO[0000] loading plugin "io.containerd.runtime.v1.linux"...  module=containerd type=io.containerd.runtime.v1
INFO[0000] loading plugin "io.containerd.grpc.v1.tasks"...  module=containerd type=io.containerd.grpc.v1
INFO[0000] loading plugin "io.containerd.grpc.v1.version"...  module=containerd type=io.containerd.grpc.v1
INFO[0000] loading plugin "io.containerd.grpc.v1.introspection"...  module=containerd type=io.containerd.grpc.v1
INFO[0000] serving...                                    address=/var/run/balena-engine/containerd/balena-engine-containerd-debug.sock module=containerd/debug
INFO[0000] serving...                                    address=/var/run/balena-engine/containerd/balena-engine-containerd.sock module=containerd/grpc
INFO[0000] containerd successfully booted in 0.190000s   module=containerd
INFO[2021-10-13T06:56:17.900000000Z] Graph migration to content-addressability took 0.00 seconds
WARN[2021-10-13T06:56:17.920000000Z] Your kernel does not support swap memory limit
WARN[2021-10-13T06:56:17.920000000Z] Your kernel does not support kernel memory limit
WARN[2021-10-13T06:56:17.920000000Z] Your kernel does not support cgroup cfs period
WARN[2021-10-13T06:56:17.920000000Z] Your kernel does not support cgroup cfs quotas
WARN[2021-10-13T06:56:17.920000000Z] Unable to find blkio cgroup in mounts
WARN[2021-10-13T06:56:17.940000000Z] mountpoint for pids not found
INFO[2021-10-13T06:56:17.960000000Z] Loading containers: start.
WARN[2021-10-13T06:56:18.010000000Z] Running modprobe nf_nat failed with message: `modprobe: can't change directory to '/lib/modules': No such file or directory`, error: exit status 1
WARN[2021-10-13T06:56:18.060000000Z] Running modprobe xt_conntrack failed with message: `modprobe: can't change directory to '/lib/modules': No such file or directory`, error: exit status 1
WARN[2021-10-13T06:56:19.810000000Z] Could not load necessary modules for IPSEC rules: Running modprobe xfrm_user failed with message: `modprobe: can't change directory to '/lib/modules': No such file or directory`, error: exit status 1
INFO[2021-10-13T06:56:26.480000000Z] Default bridge (balena0) is assigned with an IP address 172.17.0.0/16. Daemon option --bip can be used to set a preferred IP address
INFO[2021-10-13T06:56:28.920000000Z] Loading containers: done.
WARN[2021-10-13T06:56:28.920000000Z] Could not get operating system name: Error opening /usr/lib/os-release: open /usr/lib/os-release: no such file or directory
WARN[2021-10-13T06:56:30.450000000Z] failed to retrieve balena-engine-init version: exec: "balena-engine-init": executable file not found in $PATH
INFO[2021-10-13T06:56:30.450000000Z] Docker daemon                                 commit=89658be graphdriver(s)=vfs version=dev
INFO[2021-10-13T06:56:30.450000000Z] Daemon has completed initialization
INFO[2021-10-13T06:56:31.060000000Z] API listen on /var/run/balena-engine.sock
```

查看 Docker 信息：

```console
[root@sx binary-balena]# ./balena-engine info
Containers: 0
 Running: 0
 Paused: 0
 Stopped: 0
Images: 0
Server Version: dev
Storage Driver: vfs
Logging Driver: json-file
Cgroup Driver: cgroupfs
Plugins:
 Volume: local
 Network: bridge host null
 Log: journald json-file
Swarm:
 NodeID:
 Is Manager: false
 Node Address:
Runtimes: bare runc
Default Runtime: runc
Init Binary: balena-engine-init
containerd version:
runc version: 13e66eedaddfbfeda2a73d23701000e4e63b5471
init version: N/A (expected: )
Kernel Version: 3.10.108
Operating System: <unknown>
OSType: linux
Architecture: armv5tejl
CPUs: 1
Total Memory: 57.15MiB
Name: sx
ID: W6OF:ZM5H:HNWK:YOLX:3KPV:S4ZX:5CKC:A5YE:NKEP:CMTK:2JIW:GFTN
Docker Root Dir: /media/disk/balena-engine/lib/docker
Debug Mode (client): false
Debug Mode (server): false
Registry: https://index.docker.io/v1/
Labels:
Experimental: false
Insecure Registries:
 127.0.0.0/8
Live Restore Enabled: false

WARNING: No swap limit support
WARNING: No kernel memory limit support
WARNING: No cpu cfs quota support
WARNING: No cpu cfs period support
```

至此，Docker 已经启动完毕，后面就是通过 docker 命令安装镜像，启动容器之类的了，这里不在赘述。有关本地载入镜像的说明可以参考此博客《[Docker 本地导入镜像/保存镜像/载入镜像/删除镜像](https://www.cnblogs.com/linjiqin/p/8604756.html)》

## 参考

- [在 mac 环境下交叉编译 ARM32 版 Docker](https://blog.csdn.net/talkxin/article/details/83011017)
- [解决：dockerd: failed to start daemon: Devices cgroup isn‘t mounted](https://zmedu.blog.csdn.net/article/details/118293022)
- [Docker storage drivers](https://docs.docker.com/storage/storagedriver/select-storage-driver/)
- [Docker 之几种 storage-driver 比较](https://blog.csdn.net/vchy_zhao/article/details/70238690)
- [移植 iptables 扩展依赖问题](https://zhuanlan.zhihu.com/p/159638436)
- [Docker 本地导入镜像/保存镜像/载入镜像/删除镜像](https://www.cnblogs.com/linjiqin/p/8604756.html)
