---
title: "《Operating Systems: Three Easy Pieces》学习笔记(一) 操作系统介绍"
author: Jinkai
date: 2021-03-11 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

本系列文章将按照《Operating Systems: Three Easy Pieces》一书的章节顺序编写，结合原文与自己的感悟，以作笔记之用，如有不足之处，恳请在评论区指出

## 虚拟化 CPU

首先看个例子

```c
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <assert.h>
#include "common.h"

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        fprintf(stderr, "usage: cpu <string>\n");
        exit(1);
    }
    char *str = argv[1];
    while (1)
    {
        Spin(1);
        printf("%s\n", str);
    }
    return 0;
}
```

该程序每秒打印一次输入参数，是个死循环，不会退出

```shell
prompt> ./cpu A & ; ./cpu B & ; ./cpu C & ; ./cpu D &
[1] 7353
[2] 7354
[3] 7355
[4] 7356
A
B
D
C
A
B
D
C
A
C
B
D
...
```

当同时执行运行 4 个程序的命令时，打印几乎是同时运行的，而不是等待第一个程序运行结束才运行下个程序

对应单核的处理器，同时运行 4 个进程是不可能的，所有这里就要介绍 CPU 的虚拟化

事实证明，在硬件的一些帮助下，操作系统负责提供这种`假象`（illusion），即系统拥有非常多的`虚拟 CPU` 的假象。将单个 CPU（或其中一小部分）转换为看似无限数量的 CPU，从而让许多程序看似同时运行，这就是所谓的`虚拟化 CPU`（virtualizing the CPU）

当然运行不同进程时的策略，如优先级等也是需要讨论的

知识点：时分共享，上下文切换

## 虚拟化内存

```c
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include "common.h"

int main(int argc, char *argv[])
{
    int *p = malloc(sizeof(int)); // a1
    assert(p != NULL);
    printf("(%d) memory address of p: %08x\n",
           getpid(), (unsigned)p); // a2
    *p = 0;                        // a3
    while (1)
    {
        Spin(1);
        *p = *p + 1;
        printf("(%d) p: %d\n", getpid(), *p); // a4
    }
    return 0;
}
```

这是一个访问内存的程序（mem.c）

该程序做了几件事。首先，它分配了一些内存（a1 行）。然后，打印出内存的地址（a2 行），然后将数字 0 放入新分配的内存的第一个空位中（a3 行）。最后，程序循环，延迟一秒钟并`递增 p` 中保存的值。在每个打印语句中，它还会打印出所谓的正在运行程序的`进程标识符`（PID）（a4 行）。该 PID 对每个运行进程是唯一的。

该程序的输出如下：

```shell
prompt> ./mem
(2134) memory address of p: 00200000
(2134) p: 1
(2134) p: 2
(2134) p: 3
(2134) p: 4
(2134) p: 5
ˆC
```

当只运行一个程序时，p 递增，一切正常

```shell
prompt> ./mem &; ./mem &
[1] 24113
[2] 24114
(24113) memory address of p: 00200000
(24114) memory address of p: 00200000
(24113) p: 1
(24114) p: 1
(24114) p: 2
(24113) p: 2
(24113) p: 3
(24114) p: 3
(24113) p: 4
(24114) p: 4
...
```

当同时运行多个相同的程序时，分配的内存地址竟然是相同的，先抛开虚拟化的概念，以物理内存的角度看待，这几个程序分配的内存指针指向了同一块内存空间，也就是修改其中一个程序修改内存也会导致另一个程序中的值改变

但是从结果来看这两块内存相互独立，并不影响，就好像每个正在运行的程序都有自己的`私有内存`，而不是与其他正在运行的程序共享相同的物理内存

实际上，这正是操作系统虚拟化内存（virtualizing memory）时发生的情况。每个进程访问自己的私有虚拟地址空间（virtual address space）（有时称为地址空间，address space），操作系统以某种方式映射到机器的物理内存上。一个正在运行的程序中的内存引用不会影响其他进程（或操作系统本身）的地址空间。对于正在运行的程序，它完全拥有自己的物理内存。但实际情况是，物理内存是由操作系统管理的共享资源。

知识点：(等待补充)

## 并发

```c
#include <stdio.h>
#include <stdlib.h>
#include "common.h"

volatile int counter = 0;
int loops;

void *worker(void *arg)
{
    int i;
    for (i = 0; i < loops; i++)
    {
        counter++;
    }
    return NULL;
}

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        fprintf(stderr, "usage: threads <value>\n");
        exit(1);
    }
    loops = atoi(argv[1]);
    pthread_t p1, p2;
    printf("Initial value : %d\n", counter);

    Pthread_create(&p1, NULL, worker, NULL);
    Pthread_create(&p2, NULL, worker, NULL);
    Pthread_join(p1, NULL);
    Pthread_join(p2, NULL);
    printf("Final value : %d\n", counter);
    return 0;
}
```

主程序利用 Pthread_create()创建了两个线程（thread），每个线程中循环了 loops 次来递增全局变量`counter`。

理想情况下，counter 最终的值应该为 2xloops，因为两个线程各把 counter 递增了 loops 次

```shell
prompt> ./thread 100000
Initial value : 0
Final value : 143012 // huh??
prompt> ./thread 100000
Initial value : 0
Final value : 137298 // what the??
```

当运行时，发现值每次各不相同，且小于 2xloops。

事实证明，这些奇怪的、不寻常的结果与指令如何执行有关，指令每一执行一条。遗憾的是，上面的程序中的关键部分是增加共享计数器的地方，它需要 3 条指令：

- 一条将计数器的值从内存加载到寄存器
- 一条将其递增
- 一条将其保存回内存。

因为这 3 条指令甚不是以`原子方式`（atomically）执行（所有的指令一一性执行）的，所以奇怪的事情可能会发生。

知识点:`原子操作`,

## 持久性

操作系统中管理磁盘的软件通常称为文件系统（file system）。因此它负责以可靠和高效的方式，将用户创建的任何文件（file）存储在系统的磁盘上。

```c
#include <stdio.h>
#include <unistd.h>
#include <assert.h>
#include <fcntl.h>
#include <sys/types.h>

int main(int argc, char *argv[])
{
    int fd = open("/tmp/file", O_WRONLY | O_CREAT | O_TRUNC, S_IRWXU);
    assert(fd > -1);
    int rc = write(fd, "hello world\n", 13);
    assert(rc == 13);
    close(fd);
    return 0;
}
```

为了完成这个任务，该程序向操作系统发出 3 个调用。第一个是对 open()的调用，它打开文件并创建它。第二个是 write()，将一些数据写入文件。第三个是 close()，只是简单地关闭文件，从而表明程序不会再向它写入更多的数据。这些系统调用（system call）被转到称为文件系统（file system）的操作系统部分，然后该系统处理这些请求，并向用户返回某种错误代码。

首先确定新数据将驻留在磁盘上的哪个位置，然后在文件系统所维护的各种结构中对其进行记录。这样做需要向底层存储设备发出 I/O 请求，以读取现有结构或更新（写入）它们。所有写过设备驱动程序（device driver）的人都知道，让设备现表你执行某项操作是一个复杂而详细的过程。它需要深入了解低级别设备接口及其确切的语义。幸运的是，操作系统提供了一种通过系统调用来访问设备的标准和简单的方法。因此，OS 有时被视为标准库（standard library）。

出于性能方面的原因，大多数文件系统首先会`延迟`这些写操作一段时间，希望将其`批量分组`为较大的组。为了处理写入期间系统崩溃的问题，大多数文件系统都包含某种复杂的写入协议，如日志（journaling）或写时复制（copy-on-write），仔细`排序`写入磁盘的操作，以确保如果在写入序列期间发生故障，系统可以在之后恢复到合理的状态。为了使不同的通用操作更高效，文件系统采用了许多不同的数据结构和访问方法，从简单的列表到复杂的 `B 树`。

## 设计目标

**一个最基本的目标，是建立一些抽象（abstraction）**，让系统方便和易于使用。抽象对我们在计算机科学中做的每件事都很有帮助。抽象使得编写一个大型程序成为可能，将其划分为小而且容易理解的部分

**设计和实现操作系统的一个目标，是提供高性能（performance）**。换言之，我们的目标是`最小化`操作系统的`开销`（minimize the overhead）。但是虚拟化的设计是为了易于使用，无形之中会增大开销，比如虚拟页的切换，cpu 的调度等等，所以尽可能的保持易用性与性能的平衡至关重要

**另一个目标是在应用程序之间以及在 OS 和应用程序之间提供保护（protection）**。因为我们希望让许多程序同时运行，所以要确保一个程序的恶意或偶然的不良行为不会损害其他程序。保护是操作系统基本原理之一的核心，这就是`隔离`（isolation）。让进程彼此隔离是保护的关键，因此决定了 OS 必须执行的大部分任务

**操作系统也必须不间断运行**。当它失效时，系统上运行的所有应用程序也会失效。由于这种依赖性，操作系统往往力求提供高度的`可靠性`（reliability）。

## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/)
