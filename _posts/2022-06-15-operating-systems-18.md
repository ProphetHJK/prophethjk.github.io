---
title: "《Operating Systems: Three Easy Pieces》学习笔记(十八) 超越物理内存：策略"
author: Jinkai
date: 2022-06-15 09:00:00 +0800
published: true
math: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

由于`内存压力`（memory pressure）迫使操作系统`换出`（paging out）一些页，为常用的页腾出空间。确定要`踢出`（evict）哪个页（或哪些页）封装在操作系统的`替换策略`（replacement policy）中。

这章讲的是 cache，就是加速硬盘读取，以页为单位，在内存中创建硬盘页的缓存

## 缓存管理

将`物理内存页`作为`硬盘内存页`的`缓存cache`

能直接从物理内存页中找到即为`缓存命中`，未找到即为`缓存未命中`

就可以计算程序的`平均内存访问时间`（Average Memory Access Time，AMAT）：

${AMAT} = (P_{Hit}·T_M) + (P_{Miss}·T_D)$

其中 $T_M$ 表示访问`内存`的`成本`， $T_D$ 表示访问`磁盘`的`成本`， $P_{Hit}$ 表示在缓存中找到数据的`概率`（`命中`），$P_{Miss}$ 表示在缓存中找不到数据的`概率`（`未命中`）。 $P_{Hit}$ 和 $P_{Miss}$ 从 0.0 变化到 1.0，并且 $P_{Miss}$ + $P_{Hit}$ = 1.0。

在现代系统中，`磁盘`访问的`成本非常高`，即使很小概率的未命中也会拉低正在运行的程序的总体 `AMAT`。显然，我们必须尽可能地避免缓存未命中，避免程序以磁盘的速度运行。

## 最优替换策略

最优（optimal）策略:
: 替换内存中在`最远将来`才会被访问到的页，可以达到缓存未命中率`最低`。

> **提示：与最优策略对比`非常有用`**
>
> 用于自己实现的算法的评估依据。
> 虽然最优策略非常`不切实际`，但作为仿真或其他研究的比较者还是非常有用的。比如，单说你喜欢的新算法有 80% 的命中率是没有意义的，但加上最优算法只有 82% 的命中率（因此你的新方法非常`接近最优`），就会使得结果很`有意义`，并给出了它的上下文。因此，在你进行的任何研究中，知道最优策略可以方便进行`对比`，知道你的策略有多大的改进空间，也用于决定当策略已经`非常接近`最优策略时，停止做`无谓`的`优化`[AD03]。

遗憾的是，正如我们之前在开发调度策略时所看到的那样，未来的访问是`无法知道`的，你无法为通用操作系统实现最优策略。在开发一个真正的、可实现的策略时，我们将聚焦于寻找其他决定把哪个页面踢出的方法。因此，最优策略只能`作为比较`，知道我们的策略有`多接近“完美”`。

## 简单策略：FIFO

页在进入系统时，简单地放入一个队列。当发生替换时，队列`尾部`的页（“先入”页）被`踢出`。

先进先出（FIFO）根本无法确定页的`重要性`：即使页 0 已被多次访问，FIFO 仍然会将其踢出，因为它是第一个进入内存的

## 另一简单策略：随机

在内存满的时候它随机选择一个页进行替换。

有些时候（仅仅 40%的概率），随机和最优策略一样好，有时候情况会更糟糕，随机策略取决于当时的运气。

## 利用历史数据：LRU

如果某个程序在`过去访问`过某个页，则很有可能在不久的将来会`再次访问`该页

`页替换策略`可以使用的一个历史信息是`频率`（frequency）。如果一个页被访问了很多次，也许它不应该被替换，因为它显然更有价值。页更常用的属性是访问的`近期性`（recency），越近被访问过的页，也许再次访问的可能性也就越大。

这一系列的策略是基于人们所说的`局部性原则`（principle of locality）

> **补充：局部性类型**
>
> 程序倾向于表现出两种类型的局部。第一种是`空间局部性`（spatial locality），它指出如果页 P 被访问，可能`围绕它的页`（比如 P−1 或 P + 1）也会`被访问`。第二种是`时间局部性`（temporal locality），它指出`近期访问`过的页面很可能在`不久的将来`再次`访问`。假设存在这些类型的局部性，对硬件系统的缓存层次结构起着重要作用，硬件系统部署了许多级别的指令、数据和地址转换缓存，以便在存在此类局部性时，能帮助程序快速运行。
>
> 当然，通常所说的局部性原则（principle of locality）并不是硬性规定，所有的程序都必须遵守。事实上，一些程序以相当`随机`的方式访问内存（或磁盘），并且在其访问序列中不显示太多或完全没有局部性。因此，尽管在设计任何类型的缓存（硬件或软件）时，局部性都是一件好事，但它并不能保证成功。相反，它是一种经常证明在计算机系统设计中有用的启发式方法

基于局部性原则，有两种替换策略。“`最不经常使用`”（Least-Frequently-Used，`LFU`）策略会替换`最不经常使用`的页。同样，“`最近最少使用`”（Least-Recently-Used，`LRU`） 策略替换`最近最少使用`的页面。

## 工作负载示例

当工作负载`不存在局部性`时，使用的策略
`区别不大`。LRU、FIFO 和随机都执行`相同的操作`，命中率完全由`缓存的大小`决定。

![F22.2](/assets/img/2022-06-15-operating-systems-18/F22.2.jpg)

`“80—20”负载场景`，它表现出`局部性`：80%的引用是访问 20%的页（“热门”页）。剩下的 20%是对剩余的 80%的页（“冷门”页）访问。

![F22.3](/assets/img/2022-06-15-operating-systems-18/F22.3.jpg)

`“循环顺序”工作负载`，其中依次引用 50
个页，从 0 开始，然后是 1，…，49，然后循环，重复访问。展示了 LRU 或者 FIFO 的最差情况。

![F22.4](/assets/img/2022-06-15-operating-systems-18/F22.4.jpg)

## 实现基于历史信息的算法

如何找到`最近最少使用`的页，也就是找到更新时间最久的页

硬件可以在每个页访问时`更新`内存中的`时间字段`（时间字段可以在每个进程的`页表`中，`或`者在内存的某个`单独的数组`中，每个物理页有一个）。因此，当页`被访问时`，时间字段将被硬件`设置为当前时间`。 然后，在需要替换页时，操作系统可以简单地`扫描`系统中所有页的`时间字段`以找到`最近最少使用`的页。

遗憾的是，随着系统中页数量的增长，扫描所有页的时间字段只是为了找到最精确最少使用的页，这个`代价太昂贵`。

## 近似 LRU

需要`硬件`增加一个`使用位`（use bit，有时称为`引用位`，reference bit）,系统的`每个页`有`一个使用位`，然后这些使用位存储在某个地方（例如，它们可能在每个进程的`页表`中，或者只在`某个数组`中）。每当页`被引用`（即读或写）时，`硬件`将使用位`设置为 1`。但是，硬件不会`清除该位`（即将其设置为 0），这由`操作系统`负责。

Corbato 的时钟算法：

`时钟指针`（clock hand）开始时指向随便`某个`特定的页（哪个页不重要）。当必须进行页替换时，操作系统检查当前指向的页 `P 的使用位`是 1 还是 0。如果是 `1`，则意味着页面 P`最近被使用`，因此`不适合被替换`。然后，P 的使用位`设置为0`，时钟指针递增到`下一页`（P + 1）。该算法一直持续到`找到一个使用位为 0` 的页，使用位为 0 意味着这个页最近没有被使用过（在最坏的情况下，所有的页都已经被使用了，那么就将所有页的使用位都设置为 0）。

这个算法有个问题，就是查找次数不稳定，如果是随机扫描而不是指针递增就好很多

## 考虑脏页

这章讲的其实不是 swap，而是`cache`，就是加速硬盘读取，以页为单位，在内存中创建硬盘页的缓存

如果页`已被修改`（modified）并因此变脏（dirty），则踢出它就必须将它`写回磁盘`，这很`昂贵`。如果它没有被修改（因此是干净的，clean），踢出就没成本。物理帧可以简单地重用于其他目的而无须额外的 I/O。因此，一些虚拟机系统更倾向于`踢出干净页`，而不是脏页。

为了支持这种行为，硬件应该包括一个`修改位`（modified bit，又名脏位，dirty bit）。每次写入页时都会设置此位，因此可以将其合并到页面替换算法中。例如，时钟算法可以被改变，以扫描既未使用又干净的页先踢出。无法找到这种页时，再查找脏的未使用页面，等等。

## 其他虚拟内存策略

操作系统还必须决定`何时`将页`载入`内存。

操作系统可能会猜测一个页面即将被使用，从而提前载入。这种行为被称为`预取`（prefetching），只有在有合理的成功机会时才应该这样做。例如，一些系统将假设如果代码页 P 被载入内存，那么代码页 P + 1 很可能很快被访问，因此也应该被载入内存。

这种行为通常称为`聚集（clustering）写入`，或者就是分组写入（grouping），这样做有效是因为硬盘驱动器的性质，执行`单次大的`写操作，比`许多小的`写操作`更有效`。

## 抖动

当内存就是被`超额请求`时，这组正在运行的进程的内存需求是否超出了可用物理内存？系统将`不断`地进行`换页`，这种情况有时被称为`抖动`（thrashing）

当内存超额请求时，某些版本的 Linux 会运行“内存不足的杀手程序（out-of-memory killer）”。这个守护进程选择一个内存密集型进程并杀死它，从而以不怎么委婉的方式减少内存。

## 小结

终极解决方案：加内存

## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/22.pdf)
