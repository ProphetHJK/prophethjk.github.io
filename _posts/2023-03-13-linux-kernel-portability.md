---
title: "Linux内核学习笔记之可移植性"
author: Jinkai
date: 2023-03-08 16:00:00 +0800
published: true
categories: [学习笔记]
tags: [kernel, Linux]
---

## 体系结构

与体系结构相关的代码都存放在`arch/architecture/`目录中，architecture 是 Linux 支持的体系结构的简称。比如说，Intel x86 体系结构对应的简称是 x86

## 字长和数据类型

能够由机器一次完成处理的数据称为**字**。

**处理器通用寄存器**(general-purposeregisters，GPR)的大小和它的字长是相同的。一般来说，对于一个体系结构，它各个部件的宽度(比如说内存总线)最少要和它的字长一样大。

C 语言定义的 long 类型总是对等于机器的字长，而 int 类型有时会比字长小。

对于支持的每一种体系结构，Linux 都要将`<asm/types.h>`中的 `BITS_PER_LONG` 定义为
C long 类型的长度，也就是系统的字长。

Linux 规定的准则：

- ANSI C 标准规定，一个 char 的长度一定是 1 字节。
- 尽管没有规定 int 类型的长度是 32 位，但在 Linux 当前所有支持的体系结构中，它都是 32 位的。
- short 类型也类似，在当前所有支持的体系结构中，虽然没有明文规定，但是它都是 16 位的。
- 绝不应该假定指针和 long 的长度，在 Linux 当前支持的体系结构中，它们可以在 32 位和 64 位中变化。也不要假设指针和 int 长度相等
- 由于不同的体系结构 long 的长度不同，决不应该假设 sizeof(int)=sizeof(long)。

### 不透明类型

不透明数据类型隐藏了它们的内部格式或结构。

- 不要假设该类型的长度。这些类型在某些系统中可能是 32 位，而在其他系统中又可能是 64 位。并且，内核开发者可以任意修改这些类型的大小。
- 不要将该类型转化回其对应的 C 标准类型使用。
- 成为一个大小不可知论者。编程时要保证在该类型实际存储空间和格式发生变化时代码不受影响。

### 长度明确的类型

内核在`<asm/typs.h>`中定义了这些长度明确的类型，比如 `s8` 表示**有符号 8 位长类型**，`u64` 表示**无符号 64 位长类型**。

这些类型只能在内核内使用，不可以在用户空间出现，这是为了保护命名空间，让程序员在代码中看到这种类型就知道这是内核空间的变量。

内核提供带双下划线的版本，可以在用户空间使用，如 `__u32`

### char 型的符号问题

C 标准表示 char 类型可以带符号也可以不带符号，由具体的编译器、处理器或由它们两者共同决定到底 char 是带符号还是不带符号。

最好还是明确声明 `signed char` 还是 `unsigned char`

## 数据对齐

如果一个变量的**内存地址**正好是它长度的**整数倍**，它就称作是**自然对齐**的。比如 32 位的 int 类型，其内存地址能被 4 整除就是自然对齐；64 位的 long 类型内存地址能被 8 整除就是自然对齐

### 非标准类型的对齐

- **数组**：只要第一个元素对齐，后面的元素自然而然的也就对齐了
- **union 联合体**：联合体内最大长度的成员能对齐
- **结构体**：每个元素都要正确对齐

### 结构体填补

```c
struct animal_struct
{
    char dog;           // 1 字节
    unsigned long cat;  // 4
    unsigned short pig; // 2
    char fox;           // 1
}
```

在大部分 32 位系统上，对于任何一个这样的结构体，`sizeof(animal_struct)`都会返回 12。C 编译器自动进行填补以保证自然对齐:

```c
struct animal _struct
{
    char dog;           // 1
    u8 __pad0[3];       // 3(填充)
    // 为了cat能按4字节对齐，必须加上3字节的pad0
    unsigned long cat;  // 4
    unsigned short pig; // 2
    char fox;           // 1
    // 为了整个结构体能按4字节对齐，加上了1字节的pad1
    // 这样由该结构体构成的数组也能自然对齐
    u8 __pad1;          // 1(填充)
}
```

通常你可以通过重新排列结构体中的对象来避免填充。这样既可以得到一个较小的结构体，又能保证无须填补它也是自然对齐的:

```c
struct animal_struct
{
    unsigned long cat;  // 4
    unsigned short pig; // 2
    char dog;           // 1
    char fox;           // 1
}
```

因为内核中会用到结构体内的成员**顺序**来实现一些特性，如为提高缓存命中率优化的成员排布、面向对象的多态实现时基类放在开头、数组扩展时成员必须是最后一个等。

同时 ANSI C 明确规定**不允许**编译器改变结构体内成员对象的次序，如果需要对齐，编译器一般使用填充的方式。这也说明成员次序的重要性。

所以绝对**不要随便修改**已经定义好的结构体内的成员顺序！

## 字节序

- 大端字节序：高位低地址，低位高地址，符合人类书写习惯

  1234，对应 00000001(LSB) 00000010 00000011 00000100(MSB)

- 小端字节序：低位低地址，高位高地址

对于 Linux 支持的每一种体系结构，相应的内核都会根据机器使用的字节顺序在它的`<asm/byteorder.h>`中定义 `__BIG_ENDIAN` 或`__LITTLE_ENDIAN` 中的一个。

这个头文件还从`include/linux/byteorder/`中包含了一组宏命令用于完成字节顺序之间的相互转换。最常用的宏命令有:

```c
cpu_to_be32(u32); /*把cpu字节顺序转换为高位优先字节顺序*/
cpu_to_le32(u32); /*把cpu字节顺序转换为低位优先字节顺序*/
be32_to_cpu(u32); /*把高位优先字节顺序转换为cpu字节顺序*/
le32_to_cpu(u32); /*把低位优先字节顺序转换为cpu字节顺序*/
```

## 时间

不同架构的默认 HZ 并不同，注意 jiffies 的使用。

## 页长度

`PAGE_SIZE` 以字节数来表示页长度，`PAGE_SHIFT` 表示地址中页号偏移。

如 4KB 的页，PAGE_SHIFT 就为 12，表示内存地址右移 12 位得到页号

各体系结构相关的宏都定义于`<asm/page.h>`中。

## 处理器排序

有些处理器严格限制指令排序，代码指定的所有装载或存储指令都不能被重新排序;而另外一些体系结构对排序要求则很弱，可以自行排序指令序列。

通过`rmb()`，`mb()`等屏障函数能实现确定的指令顺序。

## SMP、内核抢占、高端内存

- 假设你的代码会在 SMP 系统上运行，要正确地选择和使用**锁**。
- 假设你的代码会在支持内核抢占的情况下运行，要正确地选择和使用**锁和内核抢占**语句。
- 假设你的代码会运行在使用高端内存(非永久映射内存)的系统上，必要时使用**kmap()**。

## 参考

- [Linux 内核设计与实现（第三版）第十九章](https://www.amazon.com/Linux-Kernel-Development-Robert-Love/dp/0672329468/ref=as_li_ss_tl?ie=UTF8&tag=roblov-20)
- [Robert Love](https://rlove.org/)
