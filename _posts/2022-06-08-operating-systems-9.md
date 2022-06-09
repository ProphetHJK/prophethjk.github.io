---
title: "《Operating Systems: Three Easy Pieces》学习笔记(九) 抽象：地址空间"
author: Jinkai
date: 2022-06-08 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

## 早期系统

操作系统曾经是一组函数（实际上是一个库），在内存中（在本例中，从物理地址 0 开始），然后有一个正在运行的程序（进 程），目前在物理内存中（在本例中，从物理地址 64KB 开始）， 并使用剩余的内存。这里几乎没有抽象。

![F13.1](/assets/img/2022-06-08-operating-systems-9/F13.1.jpg)

## 多道程序和时分共享

![F13.2](/assets/img/2022-06-08-operating-systems-9/F13.2.jpg)

3 个进程（A、B、C），每个进程拥有从 512KB 物理内存中切出来给它们的一小部分内存。假定只有一 个 CPU，操作系统选择运行其中一个进程（比如 A），同时其 他进程（B 和 C）则在队列中等待运行。

## 地址空间

![F13.3](/assets/img/2022-06-08-operating-systems-9/F13.3.jpg)

代码
: 程序代码位置，静态的

栈
: 向上增长，不一定放在底部

堆
: 向下增长，不一定放在代码段下

这个 0-16KB 的地址空间是虚拟的，不是实际的物理地址（0 物理地址一般是 boot 程序，不可能给一个用户程序用）

内存虚拟化也保证了隔离性和安全性。

## 目标

- 透明：进程不知道自己运行在虚拟内存环境下，就好像地址都是物理地址一样
- 效率：虚拟化时不应该拖慢调度和运行时间，不应该占用更多内存
- 保护：不会影响操作系统和其他进程的内存空间

## 小结

## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/13.pdf)
