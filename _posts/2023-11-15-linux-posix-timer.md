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
