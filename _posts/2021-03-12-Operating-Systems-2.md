---
title: "《Operating Systems: Three Easy Pieces》学习笔记(二) 抽象：进程"
author: Jinkai
date: 2021-03-12 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

> 参考：
>
> - [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/04.pdf)

本系列文章将按照《Operating Systems: Three Easy Pieces》一书的章节顺序编写，结合原文与自己的感悟，以作笔记之用，如有不足之处，恳请在评论区指出

## 进程API

### 创建（create）

操作系统必须包含一些创建新进程的方法。在 shell 中键入命令或双击应用程序图标时，会调用操作系统来创建新进程，运行指定的程序。

### 销毁（destroy）

由于存在创建进程的接口，因此系统还提供了一个强制销毁进程的接口。当然，很多进程会在运行完成后自行退出。但是，如果它们不退出，用户可能希望终止它们，因此停止失控进程的接口非常有用。

### 等待（wait）

有时等待进程停止运行是有用的，因此经常提供某种等待接口。

### 其他控制（miscellaneous control）

除了杀死或等待进程外，有时还可能有其他控制。例如，大多数操作系统提供某种方法来暂停进程（停止运行一段时间），然后恢复（继续运行）。

### 状态（statu）

通常也有一些接口可以获得有关进程的状态信息，例如运行了多长时间，或者处于什么状态。

## 进程创建

### 1. 加载数据到内存

**操作系统运行程序必须做的第一件事是将`代码`和`所有静态数据`（例如初始化变量）从`磁盘`加载（load）到`内存`中**，加载到进程的地址空间中。

![加载：从程序到进程](/assets/img/2021-03-12-Operating-Systems-2/加载：从程序到进程.png)

在早期的（或简单的）操作系统中，加载过程尽早（eagerly）完成，即在运行程序之前全部完成。现代操作系统`惰性`（lazily）执行该过程，即仅在程序执行期间需要加载的代码或数据片段，才会加载。

### 2. 为栈分配空间

**将代码和静态数据加载到内存后，必须为程序的`运行时栈`（run-time stack 或 stack）分配一些内存**。C程序使用栈存放局部变量、函数参数和返回地址。操作系统也可能会用**参数初始化栈**。具体来说，它会将参数填入 main()函数，即 argc 和 argv数组。

### 3. 为堆分配空间

**操作系统也可能为程序的`堆`（heap）分配一些内存**。程序通过调用 `malloc`()来请求这样的空间，并通过调用 `free`()来明确地释放它。`数据结构`（如链表、散列表、树和其他有趣的数据结构）需要堆。

### 4. I/O初始化

**操作系统还将执行一些其他初始化任务，特别是与输入/输出（I/O）相关的任务**。例如，在 UNIX 系统中，默认情况下每个进程都有 3 个打开的`文件描述符`（file descriptor），用于`标准输入、输出和错误`。这些描述符让程序轻松读取来自终端的输入以及打印输出到屏幕。

### 5. 运行程序入口

通过将代码和静态数据加载到内存中，通过创建和初始化栈以及执行与 I/O 设置相关的其他工作，完成准备后，接下来就是`启动程序`，在入口处运行，即 `main()`。

## 进程状态

### 进程的三种状态

- **运行（running）**

    在运行状态下，进程正在处理器上运行。这意味着它正在执行指令。

- **就绪（ready）**

    在就绪状态下，进程已准备好运行，但由于某种原因，操作系统选择不在此时运行。

- **阻塞（blocked）**

    在阻塞状态下，一个进程执行了某种操作，直到发生其他事件时才会准备运行。一个常见的例子是，当进程向磁盘发起 I/O 请求时，它会被阻塞，因此其他进程可以使用处理器

![进程：状态创建](/assets/img/2021-03-12-Operating-Systems-2/进程：状态创建.jpg)

可以根据操作系统的载量，让进程在就绪状态和运行状态之间转换。从就绪到运行意味着该进程已经被调度（scheduled）。从运行转移到就绪意味着该进程已经取消调度（descheduled）。一旦进程被阻塞（例如，通过发起 I/O 操作），OS 将保持进程的这种状态，直到发生某种事件（例如，I/O 完成）。此时，进程再次转入就绪状态（也可能立即再次运行，如果操作系统这样决定）。

关于调度的策略，原文写得过于仔细，我总结下，就是`一个进程阻塞或停止时，就会去调度另一个就绪的进程`，从而让cpu一直保持在满负荷状态

## 数据结构

为了跟踪每个进程的状态，操作系统可能会为所有就绪的进程保留某种`进程列表`（process list），以及跟踪当前正在运行的进程的一些附加信息。操作系统还必须以某种方式跟踪`被阻塞的进程`。当 I/O 事件完成时，操作系统应确保`唤醒`正确的进程，让它准备好再次运行。

```c
// the registers xv6 will save and restore
// to stop and subsequently restart a process
struct context
{
    int eip;
    int esp;
    int ebx;
    int ecx;
    int edx;
    int esi;
    int edi;
    int ebp;
};
// the different states a process can be in
// 可以看到实际操作系统对于进程状态的定义远不止上面介绍的3种
enum proc_state
{
    UNUSED,
    EMBRYO,
    SLEEPING,
    RUNNABLE,
    RUNNING,
    ZOMBIE
};
// the information xv6 tracks about each process
// including its register context and state
struct proc
{
    char *mem;    // Start of process memory
    uint sz;      // Size of process memory
    char *kstack; // Bottom of kernel stack
    // for this process
    enum proc_state state;      // Process state
    int pid;                    // Process ID
    struct proc *parent;        // Parent process
    void *chan;                 // If non-zero, sleeping on chan
    int killed;                 // If non-zero, have been killed
    struct file *ofile[NOFILE]; // Open files
    struct inode *cwd;          // Current directory
    struct context context;     // Switch here to run process
    struct trapframe *tf;       // Trap frame for the
                                // current interrupt
};
```

该数据结构展示了 OS 需要跟踪 xv6[^1] 内核中每个进程的信息类型[CK+08]。“真正的”操作系统中存在类似的进程结构，如 Linux、macOS X 或 Windows。

[^1]: xv6是在ANSI C中针对多处理器x86系统的Unix第六版的现代重新实现。它足够简单，是上手操作系统的一个不错选择

对于停止的进程，寄存器上下文将保存其寄存器的内容。

除了`运行`、`就绪`和`阻塞`之外，还有其他一些进程可以处于的状态：

- **初始（initial）状态**
    有时候系统会有一个初始（initial）状态，表示进程在创建时处于的状态。

- **最终（final）状态**

    另外，一个进程可以处于已退出但尚未清理的最终（final）状态（在基于 UNIX 的系统中，这称为`僵尸状态`）。这个最终状态非常有用，因为它允许其他进程（通常是创建进程的父进程）检查进程的`返回代码`，并查看刚刚完成的进程`是否成功执行`（通常，在基于 UNIX 的系统中，程序成功完成任务时返回零，否则返回非零）。完成后，父进程将进行最后一次调用（例如，wait()），以等待子进程的完成，并告诉操作系统它可以清理这个正在结束的进程的所有相关数据结构

## 作业

关于作业，本文只摘取部分我认为比较重要的部分

6. 另一个重要的行为是 I/O 完成时要做什么。**利用-I IO_RUN_LATER，当 I/O 完成时，I/O完成的进程不会被优先调度，而是按照排队顺序来**。相反，当时运行的进程一直运行。当你运行这个进程组合时会发生什么？（./process-run.py -l 3:0,5:100,5:100,5:100 -S SWITCH_ON_IO -I IO_RUN_LATER -c -p）系统资源是否被有效利用？

```shell
    $ ./process-run.py -l 3:0,5:100,5:100,5:100 -S SWITCH_ON_IO -I IO_RUN_LATER -c -p
Time        PID: 0        PID: 1        PID: 2        PID: 3           CPU           IOs
  1         RUN:io         READY         READY         READY             1
  2        WAITING       RUN:cpu         READY         READY             1             1
  3        WAITING       RUN:cpu         READY         READY             1             1
  4        WAITING       RUN:cpu         READY         READY             1             1
  5        WAITING       RUN:cpu         READY         READY             1             1
  6        WAITING       RUN:cpu         READY         READY             1             1
  7*         READY          DONE       RUN:cpu         READY             1
  8          READY          DONE       RUN:cpu         READY             1
  9          READY          DONE       RUN:cpu         READY             1
 10          READY          DONE       RUN:cpu         READY             1
 11          READY          DONE       RUN:cpu         READY             1
 12          READY          DONE          DONE       RUN:cpu             1
 13          READY          DONE          DONE       RUN:cpu             1
 14          READY          DONE          DONE       RUN:cpu             1
 15          READY          DONE          DONE       RUN:cpu             1
 16          READY          DONE          DONE       RUN:cpu             1
 17    RUN:io_done          DONE          DONE          DONE             1
 18         RUN:io          DONE          DONE          DONE             1
 19        WAITING          DONE          DONE          DONE                           1
 20        WAITING          DONE          DONE          DONE                           1
 21        WAITING          DONE          DONE          DONE                           1
 22        WAITING          DONE          DONE          DONE                           1
 23        WAITING          DONE          DONE          DONE                           1
 24*   RUN:io_done          DONE          DONE          DONE             1
 25         RUN:io          DONE          DONE          DONE             1
 26        WAITING          DONE          DONE          DONE                           1
 27        WAITING          DONE          DONE          DONE                           1
 28        WAITING          DONE          DONE          DONE                           1
 29        WAITING          DONE          DONE          DONE                           1
 30        WAITING          DONE          DONE          DONE                           1
 31*   RUN:io_done          DONE          DONE          DONE             1

Stats: Total Time 31
Stats: CPU Busy 21 (67.74%)
Stats: IO Busy  15 (48.39%)
```

在本题中，进程0首先进入IO，此时由于`-S SWITCH_ON_IO`参数，进程0进入阻塞状态，cpu被切换到运行进程1，当进程0的IO完成后，进程1继续执行，直到完成。也就是IO完成事件不会被立即处理，由于进程0的IO动作较为频繁，会使它长时间处于IO完成等待状态，导致后续的IO操作时cpu已经无事可做了，在本例条件下降低了效率

7. 现在运行相同的进程，但使用-I IO_RUN_IMMEDIATE 设置，该设置立即运行发出I/O 的进程。这种行为有何不同？为什么运行一个刚刚完成 I/O 的进程会是一个好主意？

```shell
$ ./process-run.py -l 3:0,5:100,5:100,5:100 -S SWITCH_ON_IO -I IO_RUN_IMMEDIATE -c -p
Time        PID: 0        PID: 1        PID: 2        PID: 3           CPU           IOs
  1         RUN:io         READY         READY         READY             1
  2        WAITING       RUN:cpu         READY         READY             1             1
  3        WAITING       RUN:cpu         READY         READY             1             1
  4        WAITING       RUN:cpu         READY         READY             1             1
  5        WAITING       RUN:cpu         READY         READY             1             1
  6        WAITING       RUN:cpu         READY         READY             1             1
  7*   RUN:io_done          DONE         READY         READY             1
  8         RUN:io          DONE         READY         READY             1
  9        WAITING          DONE       RUN:cpu         READY             1             1
 10        WAITING          DONE       RUN:cpu         READY             1             1
 11        WAITING          DONE       RUN:cpu         READY             1             1
 12        WAITING          DONE       RUN:cpu         READY             1             1
 13        WAITING          DONE       RUN:cpu         READY             1             1
 14*   RUN:io_done          DONE          DONE         READY             1
 15         RUN:io          DONE          DONE         READY             1
 16        WAITING          DONE          DONE       RUN:cpu             1             1
 17        WAITING          DONE          DONE       RUN:cpu             1             1
 18        WAITING          DONE          DONE       RUN:cpu             1             1
 19        WAITING          DONE          DONE       RUN:cpu             1             1
 20        WAITING          DONE          DONE       RUN:cpu             1             1
 21*   RUN:io_done          DONE          DONE          DONE             1

Stats: Total Time 21
Stats: CPU Busy 21 (100.00%)
Stats: IO Busy  15 (71.43%)
```

在本例中，由于使用了`-I IO_RUN_IMMEDIATE`设置，IO完成事件被立即处理，此时进程0继续运行，对于IO操作较为频繁的进程0来说这是一件好事

思考：立即处理阻塞完成的进程是否是一个好主意?
