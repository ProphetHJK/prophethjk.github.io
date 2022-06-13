---
title: "《Operating Systems: Three Easy Pieces》学习笔记(十四) 空闲空间管理"
author: Jinkai
date: 2022-06-13 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

## 一个简单例子

在这个例子中，有 8 个页帧（由 128 字节物理内存构成，也是极小的）

![F18.1](/assets/img/2022-06-13-operating-systems-14/F18.1.jpg)

为了记录地址空间的每个虚拟页放在物理内存中的位置，操作系统通常为每个进程保存一个数据结构，称为`页表`（page table）。页表的主要作用是为地址空间的每个虚拟页面保存`地址转换`（address translation）

为了转换（translate）该过程生成的虚拟地址，我们必须首先将它分成两个组件：`虚拟页面号`（virtual page number，`VPN`）和`页内的偏移量`（offset）。

![F18.1](/assets/img/2022-06-13-operating-systems-14/VPN.jpg)

检索`页表`，找到`虚拟页 1` 所在的物理页面, `物理帧号`（PFN）（有时也称为物理页号，physical page number 或 PPN）是 `7`（二进制 111）,最终物理地址是 1110101

![F18.3](/assets/img/2022-06-13-operating-systems-14/F18.3.jpg)

## 页表存在哪里

一般放在内存中。

![F18.4](/assets/img/2022-06-13-operating-systems-14/F18.4.jpg)

## 列表中究竟有什么

最简单的形式称为`线性页表`（linear page table），就是一个`数组`。操作系统通过`虚拟页号`（VPN）`检索`该数组，并在该索引处查找`页表项`（`PTE`），以便找到期望的`物理帧号`（PFN）。

- PTE 的内容:

  - 有效位（valid bit）

    特定地址转换是否有效,例如，当一个程序开始运行时，它的`代码和堆`在其地址空间的一端，`栈`在另一端。所有`未使用`的`中间空间`都将被标记为`无效`（invalid），如果进程尝试访问这种内存，就会陷入操作系统，可能会导致该进程终止。因此，有效位对于支持`稀疏地址空间`至关重要。通过简单地将地址空间中所有未使用的页面标记为`无效`，我们不再需要为这些页面分配物理帧，从而`节省`大量内存。
  - 保护位（protection bit）

    表明页是否可以读取、写入或执行
  - 存在位（present bit）

    表示该页是在物理存储器还是在磁盘上（即它已被换出，swapped out）
  - 脏位（dirty bit）

    表明页面被带入内存后是否被修改过

  图 18.5 显示了来自 x86 架构的示例页表项[I09]。它包含一个存在位（P），确定是否允许写入该页面的读/写位（R/W） 确定用户模式进程是否可以访问该页面的用户/超级用户位（U/S），有几位（PWT、PCD、PAT 和G）确定硬件缓存如何为这些页面工作，一个访问位（A）和一个脏位（D），最后是页帧号（PFN）本身。

  ![F18.5](/assets/img/2022-06-13-operating-systems-14/F18.5.jpg)

## 分页消耗

假设一个页表基址寄存器（page-table base register）包含页表的起始位置的物理地址。

```c
VPN = (VirtualAddress & VPN_MASK) >> SHIFT
PTEAddr = PageTableBaseRegister + (VPN * sizeof(PTE))
```

`VPN MASK`将被设置为 0x30（十六进制 30，或二进制 `110000`），它从完整的虚拟地址中挑选出 VPN位；`SHIFT` 设置为 4（偏移量的位数），这样我们就可以将 VPN 位向右移动以形成正确的整数虚拟页码。例如，使用虚拟地址 21（010101），掩码将此值转换为 010000，移位将它变成 01，或虚拟页 1，正是我们期望的值。然后，我们使用该值作为页表基址寄存器指向的 PTE 数组的索引。

```c
offset = VirtualAddress & OFFSET_MASK
PhysAddr = (PFN << SHIFT) | offset
// Extract the VPN from the virtual address
VPN = (VirtualAddress & VPN_MASK) >> SHIFT
// Form the address of the page-table entry (PTE)
PTEAddr = PTBR + (VPN * sizeof(PTE))
// Fetch the PTE
PTE = AccessMemory(PTEAddr)
// Check if process can access the page
if (PTE.Valid == False)
  RaiseException(SEGMENTATION_FAULT)
else if (CanAccess(PTE.ProtectBits) == False)
  RaiseException(PROTECTION_FAULT)
else
  // Access is OK: form physical address and fetch it
  offset = VirtualAddress & OFFSET_MASK
  PhysAddr = (PTE.PFN << PFN_SHIFT) | offset
  Register = AccessMemory(PhysAddr)
```

## 内存追踪

一段循环赋值c代码：

```c
int array[1000];
...
for (i = 0; i < 1000; i++)
  array[i] = 0;
```

编译：

```shell
prompt> gcc -o array array.c -Wall -O
prompt> ./array
```

反编译后的汇编：

```x86asm
0x1024 movl $0x0,(%edi,%eax,4)
0x1028 incl %eax
0x102c cmpl $0x03e8,%eax
0x1030 jne 0x1024
```

第一条指令将`零值`（显示为$0x0）移动到数组位置的虚拟内存地址，这个地址是通过取`%edi`的内容并将其`加上%eax``乘以4`来计算的。`%edi` 保存`数组的基址`，而`%eax` 保存`数组索引`（`i`）。(array[i]=0)

第二条指令增加保存在`%eax`中的数组索引(`i++`)

第三条指令将该寄存器的内容与十六进制值 0x03e8 或十进制数 1000 进行`比较`(`i<1000`)。如果比较结果显示两个值不相等（这就是 jne 指令测试）第四条指令跳回到循环的顶部。

假设一个大小为 `64KB` 的`虚拟地址空间`。我们还假定`页面大小`为 `1KB`。

- 页表：物理地址1KB(1024)
- 代码段：虚拟地址1KB,大小1KB,VPN=1,映射到物理页4(VPN 1->PFN 4)
- 数组：4000字节（1000X`4`)，`int占4字节`,我们假设它驻留在虚拟地址40000 到 44000（不包括最后一个字节）。(VPN 39 → PFN 7), (VPN 40 → PFN 8), (VPN 41 → PFN 9), (VPN 42 → PFN 10)

当它运行时，`每个指令`将产生两个内存引用：一个`访问页表`以`查找指令`所在的物理框架，另一个`访问指令`本身将其`提取`到 CPU 进行处理

另外，在 `mov 指令`的形式中，有一个显式的内存引用，这会首先增加`另一个页表访问`（将数组虚拟地址转换为正确的物理地址），然后时数组访问本身。

图 18.7 展示了前 5 次循环迭代的整个过程。`左边虚拟地址`和`右边实际物理地址`。

![F18.7](/assets/img/2022-06-13-operating-systems-14/F18.7.jpg)

1. 访问页表取物理地址，1024是指令所在内存对应的页表，1174是数组所在内存对应的页表
2. 访问数组内存
3. 访问代码段内存取指令

## 小结

分页（paging）不会导致`外部碎片`，因为分页（按设计）将内存划分为`固定大小`的单元。其次，它非常灵活，支持`稀疏虚拟地址空间`

会导致`较慢`的机器（有许多`额外的内存访问`来访问页表）和`内存浪费`（内存被页表塞满而不是有用的应用程序数据）。

## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/18.pdf)
