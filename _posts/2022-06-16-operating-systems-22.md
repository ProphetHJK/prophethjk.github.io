---
title: "《Operating Systems: Three Easy Pieces》学习笔记(二十二) 锁"
author: Jinkai
date: 2022-06-16 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

## 锁的基本思想

lock()和 unlock()函数的语义很简单。调用 `lock()` 尝试获取锁，如果没有其他线程持有锁（即它是`可用的`），该线程会`获得锁`，进入`临界区`

当持有锁的线程在临界区时，其他线程就无法进入临界区。

## Pthread 锁

POSIX 库将锁称为互斥量（mutex），因为它被用来提供线程之间的互斥。即当一个线程在临界区，它能够阻止其他线程进入直到本线程离开临界区。

```c
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_lock(&lock); // wrapper for pthread_mutex_lock()
balance = balance + 1;
pthread_mutex_unlock(&lock);
```

## 评价锁

互斥（mutual exclusion）
: 能够阻止多个线程 进入临界区

公平性（fairness）
: 每一个竞争线程有公平的机会抢到锁。是否有竞争锁的线程会饿死（starve），一直无法获得锁

性能（performance）
: 使用锁之后增加的时间开销

## 控制中断

最早提供的`互斥`解决方案之一，就是在临界区关闭中断:

```c
void lock() {
    DisableInterrupts();
}
void unlock() {
    EnableInterrupts();
}
```

假设我们运行在这样一个单处理器系统上。通过在进入`临界区`之前`关闭中断`（使用特殊的硬件指令），可以保证临界区的代码不会被中断，从而`原子`地执行。

缺点:

1. 要求我们允许所有调用线程执行`特权操作`（打开关闭中断），即信任这种机制不会被`滥用`。关中断后操作系统无法获得`控制权`
2. 这种方案不支持`多处理器`。如果多个线程运行在`不同`的 CPU 上，每个线程都试图进入`同一个`临界区，关闭中断也没有作用。线程可以运行在其他处理器上，因此`能够进入临界区`
3. 关闭中断导致`中断丢失`，可能会导致严重的系统问题。假如磁盘设备完成了读取请求，正常应该会给个中断，但 CPU 错失了这一中断，那么，操作系统如何知道去唤醒等待读取的进程

## 测试并设置指令（原子交换）

最简单的`硬件支持`是`测试并设置指令`（test-and-set instruction），也叫作`原子交换`（atomic exchange）。

```c
typedef struct lock_t { int flag; } lock_t;

void init(lock_t *mutex) {
    // 0 -> lock is available, 1 -> held
    mutex->flag = 0;
}

void lock(lock_t *mutex) {
    while (mutex->flag == 1) // TEST the flag
        ; // spin-wait (do nothing)
    mutex->flag = 1; // now SET it!
}

void unlock(lock_t *mutex) {
    mutex->flag = 0;
}
```

上述代码中，每次 lock 会判断 flag 的值，也就是`测试并设置指令（test-and-set instruction）`中的`test`，然后判断成功才`set`

但如果没有硬件辅助，也就是让测试并设置作为一个原子操作，会导致两个线程有可能`同时进入`临界区。

`自旋等待spin-wait`也影响`性能`

自旋锁（spin lock）
: 一直自旋，利用 CPU 周期，直到锁可用。

### 实现可用的自旋锁

在 SPARC 上，这个指令叫 ldstub（load/store unsigned byte，加载/保存无符号字节）；在 x86 上，是 xchg（atomic exchange，原子交换）指令。但它们基本上在不同的平台上做同样的事，通常称为`测试并设置指令`（test-and-set）。

```c
int TestAndSet(int *old_ptr, int new) {
    int old = *old_ptr; // fetch old value at old_ptr
    *old_ptr = new; // store 'new' into old_ptr
    return old; // return the old value
}
```

将`测试并设置`作为`原子操作`

```c
typedef struct lock_t {
    int flag;
} lock_t;

void init(lock_t *lock) {
    // 0 indicates that lock is available, 1 that it is ld
    lock->flag = 0;
}

void lock(lock_t *lock) {
    while (TestAndSet(&lock->flag, 1) == 1)
        ; // spin-wait (do nothing)
}

void unlock(lock_t *lock) {
    lock->flag = 0;
}
```

### 评价自旋锁

正确性（correctness）: 自旋锁一次只允许一个线程进入临界区。因此，这是`正确`的锁

公平性（fairness）: 自旋锁`不提供`任何`公平`性保证

性能（performance）: 在`单 CPU` 的情况下，性能开销相当大。其他线程都在竞争锁，都会在放弃 CPU 之前，自旋一个时间片，浪费 CPU 周期。在`多 CPU` 上，自旋锁性能不错（如果线程数大致等于 CPU 数）

## 比较并交换

`比较并交换指令`（SPARC 系统中是 compare-and-swap，
x86 系统是 compare-and-exchange）

```c
int CompareAndSwap(int *ptr, int expected, int new) {
    int actual = *ptr;
    if (actual == expected)
        *ptr = new;
    return actual;
}
```

比较并交换的基本思路是检测 ptr 指向的值是否和 expected `相等`；如果`是`，`更新` ptr 所指的值为新值。否则，什么也不做。不论哪种情况，都返回该内存地址的实际值，让调用者能够知道执行是否成功。

在自旋锁中可以`替换`测试并设置指令

```c
void lock(lock_t *lock) {
while (CompareAndSwap(&lock->flag, 0, 1) == 1)
    ; // spin
}
```

C 中实现(x86)：

```c
char CompareAndSwap(int *ptr, int old, int new) {
    unsigned char ret;

    // Note that sete sets a 'byte' not the word
    __asm__ __volatile__ (
        " lock\n"
        " cmpxchgl %2,%1\n"
        " sete %0\n"
        : "=q" (ret), "=m" (*ptr)
        : "r" (new), "m" (*ptr), "a" (old)
        : "memory");
    return ret;
}
```

## 链接的加载和条件式存储指令

一些平台提供了实现临界区的一对指令

`链接的加载`（`load-linked`）和`条件式存储`（`store-conditional`）

```c
int LoadLinked(int *ptr) {
    return *ptr;
}

int StoreConditional(int *ptr, int value) {
    if (no one has updated *ptr since the LoadLinked to this address) {
        *ptr = value;
        return 1; // success!
    } else {
        return 0; // failed to update
    }
}
```

`条件式存储`（store-conditional）指令，只有上一次执行`LoadLinked`的地址在期间`都没有更新`时， 才会成功，同时更新了该地址的值

先通过 `LoadLinked` 尝试获取锁值，如果判断到锁被释放了，就执行`StoreConditional`判断在`执行完LoadLinked`到`StoreConditional执行前`ptr 有没有被`更新`，`没有`:说明`没有`其他线程来`抢`，可以进临界区，`有`:说明已经被其他线程`抢走了`，继续重复本段落所述内容循环：

```c
void lock(lock_t *lock) {
    while (1) {
        while (LoadLinked(&lock->flag) == 1)
            ; // spin until it's zero
        if (StoreConditional(&lock->flag, 1) == 1)
            return; // if set-it-to-1 was a success: all done
                // otherwise: try it all over again
    }
}

void unlock(lock_t *lock) {
    lock->flag = 0;
}
```

## 获取并增加

`获取并增加`（fetch-and-add）指令
: 它能`原子`地`返回`特定地址的`旧值`，并且让该值`自增一`。

```c
int FetchAndAdd(int *ptr) {
    int old = *ptr;
    *ptr = old + 1;
    return old;
}
typedef struct lock_t {
    int ticket;
    int turn;
} lock_t;

void lock_init(lock_t *lock) {
    lock->ticket = 0;
    lock->turn = 0;
}

void lock(lock_t *lock) {
    int myturn = FetchAndAdd(&lock->ticket);
    while (lock->turn != myturn)
        ; // spin
}

void unlock(lock_t *lock) {
    FetchAndAdd(&lock->turn);
}
```

原理是每次进入 lock，就获取当前`ticket值`，相当于`挂号`，然后全局 ticket 本身会`自增一`，后续线程都会获得属于自己的`唯一ticket值`，`lock->turn`表示当前`叫号值`，叫到号的运行，unlock 时`递增lock->turn`更新`叫号值`就行。

这种方法保证了公平性，FIFO

## 自旋过多：怎么办

一个线程会一直自旋检查一个`不会改变`的值，`浪费`掉整个时间片！如果有 `N 个`线程去`竞争`一个锁，情况会更糟糕。同样的场景下，会浪费 `N−1 个时间片`，只是自旋并等待一个线程释放该锁。

如何让锁不会`不必要地自旋`，浪费 CPU 时间？

## 使用队列：休眠替代自旋

需要一个队列来保存等待锁的线程。

Solaris 中 park()能够让调用线程休眠，unpark(threadID)则会唤醒 threadID 标识的线程。

## 两阶段锁

`两阶段锁`（two-phase lock）
: 如果第一个`自旋阶段`没有获得锁，`第二阶段`调用者会`睡眠`，直到锁可用。上文的 Linux 锁就是这种锁，不过只自旋一次；更常见的方式是在循环中自旋固定的次数(`希望`这段时间内能`获取到锁`)，然后使用 futex 睡眠。

## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/28.pdf)
