---
title: "《Operating Systems: Three Easy Pieces》学习笔记(二十四) 条件变量"
author: Jinkai
date: 2022-06-16 09:02:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

锁并不是并发程序设计所需的唯一原语。在很多情况下，线程需要检查某一`条件`（condition）满足之后，才会继续运行。

```c
void *child(void *arg)
{
    printf("child\n");
    // XXX how to indicate we are done?
    // 自旋锁标记
    done = 1;
    return NULL;
}

int main(int argc, char *argv[])
{
    printf("parent: begin\n");
    pthread_t c;
    Pthread_create(&c, NULL, child, NULL); // create child
    // XXX how to wait for child?
    // 加个自旋锁等待done为1
    while (done == 0)
        ; // spin
    printf("parent: end\n");
    return 0;
}
```

要父线程等待子线程的话，需要加个自旋锁

## 定义和程序

线程可以使用条件变量（condition variable），来等待一个条件变成真。条件变量是一个`显式队列`，当某些执行状态（即条件，condition）不满足时，线程可以把自己`加入队列`，`等待`（waiting）该条件。另外某个线程，当它改变了上述状态时，就可以`唤醒`一个或者多个`等待线程`（通过在该条件上发信号），让它们继续执行。

声明：pthread_cond_t c
相关操作：wait()和 signal()

父线程等待子线程--使用条件变量:

```c
pthread_cond_wait(pthread_cond_t *c, pthread_mutex_t *m);
pthread_cond_signal(pthread_cond_t *c);
int done = 0;
pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t c = PTHREAD_COND_INITIALIZER;

void thr_exit()
{
    Pthread_mutex_lock(&m);
    done = 1;
    // 如果有等待的线程，就唤醒它(们)
    Pthread_cond_signal(&c);
    Pthread_mutex_unlock(&m);
}

void *child(void *arg)
{
    printf("child\n");
    thr_exit();
    return NULL;
}

void thr_join()
{
    Pthread_mutex_lock(&m);
    // 这里先判断done防止done为1时永久休眠
    while (done == 0)
        // 休眠，等待被唤醒
        Pthread_cond_wait(&c, &m);
    Pthread_mutex_unlock(&m);
}

int main(int argc, char *argv[])
{
    printf("parent: begin\n");
    pthread_t p;
    Pthread_create(&p, NULL, child, NULL);
    thr_join();
    printf("parent: end\n");
    return 0;
}
```

wait()调用有一个`参数`，它是`互斥量`。

它假定在 wait()调用时，这个互斥量是`已上锁`状态。wait()的职责是`释放锁`，并让调用线程`休眠`（原子地）。当线程被`唤醒`时（在另外某个线程发信号给它后），它必须`重新获取锁`，再返回调用者。

> **提示：发信号时总是持有锁**
>
> 尽管并不是所有情况下都严格需要，但有效且简单的做法，还是在使用条件变量发送信号时持有锁。虽然上面的例子是必须加锁的情况，但也有一些情况可以不加锁，而这可能是你应该避免的。因此，为了简单，请在`调用 signal` 时`持有锁`（hold the lock when calling signal）。
>
> 这个提示的反面，即调用 wait 时持有锁，不只是建议，而是 wait 的语义强制要求的。因为 wait 调用总是假设你调用它时已经持有锁、调用者睡眠之前会释放锁以及返回前重新持有锁。因此，这个提示的一般化形式是正确的：调用 signal 和 wait 时要持有锁（hold the lock when calling signal or wait），你会保持身心健康的。

## 生产者/消费者（有界缓冲区）问题

```c
cond_t cond;
mutex_t mutex;

void *producer(void *arg)
{
    int i;
    for (i = 0; i < loops; i++)
    {
        Pthread_mutex_lock(&mutex);           // p1
        if (count == 1)                       // p2
            Pthread_cond_wait(&cond, &mutex); // p3
        put(i);                               // p4
        Pthread_cond_signal(&cond);           // p5
        Pthread_mutex_unlock(&mutex);         // p6
    }
}

void *consumer(void *arg)
{
    int i;
    for (i = 0; i < loops; i++)
    {
        Pthread_mutex_lock(&mutex);           // c1
        // 1. 此处存在问题，当有两个消费者（Cus1,Cus2）时，其中Cus1进入休眠，
        // Cus2正好在生产者生产后执行get把count消费掉，此时
        // 生产者又调用signal唤醒Cus1休眠的，直接执行了get发现
        // 没有count了,所以要把if改成while，wait出来还要再
        // 判断一次count
        // 2. 使用while带来另一个问题，Cus1消费后本该唤醒生产者，
        // 但如果唤醒了Cus2线程，因为没东西消费，Cus2也会等待，
        // 就会导致三个线程都在等待中。解决方法是设置两个条件变量，
        // 保证消费者唤醒生产者，生产者唤醒消费者
        if (count == 0)                       // c2
            Pthread_cond_wait(&cond, &mutex); // c3
        int tmp = get();                      // c4
        Pthread_cond_signal(&cond);           // c5
        Pthread_mutex_unlock(&mutex);         // c6
        printf("%d\n", tmp);
    }
}
```

> 一条关于条件变量的简单规则：总是`使用 while 循环`（always use while loop）。
> {: .prompt-tip }

最终代码：

```c
int buffer[MAX];
int fill = 0;
int use = 0;
int count = 0;

void put(int value)
{
    buffer[fill] = value;
    fill = (fill + 1) % MAX;
    count++;
}

int get()
{
    int tmp = buffer[use];
    use = (use + 1) % MAX;
    count--;
    return tmp;
}
cond_t empty, fill;
mutex_t mutex;

void *producer(void *arg)
{
    int i;
    for (i = 0; i < loops; i++)
    {
        Pthread_mutex_lock(&mutex);            // p1
        while (count == MAX)                   // p2
            Pthread_cond_wait(&empty, &mutex); // p3
        put(i);                                // p4
        Pthread_cond_signal(&fill);            // p5
        Pthread_mutex_unlock(&mutex);          // p6
    }
}

void *consumer(void *arg)
{
    int i;
    for (i = 0; i < loops; i++)
    {
        Pthread_mutex_lock(&mutex);           // c1
        while (count == 0)                    // c2
            Pthread_cond_wait(&fill, &mutex); // c3
        int tmp = get();                      // c4
        Pthread_cond_signal(&empty);          // c5
        Pthread_mutex_unlock(&mutex);         // c6
        printf("%d\n", tmp);
    }
}
```

## 覆盖条件

以下代码用于内存分配管理，free 后会唤醒 allocate 时因空间不够而等待的线程

```c
// how many bytes of the heap are free?
int bytesLeft = MAX_HEAP_SIZE;

// need lock and condition too
cond_t c;
mutex_t m;

void *
allocate(int size)
{
    Pthread_mutex_lock(&m);
    while (bytesLeft < size)
        Pthread_cond_wait(&c, &m);
    void *ptr = ...; // get mem from heap
    bytesLeft -= size;
    Pthread_mutex_unlock(&m);
    return ptr;
}

void free(void *ptr, int size)
{
    Pthread_mutex_lock(&m);
    bytesLeft += size;
    Pthread_cond_signal(&c); // whom to signal??
    Pthread_mutex_unlock(&m);
}
```

但 pthread_cond_signal()无法得知应该唤醒哪个线程，比如 free(50)后应该唤醒 allocate(10)等待线程而不是 allocate(100)等待线程。

使用 pthread_cond_broadcast()唤醒所有等待的线程。这样做，确保了所有应该唤醒的线程都被唤醒。当然，不利的一面是可能会影响性能。

Lampson 和 Redell 把这种`条件变量`叫作`覆盖条件`（covering condition），因为它能覆盖所有需要唤醒线程的场景（保守策略）

## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/30.pdf)
