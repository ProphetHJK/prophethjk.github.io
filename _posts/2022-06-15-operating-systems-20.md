---
title: "《Operating Systems: Three Easy Pieces》学习笔记(二十) 并发：介绍"
author: Jinkai
date: 2022-06-15 11:00:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

单个线程的状态与进程状态非常类似。线程有一个`程序计数器`（PC），记录程序从哪里获取指令。`每个线程`有自己的`一组`用于计算的`寄存器`。所以，如果有两个线程运行在一个处理器上，从运行一个线程（T1）`切换`到另一个线程（T2）时，必定发生`上下文切换`（context switch）。线程之间的上下文切换类似于进程间的上下文切换。对于进程，我们将状态保存到进程控制块（Process Control Block，PCB）。现在，我们需要一个或`多个线程控制块`（Thread Control Block，TCB），保存每个线程的状态。但是，与进程相比，线程之间的`上下文切换`有一点主要区别：`地址空间保持不变`（即`不需要切换`当前使用的`页表`）。

在多线程的进程中，每个线程独立运行，当然可以调用各种例程来完成正在执行的任何工作。不是地址空间中只有一个栈，而是每个线程都有一个栈。

![F26.1](/assets/img/2022-06-15-operating-systems-20/F26.1.jpg)

## 实例：线程创建

```c
#include <stdio.h>
#include <assert.h>
#include <pthread.h>

void *mythread(void *arg) {
    printf("%s\n", (char *) arg);
    return NULL;
}

int
main(int argc, char *argv[]) {
    pthread_t p1, p2;
    int rc;
    printf("main: begin\n");
    rc = pthread_create(&p1, NULL, mythread, "A"); assert(rc == 0);
    rc = pthread_create(&p2, NULL, mythread, "B"); assert(rc == 0);
    // join waits for the threads to finish
    rc = pthread_join(p1, NULL); assert(rc == 0);
    rc = pthread_join(p2, NULL); assert(rc == 0);
    printf("main: end\n");
    return 0;
}
```

## 为什么更糟糕：共享数据

两个线程递增同一个数，每次运行最终结果都不一样

原因是共享数据未保证操作`原子性`

后面都是些概念性的东西，不做赘述

## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/26.pdf)
