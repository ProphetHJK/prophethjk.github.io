---
title: "《Operating Systems: Three Easy Pieces》学习笔记(二十七) 基于事件的并发（进阶）"
author: Jinkai
date: 2022-06-16 10:00:00 +0800
published: false
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

`基于事件的并发`（event-based concurrency），在一些现代系统中较为流行，比如 `node.js`，但它源自于 C/UNIX 系统，我们下面将讨论。

基于事件的并发针对两方面的问题。一方面是多线程应用中，正确处理并发很有难度。 正如我们讨论的，`忘加锁`、`死锁`和其他烦人的问题会发生。另一方面，开发者无法`控制`多线程在某一时刻的`调度`(由系统调度)。

## 基本想法：事件循环

我们使用的基本方法就是`基于事件的并发`（event-based concurrency）。该方法很简单：我们等待某事（即“`事件`”）`发生`；当它发生时，检查事件类型，然后做少量的`相应工作`（可能是 I/O 请求，或者调度其他事件准备后续处理）。

这种应用都是基于一个简单的结构，称为`事件循环（event loop）`:

```c
while (1) {
    events = getEvents();
    for (e in events)
    processEvent(e);
}
```

` 主循环``等待 `某些`事件发生`（通过 getEvents()调用），然后依次`处理`这些发生的`事件`。处理事件的代码叫作`事件处理程序（event handler）`。重要的是，处理程序在处理一个事件时，它是系统中发生的唯一活动。因此，`调度`就是决定接下来处理哪个事件。这种对调度的`显式控制`，是基于事件方法的一个`重要优点`。

## 重要 API：select()（或 poll()）

如何`接收事件`?

`检查`是否有任何应该关注的`进入 I/O`。例如，假定`网络`应用程序（如 Web 服务器）希望检查是否有`网络数据包已到达`，以便为它们提供服务。

下面以 select()为例，手册页（在 macOS X 上）以这种方式描述 API：

```c
int select(
    int nfds,
    fd_set *restrict readfds,
    fd_set *restrict writefds,
    fd_set *restrict errorfds,
    struct timeval *restrict timeout);
```

select()检查 I/O 描述符`集合`，它们的地址通过 readfds、writefds 和 errorfds `参数`传入(相当于多个 readfd 组成的数组，write 同理)，分别查看它们中的某些描述符是否已`准备好读取`，是否`准备好写入`，或有`异常情况`待处理。在每个集合中检查`前 nfds 个`描述符，即检查描述符集合中从 `0 到 nfds-1` 的描述符。返回时，select()用给定请求操作准备好的描述符组成的`子集替换`给定的描述符集合。select()返回所有集合中就绪描述符的`总数`。

一个 select 调用就能识别所有句柄状态

关于 select()有几点要注意。首先，请注意，它可以让你检查描述符`是否可以读取和写入`。`前者`让服务器确定新数据包`已到达`并且`需要处理`，而`后者`则让服务知道`何时可以回复` （即出站队列未满）。

## 使用 select()

```c
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>

int main(void) {
    // open and set up a bunch of sockets (not own)
    // main loop
    while (1) {
        // initialize the fd_set to all zero
        fd_set readFDs;
        FD_ZERO(&readFDs);

        // now set the bits for the descriptors
        // this server is interested in
        // (for simplicity, all of them from min max)
        int fd;
        // 将初始化完的句柄都加入到readFDs句柄集合中
        for (fd = minFD; fd < maxFD; fd++)
            FD_SET(fd, &readFDs);

        // 调用select检测句柄是否可读，可读的句柄作为子集替换readFDs指针内容作为返回值
        int rc = select(maxFD+1, &readFDs, NULL,LL, NULL);

        // check which actually have data using_ISSET()
        int fd;
        for (fd = minFD; fd < maxFD; fd++)
            // 检测在readFDs中存在句柄
            if (FD_ISSET(fd, &readFDs))
                // 处理对应的句柄
                processFD(fd);
    }
}
```

## 为何更简单？无须锁

因为一次只处理一个事件，所以`不需要`获取或释放`锁`。基于事件的服务器`不能`被另一个线程`中断`，因为它确实是`单线程`的。因此，线程化程序中常见的`并发性错误`并没有出现在基本的基于事件的方法中。

## 一个问题：阻塞系统调用

在多线程框架下，一个线程因 IO 阻塞，其他线程也能执行。而因为事件系统本质是单线程，会导致整个线程阻塞。

我们在基于事件的系统中必须遵守一条规则：`不允许阻塞调用`。

## 解决方案：异步 I/O

异步 I/O（asynchronous I/O）。这些接口使应用程序能够发出 I/O 请求，并在 I/O 完成之前立即将`控制权返回`给调用者，`另外的接口`让应用程序能够`确定`各种 I/O 是否`已完成`。

macOS X 上提供的接口（其他系统有类似的 API）。这些 API 围绕着一个基本的结构，即 struct `aiocb` 或 `AIO 控制块`（AIO control block）。该结构的简化版本如下:

```c
struct aiocb {
    int aio_fildes; /* 文件
描述符File descriptor */
    off_t aio_offset; /* 文件内的偏移量File offset */
    volatile void *aio_buf; /* 读取结果的目标内存位置Location of buffer */
    size_t aio_nbytes; /* 长度Length of transfer */
};
```

`异步读取`（asynchronous read）API:

```c
int aio_read(struct aiocb *aiocbp);
```

检查 I/O `是否完成`，并且缓冲区（由 aio_buf 指向）现在是否有了请求的数据，可以通过轮询调用检查:

```c
int aio_error(const struct aiocb *aiocbp);
```

一些系统提供了基于`中断`（interrupt）的方法。此方法使用 `UNIX信号`（signal）在异步 I/O 完成时`通知应用程序`，从而`消除`了`重复询问`系统的需要。

## 另一个问题：状态管理

当事件处理程序发出`异步 I/O` 时，它必须打包一些`程序状态`，以便下一个`事件处理程序`在 I/O 最终完成时使用。

这个`额外的工作`在基于线程的程序中是不需要的，因为程序需要的状态在线程栈中。

基于事件的系统的`手工栈管理`（manual stack management），这是基于事件编程的基础

例子：

```c
int rc = read(fd, buffer, size); rc = write(sd, buffer, size);
```

在一个`多线程程序`中，做这种工作很`容易`。当 read()最终返回时，代码`立即知道`要写入哪个`套接字`，因为该信息位于`线程堆栈`中（在`变量 sd` 中）。

在`基于事件`的系统中，为了执行相同的任务，我们首先使用上面描述的 AIO 调用`异步`地发出`读取`。假设我们使用 `aio_error()`调用`定期检查`读取的完成情况。当该调用告诉我们`读取完成`时，基于事件的服务器如何知道该怎么做？

使用一种称为“`延续`（continuation）”的老编
程语言结构。在某些`数据结构`中，记录完成处理该事件需要的信息。当事件发生时（即磁盘 I/O 完成时），`查找所需信息`并处理事件。

在这个特定例子中，解决方案是将`套接字描述符（sd）`记录在由文件描述符（fd）`索引`的某种数据结构（例如，`散列表`）中。当磁盘 I/O 完成时，事件处理程序将使用文件描述符来`查找延续`，这会将套接字描述符的值返回给调用者。此时（最后），服务器可以完成最后的工作将数据写入套接字。

## 什么事情仍然很难

当系统从单个 CPU 转向多个 CPU 时，基于事件的方法的一些`简单性`就消失了。

它不能很好地与某些类型的系统活动集成，如分页
（paging）。例如，如果事件处理程序发生页错误，它将被阻塞(`隐式阻塞`，无法规避)，并且因此服务器在页错误完成之前不会有进展。

`阻塞`对于基于事件的服务器而言是灾难性的，因此程序员必须始终注意每个事件使用的 API 语义的这种变化。

## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/33.pdf)
