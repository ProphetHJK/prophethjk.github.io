---
title: "Linux内核学习笔记之内存管理"
author: Jinkai
date: 2022-12-28 09:00:00 +0800
published: false
math: true
categories: [学习笔记]
tags: [kernel, Linux]
---

有两种类型计算机，分别以不同的方法管理物理内存:

- **UMA 计算机**（一致内存访问，uniform memory access）将可用内存以连续方式组织起来（可能有小的缺口）。SMP 系统中的每个处理器访问各个内存区都是同样快。
- **NUMA 计算机**（非一致内存访问，non-uniform memory access）总是多处理器计算机。系统的各个 CPU 都有本地内存，可支持特别快速的访问。各个处理器之间通过总线连接起来，以支持对其他 CPU 的本地内存的访问，当然比访问本地内存慢些。

![F3-1](/assets/img/2022-12-28-linux-kernel-memory/F3-1.jpg)

## (N)UMA 模型中的内存组织

内核对一致和非一致内存访问系统使用相同的数据结构。在 UMA 系统上，只使用一个 NUMA 结点来管理整个系统内存（相当于一种特殊的 NUMA）。而内存管理的其他部分则相信它们是在处理一个伪 NUMA 系统。

### 概述

内存划分为`结点`。每个结点关联到系统中的一个处理器，在内核中表示为 `pg_data_t` 的实例

各个结点又划分为`内存域`:

```c
// <mmzone.h>
enum zone_type
{
#ifdef CONFIG_ZONE_DMA
    ZONE_DMA, // 标记适合DMA的内存域
#endif
#ifdef CONFIG_ZONE_DMA32
    ZONE_DMA32, // 标记了使用32位地址字可寻址、适合DMA的内存域。
#endif
    ZONE_NORMAL, // 标记了可直接映射到内核段的普通内存域。
#ifdef CONFIG_HIGHMEM
    ZONE_HIGHMEM, // 标记了超出内核段的物理内存。
#endif
    ZONE_MOVABLE, // 在防止物理内存碎片的机制中需要使用该内存域。
    MAX_NR_ZONES
};
```

![F3-3](/assets/img/2022-12-28-linux-kernel-memory/F3-3.jpg)

各个内存结点保存在一个单链表中，供内核遍历。如果是 UMA ，就只有一个结点。

### 数据结构

#### 节点管理

```c
// <mmzone.h>
typedef struct pglist_data
{
    struct zone node_zones[MAX_NR_ZONES]; // 内存域列表
    struct zonelist node_zonelists[MAX_ZONELISTS]; // 备用内存域列表
    int nr_zones;
    struct page *node_mem_map; // 指向page实例数组的指针
    struct bootmem_data *bdata; // 自举内存分配器（boot memory allocator）
    unsigned long node_start_pfn; // 关联的物理页们的起始编号，每个物理页的编号全局唯一
    unsigned long node_present_pages; /* 物理内存页的总数 */
    unsigned long node_spanned_pages; /* 物理内存页的总长度，包含洞在内 */
    int node_id; // 全局结点ID
    struct pglist_data *pgdat_next;// 连接到下一个内存结点
    wait_queue_head_t kswapd_wait;// 交换守护进程（swap daemon）的等待队列
    struct task_struct *kswapd;
    int kswapd_max_order;
} pg_data_t;
```

结点的内存域保存在 `node_zones[MAX_NR_ZONES]`。该数组`至少`要有`3个项`，即使结点没有那么多内存域，也是如此。如果不足 3 个，则其余的数组项`用0填充`。

#### 结点状态管理

状态是用`位掩码`指定的：

```c
// <nodemask.h>
enum node_states
{
    N_POSSIBLE,      /* 结点在某个时候可能变为联机 */
    N_ONLINE,        /* 结点是联机的 */
    N_NORMAL_MEMORY, /* 结点有普通内存域 */
#ifdef CONFIG_HIGHMEM
    N_HIGH_MEMORY, /* 结点有普通或高端内存域 */
#else
    N_HIGH_MEMORY = N_NORMAL_MEMORY,
#endif
    N_CPU, /* 结点有一个或多个CPU */
    NR_NODE_STATES
};
```

#### 内存域

```c
// <mmzone.h>
struct zone
{ /*通常由页分配器访问的字段 */
    //  如果空闲页多于pages_high，则内存域的状态是理想的。  如果空闲页的数目低于pages_low，则内核开始将页换出到硬盘。  如果空闲页的数目低于pages_min，那么页回收工作的压力就比较大，因为内存域中急需空闲页。
    unsigned long pages_min, pages_low, pages_high;
    // 每个内存域的预留空间
    unsigned long lowmem_reserve[MAX_NR_ZONES];
    // 用于实现每个CPU的热/冷页帧列表
    struct per_cpu_pageset pageset[NR_CPUS];
    /*
     * 不同长度的空闲区域
     */
    spinlock_t lock;
    // 用于实现伙伴系统
    struct free_area free_area[MAX_ORDER];
    // ZONE_PADDING用于把整个结构体分成几段，
    // 当前这个是用于确保lock和lru_lock两个锁以及它们上锁的内容处于不同的CPU缓存行中
    // 避免形成伪共享
    ZONE_PADDING(_pad1_)
    /* 通常由页面收回扫描程序访问的字段 */
    spinlock_t lru_lock;
    // 活动页的集合
    struct list_head active_list;
    // 不活动页的集合
    struct list_head inactive_list;
    // 页数量
    unsigned long nr_scan_active;
    unsigned long nr_scan_inactive;
    unsigned long pages_scanned; /* 上一次回收以来扫描过的页 */
    unsigned long flags;         /* 内存域标志，见下文 */
    /* 内存域统计量 */
    atomic_long_t vm_stat[NR_VM_ZONE_STAT_ITEMS];
    int prev_priority;
    ZONE_PADDING(_pad2_)
    /* 很少使用或大多数情况下只读的字段 */
    wait_queue_head_t *wait_table;
    unsigned long wait_table_hash_nr_entries;
    unsigned long wait_table_bits;
    /* 支持不连续内存模型的字段。 */
    struct pglist_data *zone_pgdat;
    unsigned long zone_start_pfn;
    unsigned long spanned_pages; /* 总长度，包含空洞 */
    unsigned long present_pages; /* 内存数量（除去空洞） */
    /*
    * 很少使用的字段：
    */
    char *name;
} ____cacheline_maxaligned_in_smp;
```

[CPU缓存行](https://www.jianshu.com/p/e338b550850f)相关资料



## 参考

- [深入理解 linux 内核(Professional Linux Kernel Architecture) - Wolfgang Mauerer](https://www.amazon.com/Professional-Kernel-Architecture-Wolfgang-Mauerer/dp/0470343435)
