---
title: "Linux内核学习笔记之内存管理"
author: Jinkai
date: 2023-02-20 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [kernel, Linux]
---

## 页

内核把物理`页`作为内存管理的基本单位。尽管 CPU 最小可以按`字`(甚至`字节`)寻址内存。主要原因是`MMU（内存管理单元）`只支持按页管理页表。

大多数 32 位体系结构支持 4KB 的页，而 64 位体系结构一般会支持 8KB 的页。

struct page 结构表示系统中的每个**物理页**：

```c
// <linux/mm_types.h>
struct page
{
    unsigned long flags;// 状态。每一位表示脏页、锁定页等,在<linux/page-flags.h>中
    atomic_t _count;// 引用计数。-1表示没有被引用。私有成员，需要专用函数访问
    atomic_t _mapcount;
    unsigned long private;
    struct address_space *mapping;// 本页所为缓存页时，关联的实际页
    pgoff_t index;
    struct list_head iru;
    void *virtual;// 虚拟地址，有些物理页不会映射到虚拟的内核空间上，就为NULL
}
```

> 以上结构体做了简化，将一些内部结构和 union 展开了。

内核用这一结构来管理系统中所有的物理页，因为内核需要知道一个页是否**空闲**(也就是页有没有被分配)。如果页已经被分配，内核还需要知道谁拥有这个页。拥有者可能是用户空间进程、动态分配的内核数据、静态内核代码或页高速缓存等。

## 区

一些问题：

- 一些硬件只能用某些**特定**的内存地址来执行 `DMA`(直接内存访问)。
- 一些体系结构的内存的**物理寻址范围**比虚拟寻址范围大得多。这样，就有一些内存不能永久地映射到内核空间上。(理论上 32 位系统能物理和虚拟寻址 4GB 内存，因为一些保留，可能虚拟寻址范围没那么多，64 位系统一般不需要考虑这个)

内存分区：

- **ZONE_DMA**————这个区包含的页能用来执行 DMA 操作。
- **ZONE_DMA32**————和 `ZONE_DMA` 类似，该区包含的页面可用来执行 DMA 操作;而和 `ZONE_DMA` 不同之处在于，这些页面只能被 32 位设备访问。在某些体系结构中，该区将比 `ZONE_DMA` 更大。
- **ZONE_NORMAL**————这个区包含的都是能正常映射的页。
- **ZONE_HIGHEM**————这个区包含“**高端内存**”，其中的页并不能永久地映射到内核地址空间。（32 位 x86 系统上，为 >896MB 部分。64 位系统没有该区）

这些区(还有两种不大重要的)在`<linux/mmzone.h>`中定义。

`x86-32` 上的区：

| 区           | 描述           | 物理内存 |
| :----------- | :------------- | :------- |
| ZONE_DMA     | DMA 使用的页   | <16MB    |
| ZONE_NORMAL  | 正常可寻址的页 | 16~896MB |
| ZONE_HIGHMEM | 动态映射的页   | >896MB   |

某些类型的分配可以混用这些区(但最好不要)，比如分配时如果 `ZONE_NORMAL` 区内的页不够用了，可以使用一部分 `ZONE_DMA` 内的页。

`x86-64` 没有 `ZONE_HIGHMEM` 区，所有的物理内存都处于 `ZONE_DMA` 和 `ZONE_NORMAL` 区。

```c
// <include/linux/mmzone.h>
struct zone
{
    // 持有该区的最小值、最低和最高水位值，作为内核管理分配各区的参考
    unsigned long watermark[NR_WMARK];
    unsigned long percpu_drift_mark;
    unsigned long lowmem_reserve[MAX_NR_ZONES];
    unsigned long dirty_balance_reserve;
    struct per_cpu_pageset __percpu *pageset;
    // 自旋锁，保护本结构被并发访问
    spinlock_t lock;
    int all_unreclaimable; /* All pages pinned */
    struct free_area free_area[MAX_ORDER];
    ZONE_PADDING(_pad1_)
    spinlock_t lru_lock;
    struct lruvec lruvec;

    unsigned long pages_scanned; /* since last reclaim */
    unsigned long flags;         /* zone flags, see below */
    atomic_long_t vm_stat[NR_VM_ZONE_STAT_ITEMS];
    unsigned int inactive_ratio;
    ZONE_PADDING(_pad2_)
    wait_queue_head_t *wait_table;
    unsigned long wait_table_hash_nr_entries;
    unsigned long wait_table_bits;

    struct pglist_data *zone_pgdat;
    unsigned long zone_start_pfn;
    unsigned long spanned_pages;
    unsigned long present_pages;
    unsigned long managed_pages;
    // 分区名字： “DMA”、“Normal” 和 “HighMem”
    const char *name;
} ____cacheline_internodealigned_in_smp;
```

## gfp_mask 标志

分配器标志。

可分为三类:

- 行为修饰符
- 区修饰符
- 类型标志

### 行为修饰符

表示内核应当如何分配所需的内存。

在某些特定情况下，只能使用某些特定的方法分配内存。例如中断处理程序就要求内核在分配内存的过程中**不能睡眠**(因为中断处理程序不能被重新调度)。

| 标志            | 描述                                                         |
| :-------------- | :----------------------------------------------------------- |
| \_\_GFP_WAIT    | 分配器可以睡眠                                               |
| \_\_GFP_HIGH    | 分配器可以访问紧急事件缓冲地                                 |
| \_\_GFP_IO      | 分配器可以启动磁盘 IO                                        |
| \_\_GFP_FS      | 分配器可以启动文件系统 IO                                    |
| \_\_GFP_COLD    | 分配器应该使用高速缓在中快要淘汰出去的页                     |
| \_\_GFP_NOWARN  | 分配器将不打印失败警告                                       |
| \_\_GFP_REPEAT  | 分配器在分配失败时重复进行分配，但是这次分配还存在失败的可能 |
| \_\_GFP_NOFALL  | 分配器将无限地重复进行分配。分配不能失败描述                 |
| \_\_GFP_NORETRY | 分配器在分配失败时绝不会重新分配                             |
| \_\_GFP_NO_GROW | 由 slab 层内部使用                                           |
| \_\_GFP_COMP    | 添加混合页元数据，在 hugetlb 的代码内部使用                  |

示例：

```c
ptr = kmalloc(size, __GFP_WAIT | __GFP_IO | __GFP_FS)
```

表示分配时可以阻塞，可以启动 IO，还可以执行文件系统操作，给了分配器很大的自由。

不过一般不直接这样使用行为修饰符，而是使用像`GFP_KERNEL`这样的类型标志。

### 区修饰符

区修饰符表示内存区应当从何处分配。

通常，分配可以从任何区开始。不过，内核优先从 `ZONE_NORMAL` 开始，这样可以确保其他区在需要时有足够的空闲页可供使用。

| 标志            | 描述                                |
| :-------------- | :---------------------------------- |
| \_\_GFP_DMA     | 只从 ZONE_DMA 分 配                 |
| \_\_GFP_DMA32   | 只在 ZONE_DMA32 分 配               |
| \_\_GFP_HIGHMEM | 从 ZONE_HIGHMEM 或 ZONE_NORMAL 分配 |

不指定标志就是默认优先从 ZONE_NORMAL 分配，`__GFP_HIGHMEM` 不具备强制性，而`__GFP_DMA`具有强制性。

不能给`_get_free_pages()`或 `kalloc()` 指定 `ZONE_HIGHMEM`，因为这两个函数需要返回**逻辑地址**，而不是 **page 结构**。如果内存分配在`ZONE_HIGHMEM`中，那该内存页可能还没有映射到内核的虚拟地址空间，无法返回**逻辑地址**

绝大多数情况下无需指定区修饰符

### 类型标志

类型标志组合所需的**行为描述符**和**区描述符**以完成特殊类型的处理。

| 标志         | 修饰符标志                                                  | 描述                                                                                                                                           |
| :----------- | :---------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| GFP_ATOMIC   | \_\_GFP_HIGH                                                | 这个标志用在中断处理程序、下半部、持有自旋锁以及其他不能睡眠的地方                                                                             |
| GFP_NOWAIT   | 0                                                           | 与 GFP_ATOMIC 不同之处在于，调用不会退给紧急内存池。这就增加了内存分配失败的可能性。                                                           |
| GFP_NOIO     | \_\_GFP_WAIT                                                | 这种分配可以阻塞，但不会启动磁盘 I/O。这个标志在不能引发更多磁盘 I/O 时能阻塞 I/O 代码，这可能导致令人不愉快的递归                             |
| GFP_NOFS     | (\_\_GFP_WAIT\|\_\_GFP_IO)                                  | 这种分配在必要时可能阻塞，也可能启动磁盘 I/O，但是不会启动文件系统操作。这个标志在你不能再启动另一个文件系统的操作时，用在文件系统部分的代码中 |
| GFP_KERNEL   | (\_\_GFP_WAIT\|\_\_GFP_IO\|\_\_GFP_FS)                      | 这是一种常规分配方式，可能会阻塞。这个标志在睡眠安全时用在进程上下文代码中。为了获得调用者所需的内存，内核会尽力而为。这个标志应当是首选标志   |
| GFP_USER     | (\_\_GFP_WAIT\|\_\_GFP_IO\|\_\_GFP_FS)                      | 这是一种常规分配方式，可能会阻塞。这个标志用于为用户空间进程分配内存时                                                                         |
| GFP_HIGHUSER | (\_\_GFP_WAIT\|\_\_GFP_IO\|\_\_GFP_FS\|<br>\_\_GFP_HIGHMEM) | 这是从 ZONE_HIGHMEM 进行分配，可能会阻塞。这个标志用于为用户空间进程分配内存                                                                   |
| GFP_DMA      | \_\_GFP_DMA                                                 | 这是从 ZONE_DMA 进行分配。需要获取能供 DMA 使用的内存的设备驱动程序使用这个标志,GFP_DMA 通常与以上的某个标志组合在一起使用                     |

GFP_KERNEL 比较常用，因为它比较宽容，允许在分配过程休眠、交换页到硬盘等，分配成功率会较高，一般在进程上下文使用。相反，GFP_ATOMIC 就会比较严格，不允许睡眠和 I/O 操作，成功率较低，一般用在中断处理程序、软中断和 tasklet 等不能睡眠的代码中。

GFP_NOFS 相较于 GFP_KERNEL 少了 \_\_GFP_FS，一般在文件系统代码中使用，防止分配过程中再次调用文件系统代码，又再次分配，导致无限 loop，形成死锁。

GFP_DMA 标志表示分配器必须满足从 ZONE_DMA 进行分配的请求。这个标志用在需要
DMA 的内存的设备驱动程序中。一般和 GFP_KERNEL 或 GFP_ATOMIC 配合使用：(GFP_DMA|GFP_KERNEL)

## 获得页

_以页为单位分配内存（多页）：_

```c
// <include/linux/gfp.h>
static inline
struct page * alloc_pages(gfp_t gfp_mask, unsigned int order)
```

该函数分配 `2^order`(`1<<order`)个**连续**的物理页，并返回一个指针，该指针指向第一个页的 page 结构体;如果出错，就返回 NULL。

_返回页的逻辑地址：_

```c
void * page_address(struct page *page)
```

_分配页并返回逻辑地址：_

```c
unsigned long __get_free_pages(gfp_t gfp_mask, unsigned int order)
```

_分配一页内存（`alloc_pages()`的封装）：_

```c
struct page * alloc_page(gfp_t gfp_mask) // 返回页结构
unsigned long __get_free_page(gfp_t gfp_mask) // 返回逻辑地址
```

_获得填充为 0 的页:_

```c
unsigned long get_zeroed_page(unsigned int gfp_mask)
```

| 标志                               | 描述                                                 |
| :--------------------------------- | :--------------------------------------------------- |
| alloc_page(gfp_mask)               | 只分配一页，返回指向页结构的指针                     |
| alloc_pages(gfp_mask,order)        | 分配 2^order 页，返回指向第一页页结构的指针          |
| \_\_set_free_page(gfp_mask)        | 只分配一页，返回指向其逻辑地址的指针                 |
| \_\_get_free_pages(gfp_mask,order) | 分配 2^order 页，返回指向第一页逻辑地址的指针        |
| get_zeroed_page(gfp_mask)          | 只分配一页，让其内容填充 0，返回指向其逻辑地址的指针 |

### 释放页

```c
void __free_pages(struct page *page, unsigned int order)
void free_pages(unsigned long addr, unsigned int order)
void free_page(unsigned long addr)
```

只能释放属于自己的页，释放后不能直接使用已经释放的页。

> 对内核函数使用错误参数会导致崩溃，因为内核函数完全信赖调用者(内核)。

示例：

```c
unsigned long page;
page = __get_free_pages(GFP_KERNEL, 3);
if (!page) {
/*没有足够的内存:你必须处理这种错误!*/
    return -ENOMEM;
}
/*“page”现在指向8个连续页中第1个页的地址...*/

dosomething...

// 释放这些页
free_pages(page, 3);
```

## 按字节获取内存 kmalloc()

返回一个指向**物理上连续**的 size 大小的内存块的指针。出错时返回 NULL(如内存不足)，需要调用者处理：

```c
// <linux/slab.h>
void * kmalloc(size_t size, gfp_t flags)
```

示例：

```c
struct dog *p;
p = kmalloc(sizeof(struct dog), GFP_KERNEL)
if (ip);
 /* 处理错误...*/
```

### kfree()

```c
// <linux/slab.h>
void kfree(const void *ptr)
```

只能释放由 `kmalloc()`分配的属于自己的内存。且一一对应，每个`kmalloc()`对应一个 `kfree()`，禁止连续调用两次 `kfree()`

调用 `kfree(NULL)` 是安全的

示例：

```c
char *buf;
buf = kmalloc(BUF_SIZE, GFP_ATOMIC);
if (!buf)
    /* 内存分配出错 ! */
...
// 释放内存，即使分配失败，buf为NULL也没关系。
kfree(buf);
```

## 按字节获取虚拟的内存 vmalloc()

kmalloc 获取内存是物理连续的，而 vmalloc 获取的内存保证虚拟连续但并不保证物理连续。

```c
// <linux/vmalloc.h>
void * vmalloc(unsigned long size); // 返回虚拟地址连续的一块空间的指针
void vfree(const void *addr); // 释放vmalloc分配的内存空间
```

一般只有硬件驱动才会要求获得的内存是物理连续的，因为它们直接访问物理地址，甚至不知道什么是虚拟地址。

内核一般也不要求获取的内存是物理连续的，因为内核可以使用虚拟地址，但是使用 `kmalloc` 可以避免使用**页表**，让物理内存页和虚拟地址直接映射(物理连续即逻辑连续，无需页表保证)，减少性能消耗。所以大部分内核代码使用 `kmalloc` 而非 `vmalloc`，除非需要分配比较大的内存空间，这种情况找到连续的大块的物理内存会相对困难。

`vmalloc` 必须配合**页表**使用，将离散的物理页通过页表映射到连续的虚拟地址上，使得逻辑连续。

两个函数都可能休眠，不能放在中断上下文或其他不能阻塞的地方。

示例：

```c
char* buf;
buf = vmalloc(16*PAGE_SIZE);
/*get 16 pages*/
if(!buf)
    /*错误!不能分配内存*/
/*buf现在指向虚拟地址连续的一块内存区，其大小至少为16*PRGE_SIZE*/

// 在分配内存之后，一定要释放它:
vfree(buf);
```

## slab 层

slab 是更高层的内存管理手段，它按对象来分配内存，而不是按字节或页。当需要为一个对象分配内存时，可以直接使用 slab 接口，而无需使用 malloc 系列函数申请。用于需要频繁分配和释放较大的数据结构的情况。

### slab 层的设计

![f12-1](/assets/img/2023-02-20-linux-kernel-memory/f12-1.jpg)

每个`高速缓存(Cache)`包含若干个 `slab` 单元，一个 `slab` 单元一般就 1 页(可能多页)，每个 `slab` 单元存放若干个对象(数据结构)。

同一个高速缓存中只存放一种类型对象(如存放 `struct inode` 磁盘索引节点结构)。多个高速缓存构成一个组，用于缓存多种类型的对象。

对于像`struct inode`这样的经常分配和释放的结构，使用 slab 会带来性能提升。

slab 会有满、半满、空三种状态，除了满的情况都可以直接分配，所有 slab 全满的情况需要高速缓存新建一个 slab 用于存放新分配的对象

每个高速缓存都使用 kmem_cache 结构来表示：

```c
// <include/linux/slub_def.h>
struct kmem_cache
{
    struct kmem_cache_cpu __percpu *cpu_slab;
    /* Used for retriving partial slabs etc */
    unsigned long flags;
    unsigned long min_partial;
    int size;        /* The size of an object including meta data */
    int object_size; /* The size of an object without meta data */
    int offset;      /* Free pointer offset. */
    int cpu_partial; /* Number of per cpu partial objects to keep around */
    struct kmem_cache_order_objects oo;

    /* Allocation and freeing of slabs */
    struct kmem_cache_order_objects max;
    struct kmem_cache_order_objects min;
    gfp_t allocflags; /* gfp flags to use on each alloc */
    int refcount;     /* Refcount for slab cache destroy */
    void (*ctor)(void *);
    int inuse;             /* Offset to metadata */
    int align;             /* Alignment */
    int reserved;          /* Reserved bytes at the end of slabs */
    const char *name;      /* Name (only for display!) */
    struct list_head list; /* List of slab caches */

    struct kmem_cache_node *node[MAX_NUMNODES];
};
```

这个结构包含三个链表:slabs_full、slabs_partial 和 slabs_empty，链表中存放的 slab 结构：

```c
// <mm/slab.c>
struct slab
{
    union
    {
        struct
        {
            struct list_head list; // 关联的链表
            unsigned long colouroff; // slab着色偏移量
            void *s_mem;        // slab中第一个对象
            unsigned int inuse; // slab中已分配的对象数
            kmem_bufctl_t free; // 第一个空闲对象(如果有的话)
            unsigned short nodeid;
        };
        struct slab_rcu __slab_cover_slab_rcu;
    };
};
```

slab 描述信息(也就是 slab 结构体对象)可以直接分配在高速缓存(cache)划分的 slab 区域的开头位置（也就是该区域包含 slab 描述信息和 slab 管理的若干个对象），如果该区域不够，也可以分配在外部其他地方。

### slab 扩展

当 slab 不能存放新的对象时（全满），因为每个 slab 能存放的对象数量是固定的不能扩展，需要扩展 slab 的数量，这就需要新申请内存页。下面是简化版的请求页函数：

```c
static inline void *kmem_getpages(struct kmem_cache *cachep, gfp_t flags)
{
    void *addr;
    flags |= cachep->gfpflags;
    addr = (void *)__get_free_pages(flags, cachep->gfporder);
    // 创建slab
    ...
    return addr;
}
```

`kmem_getpages()` 使用 `__get_free_pages` 申请新的页，然后创建 slab。

可以调用`kmem_freepages()`释放内存页

注意，slab 层的目的就是要**避免**频繁申请和释放页，所以 slab 扩展越少越好（高速缓存创建后没有 slab 单元，这时候肯定是要申请页来扩展的）。

### slab 分配器

#### 创建高速缓存

_创建一个高速缓存：_

```c
struct kmem_cache *kmem_cache_create(const char *name,
                                     size_t size,
                                     size_t align,
                                     unsigned long flags,
                                     void (*ctor)(void *));
```

- `name`：高速缓存名字符串
- `size`：高速缓存中每个对象的大小
- `align`：第一个对象的偏移。用来确保在页内进行特定的对齐。
- `flags`: 可选，控制高速缓存的行为

  - **SLAB_HWCACHE_ALIGN**: 所有对象按**高速缓存行**大小对齐，防止两个或更多个对象出现在同一高速缓存行中。但这会浪费空间

    > 高速缓存行(cache line)是 CPU cache 中术语，CPU cache 被划分成若干行(比如每行 32 字节)，CPU 读取内存时每次会读入一个高速缓存行大小的内存到 CPU cache 中，即使只读一个字节也一样。被缓存的数据以及该缓存行内的其他数据在下次被访问时会更快。

  - **SLAB_POISON**: 使 slab 层用已知的值(a5a5a5a5)填充 slab。这就是所谓的“中毒(poison)”，有利于对未初始化内存的访问。
  - **SLAB_RED_ZONE**: slab 层在已分配的内存周围插入“红色警界区”以探测缓冲越界。
  - **SLAB_PANIC**: 当分配失败时提醒 slab 层。
  - **SLAB_CACHE_DMA**: 命令 slab 层使用可以执行 DMA 的内存给每个 slab 分配空间。只有在分配的对象用于 DMA，而且必须驻留在 ZONE_DMA 区时才需要这个标志。

- `ctor`: 已废弃，新增页时构造函数

成功时会返回一个指向所创建高速缓存的指针;否则，返回 NULL。这个函数不能在中断上下文中调用，因为它可能会睡眠。

_删除一个高速缓存：_

```c
int kmem_cache_destroy(struct kmem_cache *cachep);
```

- 删除前高速缓存中的所有 slab 都必须为空。
- 调用者在调用`kmem_cache_destroy()`过程中(以及之后)不能访问这个高速缓存。

该函数在成功时返回 0，否则返回非 0 值。不能在中断上下文中调用，因为它可能会睡眠。

#### 分配对象

_分配对象：_

```c
void * kmem_cache_alloc(struct kmem_cache *cachep, gfp_t flags)
```

该函数从给定的高速缓存 cachep 中返回一个指向对象的指针。如果高速缓存的所有 slab 中都没有空闲的对象，那么 slab 层必须通过`kmem_getpages()`获取新的页（见[slab 扩展](#slab-扩展)，如果高速缓存刚初始化，一个 slab 也没有就会出现这种情况），flags 的值传递给`__get_free_pages()`（用于获取空闲内存页）。标志应该使用 GFP_KERNEL 或 GFP_ATOMIC。

_释放对象：_

```c
void kmem_cache_free(struct kmem_cache *cachep, void *objp)
```

调用后可以将已分配的对象的空间标记为空闲。

#### 分配器实例

取自`<kernel/fork.c>`中的对 `task_struct` 结构的管理

定义一个指向高速缓存的指针：

```c
struct kmem_cache *task_struct_cachep;
```

在内核初始化期间，在定义于`kernel/fork.c`的`fork_init()`中会创建高速缓存：

```c
task_struct_cachep = kmem_cache_create("task_struct",
                                       sizeof(struct task_struct),
                                       ARCH_MIN_TASKALIGN,
                                       SLAB_PANIC | SLAB_NOTRACK,
                                       NULL);
```

- 该高速缓存名为“task_struct”
- 每个对象的大小是`struct task_struct`结构体的大小，也就是专门用于存放 task_struct 结构体。
- 该对象被创建后存放在 slab 中偏移量为`ARCHMIN_TASKALIGN`个字节的地方，`ARCHMIN_TASKALIGN`预定义值与体系结构相关。通常将它定义为`L1_CACHE_BYTES`——L1 高速缓存的字节大小。
- 因为 task_struct 进程描述符是内核必不可少的部分，相关的高速缓存必须分配成功，所以指定 SLAB_PANIC 在分配失败时通知 slab 层，调用者无须检查返回值。
- 没有构造函数或析构函数。

每当进程调用`fork()`时，会创建一个新的进程描述符，这是在`dup_task_struct()`中完成的，而该函数会被`do_fork()`调用：

```c
struct task_struct *tsk;
tsk = kmem_cache_alloc(task_struct_cachep, GFP_KERNEL);
if (!tsk)
    return NULL;
```

进程退出时，在 `free_task_struct()` 中释放高速缓存内的对象：

```c
kmem_cache_free(task_struct_cachep, tsk);
```

## 在栈上的静态分配

内核栈不像用户空间栈那么大，一般每个进程只有 1 页(32 位 4KB，64 位 8KB，以前是 2 页)，所以在内核栈上必须小心使用内存，静态分配较大的空间是很有可能导致栈溢出的。

### 单页内核栈

2.6 内核开始，增加了内核栈从 2 页变为 1 页的选项。且中断处理程序开始拥有独立的[中断栈](/posts/linux-kernel-interrupt/#%E4%B8%AD%E6%96%AD%E4%B8%8A%E4%B8%8B%E6%96%87)，也为 1 页。

主要原因为：

- 减少内核栈占用的内存
- 栈必须使用连续的内存，寻找两页连续的内存会随着碎片的增加越来越难
- 中断处理程序执行时共享内核栈，导致内核程序和中断处理程序相互占用，难以预估大小

### 正确使用栈

在函数中节约使用栈资源，主要是控制所有局部变量的总大小。栈溢出会覆盖其他结构数据，如[thread_info 结构](/posts/linux-kernel-process/#%E5%A4%8D%E5%88%B6%E8%BF%9B%E7%A8%8B)，这个结构就贴着每个进程内核栈的末端。

对于大块内存的分配，应该使用之前提到的动态分配，而不是静态分配。

## 高端内存的映射

根据定义，在**高端内存**中的页不能永久地映射到内核地址空间上。

在 x86 体系结构上，高于 **896MB** 的所有物理内存的范围大都是高端内存，它并不会永久地或自动地映射到内核地址空间，尽管 x86 处理器能够寻址物理 RAM 的范围达到 **4GB**(启用 `PAE` 可以寻址到 64GB)。一旦这些页被分配，就必须映射到内核的逻辑地址空间上。在 x86 上，高端内存中的页被映射到逻辑地址空间 3GB~4GB。

### 永久映射

_映射一个给定的 page 结构到内核地址空间：_

```c
// <linux/highmem.h>
void *kmap(struct page *page);
```

- **非高端内存**：本来就是一一映射的，所以会直接返回对应的逻辑地址
- **高端内存**：会将该 page 映射到专用的永久映射区，返回逻辑地址。（永久映射区是有限的，不可能映射所有高端内存）

这个函数可以睡眠，因此`kmap()`只能用在**进程上下文**中。

_取消永久映射：_

```c
void kunmap(struct page *page)
```

只对高端内存有效，非高端内存总是一一映射的，无法取消。

### 临时映射

_建立一个临时映射:_

```c
void *kmap_atomic(struct page *page)
```

就如其名字 atomic 一样，它是原子性的，不会阻塞，不能被[内核抢占](/posts/linux-kernel-interrupt/#%E6%A3%80%E6%9F%A5%E9%87%8D%E6%96%B0%E8%B0%83%E5%BA%A6)(关内核抢占，不关中断)，可以用于中断上下文

_取消一个临时映射：_

```c
void __kunmap_atomic(void *kvaddr);
```

不会阻塞。

因为临时映射会自动覆盖，即使不取消映射也没什么关系。

## 每个 CPU 的分配

### 老的每个 CPU 分配

在 2.4 版本中，为了防止 CPU 间的竞争某个对象，可以为每个 CPU 单独定义对象：

```c
// 数组内每个元素对应一个CPU
struct MyObject my_object[NR_CPUS] ;
```

访问对应 CPU 的对象：

```c
int cpu;
cpu = get_cpu();/*获得当前处理器，并禁止内核抢占，相当于加了锁进入临界区*/
// 对CPU对应的对象进行访问修改等操作，如：
my_object[cpu]++;

printk("my_object on cpu-%d is %lu\n", cpu, my_object[cpu]);
put_cpu(); /*激活内核抢占*/
```

如果只访问本 CPU 上的数据，也就是通过`get_cpu()`获取的索引，那就是安全的，如果访问数组内其他 CPU 上的数据，不能保证其一致性

### 新的每个 CPU 接口

2.6 内核为了方便创建和操作每个 CPU 数据，而引进了新的操作接口，称作 percpu。在头文件`<linux/percpu.h>`声明

#### 编译时的每个 CPU 数据

_声明每个 CPU 对象：_

```c
DECLARE_PER_CPU(type, name);
```

_定义对象：_

```c
DEFINE_PER_CPU(type, name);
```

以上两个宏会在每个 CPU 上定义一个名为 name，类型为 type 的对象。

_获取对应 CPU 上的对象，并禁止抢占：_

```c
get_cpu_var(name);
```

_重新激活抢占：_

```c
put_cpu_var(name);
```

_访问其他 CPU 上的对象：_

```c
per_cpu(name, cpu);
```

该函数不会禁止抢占，也没有锁保护。所以使用时应该自行实现加锁同步。

#### 运行时的每个 CPU 数据

内核实现每个 CPU 数据的**动态分配**方法类似于`kmalloc()`。为系统上的每个处理器创建所需内存的实例:

```c
// <linux/percpu.h>
void *__alloc_percpu(size_t size, size_t align);

void free_percpu(const void *);

#define alloc_percpu(type)  \
    (typeof(type) __percpu *)__alloc_percpu(sizeof(type), __alignof__(type))
```

`__alloc_percpu()` 用于在给单个 CPU(就是本 CPU)分配给定大小和对齐的内存。返回分配的内存块的指针。

`alloc_percpu()`是对它的封装宏，指定其对齐方式符合当前 CPU 架构。

> **地址对齐**
>
> 部分 CPU 要求变量在内存地址上对齐的，比如 int 要按 4 字节对齐，int 类型的变量应该要放在能被 4 整除的地址上。主要原因为 CPU 一般只从对齐地址按照**字长度**读取内存，比如从 0x00000004 读取 4 字节。如果 int 类型变量的 4 个字节存放在 0x00000006-0x00000009 上，CPU 可能就无法读取，不过大多数 CPU 是可以处理的，比如 x86 会先从 0x00000004 读取 4 字节，取后两字节，再从 0x00000008 读取 4 字节，取前两字节，然后组合，这需要读两次内存加上拼接操作，显然降低了性能。GCC 提供了`__alignof__`宏用于获取某个类型的对齐长度，如`__alignof__(int)`为 4。

_获取这些对象：_

```c
// <include/linux/percpu.h>

/*关闭内核抢占，根据var指针获取该对象的引用*/
#define get_cpu_var(var) (*({                \
    preempt_disable();                \
    &__get_cpu_var(var); }))

/*重新激活内核抢占*/
#define put_cpu_var(var) do {                \
    (void)&(var);                    \
    preempt_enable();                \
} while (0)
```

根据`__alloc_percpu()`返回的内存地址指针，可以通过`get_cpu_var`函数获取到对应对象的引用。其中`__get_cpu_var`做了一些校验和类型转换工作。

示例：

```c
void *percpu_ptr;
unsigned long *foo;
percpu_ptr = alloc_percpu(unsigned long);
if (!ptr)
    /* 内存分配错误... */
// 获取该对象的引用，并关闭内核抢占
foo = get_cpu_var(percpu_ptr);
/* 操作 foo... */
...
// 激活内核抢占
put_cpu_var(percpu_ptr);
```

### 使用每个 CPU 数据的原因

优点：

- 避免了使用**锁**实现不同 CPU 间的同步，性能会更高（代价是关内核抢占，性能肯定比锁高），缺点是失去了共享的特性。这是解决软中断中的[同步问题](/posts/linux-kernel-interrupt/#%E6%B3%A8%E5%86%8C%E5%A4%84%E7%90%86%E7%A8%8B%E5%BA%8F)的一个方案
- 由于每个 CPU 的缓存也是独立的，对象不共享也能防止缓存失效。比如对象被其他 CPU 访问时本 CPU 缓存就失效了，两个 CPU 不断交替访问，导致缓存失去了意义（称为**缓存抖动**）。

注意事项：

如果只使用上述每个 CPU 接口管理这些单 CPU 数据，可以保证数据是安全和隔离的。但不能防止有人不使用接口直接访问数组获取其他 CPU 的数据，这就需要调用者自行遵守规定，当然自己关内核抢占然后访问属于自己所在 CPU 的数据也是可以的。

## 小结：分配函数的选择

上面介绍了好几种内存分配策略，下面总结一下：

- 需要连续的物理页：`kmalloc()`，这是内核中内存分配的常用的方法。通过 `GFP_ATOMIC` 或 `GFP_KERNEL` 等标志指示是分配时的行为，如是否允许休眠、访问 I/O 等。
- 需要高端内存：`alloc_pages()`。高端内存可能没有映射到虚拟地址空间，只能通过 `page` 结构的方式返回，然后可以通过 `kmap` 函数将其永久或临时映射到虚拟地址空间。
- 如果不要求连续的物理页，仅要求虚拟地址连续：`vmalloc()`，这会把离散的物理地址映射到连续的虚拟地址上，底层需要借助页表，会比`kmalloc()`来的慢
- 需要频繁分配和释放较大的对象(数据结构)，使用：`slab cache`。slab 会预分配一块空间，并划分出一个个对象容器，并用链表连接，分配和释放对象并不需要经常 malloc，而是填充或释放这些对象容器。

## 进程地址空间

Linux 操作系统采用虚拟内存技术，因此，系统中的所有进程之间以虚拟方式共享内存。对一个进程而言，它好像都可以访问整个系统的所有物理内存。更重要的是，即使单独一个进程，它拥有的地址空间也可以远远大于系统物理内存。

每个进程都有一个 32 位或 64 位的**平坦**(flat)地址空间，空间的具体大小取决于体系结构。

> **平坦**
>
> 平坦指的是地址空间范围是一个独立的连续区间(比如，地址从 0 扩展到 4294967295 的 32 位地址空间)。和[分段内存模式](/posts/operating-systems-12/)对应，也就是使用段基址加偏移的方式访问内存。

内存按字节分配地址，如 32 位地址可以表示 4GB 空间。每个进程都有特定的可以访问的一段区域，进程可以通过内核扩展和缩小该区域，如果一个进程访问了不在有效范围中的内存区域，或以不正确的方式访问了有效地址，那么内核就会终止该进程，并返回“**段错误**”信息。

每个进程的地址空间划分成很多区域：见[一文看懂内存分段](/posts/segment-ram/)

## 内存描述符

内核使用内存描述符结构体`mm_struct`表示进程的地址空间，该结构包含了和进程地址空间有关的全部信息。

```c
// <include/linux/mm_types.h>
struct mm_struct
{
    struct vm_area_struct *mmap; /* 内存区域(vma)链表 */
    struct rb_root mm_rb; /* vma形成的红黑树 */
    struct vm_area_struct *mmap_cache; /* 最近使用的vma */
    unsigned long mmap_base;           /* base of mmap area */
    unsigned long mmap_legacy_base;    /* base of mmap area in bottom-up allocations */
    unsigned long task_size;           /* size of task vm space */
    unsigned long cached_hole_size;    /* if non-zero, the largest hole below free_area_cache */
    unsigned long free_area_cache;     /* 地址空间的第一个空洞 */
    unsigned long highest_vm_end;      /* highest vma end address */
    pgd_t *pgd; // 页全局目录
    atomic_t mm_users; /* How many users with user space? */
    atomic_t mm_count; /* How many references to "struct mm_struct" (users count as 1) */
    int map_count;     /* number of VMAs */

    spinlock_t page_table_lock; /* Protects page tables and some counters */
    struct rw_semaphore mmap_sem;

    struct list_head mmlist;   /* List of maybe swapped mm's.	These are globally strung
                                * together off init_mm.mmlist, and are protected
                                * by mmlist_lock
                                */
    unsigned long hiwater_rss; /* High-watermark of RSS usage */
    unsigned long hiwater_vm;  /* High-water virtual memory usage */

    unsigned long total_vm;  /* Total pages mapped */
    unsigned long locked_vm; /* Pages that have PG_mlocked set */
    unsigned long pinned_vm; /* Refcount permanently increased */
    unsigned long shared_vm; /* Shared pages (files) */
    unsigned long exec_vm;   /* VM_EXEC & ~VM_WRITE */
    unsigned long stack_vm;  /* VM_GROWSUP/DOWN */
    unsigned long def_flags;
    unsigned long nr_ptes; /* Page table pages */
    unsigned long start_code, end_code, start_data, end_data; // 代码段数据段首尾位置
    unsigned long start_brk, brk, start_stack; // 堆首尾地址，栈首地址
    unsigned long arg_start, arg_end, env_start, env_end; // 命令行参数首尾地址
    unsigned long saved_auxv[AT_VECTOR_SIZE]; /* for /proc/PID/auxv */
    /*
     * Special counters, in some configurations protected by the
     * page_table_lock, in other configurations by being atomic.
     */
    struct mm_rss_stat rss_stat;
    struct linux_binfmt *binfmt;
    cpumask_var_t cpu_vm_mask_var;

    /* Architecture-specific MM context */
    mm_context_t context;
    unsigned long flags;           /* Must use atomic bitops to access the bits */
    struct core_state *core_state; /* coredumping support */
#ifdef CONFIG_AIO
    spinlock_t  ioctx_lock; // AIO I/O链表锁
    struct hlist_head   ioctx_list; // AIO I/O 链表
#endif
    /* store ref to file /proc/<pid>/exe symlink points to */
    struct file *exe_file;
    struct uprobes_state uprobes_state;
};
```

- mm_users 与 mm_count

  - mm_users：**使用计数器**，表示使用该进程地址空间的资源的进程数量(Linux 中线程也是进程)，由于线程的特性，可以共享如 text 代码段，所有每有一个这样的线程，mm_users 就加 1。

  - mm_count：**引用计数器**，表示对 mm_struct 对象的引用数，与 mm_struct 对象内的内容无关，也就是说表示是否还有指针指向该对象，如果没有，就可以删除该对象了。比如内核线程有时候会引用某个 mm_struct 对象，但并不会访问对象内的数据。还可以类比于 java 的自动内存回收机制，如果对象没有被引用，则视为垃圾对象，可以清理掉。

  如果有 9 个线程共享该对象，则 mm_users 为 9，而 mm_struct 为 1，当 9 个线程全部退出时，mm_struct 才会变成 0。

- mmap 和 mm_rb

  - mmap 管理的的内存区域的链表

  - mm_rb 管理的内存区域的红黑树

  这两个数据结构管理的是同样的内容，主要是为了将两种数据结构的优势结合，如链表的简单遍历（O(n)）和红黑树的简单查找（O(logn)）。

所有的 mm_struct 结构体都通过自身的 `mmlist` 域连接在一个双向链表中，该链表的首元素是 init_mm 内存描述符，它代表 `init 进程`的地址空间。另外要注意，操作该链表的时候需要使用 `mmlist_lock` 锁来防止并发访问。

### 分配内存描述符

进程的进程描述符(`task_struct` 对象)中的 `mm` 成员就是指向了该进程的内存描述符(`mm_struct` 对象)

fork 函数会使用 `copy_mm()` 函数复制父进程的 `mm_struct` 对象，并让子进程结构中的 mm 指向该副本。`copy_mm()` 过程实际上会通过 `allocate_mm()`宏从 `mm_cachep slab 缓存`中分配一个 mm_struct 结构。

使用 `clone()` 时如果指定 `CLONE_VM` 标志(也就是创建线程)，则会跳过内存描述符的分配，直接让子进程共享父进程的内存描述符。见[复制进程](/posts/linux-kernel-process/#%E5%A4%8D%E5%88%B6%E8%BF%9B%E7%A8%8B)。

线程的 mm 和父进程的 mm 相同：

```c
if (clone_flags & CLONE_VM)
{
    /* current是父进程而tsk在fork()执行期间是子进程 */
    atomic_inc(&current->mm->mm_users);
    tsk->mm = current->mm;
}
```

### 撤销内存描述符

当进程退出时，内核会调用定义在 `<kernel/exit.c>` 中的 `exit_mm()` 函数，该函数执行一些常规的撤销工作，同时更新一些统计量。

该函数会调用 `mmput()` 函数减少内存描述符中的 `mm_users` 使用计数，如果用户计数**降到零**，将调用 `mmdrop()` 函数，减少 `mm_count` 引用计数。

如果`mm_count`使用计数也等于零了，说明该内存描述符不再有任何使用者了，那么调用 `free_mm()` 宏通过 `kmem_cache_free()` 函数将 `mm_struct` 结构体归还到 `mm_cachep slab 缓存`中。

就如上面子线程共享`mm_struct`的情况，只有所有共享该结构的子线程全退出，引用计数为 0 时才析构它。

### mm_struct 与内核线程

内核线程没有属于自己的内存描述符，上下文切换时它**借用**被切换的用户进程的内存描述符并放在进程描述符的 `active_mm` 中。而且仅仅是借用，内核线程并不会修改这些用户地址空间中的内容，正因如此，连页表都不需要切换(页表切换是为了通过正确的页表将地址转为物理地址，但既然不去访问内容，也就不需要转为物理地址)。

详见[内核线程](/posts/linux-kernel-process/#%E5%86%85%E6%A0%B8%E7%BA%BF%E7%A8%8B)和[上下文切换](/posts/linux-kernel-process/#%E4%B8%8A%E4%B8%8B%E6%96%87%E5%88%87%E6%8D%A2)

## 虚拟内存区域 vma

整个虚拟内存（注意是系统级别的，不是进程私有的）被划分成几个区域，称为 vma，每个区域用一个`vm_area_struct` 结构体描述。每个区域拥有一致的属性，比如访问权限等，另外，相应的操作也都一致。每个进程的地址空间可以映射若干个 vma（每个进程的 mm 对象可以关联几个 vma），同时多个进程也可以共享某个区域（比如线程组的 mm 对象本身就是同一个，关联的 vma 也是一样的）。

```c
//include/linux/mm_types.h
struct vm_area_struct
{
    /* The first cache line has the info for VMA tree walking. */

    // vma其实虚拟地址（闭）
    unsigned long vm_start; /* Our start address within vm_mm. */
    // vma结束虚拟地址（开）
    unsigned long vm_end;   /* The first byte after our end address
                   within vm_mm. */

    /* linked list of VM areas per task, sorted by address */
    struct vm_area_struct *vm_next, *vm_prev; // 链表

    struct rb_node vm_rb; // 红黑树

    /*
     * Largest free memory gap in bytes to the left of this VMA.
     * Either between this VMA and vma->vm_prev, or between one of the
     * VMAs below us in the VMA rbtree and its ->vm_prev. This helps
     * get_unmapped_area find a free area of the right size.
     */
    unsigned long rb_subtree_gap;

    /* Second cache line starts here. */

    struct mm_struct *vm_mm; /* The address space we belong to. */
    pgprot_t vm_page_prot;   /* Access permissions of this VMA. */
    unsigned long vm_flags;  /* Flags, see mm.h. */

    /*
     * For areas with an address space and backing store,
     * linkage into the address_space->i_mmap interval tree, or
     * linkage of vma in the address_space->i_mmap_nonlinear list.
     */
    union
    {
        struct
        {
            struct rb_node rb;
            unsigned long rb_subtree_last;
        } linear;
        struct list_head nonlinear;
    } shared;

    /*
     * A file's MAP_PRIVATE vma can be in both i_mmap tree and anon_vma
     * list, after a COW of one of the file pages.	A MAP_SHARED vma
     * can only be in the i_mmap tree.  An anonymous MAP_PRIVATE, stack
     * or brk vma (with NULL file) can only be in an anon_vma list.
     */
    struct list_head anon_vma_chain; /* Serialized by mmap_sem &
                                      * page_table_lock */
    struct anon_vma *anon_vma;       /* Serialized by page_table_lock */

    /* Function pointers to deal with this struct. */
    const struct vm_operations_struct *vm_ops;

    /* Information about our backing store: */
    unsigned long vm_pgoff; /* Offset (within vm_file) in PAGE_SIZE
                   units, *not* PAGE_CACHE_SIZE */
    struct file *vm_file;   /* File we map to (can be NULL). */
    void *vm_private_data;  /* was vm_pte (shared mem) */
};
```

每个 `vm_area_struct` 描述`[vm_start,vm_end)`的左闭右开的虚拟内存空间，`vm_mm` 指向其从属的`mm_struct`。`vm_area_struct`对象间通过链表或红黑树连接。

### VMA 标志：vm_flags

VMA 标志是一种位标志，反映了内核处理 vma 时所需要遵守的行为准则，而不是硬件要求（虚拟内存实际已经和硬件无关了）。

| 标志          | 对 VMA 及其页面的影响     |
| :------------ | :------------------------ |
| VM_READ       | 页面可读取                |
| VM_WRITE      | 页面可写                  |
| VM_EXEC       | 页面可执行                |
| VM_SHARED     | 页面可共享                |
| VM_MAYREAD    | VM_READ 标志可被设置      |
| VM_MAYWRITE   | VM_WRITE 标志可被设置     |
| VM_MAYEXEC    | VM_EXEC 标志可被设置      |
| VM_MAYSHARE   | VM_SHARE 标志可被设置     |
| VM_GROWSDOWN  | 区域可向下增长            |
| VM_GROWSUP    | 区域可向上增长            |
| VM_SHM        | 区域可用作共享内存        |
| VM_DENYWRITE  | 区域映射一个不可写文件    |
| VM_EXECUTABLE | 区域映射一个可执行文件    |
| VM_LOCKED     | 区域中的页面被锁定        |
| VM_IO         | 区域映射设备 IO 空间      |
| VM_SEQ_READ   | 页面可能会被连续访问      |
| VM_RAND_READ  | 页面可能会被随机访问      |
| VM_DONTCOPY   | 区域不能在 fork()时被拷贝 |
| VM_DONTEXPAND | 区域不能通过 mremap()增加 |
| VM_RESERVED   | 区域不能被换出            |
| VM_ACCOUNT    | 该区域是一个记账 VM 对象  |
| VM_HUGETLB    | 区域使用了 hugetlb 页面   |
| VM_NONLINEAR  | 该区域是非线性映射的      |

- VM_READ,VM_WRITE,VM_EXEC

  标准的读写执行权限，如代码映射区为 VM_READ 和 VM_EXEC，只读数据段为 VM_READ

- VM_SHARED

  该区域是否可以在多个进程间共享，称为共享映射。反之，称为私有映射

- VM_IO

  表示对 I/O 空间的映射，一般同时和 VM_RESERVED 标志使用，规定了内存区域不能被换出

- VM_SEQ_READ

  规定内存会被连续访问，有利于内核使用**预读策略**提前读取即将被读取的内容，而 VM_RAND_READ 与之相反，表示随机读取。

### VMA 操作

```c
// mm.h
struct vm_operations_struct
{
    // vma加入地址空间（mm_struct结构）
    void (*open)(struct vm_area_struct *area);
    // 从地址空间（mm_struct结构）删除vma
    void (*close)(struct vm_area_struct *area);
    // 没有在物理内存中的页被访问时
    int (*fault)(struct vm_area_struct *vma, struct vm_fault *vmf);

    /* notification that a previously read-only page is about to become
     * writable, if an error is returned it will cause a SIGBUS */
    int (*page_mkwrite)(struct vm_area_struct *vma, struct vm_fault *vmf);

    /* called by access_process_vm when get_user_pages() fails, typically
     * for use by special VMAs that can switch between memory and hardware
     */
    int (*access)(struct vm_area_struct *vma, unsigned long addr,
                  void *buf, int len, int write);
    /* called by sys_remap_file_pages() to populate non-linear mapping */
    int (*remap_pages)(struct vm_area_struct *vma, unsigned long addr,
                       unsigned long size, pgoff_t pgoff);
};
```

### 内存区域的树型结构和链表结构

[之前](#内存描述符)提到过，不再赘述

### 实际使用中的内存区域

可以使用`/proc`文件系统和 `pmap(1)`工具查看给定进程的内存空间和其中所含的内存区域。

以一段简单的程序为例：

```c
int main(int argc,char *argv[]) {
    return 0;
}
```

`/proc/<pid>/maps`的输出显示了该进程地址空间中的全部内存区域(包括代码段、数据段、bss 段、堆栈等以及链接库的各段)：

```console
root@racknerd-ae2d96:~# cat /proc/3080311/maps
        开始-结束       访问权限 偏移  主:次设备号 i节点                    文件
563459b19000-563459b1a000 r--p 00000000 fc:01 3519                       /root/a.out
563459b1a000-563459b1b000 r-xp 00001000 fc:01 3519                       /root/a.out
563459b1b000-563459b1c000 r--p 00002000 fc:01 3519                       /root/a.out
563459b1c000-563459b1d000 r--p 00002000 fc:01 3519                       /root/a.out
563459b1d000-563459b1e000 rw-p 00003000 fc:01 3519                       /root/a.out
7fb2ca391000-7fb2ca394000 rw-p 00000000 00:00 0
7fb2ca394000-7fb2ca3bc000 r--p 00000000 fc:01 4221                       /usr/lib/x86_64-linux-gnu/libc.so.6
7fb2ca3bc000-7fb2ca551000 r-xp 00028000 fc:01 4221                       /usr/lib/x86_64-linux-gnu/libc.so.6
7fb2ca551000-7fb2ca5a9000 r--p 001bd000 fc:01 4221                       /usr/lib/x86_64-linux-gnu/libc.so.6
7fb2ca5a9000-7fb2ca5ad000 r--p 00214000 fc:01 4221                       /usr/lib/x86_64-linux-gnu/libc.so.6
7fb2ca5ad000-7fb2ca5af000 rw-p 00218000 fc:01 4221                       /usr/lib/x86_64-linux-gnu/libc.so.6
7fb2ca5af000-7fb2ca5bc000 rw-p 00000000 00:00 0
7fb2ca5c5000-7fb2ca5c7000 rw-p 00000000 00:00 0
7fb2ca5c7000-7fb2ca5c9000 r--p 00000000 fc:01 3999                       /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7fb2ca5c9000-7fb2ca5f3000 r-xp 00002000 fc:01 3999                       /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7fb2ca5f3000-7fb2ca5fe000 r--p 0002c000 fc:01 3999                       /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7fb2ca5ff000-7fb2ca601000 r--p 00037000 fc:01 3999                       /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7fb2ca601000-7fb2ca603000 rw-p 00039000 fc:01 3999                       /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7ffde5960000-7ffde5981000 rw-p 00000000 00:00 0                          [stack]
7ffde59ef000-7ffde59f3000 r--p 00000000 00:00 0                          [vvar]
7ffde59f3000-7ffde59f5000 r-xp 00000000 00:00 0                          [vdso]
ffffffffff600000-ffffffffff601000 --xp 00000000 00:00 0                  [vsyscall]
```

使用 pmap 打印的更人性化的信息：

```console
root@racknerd-ae2d96:~# cat /proc/3080311/maps
3080311:   ./a.out
0000563459b19000      4K r---- a.out
0000563459b1a000      4K r-x-- a.out
0000563459b1b000      4K r---- a.out
0000563459b1c000      4K r---- a.out
0000563459b1d000      4K rw--- a.out
00007fb2ca391000     12K rw---   [ anon ]
00007fb2ca394000    160K r---- libc.so.6
00007fb2ca3bc000   1620K r-x-- libc.so.6
00007fb2ca551000    352K r---- libc.so.6
00007fb2ca5a9000     16K r---- libc.so.6
00007fb2ca5ad000      8K rw--- libc.so.6
00007fb2ca5af000     52K rw---   [ anon ]
00007fb2ca5c5000      8K rw---   [ anon ]
00007fb2ca5c7000      8K r---- ld-linux-x86-64.so.2
00007fb2ca5c9000    168K r-x-- ld-linux-x86-64.so.2
00007fb2ca5f3000     44K r---- ld-linux-x86-64.so.2
00007fb2ca5ff000      8K r---- ld-linux-x86-64.so.2
00007fb2ca601000      8K rw--- ld-linux-x86-64.so.2
00007ffde5960000    132K rw---   [ stack ]
00007ffde59ef000     16K r----   [ anon ]
00007ffde59f3000      8K r-x--   [ anon ]
ffffffffff600000      4K --x--   [ anon ]
 total             2644K
```

可以推测 0000563459b1a000 段是代码段，因为它有 x 可执行权限。

563459b1d000 具有 w 可写权限的，是数据段。

7fb2ca391000 的主次设备号是 00:00，没有映射到 vma，称为零页，用于存放初始值全为 0 的 bss 段，只有被第一次修改时才会真正为其分配页，利用了写时复制思想。

stack 栈段只有 rw 读写权限，无需可执行权限。

vvar，vdso，vsyscall 段见[本文](http://readm.tech/2016/09/23/syscall/)

可以看到 `libc.so.6` 链接库占用了很大的地址空间，其实这部分是进程间共享的。

## 操作内存区域

### find_vma()

根据内存地址找对应的 vma

声明：

```c
// include/linux/mm.h
/* Look up the first VMA which satisfies  addr < vm_end,  NULL if none. */
struct vm_area_struct * find_vma(struct mm_struct *mm, unsigned long addr);
```

参数 mm 表示进程对应的地址空间(结合前文是由 mm_struct 结构管理的)，addr 表示要查找的地址，返回第一个 vm_end > addr 的 vma，注意不能保证 vm_start < addr，所以 addr 不一定属于返回的 vma（TODO:有什么用意）。

find_vma()函数返回的结果被**缓存**在内存描述符(mm_struct)的 `mmap_cache` 域中。根据**时间局部性**原则，最近被访问的区域很大概率会在再次被访问。

实现：

```c
// mm/mmap.c

/* Look up the first VMA which satisfies  addr < vm_end,  NULL if none. */
struct vm_area_struct *find_vma(struct mm_struct *mm, unsigned long addr)
{
    struct vm_area_struct *vma = NULL;

    /* Check the cache first. */
    /* (Cache hit rate is typically around 35%.) */
    // 优先检查缓存
    vma = ACCESS_ONCE(mm->mmap_cache);
    // 如果直接从缓存获取到符合条件的vma，就通过if跳过下面的步骤
    if (!(vma && vma->vm_end > addr && vma->vm_start <= addr))
    {
        struct rb_node *rb_node;

        rb_node = mm->mm_rb.rb_node;
        vma = NULL;

        // 红黑树的遍历
        while (rb_node)
        {
            struct vm_area_struct *vma_tmp;

            // 获取节点对应的vma对象
            vma_tmp = rb_entry(rb_node,
                               struct vm_area_struct, vm_rb);

            if (vma_tmp->vm_end > addr)
            {
                vma = vma_tmp;
                // 如果找到符合条件的就直接退出循环
                if (vma_tmp->vm_start <= addr)
                    break;
                // 继续往左子树找，因为左子树的vm_end要小于当前节点的
                // 目的是找vm_end最小的符合条件的vma
                rb_node = rb_node->rb_left;
            }
            else
                rb_node = rb_node->rb_right;
        }
        // 全遍历完毕时可以保证找到vm_end>addr且vm_end最小节点或没找到。

        // 找到后更新缓存
        if (vma)
            mm->mmap_cache = vma;
    }
    return vma;
}
```

### find_vma_prev()

和 `find_vma()` 相同，但还会返回结果 vma 的上一个 vma

```c
struct vm_area_struct *find_vma_prev(struct mm_struct *mm,
                                     unsigned long addr,
                                     struct vm_area_struct **pprev);
```

pprev 是双重指针，很明显是个出参，返回找到的 vma 的上一个 vma。

```c
/*
 * Same as find_vma, but also return a pointer to the previous VMA in *pprev.
 */
struct vm_area_struct *
find_vma_prev(struct mm_struct *mm, unsigned long addr,
              struct vm_area_struct **pprev)
{
    struct vm_area_struct *vma;

    vma = find_vma(mm, addr);
    if (vma)
    {
        *pprev = vma->vm_prev;
    }
    else
    {
        // 如果为NULL
        struct rb_node *rb_node = mm->mm_rb.rb_node;
        *pprev = NULL;
        // 遍历右子树，找地址值最大vma
        while (rb_node)
        {
            *pprev = rb_entry(rb_node, struct vm_area_struct, vm_rb);
            rb_node = rb_node->rb_right;
        }
    }
    return vma;
}
```

### find_vma_intersection()

找第一个与指定区间相交的 vma，vm_start <= start_addr < end_addr < vm_end

```c
/* Look up the first VMA which intersects the interval start_addr..end_addr-1,
   NULL if none.  Assume start_addr < end_addr. */
static inline struct vm_area_struct *find_vma_intersection(
    struct mm_struct *mm,
    unsigned long start_addr,
    unsigned long end_addr)
{
    // 首先找到vm_end>start_addr的节点
    struct vm_area_struct *vma = find_vma(mm, start_addr);
    // 如果能保证end_addr<vm_start，则相交
    if (vma && end_addr <= vma->vm_start)
        vma = NULL;
    return vma;
}
```

### mmap()和 do_mmap():创建地址区间

内核使用 `do_mmap()` 函数在虚拟内存中创建一个新的线性地址区间，这个区间并不等于 vma。

如果新创建的地址区间可以和已存在的 vma **合并**(地址相邻，权限相同等)，那会自动合并；否则会以该地址区间为基础创建新的 vma。

当前 Linux 中的名为`do_mmap_pgoff`：

```c
// include/linux/mm.h
unsigned long do_mmap_pgoff(
    struct file *file,
    unsigned long addr,
    unsigned long len,
    unsigned long prot,
    unsigned long flags,
    unsigned long pgoff,
    unsigned long *populate);
```

参数说明：

- file：从文件中映射，file 为句柄，pgoff 表示文件内偏移，len 表示长度。如果 file 和 offset 为 NULL，表示和文件无关，称为**匿名映射** (anonymous mapping)，否则称为**文件映射** (file-backed mapping)
- addr：可选，指定从哪里开始搜索空闲区域用于分配新区域
- prot：指定该区域的访问权限，读、写、执行
- flags：指定了和 vma 相关的[标志](#vma-标志vm_flags)

失败时返回 NULL。分配成功时判断是否可与已存在的 vma 合并，否则从 slab 分配一个新的 vm_area_struct 结构体，然后使用`vma_link()`函数将新分配的 vma 添加到内存描述符(mm)的 vma 链表和红一黑树中，随后还要更新内存描述符(mm)中的`total_vm`域，然后才返回新分配的地址区间的初始地址。

在用户空间可以通过`mmap()`系统调用获取内核函数`do_mmap()`的功能

```c
void *mmap2(unsigned long addr,
            unsigned long len,
            int prot, int flags,
            int fd, long pgoff)
```

### munmap()和 do_munmap():删除地址区间

do_munmap() 函数从特定的进程地址空间中删除指定地址空间及其映射的虚拟内存区间

```c
int do_munmap(struct mm_struct *mm, unsigned long start, size_t len)
```

如果 start 和 len 正好和一个 vma 相同，那就直接从 mm 中取消关联该 vma，然后删除这个 vma（TODO:还有个问题，如果 vma 被好几个进程共享也删掉吗）

进程空间可以使用的系统调用：

```c
int munmap(void *start, size_t length)
```

## 页表

详见[多级页表](/posts/operating-systems-16/#多级页表)

Linux 使用的是三级页表，使用了 TLB 技术，每个进程拥有独立页表，线程组共享页表，此时需要锁保护。

![f15-1](/assets/img/2023-02-20-linux-kernel-memory/f15-1.jpg)

## 参考

- [Linux 内核设计与实现（第三版）第十二、十五章](https://www.amazon.com/Linux-Kernel-Development-Robert-Love/dp/0672329468/ref=as_li_ss_tl?ie=UTF8&tag=roblov-20)
- [Robert Love](https://rlove.org/)
- [Linux 的虚拟系统调用加速](http://readm.tech/2016/09/23/syscall/)
