---
title: "《Operating Systems: Three Easy Pieces》学习笔记(十七) 超越物理内存：机制"
author: Jinkai
date: 2022-06-14 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

## 交换空间

在硬盘上开辟一部分空间用于物理页的移入和移出。一般这样的空间称为`交换空间`（`swap space`）。

![F21.1](/assets/img/2022-06-14-operating-systems-17/F21.1.jpg)

## 存在位

当`硬件`在 `PTE` 中查找时，可能发现页不在物理内存中。硬件（或操作系统，在软件管理 TLB 时）判断是否在内存中的方法，是通过`页表项`中的一条新信息，即`存在位`（present bit）。如果存在位设置为 `1`，则表示该页存在于`物理内存`中，并且所有内容都如上所述进行。如果存在位设置为`0`，则页`不在内存`中，而在硬盘上。访问不在物理内存中的页，这种行为通常被称为`页错误`（page fault）。

在页错误时，`硬件`自己无法处理，`操作系统`被唤起来处理`页错误`。一段称为“`页错误处理程序`（page-fault handler）”的代码会执行，来处理页错误。

## 页错误

在 `TLB 未命中`的情况下，我们有两种类型的系统：`硬件管理`的 TLB（硬件在页表中找到需要的转换映射）和`软件管理`的 TLB（操作系统执行查找过程）。不论在哪种系统中，如果页不存在，都由`操作系统`负责处理`页错误`。操作系统的页错误处理程序（page-fault handler）确定要做什么。

> **补充：为什么硬件不能处理页错误**
>
> 我们从 TLB 的经验中得知，硬件设计者不愿意信任操作系统做所有事情。那么为什么他们相信操作系统来处理页错误呢？有几个主要原因。首先，页错误导致的硬盘操作很慢。即使操作系统需要很长时间来处理故障，执行大量的指令，但相比于硬盘操作，这些额外开销是很小的。其次，为了能够处理页故障，硬件必须了解交换空间，如何向硬盘发起 I/O 操作，以及很多它当前所不知道的细节。因此，由于`性能和简单的原因`，操作系统来处理页错误，即使硬件人员也很开心

操作系统可以用 `PTE` 中的`某些位`来存储硬盘地址，这些位通常用来存储像页的 PFN 这样的数据。当操作系统接收到页错误时，它会在 PTE 中查找地址，并将请求发送到硬盘，将页读取到内存中。

当`硬盘 I/O` 完成时，操作系统会`更新页表`，将此页标记为存在，更新`页表项（PTE）`的 `PFN` 字段以记录新获取页的内存位置，并重试指令。下一次重新访问 TLB 还是未命中，然而这次因为页在内存中，因此会将页表中的地址更新到 TLB 中（也可以在处理页错误时更新 TLB 以避免此步骤）。最后的重试操作会在 TLB 中找到转换映射，从已转换的内存物理地址，获取所需的数据或指令。

请注意，当 `I/O` 在运行时，进程将处于`阻塞（blocked）`状态。因此，当页错误正常处理时，操作系统可以自由地运行`其他可执行的进程`。因为 I/O 操作是昂贵的，一个进程进行 I/O（页错误）时会执行另一个进程，这种交叠（overlap）是多道程序系统充分利用硬件的一种方式。

## 内存满了怎么办

`页交换策略`（page-replacement policy）：

从`硬盘`中`换入`（page in），`换出`（page out）

当然是有`性能损失`的

## 页错误处理流程

页错误控制流算法（硬件）:

```c
VPN = (VirtualAddress & VPN_MASK) >> SHIFT
(Success, TlbEntry) = TLB_Lookup(VPN)
if (Success == True) // TLB Hit
    if (CanAccess(TlbEntry.ProtectBits) == True)
        Offset = VirtualAddress & OFFSET_MASK
        PhysAddr = (TlbEntry.PFN << SHIFT) | Offset
        Register = AccessMemory(PhysAddr)
    else
        RaiseException(PROTECTION_FAULT)
else // TLB Miss
    PTEAddr = PTBR + (VPN * sizeof(PTE))
    PTE = AccessMemory(PTEAddr)
    if (PTE.Valid == False)
        RaiseException(SEGMENTATION_FAULT) // 不合法，超界限，段错误
    else
        if (CanAccess(PTE.ProtectBits) == False)
            RaiseException(PROTECTION_FAULT) // 无权限错误
        else if (PTE.Present == True)
            // assuming hardware-managed TLB
            TLB_Insert(VPN, PTE.PFN, PTE.ProtectBits) // 在物理内存，插入TLB
            RetryInstruction()
        else if (PTE.Present == False)
            RaiseException(PAGE_FAULT) // 不在物理内存，页错误
```

页错误处理算法（软件）:

```C
PFN = FindFreePhysicalPage() // 找用于换入的物理内存页
if (PFN == -1)              // no free page found
    PFN = EvictPage()       // run replacement algorithm
DiskRead(PTE.DiskAddr, pfn) // sleep (waiting for I/O)
PTE.present = True          // update page table with present
PTE.PFN = PFN               // bit and translation (PFN)
RetryInstruction()          // retry instruction，重试后TLB还是未命中的，需要再做插入TLB操作
```

## 交换何时真正发生

为了保证有少量的空闲内存，大多数操作系统会设置`高水位线`（High Watermark，HW）和`低水位线`（Low Watermark，LW），来帮助决定何时从内存中清除页。当操作系统发现有`少于 LW` 个页可用时，后台负责`释放内存`的线程会开始运行，`直到`有 `HW` 个可用的物理页。这个后台线程有时称为交换守护进程（swap daemon）或页守护进程（page daemon）

## 小结

在页表结构中需要添加额外信息，比如增加一个存在位（present bit，或者其他类似机制），告诉我们页是不是在内存中。如果不存在，则操作系统页错误处理程序（page-fault handler）会运行以处理页错误（page fault），从而将需要的页从硬盘读取到内存，可能还需要先换出内存中的一些页，为即将换入的页腾出空间。

## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/21.pdf)
