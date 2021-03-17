---
title: "《Operating Systems: Three Easy Pieces》学习笔记(五) 进程调度：介绍"
author: Jinkai
date: 2021-03-17 9:00:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

> 参考：
>
> - [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/07.pdf)

## 假设

为了方便概念的描述，对操作系统中运行的进程（有时也叫工作任务）做出如下的假设：

### 工作负载

1. 每一个工作运行相同的时间。
2. 所有的工作同时到达。
3. 一旦开始，每个工作保持运行直到完成。
4. 所有的工作只是用 CPU（即它们不执行 IO 操作）。
5. 每个工作的运行时间是已知的。

### 调度指标

任务的周转时间定义为任务完成时间减去任务到达系统的时间。更正式的周转时间定义 T_{周转时间} 是：

    T_{周转时间}= T_{完成时间}−T_{到达时间}

因为我们假设所有的任务在同一时间到达，那么 T_{到达时间}= 0，因此 T_{周转时间}= T_{完成时间}。随着我们放宽上述假设，这个情况将改变
