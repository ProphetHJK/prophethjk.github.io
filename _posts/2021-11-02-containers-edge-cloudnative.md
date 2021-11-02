---
title: "容器,边缘计算与云原生"
author: Jinkai
date: 2021-11-02 09:00:00 +0800
published: true
categories: [技术]
tags: [containers, edge computing, cloud native, 容器, 边缘计算]
---

本文将会介绍现代容器技术的原理，以及容器如何与边缘计算和云原生结合起来，实现基于容器技术的物联网框架

## 容器定义

`操作系统层虚拟化`（Operating system–level virtualization），亦称`容器`化（Containerization）,是一种虚拟化技术，这种技术将操作系统内核虚拟化，可以让我们在一个`资源隔离`的进程中运行应用及其依赖项

运行应用程序所必需的组件都将打包成一个镜像并可以复用。执行镜像时，它运行在一个隔离环境中，并且不会共享宿主机的内存、CPU 以及磁盘，这就保证了容器内进程不能监控容器外的任何进程。

## 容器作用

### 可移植性

在操作系统层虚拟化之后，容器封装了运行应用程序所必需的所有相关细节，如应用程序依赖性和操作系统，可以实现软件的即时迁移（Live migration），使一个软件容器中的实例，即时移动到另一个操作系统下，再重新运行起来。但是在这种技术下，软件即时迁移，只能在同样的操作系统下进行。

### 隔离性与安全性

容器将一个容器的进程与另一个容器以及底层基础架构隔离开来。因此，一个容器中的任何升级或更改都不会影响另一个容器。一个容器内的应用也无法获取宿主机或其他容器的信息。不过容器也提供了共享机制，可以指定允许被共享的资源

### 资源限制

部分容器应用支持为每个容器分配指定比例的资源（包括 CPU、内存和磁盘空间），防止某个应用程序占用全部的系统资源，影响其他应用程序的正常工作

## 容器优缺点

### 容器的优点

- **敏捷环境：**

  容器技术最大的优点是创建容器实例比创建虚拟机示例快得多，容器轻量级的脚本可以从性能和大小方面减少开销。

- **提高生产力：**

  容器通过移除跨服务依赖和冲突提高了开发者的生产力。每个容器都可以看作是一个不同的微服务，因此可以独立升级，而不用担心同步。

- **版本控制：**

  每一个容器的镜像都有版本控制，这样就可以追踪不同版本的容器，监控版本之间的差异等等。

- **运行环境可移植：**

  容器封装了所有运行应用程序所必需的相关的细节比如应用依赖以及操作系统。这就使得镜像从一个环境移植到另外一个环境更加灵活。比如，同一个镜像可以在 Windows 或 Linux 或者 开发、测试或 stage 环境中运行。

- **标准化：**

  大多数容器基于开放标准，可以运行在所有主流 Linux 发行版、Microsoft 平台等等。

- **安全：**

  容器之间的进程是相互隔离的，其中的基础设施亦是如此。这样其中一个容器的升级或者变化不会影响其他容器。

### 容器的缺点

- **复杂性增加：**

  随着容器及应用数量的增加，同时也伴随着复杂性的增加。在生产环境中管理如此之多的容器是一个极具挑战性的任务，可以使用 Kubernetes 和 Mesos 等工具管理具有一定规模数量的容器。

- **原生 Linux 支持：**

  大多数容器技术，比如 Docker，基于 Linux 容器（LXC），相比于在原生 Linux 中运行容器，在 Microsoft 环境中运行容器略显笨拙，并且日常使用也会带来复杂性。

- **不成熟：**

  容器技术在市场上是相对新的技术，需要时间来适应市场。开发者中的可用资源是有限的，如果某个开发者陷入某个问题，可能需要花些时间才能解决问题。

## 容器 vs 虚拟机

### 虚拟机

- 特点:

  虚拟机(VM)是一种创建于物理硬件系统(位于外部或内部)、充当虚拟计算机系统的虚拟环境，它模拟出了自己的整套硬件，包括 CPU、内存、网络接口和存储器。需要系统管理程序或虚拟机监视器(Hypervisor)作为中间层

- 不足:
  1. 镜像较大
  2. 启动较慢
  3. 资源消耗较大

![vm](/assets/img/2021-11-02-containers-edge-cloudnative/vm.png)

### 容器

- 特点：

  容器位于物理服务器及其主机操作系统（通常为 Linux 或 Windows）的顶部。每个容器共享主机 OS 内核，通常也共享二进制文件和库。

- 优点：

  1. 镜像较小
  2. 启动较快
  3. 资源消耗较小，甚至可以忽略不计

![container](/assets/img/2021-11-02-containers-edge-cloudnative/container.png)

### 对比总览

|            虚拟机            |           容器           |
| :--------------------------: | :----------------------: |
|            重量级            |          轻量级          |
|           性能有限           |         本机性能         |
| 每个 VM 都在自己的 OS 中运行 | 所有容器共享主机操作系统 |
|         硬件级虚拟化         |      操作系统虚拟化      |
|   启动时间（以分钟为单位）   | 启动时间（以毫秒为单位） |
|        分配所需的内存        |    需要更少的内存空间    |
|     完全隔离，因此更安全     | 进程级隔离，可能不太安全 |

## 容器种类

现代容器技术大致可以分为两类：系统容器与应用容器

![containertype](/assets/img/2021-11-02-containers-edge-cloudnative/containertype.jpg)

### 系统容器

LXC，OpenVZ，Linux VServer，BSD Jails 和 Solaris

为运行完整的系统而设计，可以在一个容器内运行多个应用，镜像会较大

系统容器旨在运行多个进程和服务

### 应用容器

Docker 和 Rocket

为运行单个应用而设计，启动应用容器时，一般只会运行一个应用进程。(docker 也是支持在一个容器内运行多个进程的，但这不符合 docker 的设计理念)

应用程序容器旨在打包和运行单个服务

### LXC 简介

LXC，其名称来自 Linux 软件容器（Linux Containers）的缩写，一种操作系统层虚拟化（Operating system–level virtualization）技术，为 Linux 内核容器功能的一个用户空间接口。它将应用软件系统打包成一个软件容器（Container），内含应用软件本身的代码，以及所需要的操作系统核心和库。透过统一的名字空间和共享 API 来分配不同软件容器的可用硬件资源，创造出应用程序的独立沙箱运行环境，使得 Linux 用户可以容易的创建和管理系统或应用容器。

### Docker 简介

docker 出现之初，便是采用了 lxc 技术作为 docker 底层，对容器虚拟化的控制。后来随着 docker 的发展，Docker 引擎自己封装了 libcontainer （golang 的库）来实现 Cgroup 和 Namespace 控制，从而消除了对 lxc 的依赖。

Docker 发展到现在，已经不只是一项容器化技术那么简单。Docker 形成了一整套的平台，用于开发应用、交付（shipping）应用、运行应用、管理应用。

## Linux 容器原理

Linux 内核提供了几项特性（chroot、Namespace、Cgroups 和联合文件系统）用于虚拟化，现代容器技术正是利用了这些特性实现的

如果说 chroot 是用于隔离目录，那 namespace 就是用于隔离系统资源，cgroups 适用于物理资源分配

### chroot

chroot 是在 Unix 和 Linux 系统的一个操作，针对正在运作的软件进程和它的子进程，改变它外显的根目录，让进程以为该目录即为根目录。一个运行在这个环境下，经由 chroot 设置根目录的程序，它不能够对这个指定根目录之外的文件进行访问动作，不能读取，也不能更改它的内容。

### Namespace

Linux Namespace 是 kernel 的一个功能，它可以隔离一系列系统的资源，比如 PID(Process ID)，User ID, Network 等等。一般看到这里，很多人会想到一个命令 chroot，就像 chroot 允许把当前目录变成根目录一样(被隔离开来的)，Namesapce 也可以在一些资源上，将进程隔离起来，这些资源包括进程树，网络接口，挂载点等等。

在同一个 namespace 下的进程可以感知彼此的变化，而对外界的进程一无所知。这样就可以让容器中的进程产生错觉，认为自己置身于一个独立的系统中，从而达到隔离的目的。也就是说 linux 内核提供的 namespace 技术为 docker 等容器技术的出现和发展提供了基础条件。

对于容器管理进程，在创建一个容器时，需要通过 clone()和 setns()等系统调用来创建属于同一个 namespace 的若干子进程，这样这些子进程就拥有一个与宿主机系统隔离的用户空间，其只能访问指定的参数，无法访问其他命名空间参数，隔离了诸如进程列表、网卡信息、用户列表、主机名等用户空间参数。

涉及到的三个系统调用(system call)的 API：

- clone()：用来创建新进程，与 fork 创建新进程不同的是，clone 创建进程时候运行传递如 CLONE_NEW\* 的 namespace 隔离参数，来控制子进程所共享的内容，更多内容请查看 clone 手册
- setns()：让某个进程加入某个 namespace 之中
- unshare()：让某个进程脱离某个 namespace

以下是一些可以使用 namespace 进行隔离的系统参数：

- **UTS**

  主机名和域名

- **Mount**

  挂载点

- **IPC(Inter-Process Communication)**

  每个用户空间的 IPC 专有通道 , 若是 2 个用户空间可以互相通信, 这就隔离没有了意义, 所以要确保 2 个用户空间的 IPC 是独立的

- **PID(Process ID)**

  一个系统运行是基于 2 颗”树”, 一个是进程树, 一个是文件系统树, 所以 在一个用户空间上,一个进程要么是 init , 一个是属于某个进程的子进程, 在虚拟用户空间上, 我们要营造一个假象, 让里面的进程以为自己是 init 或者是属于某个进程的子进程, 但是一个主机上又只能有一个 init, 其他进程都是 init 的子进程 或者子子进程, 进程的消灭也得由其父进程进行消灭, 所以, 在每个虚拟的用户空间上, 都得有一个 init 进程 , 但事实上 init 只能有一个, 那就是宿主机的 init, **所以只能在每个用户空间上做一个假的 init, 在这个用户空间上只有一个进程 , 那就是假的 init , 这个假的 init 消失, 所有进程也都得消失, 所以,在每个虚拟用户空间上得有自己专有的 PID**

- **User**

  一个虚拟的用户空间得有一个 root , 但是一个内核只能有一个 root , 那就是宿主机的 root , 所以我们只能在每个用户空间上虚造一个 root , 这个 root 在内核看来只是一个普通的进程而已 ,但是对于这个虚拟用户空间来说 , 他有全部权限,对这个虚拟用户空间的进程来说, 这个假的 root 就是真 root

- **Network**

  每个虚拟的用户空间都以为自己是这个系统上的唯一的用户空间 , 所以对于虚拟用户空间来说 , 它得有自己的 ip , 网络协议栈 , 80 端口等 , 而且 2 个互相不同的虚拟用户空间还得互相通信调度

Linux Namespaces 功能参数和内核要求:

| namespace                        | 系统调用参数  | 隔离内容                  | 内核版本 |
| :------------------------------- | :------------ | :------------------------ | :------- |
| UTS                              | CLONE_NEWUTS  | 主机或域名                | 2.6.19   |
| IPC(Inter-Process Communication) | CLONE_NEWIPC  | 信号量,消息队列和共享内存 | 2.6.19   |
| PID(Process ID)                  | CLONE_NEWPID  | 进程编号                  | 2.6.24   |
| Network                          | CLONE_NEWNET  | 网络设备,网络栈,端口等    | 2.6.29   |
| Mount                            | CLONE_NEWNS   | 挂载点(文件系统)          | 2.6.19   |
| User                             | CLONE_NEWUSER | 用户和用户组              | 3.8      |

### Cgroups(Control Groups)

Cgroups(Control Groups) 是 Linux 内核提供的一种可以限制、记录、隔离进程组（process groups）所使用的物理资源（如：cpu,memory,IO 等等）的机制。可以对一组进程及将来的子进程的资源的限制、控制和统计的能力，这些资源包括 CPU，内存，存储，网络等。通过 Cgroups，可以方便的限制某个进程的资源占用，并且可以实时的监控进程的监控和统计信息。最初由 google 的工程师提出，后来被整合进 Linux 内核。Cgroups 也是 LXC 为实现虚拟化所使用的资源管理手段，可以说没有 Cgroups 就没有 LXC (Linux Container)。

Cgroup 作用：

1.限制进程组可以使用的资源数量（Resource limiting ）。比如：memory 子系统可以为进程组设定一个 memory 使用上限，一旦进程组使用的内存达到限额再申请内存，就会出发 OOM（out of memory）。

2.进程组的优先级控制（Prioritization ）。比如：可以使用 cpu 子系统为某个进程组分配特定 cpu share。

3.记录进程组使用的资源数量（Accounting ）。比如：可以使用 cpuacct 子系统记录某个进程组使用的 cpu 时间

4.进程组隔离（isolation）。比如：使用 ns 子系统可以使不同的进程组使用不同的 namespace，以达到隔离的目的，不同的进程组有各自的进程、网络、文件系统挂载空间。

5.进程组控制（control）。比如：使用 freezer 子系统可以将进程组挂起和恢复。

通过 mount -t cgroup 命令或进入/sys/fs/cgroup 目录，我们看到目录中有若干个子目录，我们可以认为这些都是受 cgroups 控制的资源以及这些资源的信息：

- blkio — 这 ​​​ 个 ​​​ 子 ​​​ 系 ​​​ 统 ​​​ 为 ​​​ 块 ​​​ 设 ​​​ 备 ​​​ 设 ​​​ 定 ​​​ 输 ​​​ 入 ​​​/输 ​​​ 出 ​​​ 限 ​​​ 制 ​​​，比 ​​​ 如 ​​​ 物 ​​​ 理 ​​​ 设 ​​​ 备 ​​​（磁 ​​​ 盘 ​​​，固 ​​​ 态 ​​​ 硬 ​​​ 盘 ​​​，USB 等 ​​​ 等 ​​​）。
- cpu — 这 ​​​ 个 ​​​ 子 ​​​ 系 ​​​ 统 ​​​ 使 ​​​ 用 ​​​ 调 ​​​ 度 ​​​ 程 ​​​ 序 ​​​ 提 ​​​ 供 ​​​ 对 ​​​ CPU 的 ​​​ cgroup 任 ​​​ 务 ​​​ 访 ​​​ 问 ​​​。​​​
- cpuacct — 这 ​​​ 个 ​​​ 子 ​​​ 系 ​​​ 统 ​​​ 自 ​​​ 动 ​​​ 生 ​​​ 成 ​​​ cgroup 中 ​​​ 任 ​​​ 务 ​​​ 所 ​​​ 使 ​​​ 用 ​​​ 的 ​​​ CPU 报 ​​​ 告 ​​​。​​​
- cpuset — 这 ​​​ 个 ​​​ 子 ​​​ 系 ​​​ 统 ​​​ 为 ​​​ cgroup 中 ​​​ 的 ​​​ 任 ​​​ 务 ​​​ 分 ​​​ 配 ​​​ 独 ​​​ 立 ​​​ CPU（在 ​​​ 多 ​​​ 核 ​​​ 系 ​​​ 统 ​​​）和 ​​​ 内 ​​​ 存 ​​​ 节 ​​​ 点 ​​​。​​​
- devices — 这 ​​​ 个 ​​​ 子 ​​​ 系 ​​​ 统 ​​​ 可 ​​​ 允 ​​​ 许 ​​​ 或 ​​​ 者 ​​​ 拒 ​​​ 绝 ​​​ cgroup 中 ​​​ 的 ​​​ 任 ​​​ 务 ​​​ 访 ​​​ 问 ​​​ 设 ​​​ 备 ​​​。​​​
- freezer — 这 ​​​ 个 ​​​ 子 ​​​ 系 ​​​ 统 ​​​ 挂 ​​​ 起 ​​​ 或 ​​​ 者 ​​​ 恢 ​​​ 复 ​​​ cgroup 中 ​​​ 的 ​​​ 任 ​​​ 务 ​​​。​​​
- memory — 这 ​​​ 个 ​​​ 子 ​​​ 系 ​​​ 统 ​​​ 设 ​​​ 定 ​​​ cgroup 中 ​​​ 任 ​​​ 务 ​​​ 使 ​​​ 用 ​​​ 的 ​​​ 内 ​​​ 存 ​​​ 限 ​​​ 制 ​​​，并 ​​​ 自 ​​​ 动 ​​​ 生 ​​​ 成 ​​​​​ 内 ​​​ 存 ​​​ 资 ​​​ 源使用 ​​​ 报 ​​​ 告 ​​​。​​​
- net_cls — 这 ​​​ 个 ​​​ 子 ​​​ 系 ​​​ 统 ​​​ 使 ​​​ 用 ​​​ 等 ​​​ 级 ​​​ 识 ​​​ 别 ​​​ 符 ​​​（classid）标 ​​​ 记 ​​​ 网 ​​​ 络 ​​​ 数 ​​​ 据 ​​​ 包 ​​​，可 ​​​ 允 ​​​ 许 ​​​ Linux 流 ​​​ 量 ​​​ 控 ​​​ 制 ​​​ 程 ​​​ 序 ​​​（tc）识 ​​​ 别 ​​​ 从 ​​​ 具 ​​​ 体 ​​​ cgroup 中 ​​​ 生 ​​​ 成 ​​​ 的 ​​​ 数 ​​​ 据 ​​​ 包 ​​​。​​​
- net_prio — 这个子系统用来设计网络流量的优先级
- hugetlb — 这个子系统主要针对于 HugeTLB 系统进行限制，这是一个大页文件系统。

更多 Cgroups 信息详见:

- <https://www.cnblogs.com/wjoyxt/p/9935098.html>

- <https://tech.meituan.com/2015/03/31/cgroups.html>

## LXC 原理

LXC，其名称来自 Linux 软件容器（Linux Containers）的缩写，一种操作系统层虚拟化（Operating system–level virtualization）技术，为 Linux 内核容器功能的一个用户空间接口。它将应用软件系统打包成一个软件容器（Container），内含应用软件本身的代码，以及所需要的操作系统核心和库。透过统一的名字空间和共享 API 来分配不同软件容器的可用硬件资源，创造出应用程序的独立沙箱运行环境，使得 Linux 用户可以容易的创建和管理系统或应用容器。

在 Linux 内核中，提供了 cgroups 功能，来达成资源的区隔化。它同时也提供了名称空间区隔化的功能，使应用程序看到的操作系统环境被区隔成独立区间，包括行程树，网络，用户 id，以及挂载的文件系统。但是 cgroups 并不一定需要引导任何虚拟机。

LXC 利用 cgroups 与 namespace 的功能，提供应用软件一个独立的操作系统环境。LXC 不需要 Hypervisor 这个软件层，软件容器（Container）本身极为轻量化，提升了创建虚拟机的速度。

作为一个开源容器平台，Linux 容器项目（LXC）提供了一组工具、模板、库和语言绑定。LXC 采用简单的命令行界面，可改善容器启动时的用户体验。

LXC 工作模式是这样的，使用 lxc-create 创建一个容器(名称空间)，然后通过模板(早期 shell 脚本，目前 yaml 脚本)，执行安装过程。这个模板，会自动实现安装过程，这个安装就是指向了你想创建的容器（名称空间）的系统发行版的仓库，利用仓库中的程序包下载至本地来完成安装过程。于是这个容器(名称空间)就像虚拟机一样使用。

LXC 依赖于 Linux 内核提供的 cgroup，chroot，namespace 特性

## Docker 原理

从 Docker 1.11 版本开始，Docker 容器运行就不是简单通过 Docker Daemon 来启动了，而是通过集成 containerd、runc 等多个组件来完成的。虽然 Docker Daemon 守护进程模块在不停的重构，但是基本功能和定位没有太大的变化，一直都是 CS 架构，守护进程负责和 Docker Client 端交互，并管理 Docker 镜像和容器。现在的架构中组件 containerd 就会负责集群节点上容器的生命周期管理，并向上为 Docker Daemon 提供 gRPC 接口。

![docker](/assets/img/2021-11-02-containers-edge-cloudnative/docker.png)

### Docker 组件

#### docker

docker 的命令行工具，是给用户和 docker daemon 建立通信的客户端。

#### dockerd

dockerd 是 docker 架构中一个常驻在后台的系统进程，称为 docker daemon，dockerd 实际调用的还是 containerd 的 api 接口（rpc 方式实现）,docker daemon 的作用主要有以下两方面：

- 接收并处理 docker client 发送的请求
- 管理所有的 docker 容器

有了 containerd 之后，dockerd 可以独立升级，以此避免之前 dockerd 升级会导致所有容器不可用的问题。

#### containerd

containerd 是 dockerd 和 runc 之间的一个中间交流组件，docker 对容器的管理和操作基本都是通过 containerd 完成的。containerd 的主要功能有：

- 容器生命周期管理
- 日志管理
- 镜像管理
- 存储管理
- 容器网络接口及网络管理

#### containerd-shim

containerd-shim 是一个真实运行容器的载体，每启动一个容器都会起一个新的 containerd-shim 的一个进程， 它直接通过指定的三个参数：容器 id，boundle 目录（containerd 对应某个容器生成的目录，一般位于：/var/run/docker/libcontainerd/containerID，其中包括了容器配置和标准输入、标准输出、标准错误三个管道文件），运行时二进制（默认为 runC）来调用 runc 的 api 创建一个容器，上面的 docker 进程图中可以直观的显示。其主要作用是：

- 它允许容器运行时(即 runC)在启动容器之后退出，简单说就是不必为每个容器一直运行一个容器运行时(runC)
- 即使在 containerd 和 dockerd 都挂掉的情况下，容器的标准 IO 和其它的文件描述符也都是可用的
- 向 containerd 报告容器的退出状态

有了它就可以在不中断容器运行的情况下升级或重启 dockerd，对于生产环境来说意义重大。

#### runC

runC 是 Docker 公司按照 OCI 标准规范编写的一个操作容器的命令行工具，其前身是 libcontainer 项目演化而来，runC 实际上就是 libcontainer 配上了一个轻型的客户端，是一个命令行工具端，根据 OCI（开放容器组织）的标准来创建和运行容器，实现了容器启停、资源隔离等功能。

### Docker 启动过程

当我们要创建一个容器的时候， Docker Daemon 请求  containerd  来创建一个容器，containerd 收到请求后，创建一个叫做  containerd-shim  的进程去操作容器，我们指定容器进程是需要一个父进程来做状态收集、维持 stdin 等 fd 打开等工作的，假如这个父进程就是 containerd，那如果 containerd 挂掉的话，整个宿主机上所有的容器都得退出了，而引入  containerd-shim  这个垫片就可以来规避这个问题了。

然后创建容器需要做一些 namespaces 和 cgroups 的配置，以及挂载 root 文件系统等操作，这些操作其实已经有了标准的规范，那就是 OCI（开放容器标准），runc  就是它的一个参考实现（runc 的前身是 libcontainer），这个标准其实就是一个文档，主要规定了容器镜像的结构、以及容器需要接收哪些操作指令，比如 create、start、stop、delete 等这些命令。runc  就可以按照这个 OCI 文档来创建一个符合规范的容器，既然是标准肯定就有其他 OCI 实现，比如 Kata、gVisor 这些容器运行时都是符合 OCI 标准的。

（ 2015 年 6 月 ，docker 公司将 libcontainer 捐出并改名为 runC 项目，交由一个完全中立的基金会管理，然后以 runC 为依据，大家共同制定一套容器和镜像的标准和规范 OCI。）

所以真正启动容器是通过  containerd-shim  去调用  runc  来启动容器的，runc  启动完容器后本身会直接退出，containerd-shim  则会成为容器进程的父进程, 负责收集容器进程的状态, 上报给 containerd, 并在容器中 pid 为 1 的进程退出后接管容器中的子进程进行清理, 确保不会出现僵尸进程。

## 容器管理

### Kubernetes

Kubernetes，又称为 k8s（首字母为 k、首字母与尾字母之间有 8 个字符、尾字母为 s，所以简称 k8s）或者简称为 "kube" ，是一种可自动实施 Linux 容器操作的开源平台。它可以帮助用户省去应用容器化过程的许多手动部署和扩展操作。也就是说，您可以将运行 Linux 容器的多组主机聚集在一起，由 Kubernetes 帮助您轻松高效地管理这些集群。而且，这些集群可跨公共云、私有云或混合云部署主机。因此，对于要求快速扩展的云原生应用而言（例如借助 Apache Kafka 进行的实时数据流处理），Kubernetes 是理想的托管平台。

### CRI 接口

CRI（Container Runtime Interface 容器运行时接口）本质上就是 Kubernetes 定义的一组与容器运行时进行交互的接口，所以只要实现了这套接口的容器运行时都可以对接到 Kubernetes 平台上来。不过 Kubernetes 推出 CRI 这套标准的时候还没有现在的统治地位，所以有一些容器运行时可能不会自身就去实现 CRI 接口，于是就有了  shim（垫片）， 一个 shim 的职责就是作为适配器将各种容器运行时本身的接口适配到 Kubernetes 的 CRI 接口上，其中  dockershim  就是 Kubernetes 对接 Docker 到 CRI 接口上的一个垫片实现。

![cri](/assets/img/2021-11-02-containers-edge-cloudnative/cri.png)

Kubelet 通过 gRPC 框架与容器运行时或 shim 进行通信，其中 kubelet 作为客户端，CRI shim（也可能是容器运行时本身）作为服务器

![cri1](/assets/img/2021-11-02-containers-edge-cloudnative/cri1.png)
![cri2](/assets/img/2021-11-02-containers-edge-cloudnative/cri2.png)
![cri3](/assets/img/2021-11-02-containers-edge-cloudnative/cri3.png)
![cri4](/assets/img/2021-11-02-containers-edge-cloudnative/cri4.png)

然后到了 containerd 1.1 版本后就去掉了  CRI-Containerd  这个 shim，直接把适配逻辑作为插件的方式集成到了 containerd 主进程中，现在这样的调用就更加简洁了。

### KubeEdge

KubeEdge 是一个开源的系统，可将本机容器化应用编排和管理扩展到边缘端设备。 它基于 Kubernetes 构建，为网络和应用程序提供核心基础架构支持，并在云端和边缘端部署应用，同步元数据。KubeEdge 还支持 MQTT 协议，允许开发人员编写客户逻辑，并在边缘端启用设备通信的资源约束。KubeEdge 包含云端和边缘端两部分。

#### KubeEdge 特点

- **边缘计算**

  通过在边缘端运行业务逻辑，可以在本地保护和处理大量数据。KubeEdge 减少了边和云之间的带宽请求，加快响应速度，并保护客户数据隐私。

- **简化开发**

  开发人员可以编写常规的基于 http 或 mqtt 的应用程序，容器化并在边缘或云端任何地方运行。

- **Kubernetes 原生支持**

  使用 KubeEdge 用户可以在边缘节点上编排应用、管理设备并监控应用程序/设备状态，就如同在云端操作 Kubernetes 集群一样。

- **丰富的应用程序**

  用户可以轻松地将复杂的机器学习、图像识别、事件处理等高层应用程序部署到边缘端。

#### KubeEdge 架构

![kubeedge](/assets/img/2021-11-02-containers-edge-cloudnative/kubeedge.png)

##### 云上部分

- CloudHub: CloudHub 是一个 Web Socket 服务端，负责监听云端的变化, 缓存并发送消息到 EdgeHub。
- EdgeController: EdgeController 是一个扩展的 Kubernetes 控制器，管理边缘节点和 Pods 的元数据确保数据能够传递到指定的边缘节点。
- DeviceController: DeviceController 是一个扩展的 Kubernetes 控制器，管理边缘设备，确保设备信息、设备状态的云边同步。

##### 边缘部分

- EdgeHub: EdgeHub 是一个 Web Socket 客户端，负责与边缘计算的云服务（例如 KubeEdge 架构图中的 Edge Controller）交互，包括同步云端资源更新、报告边缘主机和设备状态变化到云端等功能。
- Edged: Edged 是运行在边缘节点的代理，用于管理容器化的应用程序。
- EventBus: EventBus 是一个与 MQTT 服务器（mosquitto）交互的 MQTT 客户端，为其他组件提供订阅和发布功能。
- ServiceBus: ServiceBus 是一个运行在边缘的 HTTP 客户端，接受来自云上服务的请求，与运行在边缘端的 HTTP 服务器交互，提供了云上服务通过 HTTP 协议访问边缘端 HTTP 服务器的能力。
- DeviceTwin: DeviceTwin 负责存储设备状态并将设备状态同步到云，它还为应用程序提供查询接口。
  MetaManager: MetaManager 是消息处理器，位于 Edged 和 Edgehub 之间，它负责向轻量级数据库（SQLite）存储/检索元数据。

## 参考

- [虚拟机和容器有什么不同*ThinkWon 的博客-CSDN 博客*容器和虚拟机的区别](https://blog.csdn.net/thinkwon/article/details/107476886)
- [容器技术概览 - DockOne.io](http://dockone.io/article/2442)
- [操作系统容器与应用程序容器 - 技术记录栈 (xieyonghui.com)](https://cs.xieyonghui.com/container/os-container-and-app-container_172.html)
- [操作系统层虚拟化 - 维基百科，自由的百科全书 (wikipedia.org)](https://zh.wikipedia.org/wiki/%E4%BD%9C%E6%A5%AD%E7%B3%BB%E7%B5%B1%E5%B1%A4%E8%99%9B%E6%93%AC%E5%8C%96)
- [什么是容器化？ (redhat.com)](https://www.redhat.com/zh/topics/cloud-native-apps/what-is-containerization)
- [容器核心技术--chroot,namespace,cgroups,LCX,和 docker](https://haojianxun.github.io/2017/11/05/%E5%AE%B9%E5%99%A8%E5%8F%91%E5%B1%95%E5%8F%B2%E5%92%8Cdocker%E5%AE%B9%E5%99%A8%E6%A0%B8%E5%BF%83%E6%8A%80%E6%9C%AF--chroot%20,namespace%E5%92%8Ccgroups/)
- [Docker 容器技术基础入门-Hukey's Blog](https://www.cnblogs.com/hukey/p/14055907.html)
- [一文搞懂容器运行时 Containerd](https://www.qikqiak.com/post/containerd-usage/)
- [Linux Namespace 技术与 Docker 原理浅析](https://creaink.github.io/post/Computer/Linux/Linux-namespace.html)
- [Linux 的 Namespace 与 Cgroups 介绍](https://www.cnblogs.com/wjoyxt/p/9935098.html)
- [Linux 资源管理之 cgroups 简介-美团技术团队](https://tech.meituan.com/2015/03/31/cgroups.html)
- [Docker 架构中的几个核心概念](https://www.jianshu.com/p/de3184ad0800)
- [Docker 实现原理/容器原理（LXC,Cgroups，Docker）](http://www.voycn.com/article/dockershixianyuanlirongqiyuanlilxccgroupsdocker)
- [云原生在物联网中的应用【拜托了，物联网！】](https://bbs.huaweicloud.com/blogs/301069)
