---
title: "《Operating Systems: Three Easy Pieces》学习笔记(十) 插叙：内存操作 API"
author: Jinkai
date: 2022-06-08 10:00:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

在本章中，我们将介绍 UNIX 操作系统的内存分配接口

## 内存类型

- 栈内存

  它的申请和释放操作是编译器来`隐式`管理的，所以有时也称为`自动（automatic）内存`。比如，一个函数的`局部变量`，在进入函数时分配，退出时释放。

- 堆内存

  申请和释放都是`显式`的，比如 C 语言的`malloc`。

## malloc()调用

malloc 的用法，应该都会，不介绍了

## free()调用

释放 malloc 分配的空间

## calloc()调用

类似 malloc()，返回前会将区域全置 0。

## realloc()

创建一个更大的内存区域，并将旧区域拷贝到新区域

## 常见错误

1. 声明指针，但未分配空间
2. 分配的空间不够，导致溢出
3. 分配后未初始化
4. 分配后忘记释放（带 GC 的语言可以自动回收内存）
5. 在用完前释放了内存（悬挂指针）
6. 重复释放内存
7. free()传入的指针参数错误

进程结束时操作系统会回收所有内存，即使不进行 free()

内存分析工具：`purify`和`valgrind`

## 底层操作系统支持

malloc 和 free 依赖于 brk 系统调用，用于改变程序分断(break)位置：堆结束位置。

## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/14.pdf)
