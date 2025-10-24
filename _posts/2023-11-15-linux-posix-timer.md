---
title: "Linux Posix定时器使用"
author: Jinkai
date: 2023-11-15 08:00:00 +0800
published: true
categories: [教程]
tags: [Linux, 定时器]
---

## 概要

Linux 中有两种设置定时器的方法：内核接口和 Posix 接口。本文介绍 Posix 定时器的使用，内核接口参考[Linux 内核学习笔记之定时器和时间管理](/posts/linux-kernel-time/)。

## 配置定时器模式

### 线程模式

线程模式就是每次定时器触发时都开启一个线程执行任务，优点是使用比较方便，缺点就是每次都会创建一个线程，如果定时器触发比较频繁就会产生大量的线程，性能也会受影响。

```c
#include <time.h>
struct sigevent sev;
static void timerCallback(union sigval sv);

// 设置定时器事件，使用线程方式
sev.sigev_notify = SIGEV_THREAD;
// 设置回调
sev.sigev_notify_function = timerCallback;
//可以传递一个参数
sev.sigev_value.sival_ptr = params;
```

回调函数：

```c
void timerCallback(union sigval sv) {
    MyStruct *params = (MyStruct *)(sv.sival_ptr); // 获取参数
}
```

### 信号模式

```c
#include <time.h>
#include <signal.h>
struct sigevent sev;
static void timerCallback(int signo, siginfo_t *si, void *data);

// 设置定时器事件，使用信号方式，仅发送一个SIGALRM信号
sev.sigev_notify          = SIGEV_SIGNAL;
sev.sigev_signo           = SIGALRM;
// 可以传递一个参数
sev.sigev_value.sival_int = params;

// 处理SIGALRM信号
struct sigaction sa;
sa.sa_flags = SA_SIGINFO;
sa.sa_sigaction = timerCallback; // 设置回调
sigaction(SIGALRM, &sa, NULL);
```

回调函数：

```c
static void timerCallback(int signo, siginfo_t *si, void *data) {
    int params = si->si_value.sival_int; // 获取参数
    // do something...
}
```

## 配置定时器触发时间

```c
struct itimerspec its;
// 设置定时器间隔为1秒
its.it_value.tv_sec    = 0;
its.it_value.tv_nsec   = 1000 * 1000 * 1000; // 初始延时

// 如果是周期定时器，需要后续延迟
its.it_interval.tv_sec = 0;
its.it_interval.tv_nsec = 1000 * 1000 * 1000;
// 如果是单次定时器，不需要后续延迟
// its.it_interval.tv_nsec = 0;
```

## 创建定时器

```c
#include <stdio.h> // for perror
timer_t timerid;
// 创建定时器，使用CLOCK_REALTIME方式保证实时性
if (timer_create(CLOCK_REALTIME, &sev, &timerid) == -1)
{
    perror("timer_create");
    return 0;
}
```

## 启动定时器

```c
// 启动定时器
if (timer_settime(timerid, 0, &its, NULL) == -1) {
    perror("timer_settime");
    return 0;
}
```

## 删除定时器

```c
timer_delete(timerid);
```

## 注意事项

- 注意在链接时加上 `-lrt` 参数。
- 如果你的编译器默认未启用 Posix 支持，需要手动添加`#define _POSIX_C_SOURCE 199309L`宏
- 还有个古老的 Posix 接口 `setitimer`，这里不再做介绍。
- 信号模式下如果配置了信号将会导致同样使用该信号的功能失效，比如使用 SIGALRM 时会让 usleep 函数因为该信号提前退出，可以考虑使用 nanosleep 函数或使用其他信号：

  ```c
  struct timespec req, rem;
  req.tv_sec  = ms / 1000;
  req.tv_nsec = ms % 1000 * 1000 * 1000;
  while (nanosleep(&req, &rem) == -1) {
      if (errno == EINTR) {
          // 因信号中断，重新设置休眠时间
          req = rem;
      }
      else {
          perror("nanosleep");
          return;
      }
  }
  ```

## async-signal-safe

在使用信号模式时需要注意：信号是异步中断，它可以在任何用户态指令之间被内核投递并打断当前程序

如果信号处理函数调用了非安全函数，可能导致：

- 死锁（如 malloc 内部加锁，而主程序已持有该锁）
- 堆损坏（如 printf 修改 stdio 缓冲区，而主程序正在使用）
- 未定义行为（如调用 C++ 析构函数、抛出异常）
- 程序崩溃或静默数据损坏

> 信号处理函数不是普通函数！它运行在“危险模式”下。

所以引申出了 async-signal-safe（异步信号安全）的概念，Linux 标准中定义了一组可以在信号处理函数（signal handler）中安全调用的函数，称为 [async-signal-safe function](https://man7.org/linux/man-pages/man7/signal-safety.7.html):

> An async-signal-safe function is one that can be safely called from within a signal handler. Many functions are not async-signal-safe. In particular, nonreentrant functions are generally unsafe to call from a signal handler.

async-signal-safe 的特点：

- 不分配内存（不调用 malloc/new）
- 不使用锁（无内部互斥）
- 不修改全局状态（或使用原子操作）
- 可重入（reentrant） 或 无状态

## 附录：timerfd

除了 POSIX 定时器之外，Linux 还支持 `timerfd`，这是 Linux 特有的一个基于文件描述符的定时器机制。

它的核心思想是：将定时器事件转化为可读的文件描述符（fd）事件，从而可以无缝集成到 select/poll/epoll 等 I/O 多路复用机制中。

可以理解为 POSIX 定时器会在时间到时自动触发动作，而 timerfd 仅仅是产生一个事件，需要在应用循环中主动去检测该事件来产生动作，适合于基于事件循环的应用。
