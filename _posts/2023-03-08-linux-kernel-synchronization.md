---
title: "Linux内核学习笔记之同步"
author: Jinkai
date: 2023-03-08 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [kernel, Linux]
---

有关并发和同步的基本知识，可见[本文](/posts/operating-systems-20/)以及后续几篇文章，这里不再赘述。

## 造成并发执行的原因

真并发和伪并发：

- **真并发**：在多处理器的情况下，多个进程(线程)能够在多个 CPU 核心上同时执行。
- **伪并发**：即使只有一个处理器，用户程序也会被调度程序抢占和重新调度，我们可以认为所有就绪的进程都在同时执行，这就是抢占式内核的特性

虽然真并发和伪并发的原因和含义不同，但它们都同样会造成竞争条件，而且也需要同样的保护。

内核中有类似可能造成并发执行的原因。它们是：

- **中断**：中断几乎可以在任何时刻异步发生，也就可能随时打断当前正在执行的代码。
- **软中断和 tasklet**：内核能在任何时刻唤醒或调度软中断和 tasklet（基于中断），打断当前正在执行的代码。
- **内核抢占**：因为内核具有抢占性，所以内核中的任务可能会被另一任务抢占。
- **睡眠及与用户空间的同步**：进程可能会睡眠（主动放弃 CPU），这就会唤醒调度程序，从而导致调度一个新的用户进程执行。
- **对称多处理**：两个或多个处理器可以同时执行代码。

在**中断处理程序**中能避免并发访问的安全代码称作**中断安全代码(interrupt-safe)**，在**对称多处理**的机器中能避免并发访问的安全代码称为**SMP 安全代码(SMP-safe)**,在**内核抢占**时能避免并发访问的安全代码称为**抢占安全代码(preempt-safe)**。

> 最开始设计代码的时候就要考虑加入锁，而不是事后才想到。

### 配置选项:SMP 与 UP

`CONFIG_SMP` 配置选项控制内核是否支持**SMP**`，CONFIG_PREEMPT` 用于配置是否开启**内核抢占**

如果都开启就要考虑上面的所有情况。

## 原子操作

原子操作可以保证指令以原子的方式执行——执行过程不被打断。

内核提供了两组原子操作接口——一组针对**整数**进行操作，另一组针对**单独的位**进行操作。在 Linux 支持的所有体系结构上都实现了这两组接口。大多数体系结构会提供支持原子操作的简单**算术指令**。而有些体系结构确实缺少简单的原子操作指令，但是也为单步执行提供了**锁内存总线**的指令，这就确保了其他改变内存的操作不能同时发生。

### 原子整数操作

引入了一个新类型`atomic_t`，用于原子变量，其好处是：

- 让原子函数能识别并仅接收该类型数据
- 让编译器做出特殊的优化
- 在不同体系架构中屏蔽差异

```c
// include/linux/types.h
typedef struct {
    int counter;
} atomic_t;

#ifdef CONFIG_64BIT
typedef struct {
    long counter;
} atomic64_t;
#endif
```

`atomic_t` 总是**32 位**的，无关体系架构。而 `atomic64_t` 是 **64 位**的，仅在 64 位体系架构中定义。

对原子变量的操作函数定义在`<include/asm/atomic.h>`中，为体系结构特有，包括初始化/增/减等。一般使用**内联(inline)函数**的形式，一般通过内嵌**汇编指令**实现。

能够使用原子操作时就尽量不要使用锁，因为原子操作的性能更好。

32 位版`atomic_t`的操作函数（64 位版`atomic64_t`差不多，函数名多了个“64”）：

| 原子操作函数                                | 描述                                               |
| :------------------------------------------ | :------------------------------------------------- |
| ATOMIC_INIT(int i)                          | 在声明一个 atomic+变量时，将它初始化为 i           |
| int atomic_read(atomic_t\* v)               | 原子地读取整数变量 v                               |
| void atomic_set(atomic_t\* y,int i)         | 原子地设置 v                                       |
| void atomic_add(intijatomic_t\* v)          | 原子地给 v 加 i                                    |
| void atomic_sub(inti,atomic_t\* v)          | 原子地从 v 减 i                                    |
| void atomic_inc(atomic_t\* v)               | 原子地给 v 加 1                                    |
| void atomic_dec(atomic_t\* v)               | 原子地从 v 减 1                                    |
| int atomic_sub_and_test(int iatomic_t\* v)  | 原子地从 v 减 i，如果结果等于 0，返回真;否则返回假 |
| int atomic_add_negative(int i,atomic_t\* v) | 原子地给 v 加 i，如果结果是负数，返回真;否则返回假 |
| int atomic_add_return(int i,atomic_t\* v)   | 原子地给 v 加 i，且返回结果                        |
| int atomic_sub_return(int i,atomic_t\* v)   | 原子地从 v 减 i，且返回结果                        |
| int atomic_inc_return(int i,atomic_t\* v)   | 原子地给 v 加 1，且返回结果                        |
| int atomic_dec_return(int i,atomic_t\* v)   | 原子地从 v 减 1，且返回结果                        |
| int atomic_dec_and_test(atomic_t\* v)       | 原子地从 v 减 1，如果结果等于 0，返回真;否则返回假 |
| int atomic_inc_and_test(atomic_t\* v)       | 原子地给 v 加 1，如果结果等于 0，返回真;否则返回假 |

使用示例：

```c
atomic_t v; // 定义原子变量v
atomic_t u = ATOMIC_INIT(0); // 定义u并初始化为0

atomic_set(&v,4); // 设置为4
atomic_add(2,&v); // 增加2
atomic_inc(&v); // 增加1，用于递增计数器
printk("%d\n",atomic_read(&v)); /* 转为int类型并打印*/
```

### 原子位操作

操作函数定义在体系特定的`<include/asm/bitops.h>`中

| 位原子操作函数                              | 说明                                             |
| :------------------------------------------ | :----------------------------------------------- |
| void set_bit(int nr,void \*addr)            | 原子地设置 addr 所指对象的第 nr 位（置 1）       |
| void clear_bit(int nr,void \*addr)          | 原子地清空 addr 所指对象的第 nr 位（清 0）       |
| void change_bit(int nr,void addr)           | 原子地翻转 addr 所指对象的第 nr 位               |
| int test_and_set_bit(int nr,void \*addr)    | 原子地设置 addr 所指对象的第 nr 位，并返回原先值 |
| int test_and_clear_bit(int nr.void \*addr)  | 原子地清空 addr 所指对象的第 nr 位，并返回原先值 |
| int test_and_change_bit(int nr,void \*addr) | 原子地翻转 addr 所指对象的第 nr 位，并返回原先值 |
| int test_bit(int nr,void \*addr)            | 原子地返回 addr 所指对象的第 nr 位               |

对位的操作看上去简单但其实并不只有一步：

```c
*p |= mask; // 应该展开为 *p = *p | mask
// *p &= ~mask;
// *p ^= mask;
```

第一步是读取并计算`*p | mask`，第二步是写入`*p`，所以该操作是非原子的，中间可以插入其他动作导致结果不正确。比如 arm 会通过关中断的方式将两步合并为原子操作。

为方便起见，内核还提供了一组与上述操作对应的**非原子位函数**。非原子位函数与原子位函数的操作完全相同，但是，前者不保证原子性，且其名字前缀多两个下划线(如`__test_bit()`)。如果你不需要原子性操作(比如说，你已经用锁保护了自己的数据)，那么这些非原子的位函数可能会执行得更快些。

## 禁止抢占

首先只考虑**伪并发**问题，如果数据是每个 CPU 唯一的，就不需要考虑多 CPU 并发时的同步问题。

只要禁止进程的**调度**，也就是关闭**内核抢占**功能，就能解决伪并发的同步问题。

| 函数                        | 描述                                                          |
| :-------------------------- | :------------------------------------------------------------ |
| preempt_disable()           | 增加抢占计数值，从而禁止内核抢占                              |
| preempt_enable()            | 减少抢占计数，并当该值降为 0 时检查和执行被挂起的需调度的任务 |
| preempt_enable_no_resched() | 激活内核抢占但不再检查任何被挂起的需调度任务                  |
| preempt_count()             | 返回抢占计数                                                  |

具体实现中，`preempt_disable()` 函数会调用 `local_irq_disable()` 函数来禁用本地 CPU 的中断，并将当前进程的 `preempt_count` 值加 1。`preempt_count` 表示当前进程的**抢占计数器**，当该值大于 0 时，表示当前进程不可被抢占。当调用 `preempt_enable()` 函数时，会将 `preempt_count` 值减 1，当 preempt_count 值为 0 时，表示当前进程可以被抢占。

根据原理可知以上接口可以嵌套使用，但 enable 和 disable 的数量要相同。

```c
preempt_disable() ;
/* 临界区 */
preempt_enable();
```

`get_cpu()`实现了对上述函数的封装，它会关闭内核抢占并返回当前 CPU 号。适用于每个 CPU 都有独立的相同类型的变量(比如放在一个数组里)，实例可见[本文](/posts/linux-kernel-memory/#老的每个-cpu-分配)：

```c
int cpu;
cpu = get_cpu();/*获得当前处理器，并禁止内核抢占，相当于加了锁进入临界区*/
// 对本CPU对应的对象进行访问修改等操作，如：
my_object[cpu]++;

printk("my_object on cpu-%d is %lu\n", cpu, my_object[cpu]);
put_cpu(); /*激活内核抢占*/
```

## 自旋锁 spinlock

Linux 内核中最常见的锁是自旋锁(spinlock)。自旋锁最多只能被一个可执行线程持有(只有一个线程能进入临界区)。

### 自旋锁方法

自旋锁相关方法定义在`<include/linux/spinlock.h>`：

| 方法                     | 描述                                                 |
| :----------------------- | :--------------------------------------------------- |
| spin_lock()              | 获取指定的自旋锁                                     |
| spin_lock_irq()          | 禁止本地中断并获取指定的锁                           |
| spin_lock_irqsave()      | 保存本地中断的当前状态，禁止本地中断，并获取指定的锁 |
| spin_unlock()            | 释放指定的锁                                         |
| spin_unlock_irq()        | 释放指定的锁，并激活本地中断                         |
| spin_unlock_irqrestore() | 释放指定的锁，并让本地中断恢复到以前状态             |
| spin_lock_init()         | 动态初始化指定的 spinlock_t                          |
| spin_trylock()           | 试图获取指定的锁，如果未获取，则返回非 0             |
| spin_is_locked()         | 如果指定的锁当前正在被获取，则返回非 0，否则返回 0   |

示例：

```c
DEFINE_SPINLOCK(&mr_lock);

spin_lock(&mr_lock);
/* 临界区... */
spin_unlock(&mr_lock);
```

`spin_lock()`会**关闭内核抢占**，也就是自旋等待以及处于临界区内时无法被调度，直到`spin_unlock()`，见[本文](/posts/linux-kernel-interrupt/#检查重新调度)。这是为了解决**伪并发**的问题。

注意不要**嵌套**和**递归**使用自旋锁，已经持有锁的情况下请求同样的锁就会发生**死锁**。

自旋锁不应被**长时间持有**，所以临界区必须很短。正是因为这个特性，自旋锁才可以使用在**中断处理程序**中（中断处理程序的要求也是尽可能的简短），前提是必须**禁止本地中断**，禁止本地中断有两个目的：

- ~~在中断处理程序中，防止在持有锁时产生中断抢占，抢占的中断也有可能请求该锁，形成死锁~~（新版本内核不允许中断抢占了，见[IRQF_DISABLED 已被移除](/posts/linux-kernel-interrupt/#参数-flags)和[Linux 的中断可以嵌套吗？](https://zhuanlan.zhihu.com/p/91338338)）
- 在用户或内核空间进程（或者是中断下半部）中，防止**持有锁时被中断**，该中断可能也请求该锁，形成死锁

禁止本地中断并使用自旋锁的示例：

```c
DEFINE_SPINLOCK(mr_lock);
unsigned long flags;
// 该函数封装了禁止本地中断操作
spin_lock_irqsave(&mr_lock, flags);
/* 临界区... */
spin_unlock_irqrestore(&mr_lock, flags);
```

> **调试自旋锁**
>
> 配置选项 `CONFIG_DEBUG_SPINLOCK` 为使用自旋锁的代码加入了许多调试检测手段。激活了该选项，内核就会检查是否使用了未初始化的锁，是否在还没加锁的时候就要对锁执行开锁操作。在测试代码时，总是应该激活这个选项。如果需要进一步全程调试锁，还应该打开 `CONFIG_DEBUG_LOCK_ALLOC` 选项。

### 自旋锁和下半部

同 CPU 下共享的情况：

- 下半部和进程上下文共享：使用 `spin_lock_bh()` 禁止下半部抢占。
- 下半部和中断处理程序共享：`使用 spin_lock_irqsave()` 禁止中断抢占和调度，和上面进程和中断处理程序共享的情况一样。

不同 CPU 下并发的情况：

- 同类的 tasklet 不可能同时运行（回忆下[tasklet-检测和处理](/posts/linux-kernel-interrupt/#tasklet-检测和处理)，运行 tasklet 服务程序前会检查是否有其他 CPU 正在运行相同的程序，如果是会直接跳过），所以对于同类 tasklet 中的共享数据**不需要保护**。
- 不同类的 tasklet 间共享时，只需使用**普通自旋锁**`spin_lock()`（回忆下 tasklet 在同一是以链表形式串行执行任务的，在同 CPU 上不可能相互抢占，无需禁止中断）
- 同类的软中断可以同时运行（在不同 CPU 上），需要使用**普通自旋锁**`spin_lock()`
- 不同类的软中断可以同时运行（在不同 CPU 上），但不能在同一 CPU 上相互抢占，所以也使用**普通自旋锁**`spin_lock()`

### 读-写自旋锁

定义在`<include/linux/rwlock.h>`

```c
typedef struct
{
    arch_rwlock_t raw_lock;
#ifdef CONFIG_GENERIC_LOCKBREAK
    unsigned int break_lock;
#endif
#ifdef CONFIG_DEBUG_SPINLOCK
    unsigned int magic, owner_cpu;
    void *owner;
#endif
#ifdef CONFIG_DEBUG_LOCK_ALLOC
    struct lockdep_map dep_map;
#endif
} rwlock_t;
```

读-写自旋锁需要实现：

- 读和写互斥
- 读者之间不互斥
- 写者之间互斥

读-写自旋锁并不公平，因为允许同时有好几个读者，只有还有读者占用锁，写者就无法使用临界资源。如果读者不断插队，会导致写者饿死。

读-写自旋锁也具备自旋锁的特性：不能用于较长的临界区，可以在中断处理程序中使用。

| 方法                      | 描述                                               |
| :------------------------ | :------------------------------------------------- |
| read_lock()               | 获得指定的读锁                                     |
| read_lock_irq()           | 禁止本地中断并获得指定读锁                         |
| read_lock_irqsave()       | 存储本地中断的当前状态，禁止本地中断并获得指定读锁 |
| read_unlock()             | 释放指定的读锁                                     |
| read_unlock_irq()         | 释放指定的读锁并激活本地中断                       |
| read_unlock_irqrestore()  | 释放指定的读锁并将本地中断恢复到指定的前状态       |
| write_lock()              | 获得指定的写锁                                     |
| write_lock_irq()          | 禁止本地中断并获得指定写锁                         |
| write_lock_irqsave()      | 存储本地中断的当前状态，禁止本地中断并获得指定写锁 |
| write_unlock()            | 释放指定的写锁                                     |
| write_unlock_irq()        | 释放指定的写锁并激活本地中断                       |
| write_unlock_irqrestore() | 释放指定的写锁并将本地中断恢复到指定的前状态       |
| write_trylock()           | 试图获得指定的写锁;如果写锁不可用，返回非 0 值     |
| rwlock_init()             | 初始化指定的 rwlock_t                              |

读/写自旋锁的使用方法类似于普通自旋锁，它们通过下面的方法初始化:

```c
DEFINE_RWLOCK(mr_rwlock);
```

读者:

```c
read_lock(&mr_rwlock); // 判断读者数非-1并增加计数
/*临界区(读者只读)…*/
read_unlock(&mr_rwlock);
```

写者:

```c
write_lock(&mr_rwlock); // 判断读者数为0，并置为-1
/*临界区(写者可读写)…*/
write_unlock(&mr_rwlock);
```

死锁示例：

```c
read_lock(&mr_rwlock);
write_lock(&mr_rwlock);// 持有读锁时获取写锁
```

## 信号量 semaphore

信号量见[《Operating Systems: Three Easy Pieces》学习笔记(二十五) 信号量](/posts/operating-systems-25/)

信号量就是锁+条件变量+单值条件，相比于自旋锁的区别是等待“锁”时可以睡眠。

### 计数信号量和二值信号量

- 二值信号量：只允许一个锁持有者，value <= 1，可以为负数
- 计数信号量：允许多个锁持有者，value 可以比 1 大。

Linux 中使用 `semaphore` 表示计数信号量，使用 `mutex` 表示二值信号量，本节介绍 `semphore`。

信号量在 1968 年由 Edsger Wybe Dijkstra 提出，此后它逐渐成为一种常用的锁机制。信号量支持两个原子操作 P() 和 V()，这两个名字来自荷兰语 Proberen 和 Vershogen。前者叫做测试操作(字面意思是探查)，后者叫做增加操作。后来的系统把两种操作分别叫做 `down()`和 `up()`。

Linux 也遵从这种叫法。`down()`操作通过对信号量计数减 1 来请求获得一个信号量（如果变为负数就进等待队列）。`up()`操作用于释放信号量并唤醒等待的进程。

### 使用信号量

定义在 `<include/linux/semaphore.h>` 中

```c
struct semaphore
{
    raw_spinlock_t lock;
    unsigned int count;
    struct list_head wait_list;
};
```

| 方法                                    | 描述                                                             |
| :-------------------------------------- | :--------------------------------------------------------------- |
| sema_init(struct semaphore \*,int)      | 以指定的计数值初始化动态创建的信号量                             |
| init_MUTEX(struct semaphore \*)         | 以计数值 1 初始化动态创建的信号量                                |
| init_MUTEX_LOCKED(struct semaphore \*)  | 以计数值 0 初始化动态创建的信号量（初始为加锁状态）              |
| down_interruptible(struct semaphore \*) | 试图获得指定的信号量，如果信号量己被争用，则进入可中断睡眠状态   |
| down(struct semaphore \*)               | 试图获得指定的信号量，如果信号量已被争用，则进入不可中断睡眠状态 |
| down_trylock(struct semaphore \*)       | 试图获得指定的信号量，如果信号量已被争用，则立刻返回非 0 值      |
| up(struct semaphore \*)                 | 释放指定信号量，如果睡眠队列不空，则唤醒其中一个任务             |

示例：

```c
/*定义并声明一个信号最，名字为mr_sem，用于信号量计数*/
static DECLARE_MUTEX(mr_sem);

/*试图获取信号量，如果信号量被争用，会进入睡眠*/
if(down_interruptible(&mr_sem)){
    // 应该返回0，否则出错
    return ERROR;
}

/*临界区...*/

/*释放给定的信号量*/
up(&mr_sem);
```

## 读-写信号量

与信号量的关系和自旋锁与读-写自旋锁关系差不多, 定义在 `<include/linux/rwsem.h>`

rw_semaphore 结构：

```c
struct rw_semaphore
{
    long count;
    raw_spinlock_t wait_lock;
    struct list_head wait_list;
#ifdef CONFIG_DEBUG_LOCK_ALLOC
    struct lockdep_map dep_map;
#endif
};
```

_示例：_

```c
static DECLARE_RWSEM(mr_rwsem);
```

读者：

````c
/*试图获取信号量用于读...*/
down_read(&mr_rwsem);

/*临界区(只读)*/

/*释放信号量*/
up_read(&mr_rwsem);

/*...*/

写者：

```c
/*试图获取信号量用于写...*/
down_write(&mr_rwsem);

/*临界区(写者可读写)*/

/*释放信号量*/
up_write(&mr_sem);
````

读-写信号量相比读-写自旋锁多一种特有的操作:`downgrade_write()`（也就是持有写锁时转为读锁，由写者变为第一个读者）。这个函数可以动态地将获取的写锁转换为读锁。

## 互斥体 mutex

目前内核对信号量的用法其实就是允许睡眠的自旋锁而已，但信号量很复杂导致使用起来并不方便，所以引入了更简洁高效的互斥体。

互斥体其实就是**二值信号量**，也就是 count<=1

```c
// include/linux/mutex.h
struct mutex
{
    /* 1: unlocked, 0: locked, negative: locked, possible waiters */
    atomic_t count;
    spinlock_t wait_lock;
    struct list_head wait_list;
#if defined(CONFIG_DEBUG_MUTEXES) || defined(CONFIG_SMP)
    struct task_struct *owner;
#endif
#ifdef CONFIG_MUTEX_SPIN_ON_OWNER
    void *spin_mlock; /* Spinner MCS lock */
#endif
#ifdef CONFIG_DEBUG_MUTEXES
    const char *name;
    void *magic;
#endif
#ifdef CONFIG_DEBUG_LOCK_ALLOC
    struct lockdep_map dep_map;
#endif
};
```

| 方法                            | 描述                                                            |
| :------------------------------ | :-------------------------------------------------------------- |
| mutex_init(struct mutex\*)      | 初始化 mutex                                                    |
| mutex_lock(struct mutex\*)      | 为指定的 mutex 上锁，如果锁不可用则睡眠                         |
| mutex_unlock(struct mutex\*)    | 为指定的 mutex 解锁                                             |
| mutex_trylock(struct mutex\*)   | 试图获取指定的 mutex，如果成功则返回 1;否则锁被获取，返回值是 0 |
| mutex_is_locked(struct mutex\*) | 如果锁已被争用，则返回 1;否则返回 0                             |

要求：

- 上锁解锁必须一一对应，上锁者负责解锁，且只在同一上下文中进行
- 同时只有一个用户可以持有锁
- 当持有 mutex 时，进程不能退出
- 禁止递归上锁解锁
- 不能在中断上下文和下半部使用，因为允许睡眠
- 只能使用接口管理，禁止直接操作 mutex 结构

打开内核配置选项`CONFIG_DEBUG_MUTEXES`，可以对 mutex 进行调试，这也是优于信号量的地方。

## 信号量、互斥体、自旋锁对比

- 自旋锁：不允许睡眠，短期使用
- 信号量：计数信号量
- 互斥体：二值信号量

| 需求             | 建议加锁方式   |
| :--------------- | :------------- |
| 低开销加锁       | 优先使用自旋锁 |
| 短期锁定         | 优先使用自旋锁 |
| 长期加锁         | 优先使用互斥体 |
| 中断上下文中加锁 | 使用自旋锁     |
| 持有锁时需要睡眠 | 使用互斥体     |

## 完成变量

完成变量是没有锁的信号量，可以理解为《操作系统导论》中提到的广播版的[条件变量](/posts/operating-systems-24/)，也就是唤醒时会唤醒所有等待的任务

可以把完成变量理解为一种异步的**通知机制**，当特定操作完成时广播通知所有等待的进程。因为是广播的方式，而且等待者和通知者一般有严格的执行先后顺序(不会发生同时使用该信号的情况)，所以并不需要自旋锁保护内部的信号。

```c
// include/linux/completion.h
struct completion {
    unsigned int done;
    wait_queue_head_t wait;
    // 相比于信号量少了用于保护done的自旋锁
};
```

| 方法                                     | 描述                             |
| :--------------------------------------- | :------------------------------- |
| init_completion(struct completion\*)     | 初始化指定的动态创建的完成变量   |
| wait_for_completion(struct completion\*) | 等待指定的完成变量接收信号发信号 |
| complete(struct completion\*)            | 唤醒任何等待任务                 |

使用完成变量的例子可以参考`kernel/sched.c`和`kernel/fork.c`。

在 `task_struct` 结构中，有一个 `completion` 类型的 `vfork_done` 成员，用处是在 `vfork` 系统调用中，让父进程知道子进程已经释放了共享的内存空间，从而可以恢复执行。详见[本文](/posts/linux-kernel-process/#do_fork-的实现)

```c
// include/linux/sched.h
struct task_struct{
    ...
    struct completion *vfork_done; /* for vfork() */
    ...
}
```

**父进程**在调用 `vfork` 时，会通过 `wait_for_vfork_done` 函数检查 `vfork_done` 的完成状态，并阻塞自己直到子进程的 do_fork 过程完成（由于 vfork 会让子进程和父进程共享内存，所以子进程运行时父进程必须等待）。

**子进程**在调用 `exec`(开始执行) 或 `_exit`(退出) 时，它会通过 `complete` 函数设置 `vfork_done` 的完成状态（此时内存不再共享），并唤醒等待队列中的父进程。

## BLK: 大内核锁

注意：大内核锁目前已废弃，这只是一个过渡功能，且已经完成使命。

BKL(大内核锁)是一个**全局自旋锁**，使用它主要是为了方便实现从 Linux 最初的 SMP 过渡到细粒度加锁机制。

BKL 的临界区是可睡眠的，当持有 BLK 的进程阻塞（无法被调度）时，内核会自动解锁 BLK，当进程被唤醒（可调度）时，内核会重新为 BLK 上锁。防止死锁的发生。

## 顺序锁 seq

顺序锁，通常简称 seq 锁。是在 2.6 版本内核中才引入的一种新型锁。

顺序锁是一种用于解决**读者-写者问题**的锁，类似于上文讨论的**读-写自旋锁**和**读-写信号量**。

使用场景：

- 你的数据存在很多读者。
- 你的数据写者很少。
- 虽然写者很少，但是你希望**写优先于读**，而且不允许读者让写者饥饿。
- 你的数据很简单，如简单结构，甚至是简单的整型。

如果要写优于读，就要保证写操作无需关心读，随时可直接执行，读操作需要判断是否可读以及读到的值是否正确（随时可能被写者修改）。

定义：

```c
// include/linux/seqlock.h

typedef struct seqcount
{
    unsigned sequence;
} seqcount_t;

// 封装了一个自旋锁，无需调用者提供自旋锁
typedef struct
{
    struct seqcount seqcount;
    spinlock_t lock;
} seqlock_t;
```

Linux 中的实现：

- 只有写者能获得和释放 lock 自旋锁，读者无需关心 lock，lock 自旋锁用于让写者之间互斥，这是读-写锁的基本要求
- seqcount 是不断递增的初值为 0 的变量。当写者获得锁时，为 seqcount 加 1；当释放锁时，再为 seqcount 加 1。如果 seqcount 为偶数，表示没有写者正在操作；如果 seqcount 为奇数，表示正在有写者操作（写者临界区内总是奇数）
- 读者不会修改 seqcount，而是自旋的读取它，当 seqcount 为奇数，自旋等待；当 seqcount 为偶数，则开始读取。（读者和写者互斥，读者之间不互斥）
- 读者读取结束后再次判断 seqcount，如果 seqcount 和读取前不同，说明至少有一个写者修改了数据，则放弃本次读取，重新回到上步。

_示例：_

定义一个 seq 锁:

```c
seqlock_t mr_seq_lock = DEFINE_SEQLOCK(mr_seq_lock);
```

写者（和读-写自旋锁类似）：

```c
write_seqlock(&mr_seq_lock); // 自旋锁，且会递增seqcount
/*临界区...*/
write_sequnlock(&mr_seq_lock); // 会递增seqcount
```

读者（和读-写自旋锁有很大区别）：

```c
unsigned long seq;
do {
    seq = read_seqbegin(&mr_seq_lock);// 保存读取前的seqcount
    /* 类似于临界区... */
}
while (read_seqretry(&mr_seq_lock, seq))// 判断当前seqcount是否等于读取前的
```

不同于读-写自旋锁，seq 中读者无法排队，而写者可以排队。读者在尝试获取自旋锁前会判断锁是否被争用（是否还有其他读者或写者占用），如果是，则不会尝试去获取自旋锁。而写者在任何情况下都直接尝试获取自旋锁，若无法获取则排队等待。

### 实例

在[Linux 内核学习笔记之定时器和时间管理](/posts/linux-kernel-time/#读取实际时间)中提到了使用 seq 锁的例子。在这个例子中写比读更加重要，所以不应该使用读-写自旋锁。

当不支持 64 位原子读取的体系架构读取 `jiffies_64` 时，实际在汇编指令上是**非原子操作**，需要加锁保护，这里使用 seq 读锁:

```c
// kernel/time/jiffies.c
#if (BITS_PER_LONG < 64)
u64 get_jiffies_64(void)
{
    unsigned long seq;
    u64 ret;

    do
    {
        seq = read_seqbegin(&jiffies_lock);
        ret = jiffies_64;
    } while (read_seqretry(&jiffies_lock, seq));
    return ret;
}
EXPORT_SYMBOL(get_jiffies_64);
#endif
```

定时器中断会更新 `jiffies_64` 的值，此刻，需要使用 seq 写锁:

```c
// kernel/time/timekeeping.c
void do_timer(unsigned long ticks)
{
    jiffies_64 += ticks;
    update_wall_time();
    calc_global_load(ticks);
}
...
write_seqlock(&jiffies_lock);
do_timer(ticks);
write_sequnlock(&jiffies_lock);
```

## 顺序和屏障

编译器有可能会对代码做优化，导致实际的汇编指令顺序和代码顺序不同。而且现代处理器为了优化其传送管道(pipeline)，也会打乱分派和提交指令的顺序。

TODO:关于乱序 CPU 流水线，需要单独写一篇文章说明。

```c
a=1;
b=2;
```

对于上述代码，编译后有可能先定义了 b 并赋值，再定义 a，虽然看上去没有影响，但在某些情况下我们希望严格的执行顺序：

```c
a=1;
b=a;
```

此时由于 b 依赖于 a，所以必须严格按照代码顺序在内存中创建对象，一般编译器也绝不会对这样的代码做顺序调整。

`屏障(barries)`用于保护执行顺序。顾名思义，屏障是无法被跨越的，在屏障后的代码绝不会在屏障之前执行，在屏障前的代码绝不会在屏障之后执行。

屏障分为两种：

- **内存屏障**：可以同时阻止编译器的顺序优化和处理器的执行顺序优化
- **编译器屏障**：只能阻止编译器的执行顺序优化，更加轻量，一般在单处理器情况下使用

### 内存屏障

`rmb()`方法提供了一个“读”内存屏障，`wmb()`方法提供了一个“写”内存屏障。`mb()`方法既提供了读屏障也提供了写屏障。

`read_barrier_depends()`是`rmb()`的变种，它提供了一个读屏障，但是仅仅是前后有**依赖关系**的读操作。对于没有依赖的读，它就是空操作，所以性能可能会比`rmb`好。(写操作好像没有对于的依赖性屏障)

```c
// 载入*pp前必须依赖载入p，载入也就是对应load指令，
// 本例有明确的依赖关系，有屏障作用
pp = p;
read_barrier_depends();
b = *pp;

// 没有明确依赖关系，read_barrier_depends()就是空操作，不起到屏障作用
d = a;
read_barrier_depends();
b = a;

// 如果一定要设立屏障，必须使用rmb()或mb()
d = a;
rmb();
b = a;
```

_示例：_

假设有两个核心 CPU-a 和 CPU-b，它们共享一个对象 obj，obj 有两个字段 data 和 ready。CPU-a 要给 obj 赋值，并把 ready 置为 1，表示 obj 已经准备好了。CPU-b 要检查 obj 是否准备好了，如果是就使用 obj 的 data 做一些事情。

```c
// CPU-a
obj->data = xxx; // 给obj的data赋值
wmb(); // 写内存屏障
obj->ready = 1; // 把obj的ready置为1

// CPU-b
if (obj->ready) // 检查obj是否准备好了
  do_something(obj->data); // 使用obj的data做一些事情
```

这里的写内存屏障`wmb()`是为了保证 CPU-a 不会对代码进行重排序，从而使得 ready 标记置位的时候，**data 一定是有效的**。但是在 alpha 机器上， CPU-b 上的 do_something 可能使用旧的 data(实际执行 do_someting 还是在 ready 判断之后的，但因为 data 是在 CPU-a 上改的，可能 CPU-b 上的 cache 未及时更新，data 的 cache 还是旧值，所以本质就是 cache 刷新指令和 load 指令的乱序以及多个 CPU 拥有各自独立的 cache，不能做到及时更新)。

```c
// CPU-a
obj->data = xxx; // 给obj的data赋值
wmb(); // 写内存屏障
obj->ready = 1; // 把obj的ready置为1

// CPU-b
if (obj->ready) // 检查obj是否准备好了（先更新了ready）
  do_something(obj->data); // 使用obj的data做一些事情（但此时data还是旧值）
```

所以需要添加读屏障 rmb()，让 cache 刷新操作必定在 data 被读取前执行。

```c
// CPU-a
obj->data = xxx; // 给obj的data赋值
wmb(); // 写内存屏障
obj->ready = 1; // 把obj的ready置为1

// CPU-b
if (obj->ready) // 检查obj是否准备好了（先更新了ready）
{
  rmb(); // 读内存屏障
  do_something(obj->data); // 使用obj的data做一些事情（此时保证读到最新值）
}
```

### 编译器屏障

`barrier()`方法可以防止编译器跨屏障对载入或存储操作进行优化。

`smp_rmb()` 等系列宏提供了**自适应**的屏障，在对称多处理器(SMP)上提供内存屏障，在单处理器(UP)上提供编译器屏障

| 屏障                       | 描述                                                                |
| :------------------------- | :------------------------------------------------------------------ |
| rmb()                      | 阻止跨越屏障的载入动作发生重排序                                    |
| read_barrier_depends()     | 阻止跨越屏障的具有数据依赖关系的载入动作重排序                      |
| wmb()                      | 阻止跨越屏障的存储动作发生重排序                                    |
| mb()                       | 阻止跨越屏障的载入和存储动作重新排序                                |
| smp_rmb()                  | 在 SMP 上提供 rmb() 功能，在 UP 上提供 barrier() 功能               |
| smp_read_barrier_depends() | 在 SMP 上提供 read_barrierdepends()功能，在 UP 上提供 barrier()功能 |
| smp_wmb()                  | 在 SMP 上提供 wmb0 功能，在 UP 上提供 barrier()功能                 |
| smp_mb()                   | 在 SMP 上提供 mb()功能，在 UP 上提供 barrier()功能                  |
| barrier()                  | 阻止编译器跨屏障对载入和存储动作进行优化                            |

## 参考

- [Linux 内核设计与实现（第三版）第九、十章](https://www.amazon.com/Linux-Kernel-Development-Robert-Love/dp/0672329468/ref=as_li_ss_tl?ie=UTF8&tag=roblov-20)
- [Robert Love](https://rlove.org/)
- [linux 顺序锁 seqlock](https://zhuanlan.zhihu.com/p/364044850)
- [原理和实战解析 Linux 中如何正确地使用内存屏障](https://mp.weixin.qq.com/s/s6AvLiVVkoMX4dIGpqmXYA)
