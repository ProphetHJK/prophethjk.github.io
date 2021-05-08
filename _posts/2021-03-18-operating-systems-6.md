---
title: "《Operating Systems: Three Easy Pieces》学习笔记(六) 调度：多级反馈队列"
author: Jinkai
date: 2021-03-18 09:00:00 +0800
published: false
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

本章将介绍一种著名的调度方法--`多级反馈队列`（Multi-level Feedback Queue，`MLFQ`）。1962 年，Corbato 首次提出多级反馈队列，应用于兼容时分共享系统（CTSS）。Corbato 因在 CTSS 中的贡献和后来在 Multics 中的贡献，获得了 ACM 颁发的图灵奖（Turing Award）。该调度程序经过多年的一系列优化，出现在许多现代操作系统中。

>**提示：从历史中学习**
>
>多级反馈队列是用历史经验预测未来的一个典型的例子，操作系统中有很多地方采用了这种技术（同样存在于计算机科学领域的很多其他地方，比如硬件的分支预测及缓存算法）。如果工作有明显的阶段性行为，因此可以预测，那么这种方式会很有效。当然，必须十分小心地使用这种技术，因为它可能出错，让系统做出比一无所知的时候更糟的决定。

## MLFQ：基本规则

MLFQ 中有许多独立的`队列`（queue），每个队列有不同的`优先级`（priority level）。任何时刻，一个工作只能存在于一个队列中。MLFQ 总是**优先执行较高优先级**的工作（即在**较高级队列**中的工作）。对于同一个队列中的任务，采用`轮转调度`。

`MLFQ`中工作优先级并不是固定的，而是会根据进程的行为`动态调整优先级`。例如，如果一个工作不断放弃CPU 去等待键盘输入，这是**交互型进程**的可能行为，MLFQ 因此会让它保持**高优先级**。相反，如果一个工作**长时间地占用** CPU，MLFQ 会**降低其优先级**。

![mlfq-1](/assets/img/2021-03-18-operating-systems-6/mlfq-1.jpg)

## 尝试 1：如何改变优先级



## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/08.pdf)
