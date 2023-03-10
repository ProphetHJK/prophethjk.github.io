---
title: "《Operating Systems: Three Easy Pieces》学习笔记(二十五) 信号量"
author: Jinkai
date: 2022-06-16 09:03:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

由[锁](/posts/operating-systems-22/)和[条件变量](/posts/operating-systems-24/)两篇文章可知条件变量必须和锁配合使用，那为什么不直接封装在一起呢？于是就有个信号量。

**信号量**只是将锁和单值条件的条件变量**封装**在一起，所以它不是一个全新的概念，它能实现的事锁加条件变量都能实现。对于比较复杂情况下的条件判断无法使用信号量解决，因为其只内置了一个简单的整型的 value 条件。

## 信号量的定义

信号量是有一个整数值的对象，可以用两个函数来操作它。在 POSIX 标准中，是`sem_wait()`和 `sem_post()`。

```c
#include <semaphore.h>
sem_t s;
sem_init(&s, 0, 1);
```

sem_init 用于初始化信号量。

```c
int sem_wait(sem_t *s) {
    decrement the value of semaphore s by one
    wait if value of semaphore s is negative
}

int sem_post(sem_t *s) {
    increment the value of semaphore s by one
    if there are one or more threads waiting, wake one
}
```

- sem_wait()要么`立刻返回`（调用 sem_wait()时，信号量的值`大于等于 1`），同时`信号量减1`，要么会让调用线程`挂起`，直到之后的一个 post 操作。
- sem_post()并没有等待某些条件满足。它直接`增加信号量`的值，如果有等待线程，`唤醒`其中一个。
- 当信号量的值为`负数`时，这个值就是`等待线程`的个数

## 二值信号量（锁）

用信号量作为锁

```c
sem_t m;
// 初值要为1
sem_init(&m, 0, 1);

sem_wait(&m);
// critical section here
sem_post(&m);
```

## 信号量用作条件变量

假设一个线程创建另外一线程，并且等待它结束:

```c
sem_t s;

void *
child(void *arg)
{
    printf("child\n");
    sem_post(&s); // signal here: child is done
    return NULL;
}

int main(int argc, char *argv[])
{
    // X初始值应是0
    sem_init(&s, 0, X); // what should X be?
    printf("parent: begin\n");
    pthread_t c;
    Pthread_create(c, NULL, child, NULL);
    sem_wait(&s); // wait here for child
    printf("parent: end\n");
    return 0;
}
```

## 生产者/消费者（有界缓冲区）问题

```c
sem_t empty;
sem_t full;
sem_t mutex;

void *producer(void *arg)
{
    int i;
    for (i = 0; i < loops; i++)
    {
        // empty/full是一个条件变量，用于唤醒和等待
        // 不过可以自动形成等待队列，比条件变量方便
        sem_wait(&empty); // line p1
        // mutex是一个锁，用于商品队列的操作的保护
        // 锁的作用域很重要，尽可能缩小临界区来避免死锁和提高性能
        sem_wait(&mutex); // line p1.5 (MOVED MUTEX HERE...)
        put(i);           // line p2
        sem_post(&mutex); // line p2.5 (... AND HERE)
        sem_post(&full);  // line p3
    }
}

void *consumer(void *arg)
{
    int i;
    for (i = 0; i < loops; i++)
    {
        sem_wait(&full);  // line c1
        sem_wait(&mutex); // line c1.5 (MOVED MUTEX HERE...)
        int tmp = get();  // line c2
        sem_post(&mutex); // line c2.5 (... AND HERE)
        sem_post(&empty); // line c3
        printf("%d\n", tmp);
    }
}

int main(int argc, char *argv[])
{
    // ...
    sem_init(&empty, 0, MAX); // MAX buffers are empty to begin with...
    sem_init(&full, 0, 0);    // ... and 0 are full
    sem_init(&mutex, 0, 1);   // mutex=1 because it is a lock
    // ...
}
```

## 读者—写者锁

读者之间不互斥，写者之间互斥，读者和写者互斥：

```c
typedef struct _rwlock_t
{
    sem_t lock;      // binary semaphore (basic lock)
    sem_t writelock; // used to allow ONE writer or MANY readers
    int readers;     // count of readers reading in critical section
} rwlock_t;

void rwlock_init(rwlock_t *rw)
{
    rw->readers = 0;
    sem_init(&rw->lock, 0, 1);
    sem_init(&rw->writelock, 0, 1);
}

void rwlock_acquire_readlock(rwlock_t *rw)
{
    // lock锁保护readers计数器
    sem_wait(&rw->lock);
    rw->readers++;
    // 第一个读者需要获取写锁，来与写者互斥
    // 不停有新读者进来会导致写者饿死
    if (rw->readers == 1)
        sem_wait(&rw->writelock); // first reader acquires writelock
    sem_post(&rw->lock);
}

void rwlock_release_readlock(rwlock_t *rw)
{
    sem_wait(&rw->lock);
    rw->readers--;
    // 最后一个读者需要释放写锁
    if (rw->readers == 0)
        sem_post(&rw->writelock); // last reader releases writelock
    sem_post(&rw->lock);
}

void rwlock_acquire_writelock(rwlock_t *rw)
{
    // 写者之间互斥，且与读者互斥，用写锁管理
    sem_wait(&rw->writelock);
}

void rwlock_release_writelock(rwlock_t *rw)
{
    sem_post(&rw->writelock);
}
```

## 哲学家就餐问题

![F31.10](/assets/img/2022-06-16-operating-systems-25/F31.10.jpg)

假定有 5 位“哲学家”围着一个圆桌。每两位哲学家之间有一把餐叉（一共 5 把）。哲学家有时要`思考`一会，不需要餐叉；有时又要`就餐`。而一位哲学家只有同时拿到了左手边和右手边的`两把餐叉`，才能吃到东西。

```c
while (1) {
    think();
    getforks();
    eat();
    putforks();
}
```

关键的挑战就是如何实现 `getforks()`和 `putforks()`函数，保证没有死锁，没有哲学家饿死，并且并发度更高（尽可能让更多哲学家同时吃东西）。

**查找餐叉的函数：**

```c
int left(int p) { return p; }
int right(int p) { return (p + 1) % 5; }
```

**为每个餐叉分配信号量：**

```c
sem_t forks[5]
```

**尝试加锁：**

```c
void getforks() {
    sem_wait(forks[left(p)]);
    sem_wait(forks[right(p)]);
}

void putforks() {
    sem_post(forks[left(p)]);
    sem_post(forks[right(p)]);
}
```

使用这个方案会形成死锁，每个人都拿着左手边的叉子就无法继续了（循环等待）

**优化方案：**

选第 4 个人改为先获取右手的叉子，打破循环等待

```c
void getforks()
{
    if (p == 4)
    {
        sem_wait(forks[right(p)]);
        sem_wait(forks[left(p)]);
    }
    else
    {
        sem_wait(forks[left(p)]);
        sem_wait(forks[right(p)]);
    }
}
```

> 还有其他一些类似的“著名”问题，比如吸烟者问题（cigarette smoker’s problem），理发师问题（sleeping barber problem）。

## 如何实现信号量

```c
typedef struct _Zem_t
{
    int value;
    pthread_cond_t cond;
    // 对value的修改锁
    pthread_mutex_t lock;
} Zem_t;

// only one thread can call this
void Zem_init(Zem_t *s, int value)
{
    s->value = value;
    Cond_init(&s->cond);
    Mutex_init(&s->lock);
}

void Zem_wait(Zem_t *s)
{
    Mutex_lock(&s->lock);
    while (s->value <= 0)
        Cond_wait(&s->cond, &s->lock);
    // 在这里递减value，value值就不会小于0了。
    s->value--;
    Mutex_unlock(&s->lock);
}

void Zem_post(Zem_t *s)
{
    Mutex_lock(&s->lock);
    s->value++;
    Cond_signal(&s->cond);
    Mutex_unlock(&s->lock);
}
```

## 小结

信号量是编写并发程序的强大而灵活的原语。有程序员会因为简单实用，只用信号量，不用锁和条件变量

信号量基于锁和条件变量，可以实现两者的功能

作为锁时，可以自动管理等待队列

作为条件变量时，免去了 while 判断是否需要等待的操作，因为内部包含了一个 value 值用于判断

## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/31.pdf)
