---
title: "《Operating Systems: Three Easy Pieces》学习笔记(四) 机制：受限直接执行"
author: Jinkai
date: 2021-03-16 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

> 参考：
>
> - [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/06.pdf)

*本文中文版翻译质量堪忧，有不少名词翻译不知所云，建议对照英文版阅读*

## 前言

在构建这样的虚拟化机制时存在一些挑战。

- 第一个是性能：如何在不增加系统开销的情况下实现虚拟化？
- 第二个是控制权：如何有效地运行进程，同时保留对 CPU 的控制？

> 控制权对于操作系统尤为重要，因为操作系统负责资源管理。如果没有控制权，一个进程可以简单地无限制运行并接管机器，或访问没有权限的信息

## 直接运行协议（无限制）

`直接执行`指的是直接在 CPU 上运行程序，该操作没有任何限制。

| 操作系统                                                                                  | 程序                                 |
| :---------------------------------------------------------------------------------------- | :----------------------------------- |
| 在进程列表上创建条目<br>为程序分配内存<br>将程序加载到内存中<br>根据 argc/argv 设置程序栈 |                                      |
| 清除寄存器<br>执行 call main() 方法                                                       |                                      |
|                                                                                           | 执行 main()<br>从 main 中执行 return |
| 释放进程的内存将进程<br>从进程列表中清除                                                  |                                      |

直接运行带来两个问题：

- `受限制的操作`：操作系统怎么能确保程序不做任何我们不希望它做的事，同时仍然高效地运行它
- `进程间切换`： 操作系统如何让一个进程停下来并切换到另一个进程，从而实现虚拟化 CPU 所需的时分共享

## 问题 1：受限制的操作

> **提示：采用受保护的控制权转移**
>
> 硬件通过提供不同的执行模式来协助操作系统。在`用户模式（user mode）`下，应用程序不能完全访问硬件资源。在`内核模式（kernel mode）`下，操作系统可以访问机器的全部资源。还提供了陷入（trap）内核和从陷阱返回（return-from-trap）到用户模式程序的特别说明，以及一些指令，让操作系统告诉硬件陷阱表（trap table）在内存中的位置。

我们采用的方法是引入新的处理器模式:

### 用户模式（user mode）

在用户模式下运行的代码会`受到限制`。例如，在用户模式下运行时，进程不能发出 I/O 请求。这样做会导致处理器引发异常，操作系统可能会终止进程。

### 内核模式（kernel mode）

操作系统（或内核）就以这种模式运行。在此模式下，运行的代码可以做它喜欢的事，包括`特权操作`，如发出 I/O 请求和执行所有类型的受限指令。

### 系统调用

`系统调用`允许内核小心地向用户程序暴露某些`关键功能`，例如**访问文件系统、创建和销毁进程、与其他进程通信，以及分配更多内存**。大多数操作系统提供几百个调用（详见 [POSIX 标准](https://zh.wikipedia.org/wiki/%E5%8F%AF%E7%A7%BB%E6%A4%8D%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E6%8E%A5%E5%8F%A3)）。早期的 UNIX 系统公开了更简洁的子集，大约 20 个调用。

如果用户希望执行某种特权操作（如从磁盘读取），可以借助硬件提供的`系统调用`功能。

要执行系统调用，程序必须执行特殊的`陷阱`（trap）指令。该指令同时跳入内核并将特权级别提升到`内核模式`。一旦进入内核，系统就可以执行任何需要的`特权操作`（如果允许），从而为调用进程执行所需的工作。完成后，操作系统调用一个特殊的`从陷阱返回`（return-from-trap）指令，如你期望的那样，**该指令返回到发起调用的用户程序中，同时将特权级别降低，回到用户模式。**

执行陷阱时，硬件需要小心，因为它必须确保存储足够的调用者寄存器，以便在操作系统发出从陷阱返回指令时能够正确返回。例如，在 x86 上，处理器会将程序计数器、标志和其他一些寄存器推送到每个进程的内核栈（kernel stack）上。从返回陷阱将从栈弹出这些值，并恢复执行用户模式程序（有关详细信息，请参阅英特尔系统手册）。其他硬件系统使用不同的约定，但基本概念在各个平台上是相似的。

> **补充：为什么系统调用看起来像过程调用**
>
> 你可能想知道，为什么对`系统调用`的调用（如 open()或 read()）看起来完全`就像` C 中的典型`过程调用`。也就是说，如果它看起来像一个过程调用，系统如何知道这是一个系统调用，并做所有正确的事情？原因很简单：**它是一个过程调用，但隐藏在过程调用内部的是著名的陷阱指令**。更具体地说，当你调用 open()（举个例子）时，你正在执行对 C 库的过程调用。其中，无论是对于 open()还是提供的其他系统调用，库都使用与内核一致的调用约定来将参数放在众所周知的位置（例如，在栈中或特定的寄存器中），将系统调用号也放入一个众所周知的位置（同样，放在栈或寄存器中），然后执行上述的陷阱指令。库中陷阱之后的代码准备好返回值，并将控制权返回给发出系统调用的程序。因此，**C 库中进行系统调用的部分是用汇编手工编码的**，因为它们需要仔细遵循约定，以便正确处理参数和返回值，以及执行硬件特定的陷阱指令。现在你知道为什么你自己不必写汇编代码来陷入操作系统了，**因为有人已经为你写了这些汇编**。

### 陷阱表（trap table）

内核通过在启动时设置`陷阱表`（trap table）来实现陷阱地址的初始化。

当机器启动时，系统在特权（内核）模式下执行，因此可以根据需要自由配置机器硬件。操作系统做的第一件事，就是**告诉硬件在发生某些异常事件时要运行哪些代码**。例如，当发生硬盘中断，发生键盘中断或程序进行系统调用时，应该运行哪些代码？操作系统通常通过某种特殊的指令，通知硬件这些陷阱处理程序的位置。一旦硬件被通知，它就会**记住这些处理程序的位置，直到下一次重新启动机器**，并且硬件知道在**发生系统调用和其他异常事件时要做什么**（即跳转到哪段代码）。

### 受限直接运行协议

LDE 协议有两个阶段:

**第一阶段：**

| 操作系统@`启动`（内核模式） | 硬件                       |     |
| :-------------------------- | :------------------------- | :-- |
| 初始化陷阱表                |                            |     |
|                             | 记住系统调用处理程序的地址 |     |

第一个阶段（在系统引导时），内核初始化陷阱表，并且 CPU 记住它的位置以供随后使用。内核通过特权指令来执行此操作（所有特权指令均以粗体突出显示）。

**第二阶段：**

| 操作系统@`运行`（内核模式）                                                                                                         | 硬件                                                           | 程序（应用模式）                                 |
| :---------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------- | :----------------------------------------------- |
| 在进程列表上创建条目<br>为程序分配内存<br>将程序加载到内存中<br>根据 argv 设置程序栈<br>用寄存器/程序计数器填充内核栈<br>从陷阱返回 |                                                                |                                                  |
|                                                                                                                                     | 从内核栈恢复寄存器<br>转向用户模式<br>跳到 main                |                                                  |
|                                                                                                                                     |                                                                | 运行 main <br>……<br>调用系统调用<br>陷入操作系统 |
|                                                                                                                                     | 将寄存器保存到内核栈<br>转向内核模式<br>跳到陷阱处理程序       |                                                  |
| 处理陷阱<br>做系统调用的工作<br>从陷阱返回                                                                                          |                                                                |                                                  |
|                                                                                                                                     | 从内核栈恢复寄存器<br>转向用户模式<br>跳到陷阱之后的程序计数器 |                                                  |
|                                                                                                                                     |                                                                | ……从 main 返回<br>陷入（通过 exit()）            |
| 释放进程的内存将进程<br>从进程列表中清除                                                                                            |                                                                |                                                  |

第二个阶段（运行进程时），在使用从陷阱返回指令开始执行进程之前，内核设置了一些内容（例如，在进程列表中分配一个节点，分配内存）。这会将 CPU 切换到用户模式并开始运行该进程。当进程希望发出系统调用时，它会重新陷入操作系统，然后再次通过从陷阱返回，将控制权还给进程。该进程然后完成它的工作，并从 main()返回。这通常会返回到一些存根代码，它将正确退出该程序（例如，通过调用 exit()系统调用，这将陷入 OS 中）。此时，OS 清理干净，任务完成了。

## 问题 2：在进程之间切换

> **关键问题：如何重获 CPU 的控制权**
>
> 操作系统如何重新获得 CPU 的控制权（regain control），以便它可以在进程之间切换？

### 协作方式：等待系统调用

**在`协作调度系统`中，OS 通过`等待系统调用`，或某种`非法操作发生`，从而重新获得 CPU 的`控制权`**。

过去某些系统采用的一种方式（例如，早期版本的 Macintosh 操作系统或旧的 Xerox Alto 系统）称为`协作`（cooperative）方式。在这种风格下，**操作系统相信系统的进程会合理运行**。运行时间过长的进程被假定会`定期放弃 CPU`，以便操作系统可以决定运行其他任务。

大多数进程通过进行`系统调用`，将 CPU 的控制权转移给操作系统，例如打开文件并随后读取文件，或者向另一台机器发送消息或创建新进程

如果应用程序执行了某些`非法操作`，也会将控制转移给操作系统。例如，如果应用程序以 0 为除数，或者尝试访问应该无法访问的内存，就会陷入（trap）操作系统。操作系统将再次控制 CPU（并可能终止违规进程）。

### 非协作方式：时钟中断

`时钟中断`（timer interrupt）。时钟设备可以编程为**每隔几毫秒产生一次中断**。产生中断时，当前正在运行的进程停止，操作系统中预先配置的`中断处理程序`（interrupt handler）会运行。此时，操作系统重新获得 CPU 的控制权，因此可以做它想做的事：停止当前进程，并启动另一个进程。

请注意，`硬件`在`发生中断`时有一定的责任，尤其是在中断发生时，要为正在运行的程序保存足够的状态，以便随后从陷阱返回指令能够正确恢复正在运行的程序。该操作可以视为隐式的操作，与显式的系统调用很相似。

### 保存和恢复上下文

当操作系统通过上述两种方式获取控制权后，就可以决定是否切换进程，这个决定是由调度程序（scheduler）做出

当操作系统决定切换进程时，需要首先进行`上下文切换`（context switch），就是为当前正在执行的进程`保存一些寄存器的值`（例如，到它的内核栈），并为即将执行的进程`恢复一些寄存器的值`（从它的内核栈）。这样一来，操作系统就可以确保最后执行从陷阱返回指令时，不是返回到之前运行的进程，而是继续执行另一个进程。

> 上下文切换并不仅仅保存和恢复寄存器，还包含了其他操作，如页表的切换等，在后续章节会提到

### 受限直接执行协议（时钟中断）

**第一阶段：**

| 操作系统@`启动`（内核模式） | 硬件                                                   |
| :-------------------------- | :----------------------------------------------------- |
| 初始化陷阱表                |                                                        |
|                             | 记住以下地址：<br> -系统调用处理程序<br> -时钟处理程序 |
| 启动中断时钟                |                                                        |
|                             | 启动时钟<br>每隔 x ms 中断 CPU                         |

**第二阶段：**

| 操作系统@`运行`（内核模式）                                                                                                                                 | 硬件                                                                               | 程序（应用模式） |
| :---------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------- | :--------------- |
|                                                                                                                                                             |                                                                                    | 进程 A……         |
|                                                                                                                                                             | 时钟中断<br>将用户寄存器（A）保存到内核栈（A）<br>转向内核模式<br>跳到陷阱处理程序 |                  |
| 处理陷阱<br>调用 switch()例程<br> -保存内核寄存器（A）->进程结构（A）<br> -恢复内核寄存器（B）<-进程结构（B）<br>-切换到内核栈（B）<br>从陷阱返回（进入 B） |                                                                                    |                  |
|                                                                                                                                                             | 恢复用户寄存器（B）<-内核栈（B）<br>转向用户模式<br>跳到 B 的程序计数器            |                  |
|                                                                                                                                                             |                                                                                    | 进程 B……         |

该表展示了整个过程的时间线。在这个例子中，进程 A 正在运行，然后`被中断时钟中断`。**硬件保存它的用户寄存器（到内核栈中），并进入内核（切换到内核模式）**。在时钟中断处理程序中，操作系统决定从正在运行的进程 A 切换到进程 B。此时，它调用 switch()例程，该例程仔细保存当前内核寄存器的值（保存到 A 的进程结构(process structure)），恢复内核寄存器进程 B（从它的进程结构(process structure)），然后`切换上下文`（switch context），具体来说是**通过改变栈指针来使用 B 的内核栈（而不是 A 的）**。最后，操作系统从陷阱返回，恢复 B 的用户寄存器并开始运行它。

请注意，在此协议中，有`两种类型`的寄存器保存/恢复:

- 第一种是发生`时钟中断`的时候。在这种情况下，运行进程的`用户寄存器`由`硬件`隐式保存，使用该进程的`内核栈`。

        原文：the user registers of the running process are implicitly saved by the hardware, using the kernel stack of that process

  根据英文原文，此处确实是保存到了内核栈中

  > **扩展：内核栈与用户栈**
  >
  > 内核在创建进程时，会同时创建 task_struct 和进程相应堆栈。每个进程都会有两个堆栈，一个用户栈，存在于用户空间，一个内核栈，存在于内核空间。当进程在用户空间运行时，`CPU 堆栈寄存器(SP)`的内容是`用户堆栈地址`，使用用户栈。当进程在内核空间时，`CPU 堆栈寄存器(SP)`的内容是`内核栈地址`，使用的是内核栈。

- 第二种是当`操作系统决定`从 A 切换到 B。在这种情况下，A 的`用户寄存器`先被`硬件`保存到`内核栈(A)`，之后进入`内核态`，此时，**用户寄存器切换成内核寄存器，存放系统和进程 A 相关的值**，操作系统接管后，调用 `switch()`通过`软件`方式将`内核寄存器`中的值保存到 A 的`进程结构`，之后从 B 的`进程结构`恢复值到`内核寄存器`，并切换到进程 B 的`内核栈(B)`，然后从陷阱返回，从`内核栈(B)`恢复 B 的`用户寄存器`，运行 B 进程

        原文：the kernel registers are explicitly saved by the software (i.e., the OS), but this time into memory in the process structure of the process. The latter action moves the system from running as if it just trapped into the kernel from A to as if it just trapped into the kernel from B.

  为了理解这个逻辑，首先把切换这步去掉，假设 A 不切换成 B，即 A 的`用户寄存器`先被`硬件`保存到`内核栈(A)`，此时，包括`PC寄存器`（需要执行的下一条指令地址）在内的寄存器都被压入内核栈(A)，从陷阱返回后，从`内核栈(A)`恢复 A 的用户寄存器，将包括 PC 寄存器在内的寄存器恢复，此时继续执行 PC 寄存器保存的下一条指令。然后加上`switch()`操作，保存/恢复内核寄存器到对应的进程结构中。

  TODO:此处后面再用实际操作系统的例子补充

### 分享：在 µC/OS-III 中遇到的上下文切换问题

在实际项目中使用 µC/OS-III 系统时遇到过一个问题，某个进程的值在没有任何修改的情况下变为了异常值。

**问题说明：**

```c
wlm_do()->the_wlm_routine[the_wlm.status].func()->wlm_chk_baudrate()->
atcmd(serfd(), "AT\r", E_OK, 500, NULL, 0)->memset(prbuf, 0, rbuf_len)
```

rbuf_len 的值变为了 536890260，显然是个异常值。

**问题分析：**

通过分析后排除了程序本身的问题，打算从操作系统角度进行问题。

在关闭 GCC 优化的情况下，该值正常，也就是说可能和 GCC 的优化有关。GCC 优化会将部分常用的变量保持到寄存器中，从而提高读写速度。

通过内存和寄存器跟踪工具，定位了该变量确实被保存在了寄存器中，也就是说寄存器出现了问题，和寄存器操作相关的就极有可能是上下文切换操作。

通过跟踪发现寄存器的值在进程切换后出现了异常，导致该变量的值改变

查看上下文切换实现源码：

```armasm
OS_CPU_PendSVHandler:
    CPSID   I                                                   @ Prevent interruption during context switch
    MRS     R0, PSP                                             @ PSP is process stack pointer

    CMP     R0, #0
    BEQ     OS_CPU_PendSVHandler_nosave                         @ equivalent code to CBZ from M3 arch to M0 arch
                                                                @ Except that it does not change the condition code flags

    SUBS    R0, R0, #0x10                                       @ Adjust stack pointer to where memory needs to be stored to avoid overwriting
    STM     R0!, {R4-R7}                                        @ Stores 4 4-byte registers, default increments SP after each storing
    SUBS    R0, R0, #0x10                                       @ STM does not automatically call back the SP to initial location so we must do this manually

    LDR     R1, =OSTCBCur                                       @ OSTCBCur->OSTCBStkPtr = SP;
    LDR     R1, [R1]
    STR     R0, [R1]                                            @ R0 is SP of process being switched out
                                                                @ At this point, entire context of process has been saved
```

此处仅保存了 r4-r7 寄存器，少了对 r8-r11 寄存器的保存

查看官网更新说明[µC/OS-III v3.06.00 Changelog](https://www.micrium.com/ucos-iii-v3-06-00/)，有如下信息：

![changelog](/assets/img/2021-03-16-operating-systems-4/changelog.png)

bug 修复后的上下文切换源码如下：

```armasm
PendSV_Handler:
    CPSID   I                                                   @ Prevent interruption during context switch
    MRS     R0, PSP                                             @ PSP is process stack pointer

    CMP     R0, #0
    BEQ     OS_CPU_PendSVHandler_nosave                         @ equivalent code to CBZ from M3 arch to M0 arch
                                                                @ Except that it does not change the condition code flags

    SUBS    R0, R0, #0x24                                       @ Adjust SP to make space for Low, High & LR registers
    LDR     R1, =OSTCBCur                                       @ OSTCBCur->OSTCBStkPtr = SP;
    LDR     R1, [R1]
    STR     R0, [R1]                                            @ R0 is SP of process being switched out

    STMIA   R0!, {R4-R7}                                        @ Store R4-R7(Low Registers) on process stack
    MOV     R4, R8                                              @ Move R8-R11 values to R4-R7 registers.
    MOV     R5, R9
    MOV     R6, R10
    MOV     R7, R11
    STMIA   R0!, {R4-R7}                                        @ Store R8-R11(High Registers) on process stack
    MOV     R3, R14                                             @ R3 is LR of process being switched out
    STMIA   R0!, {R3}                                           @ Store LR (EXC_RETURN) on process stack.

                                                                @ At this point, entire context of process has been saved
```

此处保存了 r4-r11 寄存器

至此，问题原因已明确

**问题原因：**

代码优化时将 rbuf_len 保存在了寄存器 r8 上，在进行上下文切换时，r8 寄存器没有被保存，导致 r8 寄存器的值被其他进程修改，切换回本进程后，r8 的值也无法恢复。

## 思考：并发对中断的影响

处理一个中断时发生另一个中断，会发生什么？

一种方法是，在中断处理期间`禁止中断`（disable interrupt）。这样做可以确保在处理一个中断时，不会将其他中断交给 CPU。当然，操作系统这样做必须小心。禁用中断时间过长可能导致丢失中断，这（在技术上）是不好的。

操作系统还开发了许多复杂的`加锁`（locking）方案，以保护对内部数据结构的并发访问。这使得多个活动可以同时在内核中进行，特别适用于多处理器，在下一部分关于并发的章节中将会看到

## 思考：上下文切换的消耗

你可能有一个很自然的问题：上下文切换需要多长时间？甚至系统调用要多长时间？如果感到好奇，有一种称为 `lmbench`的工具，可以准确衡量这些事情，并提供其他一些可能相关的性能指标。随着时间的推移，结果有了很大的提高，大致跟上了处理器的性能提高。例如，1996 年在 200-MHz P6 CPU 上运行 Linux 1.3.37，系统调用花费了大约 4μs，上下文切换时间大约为 6μs。现代系统的性能几乎可以提高一个数量级，在具有 2 GHz 或 3 GHz 处理器的系统上的性能可以达到亚微秒级。应该注意的是，并非所有的操作系统操作都会跟踪 CPU 的性能。正如 Ousterhout 所说的，许多操作系统操作都是`内存密集型`的，而随着时间的推移，内存带宽并没有像处理器速度那样显著提高。因此，根据你的工作负载，购买最新、性能好的处理器可能不会像你希望的那样加速操作系统。