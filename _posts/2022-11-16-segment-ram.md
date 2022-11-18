---
title: "一文看懂内存分段"
author: Jinkai
date: 2022-11-16 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [C语言, 内存]
---

## 前言

`分段`见[《Operating Systems: Three Easy Pieces》学习笔记(十二) 分段](/posts/operating-systems-12/)

本文是对上述文章的补充

## ROM 和 RAM

### ROM (Read Only Memory)程序存储器

`ROM` 全称 `Read Only Memory`，顾名思义，它是一种`只能读出`事先所存的数据的固态半导体存储器。ROM 中所存数据稳定，一旦存储数据就再也无法将之改变或者删除，断电后所存数据也不会消失。其结构简单，因而常用于存储各种固化程序和数据。

在单片机中用来存储`程序数据`及`常量数据`或`变量数据`，凡是 c 文件及 h 文件中所有`代码`、全局变量（仅声明，未分配空间）、局部变量（仅声明，未分配空间）、‘const’限定符定义的`常量数据`、startup.asm 文件中的代码（类似 ARM 中的 bootloader 或者 X86 中的 BIOS，一些低端的单片机是没有这个的）通通都存储在 ROM 中。

为了便于使用和大批量生产，进一步发展出了`可编程只读存储器（PROM）`、`EPROM(Electrically Programmable Read-Only-Memory电可编程序只读存储器)`。EPROM 需要用紫外线长时间照射才能擦除，使用很不方便。1980s 又出现了`EEPROM(电可擦可编程 只读存储器Electrically Erasable Programmable Read - Only Memory)`，它克服了 EPROM 的不足，但是集成度不高、价格较贵。于是又发展出了一种新型的存储单元结构同 `EPROM` 类似的快闪存储器（`FLASH MEMORY`）。FLASH 集成度高、功耗低、体积小，又能在线快速擦除，因而获得了快速发展。

#### FLASH 存储器

`Flash` 存储器（Flash Memory）又称闪存，快闪。Flash Memory 属于 EEPROM（但一般 EEPROM 这个词专门表示可以按字节擦除的传统式 EEPROM）。它结合了 ROM 和 RAM 的长处。不仅具备电子可擦除可编辑（EEPROM）的性能，还不会断电丢失数据同时可以快速读取数据。它于 EEPROM 的最大区别是，`FLASH` 按`扇区（block）操作`，而 `EEPROM` 按照`字节操作`。FLASH 的电路结构较简单，同样容量占芯片面积较小，`成本`自然比 EEPROM 低，因此适合用于做程序存储器。

### RAM (Random Access Memory)随机访问存储器

`RAM` 又称`随机存取存储器`，存储单元的内容可按照需要随机取出或存入，且存取的速度与存储单元的位置无关。这种存储器在断电时，将丢失其存储内容，所以主要用于存储短时间使用的程序。

它主要用来存储程序中用到的变量。凡是整个程序中，所用到的需要被改写的量（包括全局变量、局部变量、堆栈段等），都存储在 RAM 中。

### 实例

efm32-slstk3401a(ARM cortex-m4) 的 256KB ROM 和 32KB RAM 地址分配

```s
Memory Configuration

Name             Origin             Length             Attributes
ROM              0x00000000         0x00040000         xr
RAM              0x20000000         0x00008000         xrw
*default*        0x00000000         0xffffffff
```

## 内存分段

在嵌入式领域，一般将内存分为代码(TEXT)段、数据(DATA)段、 BSS 段、堆(heap)和栈(stack)

### TEXT 段

`代码段`（code segment/text segment）通常是指用来存放程序`执行代码`的一块内存区域。

这部分区域的大小在程序运行前就已经确定，并且内存区域通常属于只读(某些架构也允许代码段为可写，即允许修改程序)。

在代码段中，也有可能包含一些只读的`常数变量`，而不是放在 DATA 段，例如字符串常量等。

### DATA 段

`数据段`（data segment）通常是指用来存放程序中`已初始化的全局变量(静态变量)`的一块内存区域。

数据段属于静态内存分配。区别与栈和堆的动态分配

### BSS 段

`bss 段`（bss segment）通常是指用来存放程序中`未初始化的全局变量(静态变量)`(部分编译器会把`已初始化为 0` 的全局（静态）变量优化到 bss 段)的一块内存区域。

bss 是英文 Block Started by Symbol 的简称。

bss 段属于静态内存分配。区别与栈和堆的动态分配

#### BSS 段与 DATA 段区别

一般在初始化时 bss 段部分将会`清零`。bss 段属于静态内存分配，即程序`一开始`就将其清零了，也就是说未初始化的默认初始化为 0。

比如，在 C 语言之类的程序编译完成之后，已初始化的全局变量保存在 .data 段中，未初始化的全局变量保存在 .bss 段中。

`text 和 data 段`都在`可执行文件`中（在嵌入式系统里一般是固化在`镜像文件`中），由系统从可执行文件中加载

重点：而 `bss 段`不在可执行文件中，由系统初始化。因为这些数据没有也不需要默认值，这些数据只要在 text 段有个标记表明该数据的长度而无需分配空间和保存初始值，将这些数据放入 bss 段也就减少了`可执行文件的大小`，这在`嵌入式领域`或`早期计算机时代`非常重要。

#### BSS 段是否清零

ISO/IEC C9899:1999(Section 6.7.8 Initialization, paragraph 10):

> If an object that has static storage duration is not initialized explicitly, then:
>
> - if it has pointer type, it is initialized to a null pointer;
> - if it has arithmetic type, it is initialized to (positive or unsigned) zero;
> - if it is an aggregate, every member is initialized (recursively) according to these rules;
> - if it is a union, the first named member is initialized (recursively) according to these rules.

如果未显式初始化具有静态存储持续时间的对象，则：

- 如果它具有指针类型，则将其初始化为空指针;
- 如果它具有算术类型，则将其初始化为（正数或无符号）零;
- 如果是聚合(数组,结构体等)，则根据这些规则（递归）初始化每个成员;
- 如果是联合(union 类型)，则根据这些规则（递归）初始化第一个命名成员。

### rodata 段

rodata 又称`常量区`，ro 代表 `read only`，即`只读数据`(`const`)。

视编译器的不同，rodata 段有可能被包含在 text 段内，因为其和 text 段特性相同，都是只读的。

关于 rodata 类型的数据，要注意以下几点：

- 常量不一定就放在 rodata 里，有的立即数直接`编码在指令里`，存放在`代码段(.text)`中。
- 对于字符串常量，编译器会自动`去掉重复`的字符串，保证一个字符串在一个可执行文件(EXE/SO)中只存在一份拷贝。
- 在有的嵌入式系统中，rodata 放在 ROM(如 norflash)里，运行时`直接读取 ROM` 内存，`无需要加载`到 RAM 内存中。
- 在嵌入式 linux 系统中，通过一种叫作 `XIP（就地执行）`的技术，也可以`直接读取`，而无需要加载到 RAM 内存中。
- rodata 是在`多个进程`间是`共享`的（多个进程使用同一份 ROM，利用直接读取技术），这可以提高空间利用率。

由此可见，把在运行过程中不会改变的数据设为 rodata 类型的，是有很多好处的：在多个进程间共享，可以大大提高空间利用率，甚至`不占用 RAM 空间`。同时由于 rodata 在只读的内存页面(page)中，是`受保护`的，任何试图对它的修改都会被及时发现，这可以帮助提高程序的稳定性。

#### 示例

```c
#include <iostream>
using namespace std;
const int a = 11;
int main()
{
    const int b = 22;
    int *ptr;
    ptr = (int*) &a;
    *ptr = 21;
}
```

在本例中，a 为`全局常量`，存于 text 段或 rodata 段；b 为局部常量，函数调用时在栈中。ptr 指针修改了 a 指向的空间，因为 text 段或 rodata 段是`只读`的，所以会出错。

## 静态变量

static 关键字用途总结起来就有两种作用，`改变生命期`和`限制作用域`。如：

- 修饰 inline 函数：限制作用域（限制本`.c`文件访问）
- 修饰普通函数：限制作用域（限制本`.c`文件访问）
- 修饰局部变量：改变生命期（离开函数后不释放）
- 修饰全局变量：限制作用域（限制本`.c`文件访问）

可以将静态局部变量视为全局变量，因为其生命周期与全局变量完全相同，只不过其作用域限制在了本文件内，其实相当于编译器给这个变量进行了重命名和限制。

静态局部变量默认初始化为 0，所以对于会对 bss 段做清零的系统，可以将该变量置于 bss 段节省可执行文件大小

### 示例

```c
#include<stdio.h>
void test(){
        static int a=1;
        printf("%d",a++);
}
void main(){
        int i;
        for (i=0;i<5;i++)
                test();
}
```

汇编代码如下：

```s
.LC0:
        .string "%d"

test:
.LFB0:
        pushl   %ebp
        movl    %esp, %ebp
        subl    $8, %esp
        movl    a.1933, %eax
        leal    1(%eax), %edx
        movl    %edx, a.1933
        subl    $8, %esp
        pushl   %eax
        pushl   $.LC0
        call    printf
        addl    $16, %esp
        nop
        leave
        ret

a.1933:
        .long   1
```

a 为`局部静态变量`，离开函数不释放，所以并不在栈中，汇编代码中显示其位置与全局变量相同，不过名称被改为了 `a.1933`，为了防止`命名冲突`

## map 文件解析

附录中是一个 map 文件，map 文件就是通过编译器编译之后，生成的程序、数据及 IO 空间信息的一种映射文件，里面包含函数大小，入口地址等一些重要信息。

从 map 文件我们可以了解到：

- 程序各区段的寻址是否正确
- 程序各区段的 size，即目前存储器的使用量
- 程序中各个 symbol 的地址
- 各个 symbol 在存储器中的顺序关系（这在调试时很有用）
- 各个程序文件的存储用量

### 堆栈空间大小声明

```s
                0x00000800                STACK_SIZE = 0x800
                0x00000000                HEAP_SIZE = 0x0
```

### 中断向量表

```s
.isr_vector     0x00000000       0xc8
 *(.isr_vector)
 .isr_vector    0x00000000       0xc8 rel/startup_efm32pg1b.o
                0x00000000                g_pfnVectors
                0x000000c8                . = ALIGN (0x4)
```

### eh_frame

见[Exception Frames](https://refspecs.linuxfoundation.org/LSB_3.0.0/LSB-Core-generic/LSB-Core-generic/ehframechpt.html)，因为 C 语言不像 C++有异常处理功能，这里没有分配，长度为 0

```s
.eh_frame       0x000000c8        0x0
 .eh_frame      0x000000c8        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
```

### text 段（省略）

总长度为 16,004 Bytes，再往下是每个函数的代码占用的 text 段长度

得益于`XIP 就地执行`技术，CPU 可以直接从 ROM 中读取指令，而无需将 text 段拷贝入内存

`XIP 就地执行`技术核心是将 ROM 空间映射到 CPU 总线，能让 CPU 和访问 RAM 一样直接使用总线地址访问 ROM

```s
.text           0x000000c8     0x3e84
                0x000000c8                . = ALIGN (0x4)
 *(.text)
 .text          0x000000c8       0x40 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
 .text          0x00000108       0x30 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_aeabi_uldivmod.o)
                0x00000108                __aeabi_uldivmod
 .text          0x00000138      0x2d0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_udivmoddi4.o)
                0x00000138                __udivmoddi4
 .text          0x00000408        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_dvmd_tls.o)
                0x00000408                __aeabi_idiv0
                0x00000408                __aeabi_ldiv0
 *(.text*)
 .text.SysTick_Handler
                0x0000040c       0x70 rel/bsp.o
                0x0000040c                SysTick_Handler
 .text.GPIO_EVEN_IRQHandler
                0x0000047c       0x28 rel/bsp.o
                0x0000047c                GPIO_EVEN_IRQHandler
```

### rodata 段

保存全局常量

此处 rodata 含于 text 段，没有单独的段

```s
 *(.rodata)
 .rodata        0x00003a50        0x9 rel/udelay.o
 *fill*         0x00003a59        0x3
 .rodata        0x00003a5c       0x2b rel/displaypalemlib.o
 *(.rodata*)
 *fill*         0x00003a87        0x1
 .rodata.BSP_updateScore.str1.4
                0x00003a88        0x7 rel/bsp.o
 *fill*         0x00003a8f        0x1
 .rodata.Q_this_module_
                0x00003a90        0x9 rel/bsp.o
 *fill*         0x00003a99        0x3
 .rodata.explosion0_bits
                0x00003a9c        0x4 rel/bsp.o
 .rodata.explosion1_bits
                0x00003aa0        0x4 rel/bsp.o
```

### 其他段

中间一些段不认识，以后在研究

```s
.glue_7         0x00003f4c        0x0
 .glue_7        0x00003f4c        0x0 linker stubs

.glue_7t        0x00003f4c        0x0
 .glue_7t       0x00003f4c        0x0 linker stubs

.vfp11_veneer   0x00003f4c        0x0
 .vfp11_veneer  0x00003f4c        0x0 linker stubs

.v4_bx          0x00003f4c        0x0
 .v4_bx         0x00003f4c        0x0 linker stubs

.iplt           0x00003f4c        0x0
 .iplt          0x00003f4c        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o

.preinit_array  0x00003f4c        0x0
                0x00003f4c                PROVIDE (__preinit_array_start = .)
 *(.preinit_array*)
                0x00003f4c                PROVIDE (__preinit_array_end = .)

.init_array     0x00003f4c        0x4
                0x00003f4c                PROVIDE (__init_array_start = .)
 *(SORT_BY_NAME(.init_array.*))
 *(.init_array*)
 .init_array    0x00003f4c        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
                0x00003f50                PROVIDE (__init_array_end = .)

.fini_array     0x00003f50        0x4
                [!provide]                PROVIDE (__fini_array_start = .)
 *(.fini_array*)
 .fini_array    0x00003f50        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
 *(SORT_BY_NAME(.fini_array.*))
                [!provide]                PROVIDE (__fini_array_end = .)
                0x00003f54                _etext = .
```

### 栈空间

起始地址为 0x20000000，说明不在 ROM 中，仅在 RAM 中

```s
.stack          0x20000000      0x800
                0x20000000                __stack_start__ = .
                0x20000800                . = (. + STACK_SIZE)
 *fill*         0x20000000      0x800
                0x20000800                . = ALIGN (0x4)
                0x20000800                __stack_end__ = .
```

### data 段

初始值从 0x00003f54 地址开始的 ROM 中加载，使用时存放在内存中

```s
.data           0x20000800       0x18 load address 0x00003f54
                0x00003f54                __data_load = LOADADDR (.data)
                0x20000800                __data_start = .
 *(.data)
 *(.data*)
 .data.the_Ticker0
                0x20000800        0x4 rel/main.o
                0x20000800                the_Ticker0
 .data.SystemHFXOClock
                0x20000804        0x4 rel/system_efm32pg1b.o
 .data.SystemHfrcoFreq
                0x20000808        0x4 rel/system_efm32pg1b.o
                0x20000808                SystemHfrcoFreq
 .data.SystemLFXOClock
                0x2000080c        0x4 rel/system_efm32pg1b.o
 .data.auxHfrcoFreq
                0x20000810        0x4 rel/em_cmu.o
 .data.loops_per_jiffy
                0x20000814        0x4 rel/udelay.o
                0x20000814                loops_per_jiffy
                0x20000818                . = ALIGN (0x4)
                0x20000818                __data_end__ = .
                0x20000818                _edata = __data_end__
```

### bss 段（省略）

可以看到如果是静态变量，编译器会自动给变量起一个别名，如`buttons`的别名`buttons.2`

一般对于静态变量会赋予其初始值 0，有初始值的照理应该放在 data 段，这里还是放入了 bss 段，说明这是种优化，默认 bss 段会被清 0，尽可能减少 data 段空间

全部在 RAM 中，不用初始值，不占用 ROM 空间

```s
.bss            0x20000818     0x1374 load address 0x00003f6c
                0x20000818                __bss_start__ = .
 *(.bss)
 .bss           0x20000818       0x1c d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
 *(.bss*)
 .bss.buttons.2
                0x20000834        0x8 rel/bsp.o
 .bss.l_fb      0x2000083c      0x810 rel/bsp.o
 .bss.l_rnd     0x2000104c        0x4 rel/bsp.o
 .bss.l_walls   0x20001050      0x770 rel/bsp.o
 .bss.l_ticker0
                0x200017c0       0x20 rel/main.o
（中间省略）
 .bss.QTimeEvt_timeEvtHead_
                0x20001b64       0x28 rel/qf_time.o
                0x20001b64                QTimeEvt_timeEvtHead_
 *(COMMON)
                0x20001b8c                . = ALIGN (0x4)
                0x20001b8c                _ebss = .
                0x20001b8c                __bss_end__ = .
                0x20001b8c                __exidx_start = .
```

### heap 堆空间

不分配堆空间

```s
.heap           0x20001b94        0x0
                0x20001b94                __heap_start__ = .
                0x20001b94                . = (. + HEAP_SIZE)
                0x20001b94                . = ALIGN (0x4)
                0x20001b94                __heap_end__ = .
```

### Cross Reference Table

交叉引用表，列出了对象或函数在哪些文件被调用

```s
Cross Reference Table

Symbol                                            File
ACMP0_IRQHandler                                  rel/startup_efm32pg1b.o
ADC0_IRQHandler                                   rel/startup_efm32pg1b.o
AO_Missile                                        rel/missile.o
                                                  rel/tunnel.o
                                                  rel/ship.o
                                                  rel/mine2.o
                                                  rel/mine1.o
                                                  rel/main.o
AO_Ship                                           rel/ship.o
                                                  rel/tunnel.o
                                                  rel/missile.o
                                                  rel/mine2.o
                                                  rel/mine1.o
                                                  rel/main.o
```

## 附录

```s
Archive member included to satisfy reference by file (symbol)

d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_aeabi_uldivmod.o)
                              rel/em_usart.o (__aeabi_uldivmod)
d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_udivmoddi4.o)
                              d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_aeabi_uldivmod.o) (__udivmoddi4)
d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_dvmd_tls.o)
                              d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_aeabi_uldivmod.o) (__aeabi_ldiv0)
d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o)
                              d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o (exit)
d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
                              d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o) (_global_impure_ptr)
d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)
                              d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o (__libc_init_array)
d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-memset.o)
                              d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o (memset)
d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libnosys.a(_exit.o)
                              d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o) (_exit)

Discarded input sections

 .text          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crti.o
 .data          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crti.o
 .bss           0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crti.o
 .data          0x00000000        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
 .rodata        0x00000000       0x24 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
 .text          0x00000000       0x7c d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
 .data          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
 .bss           0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
 .ARM.extab     0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
 .ARM.exidx     0x00000000       0x10 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
 .ARM.attributes
                0x00000000       0x1c d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
 .text          0x00000000        0x0 rel/bsp.o
 .data          0x00000000        0x0 rel/bsp.o
 .bss           0x00000000        0x0 rel/bsp.o
 .text          0x00000000        0x0 rel/main.o
 .data          0x00000000        0x0 rel/main.o
 .bss           0x00000000        0x0 rel/main.o
 .text          0x00000000        0x0 rel/mine1.o
 .data          0x00000000        0x0 rel/mine1.o
 .bss           0x00000000        0x0 rel/mine1.o
 .text          0x00000000        0x0 rel/mine2.o
 .data          0x00000000        0x0 rel/mine2.o
 .bss           0x00000000        0x0 rel/mine2.o
 .text          0x00000000        0x0 rel/missile.o
 .data          0x00000000        0x0 rel/missile.o
 .bss           0x00000000        0x0 rel/missile.o
 .text          0x00000000        0x0 rel/ship.o
 .data          0x00000000        0x0 rel/ship.o
 .bss           0x00000000        0x0 rel/ship.o
 .text          0x00000000        0x0 rel/tunnel.o
 .data          0x00000000        0x0 rel/tunnel.o
 .bss           0x00000000        0x0 rel/tunnel.o
 .text          0x00000000        0x0 rel/startup_efm32pg1b.o
 .data          0x00000000        0x0 rel/startup_efm32pg1b.o
 .bss           0x00000000        0x0 rel/startup_efm32pg1b.o
 .text          0x00000000        0x0 rel/system_efm32pg1b.o
 .data          0x00000000        0x0 rel/system_efm32pg1b.o
 .bss           0x00000000        0x0 rel/system_efm32pg1b.o
 .text.SystemHFXOClockGet
                0x00000000        0xc rel/system_efm32pg1b.o
 .text.SystemHFXOClockSet
                0x00000000       0x24 rel/system_efm32pg1b.o
 .text.SystemLFXOClockSet
                0x00000000       0x24 rel/system_efm32pg1b.o
 .text          0x00000000        0x0 rel/em_cmu.o
 .data          0x00000000        0x0 rel/em_cmu.o
 .bss           0x00000000        0x0 rel/em_cmu.o
 .text.CMU_AUXHFRCOBandGet
                0x00000000        0xc rel/em_cmu.o
 .text.CMU_AUXHFRCOBandSet
                0x00000000      0x110 rel/em_cmu.o
 .text.CMU_Calibrate
                0x00000000       0x58 rel/em_cmu.o
 .text.CMU_CalibrateConfig
                0x00000000       0x64 rel/em_cmu.o
 .text.CMU_CalibrateCountGet
                0x00000000       0x24 rel/em_cmu.o
 .text.CMU_FreezeEnable
                0x00000000       0x24 rel/em_cmu.o
 .text.CMU_HFRCOBandGet
                0x00000000        0xc rel/em_cmu.o
 .text.CMU_HFRCOBandSet
                0x00000000      0x174 rel/em_cmu.o
 .text.CMU_LCDClkFDIVGet
                0x00000000        0x4 rel/em_cmu.o
 .text.CMU_LCDClkFDIVSet
                0x00000000        0x2 rel/em_cmu.o
 .text.CMU_HFXOInit
                0x00000000       0xb4 rel/em_cmu.o
 .text.CMU_LFXOInit
                0x00000000       0x38 rel/em_cmu.o
 .text.CMU_OscillatorTuningGet
                0x00000000       0x34 rel/em_cmu.o
 .text.CMU_OscillatorTuningSet
                0x00000000       0x70 rel/em_cmu.o
 .text.CMU_PCNTClockExternalGet
                0x00000000       0x1c rel/em_cmu.o
 .text.CMU_PCNTClockExternalSet
                0x00000000        0xc rel/em_cmu.o
 .text          0x00000000        0x0 rel/em_emu.o
 .data          0x00000000        0x0 rel/em_emu.o
 .bss           0x00000000        0x0 rel/em_emu.o
 .text.emuRestore
                0x00000000       0x94 rel/em_emu.o
 .text.dcdcHsFixLnBlock
                0x00000000       0x34 rel/em_emu.o
 .text.currentLimitersUpdate
                0x00000000       0x74 rel/em_emu.o
 .text.dcdcFetCntSet
                0x00000000       0x34 rel/em_emu.o
 .text.EMU_EnterEM2
                0x00000000       0x60 rel/em_emu.o
 .text.EMU_EnterEM3
                0x00000000       0x7c rel/em_emu.o
 .text.EMU_EnterEM4
                0x00000000       0x3c rel/em_emu.o
 .text.EMU_MemPwrDown
                0x00000000        0xc rel/em_emu.o
 .text.EMU_EM23Init
                0x00000000        0x2 rel/em_emu.o
 .text.EMU_EM4Init
                0x00000000       0x54 rel/em_emu.o
 .text.EMU_DCDCModeSet
                0x00000000       0x2c rel/em_emu.o
 .text.EMU_DCDCOutputVoltageSet
                0x00000000      0x298 rel/em_emu.o
 .text.EMU_DCDCOptimizeSlice
                0x00000000       0xa4 rel/em_emu.o
 .text.EMU_DCDCLnRcoBandSet
                0x00000000       0x1c rel/em_emu.o
 .text.EMU_DCDCInit
                0x00000000      0x158 rel/em_emu.o
 .text.EMU_DCDCPowerOff
                0x00000000       0x34 rel/em_emu.o
 .text.EMU_VmonInit
                0x00000000      0x118 rel/em_emu.o
 .text.EMU_VmonHystInit
                0x00000000       0x8c rel/em_emu.o
 .text.EMU_VmonEnable
                0x00000000       0x38 rel/em_emu.o
 .text.EMU_VmonChannelStatusGet
                0x00000000       0x34 rel/em_emu.o
 .bss.dcdcMaxCurrent_mA
                0x00000000        0x2 rel/em_emu.o
 .bss.dcdcReverseCurrentControl
                0x00000000        0x2 rel/em_emu.o
 .bss.emuDcdcMiscCtrlReg.0
                0x00000000        0x4 rel/em_emu.o
 .bss.errataFixDcdcHsState
                0x00000000        0x1 rel/em_emu.o
 .text          0x00000000        0x0 rel/em_gpio.o
 .data          0x00000000        0x0 rel/em_gpio.o
 .bss           0x00000000        0x0 rel/em_gpio.o
 .text.GPIO_DbgLocationSet
                0x00000000        0x2 rel/em_gpio.o
 .text.GPIO_DriveStrengthSet
                0x00000000       0x20 rel/em_gpio.o
 .text.GPIO_ExtIntConfig
                0x00000000       0xb8 rel/em_gpio.o
 .text.GPIO_PinModeGet
                0x00000000       0x26 rel/em_gpio.o
 .text.GPIO_EM4EnablePinWakeup
                0x00000000       0x40 rel/em_gpio.o
 .text          0x00000000        0x0 rel/em_int.o
 .data          0x00000000        0x0 rel/em_int.o
 .bss           0x00000000        0x0 rel/em_int.o
 .text          0x00000000        0x0 rel/em_prs.o
 .data          0x00000000        0x0 rel/em_prs.o
 .bss           0x00000000        0x0 rel/em_prs.o
 .text.PRS_SourceSignalSet
                0x00000000       0x1c rel/em_prs.o
 .text          0x00000000        0x0 rel/em_rtcc.o
 .data          0x00000000        0x0 rel/em_rtcc.o
 .bss           0x00000000        0x0 rel/em_rtcc.o
 .text.RTCC_StatusClear
                0x00000000       0x18 rel/em_rtcc.o
 .text.RTCC_Reset
                0x00000000       0x44 rel/em_rtcc.o
 .text          0x00000000        0x0 rel/em_system.o
 .data          0x00000000        0x0 rel/em_system.o
 .bss           0x00000000        0x0 rel/em_system.o
 .text.SYSTEM_ChipRevisionGet
                0x00000000       0x3c rel/em_system.o
 .comment       0x00000000       0x4a rel/em_system.o
 .ARM.attributes
                0x00000000       0x30 rel/em_system.o
 .text          0x00000000        0x0 rel/em_usart.o
 .data          0x00000000        0x0 rel/em_usart.o
 .bss           0x00000000        0x0 rel/em_usart.o
 .text.USART_BaudrateAsyncSet
                0x00000000       0x64 rel/em_usart.o
 .text.USART_BaudrateCalc
                0x00000000       0x7e rel/em_usart.o
 .text.USART_BaudrateGet
                0x00000000       0x24 rel/em_usart.o
 .text.USART_Enable
                0x00000000        0xe rel/em_usart.o
 .text.USART_InitPrsTrigger
                0x00000000       0x2a rel/em_usart.o
 .text.USART_InitAsync
                0x00000000       0x60 rel/em_usart.o
 .text.USARTn_InitIrDA
                0x00000000       0x40 rel/em_usart.o
 .text.USART_InitI2s
                0x00000000       0x4e rel/em_usart.o
 .text.USART_Rx
                0x00000000        0xe rel/em_usart.o
 .text.USART_RxDouble
                0x00000000        0xe rel/em_usart.o
 .text.USART_RxDoubleExt
                0x00000000        0xc rel/em_usart.o
 .text.USART_RxExt
                0x00000000        0xe rel/em_usart.o
 .text.USART_SpiTransfer
                0x00000000       0x18 rel/em_usart.o
 .text.USART_TxDoubleExt
                0x00000000        0xc rel/em_usart.o
 .text.USART_TxExt
                0x00000000        0xc rel/em_usart.o
 .text          0x00000000        0x0 rel/udelay.o
 .data          0x00000000        0x0 rel/udelay.o
 .bss           0x00000000        0x0 rel/udelay.o
 .text          0x00000000        0x0 rel/display_ls013b7dh03.o
 .data          0x00000000        0x0 rel/display_ls013b7dh03.o
 .bss           0x00000000        0x0 rel/display_ls013b7dh03.o
 .text.Display_refresh
                0x00000000        0xc rel/display_ls013b7dh03.o
 .text          0x00000000        0x0 rel/displaypalemlib.o
 .data          0x00000000        0x0 rel/displaypalemlib.o
 .bss           0x00000000        0x0 rel/displaypalemlib.o
 .text.PAL_SpiShutdown
                0x00000000       0x20 rel/displaypalemlib.o
 .text.PAL_TimerShutdown
                0x00000000        0x4 rel/displaypalemlib.o
 .text.PAL_GpioShutdown
                0x00000000       0x14 rel/displaypalemlib.o
 .text.PAL_GpioPinOutToggle
                0x00000000       0x1c rel/displaypalemlib.o
 .text          0x00000000        0x0 rel/qep_hsm.o
 .data          0x00000000        0x0 rel/qep_hsm.o
 .bss           0x00000000        0x0 rel/qep_hsm.o
 .text.QHsm_isIn
                0x00000000       0x40 rel/qep_hsm.o
 .text.QHsm_childState
                0x00000000       0x3c rel/qep_hsm.o
 .rodata.QP_versionStr
                0x00000000        0x8 rel/qep_hsm.o
 .text          0x00000000        0x0 rel/qep_msm.o
 .data          0x00000000        0x0 rel/qep_msm.o
 .bss           0x00000000        0x0 rel/qep_msm.o
 .text.QMsm_isInState
                0x00000000       0x20 rel/qep_msm.o
 .text.QMsm_stateObj
                0x00000000        0x4 rel/qep_msm.o
 .text.QMsm_childStateObj
                0x00000000       0x28 rel/qep_msm.o
 .text.QMsm_ctor
                0x00000000       0x14 rel/qep_msm.o
 .text.QMsm_execTatbl_
                0x00000000       0x3c rel/qep_msm.o
 .text.QMsm_init_
                0x00000000       0x4c rel/qep_msm.o
 .text.QMsm_exitToTranSource_
                0x00000000       0x34 rel/qep_msm.o
 .text.QMsm_enterHistory_
                0x00000000       0x70 rel/qep_msm.o
 .text.QMsm_dispatch_
                0x00000000      0x120 rel/qep_msm.o
 .rodata.Q_this_module_
                0x00000000        0x8 rel/qep_msm.o
 .rodata.l_msm_top_s
                0x00000000       0x14 rel/qep_msm.o
 .rodata.vtable.0
                0x00000000        0x8 rel/qep_msm.o
 .comment       0x00000000       0x4a rel/qep_msm.o
 .ARM.attributes
                0x00000000       0x30 rel/qep_msm.o
 .text          0x00000000        0x0 rel/qf_act.o
 .data          0x00000000        0x0 rel/qf_act.o
 .bss           0x00000000        0x0 rel/qf_act.o
 .rodata.dummy  0x00000000        0x1 rel/qf_act.o
 .comment       0x00000000       0x4a rel/qf_act.o
 .ARM.attributes
                0x00000000       0x30 rel/qf_act.o
 .text          0x00000000        0x0 rel/qf_actq.o
 .data          0x00000000        0x0 rel/qf_actq.o
 .bss           0x00000000        0x0 rel/qf_actq.o
 .text.QF_getQueueMin
                0x00000000       0x34 rel/qf_actq.o
 .text          0x00000000        0x0 rel/qf_defer.o
 .data          0x00000000        0x0 rel/qf_defer.o
 .bss           0x00000000        0x0 rel/qf_defer.o
 .text.QActive_defer
                0x00000000       0x12 rel/qf_defer.o
 .text.QActive_recall
                0x00000000       0x58 rel/qf_defer.o
 .text.QActive_flushDeferred
                0x00000000       0x2c rel/qf_defer.o
 .rodata.Q_this_module_
                0x00000000        0x9 rel/qf_defer.o
 .comment       0x00000000       0x4a rel/qf_defer.o
 .ARM.attributes
                0x00000000       0x30 rel/qf_defer.o
 .text          0x00000000        0x0 rel/qf_dyn.o
 .data          0x00000000        0x0 rel/qf_dyn.o
 .bss           0x00000000        0x0 rel/qf_dyn.o
 .text.QF_poolGetMaxBlockSize
                0x00000000       0x1c rel/qf_dyn.o
 .text.QF_getPoolMin
                0x00000000       0x44 rel/qf_dyn.o
 .text.QF_newRef_
                0x00000000       0x30 rel/qf_dyn.o
 .text.QF_deleteRef_
                0x00000000        0x8 rel/qf_dyn.o
 .text          0x00000000        0x0 rel/qf_mem.o
 .data          0x00000000        0x0 rel/qf_mem.o
 .bss           0x00000000        0x0 rel/qf_mem.o
 .text          0x00000000        0x0 rel/qf_ps.o
 .data          0x00000000        0x0 rel/qf_ps.o
 .bss           0x00000000        0x0 rel/qf_ps.o
 .text.QActive_unsubscribe
                0x00000000       0x68 rel/qf_ps.o
 .text.QActive_unsubscribeAll
                0x00000000       0x7c rel/qf_ps.o
 .text          0x00000000        0x0 rel/qf_qact.o
 .data          0x00000000        0x0 rel/qf_qact.o
 .bss           0x00000000        0x0 rel/qf_qact.o
 .text.QActive_unregister_
                0x00000000       0x40 rel/qf_qact.o
 .bss.QF_intLock_
                0x00000000        0x4 rel/qf_qact.o
 .bss.QF_intNest_
                0x00000000        0x4 rel/qf_qact.o
 .text          0x00000000        0x0 rel/qf_qeq.o
 .data          0x00000000        0x0 rel/qf_qeq.o
 .bss           0x00000000        0x0 rel/qf_qeq.o
 .text.QEQueue_post
                0x00000000       0x8c rel/qf_qeq.o
 .text.QEQueue_postLIFO
                0x00000000       0x70 rel/qf_qeq.o
 .text.QEQueue_get
                0x00000000       0x64 rel/qf_qeq.o
 .rodata.Q_this_module_
                0x00000000        0x7 rel/qf_qeq.o
 .text          0x00000000        0x0 rel/qf_qmact.o
 .data          0x00000000        0x0 rel/qf_qmact.o
 .bss           0x00000000        0x0 rel/qf_qmact.o
 .text.QMActive_ctor
                0x00000000       0x20 rel/qf_qmact.o
 .rodata.vtable.0
                0x00000000       0x14 rel/qf_qmact.o
 .comment       0x00000000       0x4a rel/qf_qmact.o
 .ARM.attributes
                0x00000000       0x30 rel/qf_qmact.o
 .text          0x00000000        0x0 rel/qf_time.o
 .data          0x00000000        0x0 rel/qf_time.o
 .bss           0x00000000        0x0 rel/qf_time.o
 .text.QTimeEvt_rearm
                0x00000000       0x74 rel/qf_time.o
 .text.QTimeEvt_wasDisarmed
                0x00000000       0x10 rel/qf_time.o
 .text.QTimeEvt_currCtr
                0x00000000       0x14 rel/qf_time.o
 .text.QTimeEvt_noActive
                0x00000000       0x3c rel/qf_time.o
 .text          0x00000000        0x0 rel/qv.o
 .data          0x00000000        0x0 rel/qv.o
 .bss           0x00000000        0x0 rel/qv.o
 .text          0x00000000        0x0 rel/qv_port.o
 .data          0x00000000        0x0 rel/qv_port.o
 .bss           0x00000000        0x0 rel/qv_port.o
 .text          0x00000000        0x0 rel/qstamp.o
 .data          0x00000000        0x0 rel/qstamp.o
 .bss           0x00000000        0x0 rel/qstamp.o
 .rodata.Q_BUILD_DATE
                0x00000000        0xc rel/qstamp.o
 .rodata.Q_BUILD_TIME
                0x00000000        0x9 rel/qstamp.o
 .comment       0x00000000       0x4a rel/qstamp.o
 .ARM.attributes
                0x00000000       0x30 rel/qstamp.o
 .data          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_aeabi_uldivmod.o)
 .bss           0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_aeabi_uldivmod.o)
 .data          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_udivmoddi4.o)
 .bss           0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_udivmoddi4.o)
 .ARM.extab     0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_udivmoddi4.o)
 .data          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_dvmd_tls.o)
 .bss           0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_dvmd_tls.o)
 .text          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o)
 .data          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o)
 .bss           0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o)
 .text.exit     0x00000000       0x28 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o)
 .debug_frame   0x00000000       0x28 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o)
 .ARM.attributes
                0x00000000       0x30 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o)
 .text          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
 .data          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
 .bss           0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
 .data._impure_ptr
                0x00000000        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
 .data.impure_data
                0x00000000       0x60 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
 .rodata._global_impure_ptr
                0x00000000        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
 .ARM.attributes
                0x00000000       0x30 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
 .text          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)
 .data          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)
 .bss           0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)
 .text          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-memset.o)
 .data          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-memset.o)
 .bss           0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-memset.o)
 .text.memset   0x00000000       0x10 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-memset.o)
 .debug_frame   0x00000000       0x20 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-memset.o)
 .ARM.attributes
                0x00000000       0x30 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-memset.o)
 .text          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libnosys.a(_exit.o)
 .data          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libnosys.a(_exit.o)
 .bss           0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libnosys.a(_exit.o)
 .text._exit    0x00000000        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libnosys.a(_exit.o)
 .debug_frame   0x00000000       0x20 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libnosys.a(_exit.o)
 .ARM.attributes
                0x00000000       0x30 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libnosys.a(_exit.o)
 .text          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtend.o
 .data          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtend.o
 .bss           0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtend.o
 .rodata        0x00000000       0x24 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtend.o
 .eh_frame      0x00000000        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtend.o
 .ARM.attributes
                0x00000000       0x30 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtend.o
 .text          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtn.o
 .data          0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtn.o
 .bss           0x00000000        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtn.o

Memory Configuration

Name             Origin             Length             Attributes
ROM              0x00000000         0x00040000         xr
RAM              0x20000000         0x00008000         xrw
*default*        0x00000000         0xffffffff

Linker script and memory map

LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crti.o
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
LOAD rel/bsp.o
LOAD rel/main.o
LOAD rel/mine1.o
LOAD rel/mine2.o
LOAD rel/missile.o
LOAD rel/ship.o
LOAD rel/tunnel.o
LOAD rel/startup_efm32pg1b.o
LOAD rel/system_efm32pg1b.o
LOAD rel/em_cmu.o
LOAD rel/em_emu.o
LOAD rel/em_gpio.o
LOAD rel/em_int.o
LOAD rel/em_prs.o
LOAD rel/em_rtcc.o
LOAD rel/em_system.o
LOAD rel/em_usart.o
LOAD rel/udelay.o
LOAD rel/display_ls013b7dh03.o
LOAD rel/displaypalemlib.o
LOAD rel/qep_hsm.o
LOAD rel/qep_msm.o
LOAD rel/qf_act.o
LOAD rel/qf_actq.o
LOAD rel/qf_defer.o
LOAD rel/qf_dyn.o
LOAD rel/qf_mem.o
LOAD rel/qf_ps.o
LOAD rel/qf_qact.o
LOAD rel/qf_qeq.o
LOAD rel/qf_qmact.o
LOAD rel/qf_time.o
LOAD rel/qv.o
LOAD rel/qv_port.o
LOAD rel/qstamp.o
START GROUP
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a
END GROUP
START GROUP
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libnosys.a
END GROUP
START GROUP
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libnosys.a
END GROUP
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtend.o
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtn.o
                0x00000800                STACK_SIZE = 0x800
                0x00000000                HEAP_SIZE = 0x0

.isr_vector     0x00000000       0xc8
 *(.isr_vector)
 .isr_vector    0x00000000       0xc8 rel/startup_efm32pg1b.o
                0x00000000                g_pfnVectors
                0x000000c8                . = ALIGN (0x4)

.eh_frame       0x000000c8        0x0
 .eh_frame      0x000000c8        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o

.text           0x000000c8     0x3e84
                0x000000c8                . = ALIGN (0x4)
 *(.text)
 .text          0x000000c8       0x40 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
 .text          0x00000108       0x30 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_aeabi_uldivmod.o)
                0x00000108                __aeabi_uldivmod
 .text          0x00000138      0x2d0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_udivmoddi4.o)
                0x00000138                __udivmoddi4
 .text          0x00000408        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_dvmd_tls.o)
                0x00000408                __aeabi_idiv0
                0x00000408                __aeabi_ldiv0
 *(.text*)
 .text.SysTick_Handler
                0x0000040c       0x70 rel/bsp.o
                0x0000040c                SysTick_Handler
 .text.GPIO_EVEN_IRQHandler
                0x0000047c       0x28 rel/bsp.o
                0x0000047c                GPIO_EVEN_IRQHandler
 .text.USART0_RX_IRQHandler
                0x000004a4        0x2 rel/bsp.o
                0x000004a4                USART0_RX_IRQHandler
 *fill*         0x000004a6        0x2
 .text.BSP_updateScreen
                0x000004a8       0x30 rel/bsp.o
                0x000004a8                BSP_updateScreen
 .text.BSP_clearFB
                0x000004d8       0x1c rel/bsp.o
                0x000004d8                BSP_clearFB
 .text.BSP_clearWalls
                0x000004f4       0x1c rel/bsp.o
                0x000004f4                BSP_clearWalls
 .text.BSP_isThrottle
                0x00000510       0x14 rel/bsp.o
                0x00000510                BSP_isThrottle
 .text.BSP_paintString
                0x00000524       0xa0 rel/bsp.o
                0x00000524                BSP_paintString
 .text.BSP_paintBitmap
                0x000005c4       0x78 rel/bsp.o
                0x000005c4                BSP_paintBitmap
 .text.BSP_advanceWalls
                0x0000063c       0x7c rel/bsp.o
                0x0000063c                BSP_advanceWalls
 .text.BSP_isWallHit
                0x000006b8       0x78 rel/bsp.o
                0x000006b8                BSP_isWallHit
 .text.BSP_updateScore
                0x00000730       0x88 rel/bsp.o
                0x00000730                BSP_updateScore
 .text.BSP_displayOn
                0x000007b8        0xa rel/bsp.o
                0x000007b8                BSP_displayOn
 .text.BSP_displayOff
                0x000007c2        0xa rel/bsp.o
                0x000007c2                BSP_displayOff
 .text.BSP_random
                0x000007cc       0x18 rel/bsp.o
                0x000007cc                BSP_random
 .text.BSP_randomSeed
                0x000007e4        0xc rel/bsp.o
                0x000007e4                BSP_randomSeed
 .text.QF_onStartup
                0x000007f0       0x6c rel/bsp.o
                0x000007f0                QF_onStartup
 .text.QF_onCleanup
                0x0000085c        0x2 rel/bsp.o
                0x0000085c                QF_onCleanup
 *fill*         0x0000085e        0x2
 .text.QV_onIdle
                0x00000860       0x2c rel/bsp.o
                0x00000860                QV_onIdle
 .text.Q_onAssert
                0x0000088c       0x24 rel/bsp.o
                0x0000088c                Q_onAssert
 .text.BSP_init
                0x000008b0       0xec rel/bsp.o
                0x000008b0                BSP_init
 .text.BSP_doBitmapsOverlap
                0x0000099c      0x130 rel/bsp.o
                0x0000099c                BSP_doBitmapsOverlap
 .text.main     0x00000acc      0x100 rel/main.o
                0x00000acc                main
 .text.Mine1_initial
                0x00000bcc       0x1c rel/mine1.o
 .text.Mine1_unused
                0x00000be8       0x28 rel/mine1.o
 .text.Mine1_used
                0x00000c10       0x58 rel/mine1.o
 .text.Mine1_exploding
                0x00000c68       0x7c rel/mine1.o
 .text.Mine1_planted
                0x00000ce4       0xe4 rel/mine1.o
 .text.Mine1_ctor_call
                0x00000dc8       0x2c rel/mine1.o
                0x00000dc8                Mine1_ctor_call
 .text.Mine2_initial
                0x00000df4       0x1c rel/mine2.o
 .text.Mine2_unused
                0x00000e10       0x28 rel/mine2.o
 .text.Mine2_used
                0x00000e38       0x58 rel/mine2.o
 .text.Mine2_exploding
                0x00000e90       0x7c rel/mine2.o
 .text.Mine2_planted
                0x00000f0c       0xe4 rel/mine2.o
 .text.Mine2_ctor_call
                0x00000ff0       0x2c rel/mine2.o
                0x00000ff0                Mine2_ctor_call
 .text.Missile_armed
                0x0000101c       0x2c rel/missile.o
 .text.Missile_initial
                0x00001048       0x18 rel/missile.o
 .text.Missile_flying
                0x00001060       0x98 rel/missile.o
 .text.Missile_exploding
                0x000010f8       0x8c rel/missile.o
 .text.Missile_ctor_call
                0x00001184       0x14 rel/missile.o
                0x00001184                Missile_ctor_call
 .text.Ship_active
                0x00001198       0x20 rel/ship.o
 .text.Ship_parked
                0x000011b8       0x20 rel/ship.o
 .text.Ship_initial
                0x000011d8       0x20 rel/ship.o
 .text.Ship_exploding
                0x000011f8       0xa0 rel/ship.o
 .text.Ship_flying
                0x00001298      0x150 rel/ship.o
 .text.Ship_ctor_call
                0x000013e8       0x20 rel/ship.o
                0x000013e8                Ship_ctor_call
 .text.Tunnel_dispatchToAllMines
                0x00001408       0x2a rel/tunnel.o
 *fill*         0x00001432        0x2
 .text.Tunnel_screen_saver
                0x00001434       0x30 rel/tunnel.o
 .text.Tunnel_active
                0x00001464       0x48 rel/tunnel.o
 .text.Tunnel_initial
                0x000014ac       0x70 rel/tunnel.o
 .text.Tunnel_show_logo
                0x0000151c       0xd0 rel/tunnel.o
 .text.Tunnel_final
                0x000015ec       0x24 rel/tunnel.o
 .text.Tunnel_game_over
                0x00001610       0xa8 rel/tunnel.o
 .text.Tunnel_screen_saver_show
                0x000016b8       0x90 rel/tunnel.o
 .text.Tunnel_screen_saver_hide
                0x00001748       0x4c rel/tunnel.o
 .text.Tunnel_advance
                0x00001794       0x84 rel/tunnel.o
 .text.Tunnel_demo
                0x00001818       0xc4 rel/tunnel.o
 .text.Tunnel_playing
                0x000018dc      0x220 rel/tunnel.o
 .text.Tunnel_ctor_call
                0x00001afc       0x60 rel/tunnel.o
                0x00001afc                Tunnel_ctor_call
 .text.NMI_Handler
                0x00001b5c       0x14 rel/startup_efm32pg1b.o
                0x00001b5c                NMI_Handler
 .text.MemManage_Handler
                0x00001b70       0x18 rel/startup_efm32pg1b.o
                0x00001b70                MemManage_Handler
 .text.HardFault_Handler
                0x00001b88       0x18 rel/startup_efm32pg1b.o
                0x00001b88                HardFault_Handler
 .text.BusFault_Handler
                0x00001ba0       0x18 rel/startup_efm32pg1b.o
                0x00001ba0                BusFault_Handler
 .text.UsageFault_Handler
                0x00001bb8       0x1c rel/startup_efm32pg1b.o
                0x00001bb8                UsageFault_Handler
 .text.Default_Handler
                0x00001bd4       0x18 rel/startup_efm32pg1b.o
                0x00001bd4                DebugMon_Handler
                0x00001bd4                USART0_TX_IRQHandler
                0x00001bd4                I2C0_IRQHandler
                0x00001bd4                USART1_RX_IRQHandler
                0x00001bd4                PendSV_Handler
                0x00001bd4                WDOG0_IRQHandler
                0x00001bd4                USART1_TX_IRQHandler
                0x00001bd4                MSC_IRQHandler
                0x00001bd4                ADC0_IRQHandler
                0x00001bd4                LEUART0_IRQHandler
                0x00001bd4                FPUEH_IRQHandler
                0x00001bd4                LDMA_IRQHandler
                0x00001bd4                TIMER0_IRQHandler
                0x00001bd4                LETIMER0_IRQHandler
                0x00001bd4                TIMER1_IRQHandler
                0x00001bd4                Default_Handler
                0x00001bd4                EMU_IRQHandler
                0x00001bd4                CRYOTIMER_IRQHandler
                0x00001bd4                PCNT0_IRQHandler
                0x00001bd4                ACMP0_IRQHandler
                0x00001bd4                SVC_Handler
                0x00001bd4                RTCC_IRQHandler
                0x00001bd4                CRYPTO_IRQHandler
                0x00001bd4                CMU_IRQHandler
                0x00001bd4                GPIO_ODD_IRQHandler
                0x00001bd4                IDAC0_IRQHandler
 .text.assert_failed
                0x00001bec        0xc rel/startup_efm32pg1b.o
                0x00001bec                assert_failed
 .text.Reset_Handler
                0x00001bf8       0x88 rel/startup_efm32pg1b.o
                0x00001bf8                Reset_Handler
 .text.SystemMaxCoreClockGet
                0x00001c80        0x8 rel/system_efm32pg1b.o
                0x00001c80                SystemMaxCoreClockGet
 .text.SystemHFClockGet
                0x00001c88       0x50 rel/system_efm32pg1b.o
                0x00001c88                SystemHFClockGet
 .text.SystemCoreClockGet
                0x00001cd8       0x24 rel/system_efm32pg1b.o
                0x00001cd8                SystemCoreClockGet
 .text.SystemInit
                0x00001cfc       0x14 rel/system_efm32pg1b.o
                0x00001cfc                SystemInit
 .text.SystemLFRCOClockGet
                0x00001d10        0x6 rel/system_efm32pg1b.o
                0x00001d10                SystemLFRCOClockGet
 .text.SystemULFRCOClockGet
                0x00001d16        0x6 rel/system_efm32pg1b.o
                0x00001d16                SystemULFRCOClockGet
 .text.SystemLFXOClockGet
                0x00001d1c        0xc rel/system_efm32pg1b.o
                0x00001d1c                SystemLFXOClockGet
 .text.flashWaitStateControl
                0x00001d28       0x44 rel/em_cmu.o
 .text.flashWaitStateMax
                0x00001d6c        0xc rel/em_cmu.o
 .text.CMU_ClockEnable
                0x00001d78       0x98 rel/em_cmu.o
                0x00001d78                CMU_ClockEnable
 .text.CMU_ClockPrescGet
                0x00001e10       0x9c rel/em_cmu.o
                0x00001e10                CMU_ClockPrescGet
 .text.CMU_ClockDivGet
                0x00001eac        0xa rel/em_cmu.o
                0x00001eac                CMU_ClockDivGet
 *fill*         0x00001eb6        0x2
 .text.CMU_ClockPrescSet
                0x00001eb8      0x1d0 rel/em_cmu.o
                0x00001eb8                CMU_ClockPrescSet
 .text.CMU_ClockDivSet
                0x00002088        0xa rel/em_cmu.o
                0x00002088                CMU_ClockDivSet
 *fill*         0x00002092        0x2
 .text.CMU_ClockSelectGet
                0x00002094       0xbc rel/em_cmu.o
                0x00002094                CMU_ClockSelectGet
 .text.lfClkGet
                0x00002150       0x90 rel/em_cmu.o
 .text.CMU_ClockFreqGet
                0x000021e0      0x13c rel/em_cmu.o
                0x000021e0                CMU_ClockFreqGet
 .text.CMU_OscillatorEnable
                0x0000231c       0xb4 rel/em_cmu.o
                0x0000231c                CMU_OscillatorEnable
 .text.CMU_ClockSelectSet
                0x000023d0      0x114 rel/em_cmu.o
                0x000023d0                CMU_ClockSelectSet
 .text.EMU_UpdateOscConfig
                0x000024e4       0x20 rel/em_emu.o
                0x000024e4                EMU_UpdateOscConfig
 .text.GPIO_PinModeSet
                0x00002504       0xc0 rel/em_gpio.o
                0x00002504                GPIO_PinModeSet
 .text.PRS_SourceAsyncSignalSet
                0x000025c4       0x1c rel/em_prs.o
                0x000025c4                PRS_SourceAsyncSignalSet
 .text.RTCC_ChannelInit
                0x000025e0       0x34 rel/em_rtcc.o
                0x000025e0                RTCC_ChannelInit
 .text.RTCC_Enable
                0x00002614        0xc rel/em_rtcc.o
                0x00002614                RTCC_Enable
 .text.RTCC_Init
                0x00002620       0x3c rel/em_rtcc.o
                0x00002620                RTCC_Init
 .text.USART_BaudrateSyncSet
                0x0000265c       0x4c rel/em_usart.o
                0x0000265c                USART_BaudrateSyncSet
 .text.USART_Reset
                0x000026a8       0x4c rel/em_usart.o
                0x000026a8                USART_Reset
 .text.USART_InitSync
                0x000026f4       0x82 rel/em_usart.o
                0x000026f4                USART_InitSync
 .text.USART_Tx
                0x00002776        0xc rel/em_usart.o
                0x00002776                USART_Tx
 .text.USART_TxDouble
                0x00002782        0xc rel/em_usart.o
                0x00002782                USART_TxDouble
 *fill*         0x0000278e        0x2
 .text.UDELAY_Calibrate
                0x00002790      0x1d8 rel/udelay.o
                0x00002790                UDELAY_Calibrate
 .text.UDELAY_Delay
                0x00002968       0x28 rel/udelay.o
                0x00002968                UDELAY_Delay
 .text.Display_enable
                0x00002990       0x18 rel/display_ls013b7dh03.o
                0x00002990                Display_enable
 .text.Display_clear
                0x000029a8       0x36 rel/display_ls013b7dh03.o
                0x000029a8                Display_clear
 .text.Display_init
                0x000029de       0x68 rel/display_ls013b7dh03.o
                0x000029de                Display_init
 .text.Display_sendPA
                0x00002a46       0xa2 rel/display_ls013b7dh03.o
                0x00002a46                Display_sendPA
 .text.PAL_SpiInit
                0x00002ae8       0x54 rel/displaypalemlib.o
                0x00002ae8                PAL_SpiInit
 .text.PAL_SpiTransmit
                0x00002b3c       0x54 rel/displaypalemlib.o
                0x00002b3c                PAL_SpiTransmit
 .text.PAL_TimerInit
                0x00002b90        0xa rel/displaypalemlib.o
                0x00002b90                PAL_TimerInit
 .text.PAL_TimerMicroSecondsDelay
                0x00002b9a        0xa rel/displaypalemlib.o
                0x00002b9a                PAL_TimerMicroSecondsDelay
 .text.PAL_GpioInit
                0x00002ba4       0x14 rel/displaypalemlib.o
                0x00002ba4                PAL_GpioInit
 .text.PAL_GpioPinModeSet
                0x00002bb8       0x18 rel/displaypalemlib.o
                0x00002bb8                PAL_GpioPinModeSet
 .text.PAL_GpioPinOutSet
                0x00002bd0       0x1c rel/displaypalemlib.o
                0x00002bd0                PAL_GpioPinOutSet
 .text.PAL_GpioPinOutClear
                0x00002bec       0x1c rel/displaypalemlib.o
                0x00002bec                PAL_GpioPinOutClear
 .text.PAL_GpioPinAutoToggle
                0x00002c08       0xdc rel/displaypalemlib.o
                0x00002c08                PAL_GpioPinAutoToggle
 .text.QHsm_top
                0x00002ce4        0x4 rel/qep_hsm.o
                0x00002ce4                QHsm_top
 .text.QHsm_ctor
                0x00002ce8       0x14 rel/qep_hsm.o
                0x00002ce8                QHsm_ctor
 .text.QHsm_state_entry_
                0x00002cfc       0x10 rel/qep_hsm.o
                0x00002cfc                QHsm_state_entry_
 .text.QHsm_init_
                0x00002d0c       0xa8 rel/qep_hsm.o
                0x00002d0c                QHsm_init_
 .text.QHsm_state_exit_
                0x00002db4       0x18 rel/qep_hsm.o
                0x00002db4                QHsm_state_exit_
 .text.QHsm_tran_
                0x00002dcc      0x11c rel/qep_hsm.o
                0x00002dcc                QHsm_tran_
 .text.QHsm_dispatch_
                0x00002ee8      0x12c rel/qep_hsm.o
                0x00002ee8                QHsm_dispatch_
 .text.QTicker_init_
                0x00003014        0x6 rel/qf_actq.o
                0x00003014                QTicker_init_
 *fill*         0x0000301a        0x2
 .text.QTicker_post_
                0x0000301c       0x4c rel/qf_actq.o
                0x0000301c                QTicker_post_
 .text.QTicker_postLIFO_
                0x00003068       0x10 rel/qf_actq.o
                0x00003068                QTicker_postLIFO_
 .text.QTicker_dispatch_
                0x00003078       0x2e rel/qf_actq.o
                0x00003078                QTicker_dispatch_
 *fill*         0x000030a6        0x2
 .text.QActive_post_
                0x000030a8       0xbc rel/qf_actq.o
                0x000030a8                QActive_post_
 .text.QActive_postLIFO_
                0x00003164       0x84 rel/qf_actq.o
                0x00003164                QActive_postLIFO_
 .text.QActive_get_
                0x000031e8       0x68 rel/qf_actq.o
                0x000031e8                QActive_get_
 .text.QTicker_ctor
                0x00003250       0x1c rel/qf_actq.o
                0x00003250                QTicker_ctor
 .text.QF_poolInit
                0x0000326c       0x58 rel/qf_dyn.o
                0x0000326c                QF_poolInit
 .text.QF_newX_
                0x000032c4       0x7c rel/qf_dyn.o
                0x000032c4                QF_newX_
 .text.QF_gc    0x00003340       0x64 rel/qf_dyn.o
                0x00003340                QF_gc
 .text.QMPool_init
                0x000033a4       0x90 rel/qf_mem.o
                0x000033a4                QMPool_init
 .text.QMPool_get
                0x00003434       0x94 rel/qf_mem.o
                0x00003434                QMPool_get
 .text.QMPool_put
                0x000034c8       0x44 rel/qf_mem.o
                0x000034c8                QMPool_put
 .text.QActive_psInit
                0x0000350c       0x1c rel/qf_ps.o
                0x0000350c                QActive_psInit
 .text.QActive_publish_
                0x00003528       0xa4 rel/qf_ps.o
                0x00003528                QActive_publish_
 .text.QActive_subscribe
                0x000035cc       0x64 rel/qf_ps.o
                0x000035cc                QActive_subscribe
 .text.QF_bzero
                0x00003630       0x12 rel/qf_qact.o
                0x00003630                QF_bzero
 *fill*         0x00003642        0x2
 .text.QActive_ctor
                0x00003644       0x20 rel/qf_qact.o
                0x00003644                QActive_ctor
 .text.QActive_register_
                0x00003664       0xb0 rel/qf_qact.o
                0x00003664                QActive_register_
 .text.QEQueue_init
                0x00003714       0x1e rel/qf_qeq.o
                0x00003714                QEQueue_init
 *fill*         0x00003732        0x2
 .text.QTimeEvt_ctorX
                0x00003734       0x30 rel/qf_time.o
                0x00003734                QTimeEvt_ctorX
 .text.QTimeEvt_armX
                0x00003764       0x6c rel/qf_time.o
                0x00003764                QTimeEvt_armX
 .text.QTimeEvt_disarm
                0x000037d0       0x30 rel/qf_time.o
                0x000037d0                QTimeEvt_disarm
 .text.QTimeEvt_tick_
                0x00003800       0xa4 rel/qf_time.o
                0x00003800                QTimeEvt_tick_
 .text.QF_init  0x000038a4       0x38 rel/qv.o
                0x000038a4                QF_init
 .text.QF_stop  0x000038dc        0x8 rel/qv.o
                0x000038dc                QF_stop
 .text.QF_run   0x000038e4       0x88 rel/qv.o
                0x000038e4                QF_run
 .text.QActive_start_
                0x0000396c       0x48 rel/qv.o
                0x0000396c                QActive_start_
 .text.QV_init  0x000039b4       0x54 rel/qv_port.o
                0x000039b4                QV_init
 .text.__libc_init_array
                0x00003a08       0x48 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)
                0x00003a08                __libc_init_array
 *(.rodata)
 .rodata        0x00003a50        0x9 rel/udelay.o
 *fill*         0x00003a59        0x3
 .rodata        0x00003a5c       0x2b rel/displaypalemlib.o
 *(.rodata*)
 *fill*         0x00003a87        0x1
 .rodata.BSP_updateScore.str1.4
                0x00003a88        0x7 rel/bsp.o
 *fill*         0x00003a8f        0x1
 .rodata.Q_this_module_
                0x00003a90        0x9 rel/bsp.o
 *fill*         0x00003a99        0x3
 .rodata.explosion0_bits
                0x00003a9c        0x4 rel/bsp.o
 .rodata.explosion1_bits
                0x00003aa0        0x4 rel/bsp.o
 .rodata.explosion2_bits
                0x00003aa4        0x5 rel/bsp.o
 *fill*         0x00003aa9        0x3
 .rodata.explosion3_bits
                0x00003aac        0x7 rel/bsp.o
 *fill*         0x00003ab3        0x1
 .rodata.font5x7.0
                0x00003ab4      0x299 rel/bsp.o
 *fill*         0x00003d4d        0x3
 .rodata.l_bitmap
                0x00003d50       0x48 rel/bsp.o
 .rodata.mine1_bits
                0x00003d98        0x3 rel/bsp.o
 *fill*         0x00003d9b        0x1
 .rodata.mine2_bits
                0x00003d9c        0x4 rel/bsp.o
 .rodata.mine2_missile_bits
                0x00003da0        0x3 rel/bsp.o
 *fill*         0x00003da3        0x1
 .rodata.missile_bits
                0x00003da4        0x1 rel/bsp.o
 *fill*         0x00003da5        0x3
 .rodata.ship_bits
                0x00003da8        0x3 rel/bsp.o
 *fill*         0x00003dab        0x1
 .rodata.tickEvt.3
                0x00003dac        0x4 rel/bsp.o
 .rodata.trigEvt.1
                0x00003db0        0x4 rel/bsp.o
 .rodata.Q_this_module_
                0x00003db4        0xd rel/main.o
 *fill*         0x00003dc1        0x3
 .rodata.Q_this_module_
                0x00003dc4        0xe rel/mine1.o
 *fill*         0x00003dd2        0x2
 .rodata.mine1_destroyed.0
                0x00003dd4        0x6 rel/mine1.o
 *fill*         0x00003dda        0x2
 .rodata.mine1_hit.1
                0x00003ddc        0x6 rel/mine1.o
 *fill*         0x00003de2        0x2
 .rodata.Q_this_module_
                0x00003de4        0xe rel/mine2.o
 *fill*         0x00003df2        0x2
 .rodata.mine1_hit.1
                0x00003df4        0x6 rel/mine2.o
 *fill*         0x00003dfa        0x2
 .rodata.mine2_destroyed.0
                0x00003dfc        0x6 rel/mine2.o
 *fill*         0x00003e02        0x2
 .rodata.AO_Missile
                0x00003e04        0x4 rel/missile.o
                0x00003e04                AO_Missile
 .rodata.AO_Ship
                0x00003e08        0x4 rel/ship.o
                0x00003e08                AO_Ship
 .rodata.Tunnel_show_logo.str1.4
                0x00003e0c       0x52 rel/tunnel.o
                                 0x5a (size before relaxing)
 *fill*         0x00003e5e        0x2
 .rodata.Tunnel_game_over.str1.4
                0x00003e60       0x16 rel/tunnel.o
 *fill*         0x00003e76        0x2
 .rodata.Tunnel_screen_saver_show.str1.4
                0x00003e78        0xb rel/tunnel.o
 *fill*         0x00003e83        0x1
 .rodata.AO_Tunnel
                0x00003e84        0x4 rel/tunnel.o
                0x00003e84                AO_Tunnel
 .rodata.Q_this_module_
                0x00003e88        0xf rel/tunnel.o
 *fill*         0x00003e97        0x1
 .rodata.hit.0  0x00003e98        0x4 rel/tunnel.o
 .rodata.hit.1  0x00003e9c        0x4 rel/tunnel.o
 .rodata.takeoff.2
                0x00003ea0        0x4 rel/tunnel.o
 .rodata.Reset_Handler.str1.4
                0x00003ea4        0xe rel/startup_efm32pg1b.o
 *fill*         0x00003eb2        0x2
 .rodata.Q_this_module_
                0x00003eb4        0x8 rel/qep_hsm.o
 .rodata.l_reservedEvt_
                0x00003ebc       0x10 rel/qep_hsm.o
 .rodata.vtable.0
                0x00003ecc        0x8 rel/qep_hsm.o
 .rodata.Q_this_module_
                0x00003ed4        0x8 rel/qf_actq.o
 .rodata.tickEvt.0
                0x00003edc        0x4 rel/qf_actq.o
 .rodata.vtable.1
                0x00003ee0       0x14 rel/qf_actq.o
 .rodata.Q_this_module_
                0x00003ef4        0x7 rel/qf_dyn.o
 *fill*         0x00003efb        0x1
 .rodata.Q_this_module_
                0x00003efc        0x7 rel/qf_mem.o
 *fill*         0x00003f03        0x1
 .rodata.Q_this_module_
                0x00003f04        0x6 rel/qf_ps.o
 *fill*         0x00003f0a        0x2
 .rodata.Q_this_module_
                0x00003f0c        0x8 rel/qf_qact.o
 .rodata.vtable.0
                0x00003f14       0x14 rel/qf_qact.o
 .rodata.Q_this_module_
                0x00003f28        0x8 rel/qf_time.o
 .rodata.Q_this_module_
                0x00003f30        0x3 rel/qv.o
 *(.init)
 *fill*         0x00003f33        0x1
 .init          0x00003f34        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crti.o
                0x00003f34                _init
 .init          0x00003f38        0x8 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtn.o
 *(.fini)
 .fini          0x00003f40        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crti.o
                0x00003f40                _fini
 .fini          0x00003f44        0x8 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtn.o
                0x00003f4c                . = ALIGN (0x4)

.glue_7         0x00003f4c        0x0
 .glue_7        0x00003f4c        0x0 linker stubs

.glue_7t        0x00003f4c        0x0
 .glue_7t       0x00003f4c        0x0 linker stubs

.vfp11_veneer   0x00003f4c        0x0
 .vfp11_veneer  0x00003f4c        0x0 linker stubs

.v4_bx          0x00003f4c        0x0
 .v4_bx         0x00003f4c        0x0 linker stubs

.iplt           0x00003f4c        0x0
 .iplt          0x00003f4c        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o

.preinit_array  0x00003f4c        0x0
                0x00003f4c                PROVIDE (__preinit_array_start = .)
 *(.preinit_array*)
                0x00003f4c                PROVIDE (__preinit_array_end = .)

.init_array     0x00003f4c        0x4
                0x00003f4c                PROVIDE (__init_array_start = .)
 *(SORT_BY_NAME(.init_array.*))
 *(.init_array*)
 .init_array    0x00003f4c        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
                0x00003f50                PROVIDE (__init_array_end = .)

.fini_array     0x00003f50        0x4
                [!provide]                PROVIDE (__fini_array_start = .)
 *(.fini_array*)
 .fini_array    0x00003f50        0x4 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
 *(SORT_BY_NAME(.fini_array.*))
                [!provide]                PROVIDE (__fini_array_end = .)
                0x00003f54                _etext = .

.stack          0x20000000      0x800
                0x20000000                __stack_start__ = .
                0x20000800                . = (. + STACK_SIZE)
 *fill*         0x20000000      0x800
                0x20000800                . = ALIGN (0x4)
                0x20000800                __stack_end__ = .

.data           0x20000800       0x18 load address 0x00003f54
                0x00003f54                __data_load = LOADADDR (.data)
                0x20000800                __data_start = .
 *(.data)
 *(.data*)
 .data.the_Ticker0
                0x20000800        0x4 rel/main.o
                0x20000800                the_Ticker0
 .data.SystemHFXOClock
                0x20000804        0x4 rel/system_efm32pg1b.o
 .data.SystemHfrcoFreq
                0x20000808        0x4 rel/system_efm32pg1b.o
                0x20000808                SystemHfrcoFreq
 .data.SystemLFXOClock
                0x2000080c        0x4 rel/system_efm32pg1b.o
 .data.auxHfrcoFreq
                0x20000810        0x4 rel/em_cmu.o
 .data.loops_per_jiffy
                0x20000814        0x4 rel/udelay.o
                0x20000814                loops_per_jiffy
                0x20000818                . = ALIGN (0x4)
                0x20000818                __data_end__ = .
                0x20000818                _edata = __data_end__

.igot.plt       0x20000818        0x0 load address 0x00003f6c
 .igot.plt      0x20000818        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o

.bss            0x20000818     0x1374 load address 0x00003f6c
                0x20000818                __bss_start__ = .
 *(.bss)
 .bss           0x20000818       0x1c d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
 *(.bss*)
 .bss.buttons.2
                0x20000834        0x8 rel/bsp.o
 .bss.l_fb      0x2000083c      0x810 rel/bsp.o
 .bss.l_rnd     0x2000104c        0x4 rel/bsp.o
 .bss.l_walls   0x20001050      0x770 rel/bsp.o
 .bss.l_ticker0
                0x200017c0       0x20 rel/main.o
 .bss.medPoolSto.3
                0x200017e0       0xa0 rel/main.o
 .bss.missileQueueSto.0
                0x20001880        0x8 rel/main.o
 .bss.shipQueueSto.1
                0x20001888        0xc rel/main.o
 .bss.smlPoolSto.4
                0x20001894       0x28 rel/main.o
 .bss.subscrSto.5
                0x200018bc       0x20 rel/main.o
 .bss.tunnelQueueSto.2
                0x200018dc       0x28 rel/main.o
 .bss.Mine1_inst
                0x20001904       0x50 rel/mine1.o
                0x20001904                Mine1_inst
 .bss.dict_sent.2
                0x20001954        0x1 rel/mine1.o
 *fill*         0x20001955        0x3
 .bss.Mine2_inst
                0x20001958       0x50 rel/mine2.o
                0x20001958                Mine2_inst
 .bss.dict_sent.2
                0x200019a8        0x1 rel/mine2.o
 *fill*         0x200019a9        0x3
 .bss.Missile_inst
                0x200019ac       0x24 rel/missile.o
                0x200019ac                Missile_inst
 .bss.Ship_inst
                0x200019d0       0x28 rel/ship.o
                0x200019d0                Ship_inst
 .bss.Tunnel_inst
                0x200019f8       0x8c rel/tunnel.o
                0x200019f8                Tunnel_inst
 .bss.SystemCoreClock
                0x20001a84        0x4 rel/system_efm32pg1b.o
                0x20001a84                SystemCoreClock
 .bss.cmuHfclkStatus
                0x20001a88        0x2 rel/em_emu.o
 *fill*         0x20001a8a        0x2
 .bss.cmuStatus
                0x20001a8c        0x4 rel/em_emu.o
 .bss.INT_LockCnt
                0x20001a90        0x4 rel/em_int.o
                0x20001a90                INT_LockCnt
 .bss.QF_ePool_
                0x20001a94       0x3c rel/qf_dyn.o
                0x20001a94                QF_ePool_
 .bss.QF_maxPool_
                0x20001ad0        0x4 rel/qf_dyn.o
                0x20001ad0                QF_maxPool_
 .bss.QActive_maxPubSignal_
                0x20001ad4        0x4 rel/qf_ps.o
                0x20001ad4                QActive_maxPubSignal_
 .bss.QActive_subscrList_
                0x20001ad8        0x4 rel/qf_ps.o
                0x20001ad8                QActive_subscrList_
 .bss.QActive_registry_
                0x20001adc       0x84 rel/qf_qact.o
                0x20001adc                QActive_registry_
 .bss.QF_readySet_
                0x20001b60        0x4 rel/qf_qact.o
                0x20001b60                QF_readySet_
 .bss.QTimeEvt_timeEvtHead_
                0x20001b64       0x28 rel/qf_time.o
                0x20001b64                QTimeEvt_timeEvtHead_
 *(COMMON)
                0x20001b8c                . = ALIGN (0x4)
                0x20001b8c                _ebss = .
                0x20001b8c                __bss_end__ = .
                0x20001b8c                __exidx_start = .

.ARM.exidx      0x20001b8c        0x8 load address 0x000052e0
 *(.ARM.exidx* .gnu.linkonce.armexidx.*)
 .ARM.exidx     0x20001b8c        0x8 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_udivmoddi4.o)
                0x20001b94                __exidx_end = .
                [!provide]                PROVIDE (end = _ebss)
                [!provide]                PROVIDE (_end = _ebss)
                [!provide]                PROVIDE (__end__ = _ebss)

.rel.dyn        0x20001b94        0x0 load address 0x000052e8
 .rel.iplt      0x20001b94        0x0 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o

.heap           0x20001b94        0x0
                0x20001b94                __heap_start__ = .
                0x20001b94                . = (. + HEAP_SIZE)
                0x20001b94                . = ALIGN (0x4)
                0x20001b94                __heap_end__ = .

/DISCARD/
 libc.a(*)
 libm.a(*)
 libgcc.a(*)
OUTPUT(rel/game-qv.elf elf32-littlearm)
LOAD linker stubs
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc.a
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libm.a
LOAD d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a

.ARM.attributes
                0x00000000       0x2c
 .ARM.attributes
                0x00000000       0x1e d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crti.o
 .ARM.attributes
                0x0000001e       0x30 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
 .ARM.attributes
                0x0000004e       0x30 rel/bsp.o
 .ARM.attributes
                0x0000007e       0x30 rel/main.o
 .ARM.attributes
                0x000000ae       0x30 rel/mine1.o
 .ARM.attributes
                0x000000de       0x30 rel/mine2.o
 .ARM.attributes
                0x0000010e       0x30 rel/missile.o
 .ARM.attributes
                0x0000013e       0x30 rel/ship.o
 .ARM.attributes
                0x0000016e       0x30 rel/tunnel.o
 .ARM.attributes
                0x0000019e       0x30 rel/startup_efm32pg1b.o
 .ARM.attributes
                0x000001ce       0x30 rel/system_efm32pg1b.o
 .ARM.attributes
                0x000001fe       0x30 rel/em_cmu.o
 .ARM.attributes
                0x0000022e       0x30 rel/em_emu.o
 .ARM.attributes
                0x0000025e       0x30 rel/em_gpio.o
 .ARM.attributes
                0x0000028e       0x30 rel/em_int.o
 .ARM.attributes
                0x000002be       0x30 rel/em_prs.o
 .ARM.attributes
                0x000002ee       0x30 rel/em_rtcc.o
 .ARM.attributes
                0x0000031e       0x30 rel/em_usart.o
 .ARM.attributes
                0x0000034e       0x30 rel/udelay.o
 .ARM.attributes
                0x0000037e       0x30 rel/display_ls013b7dh03.o
 .ARM.attributes
                0x000003ae       0x30 rel/displaypalemlib.o
 .ARM.attributes
                0x000003de       0x30 rel/qep_hsm.o
 .ARM.attributes
                0x0000040e       0x30 rel/qf_actq.o
 .ARM.attributes
                0x0000043e       0x30 rel/qf_dyn.o
 .ARM.attributes
                0x0000046e       0x30 rel/qf_mem.o
 .ARM.attributes
                0x0000049e       0x30 rel/qf_ps.o
 .ARM.attributes
                0x000004ce       0x30 rel/qf_qact.o
 .ARM.attributes
                0x000004fe       0x30 rel/qf_qeq.o
 .ARM.attributes
                0x0000052e       0x30 rel/qf_time.o
 .ARM.attributes
                0x0000055e       0x30 rel/qv.o
 .ARM.attributes
                0x0000058e       0x30 rel/qv_port.o
 .ARM.attributes
                0x000005be       0x1e d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_aeabi_uldivmod.o)
 .ARM.attributes
                0x000005dc       0x30 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_udivmoddi4.o)
 .ARM.attributes
                0x0000060c       0x1e d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_dvmd_tls.o)
 .ARM.attributes
                0x0000062a       0x30 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)
 .ARM.attributes
                0x0000065a       0x1e d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtn.o

.comment        0x00000000       0x49
 .comment       0x00000000       0x49 rel/bsp.o
                                 0x4a (size before relaxing)
 .comment       0x00000049       0x4a rel/main.o
 .comment       0x00000049       0x4a rel/mine1.o
 .comment       0x00000049       0x4a rel/mine2.o
 .comment       0x00000049       0x4a rel/missile.o
 .comment       0x00000049       0x4a rel/ship.o
 .comment       0x00000049       0x4a rel/tunnel.o
 .comment       0x00000049       0x4a rel/startup_efm32pg1b.o
 .comment       0x00000049       0x4a rel/system_efm32pg1b.o
 .comment       0x00000049       0x4a rel/em_cmu.o
 .comment       0x00000049       0x4a rel/em_emu.o
 .comment       0x00000049       0x4a rel/em_gpio.o
 .comment       0x00000049       0x4a rel/em_int.o
 .comment       0x00000049       0x4a rel/em_prs.o
 .comment       0x00000049       0x4a rel/em_rtcc.o
 .comment       0x00000049       0x4a rel/em_usart.o
 .comment       0x00000049       0x4a rel/udelay.o
 .comment       0x00000049       0x4a rel/display_ls013b7dh03.o
 .comment       0x00000049       0x4a rel/displaypalemlib.o
 .comment       0x00000049       0x4a rel/qep_hsm.o
 .comment       0x00000049       0x4a rel/qf_actq.o
 .comment       0x00000049       0x4a rel/qf_dyn.o
 .comment       0x00000049       0x4a rel/qf_mem.o
 .comment       0x00000049       0x4a rel/qf_ps.o
 .comment       0x00000049       0x4a rel/qf_qact.o
 .comment       0x00000049       0x4a rel/qf_qeq.o
 .comment       0x00000049       0x4a rel/qf_time.o
 .comment       0x00000049       0x4a rel/qv.o
 .comment       0x00000049       0x4a rel/qv_port.o

.debug_frame    0x00000000       0x8c
 .debug_frame   0x00000000       0x2c d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_aeabi_uldivmod.o)
 .debug_frame   0x0000002c       0x34 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_udivmoddi4.o)
 .debug_frame   0x00000060       0x2c d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)

Cross Reference Table

Symbol                                            File
ACMP0_IRQHandler                                  rel/startup_efm32pg1b.o
ADC0_IRQHandler                                   rel/startup_efm32pg1b.o
AO_Missile                                        rel/missile.o
                                                  rel/tunnel.o
                                                  rel/ship.o
                                                  rel/mine2.o
                                                  rel/mine1.o
                                                  rel/main.o
AO_Ship                                           rel/ship.o
                                                  rel/tunnel.o
                                                  rel/missile.o
                                                  rel/mine2.o
                                                  rel/mine1.o
                                                  rel/main.o
AO_Tunnel                                         rel/tunnel.o
                                                  rel/ship.o
                                                  rel/missile.o
                                                  rel/mine2.o
                                                  rel/mine1.o
                                                  rel/main.o
                                                  rel/bsp.o
BSP_advanceWalls                                  rel/bsp.o
                                                  rel/tunnel.o
BSP_clearFB                                       rel/bsp.o
                                                  rel/tunnel.o
BSP_clearWalls                                    rel/bsp.o
                                                  rel/tunnel.o
BSP_displayOff                                    rel/bsp.o
                                                  rel/tunnel.o
BSP_displayOn                                     rel/bsp.o
                                                  rel/tunnel.o
BSP_doBitmapsOverlap                              rel/bsp.o
                                                  rel/mine2.o
                                                  rel/mine1.o
BSP_init                                          rel/bsp.o
                                                  rel/main.o
BSP_isThrottle                                    rel/bsp.o
                                                  rel/ship.o
BSP_isWallHit                                     rel/bsp.o
                                                  rel/tunnel.o
BSP_paintBitmap                                   rel/bsp.o
                                                  rel/tunnel.o
BSP_paintString                                   rel/bsp.o
                                                  rel/tunnel.o
BSP_random                                        rel/bsp.o
                                                  rel/tunnel.o
BSP_randomSeed                                    rel/bsp.o
                                                  rel/tunnel.o
BSP_updateScore                                   rel/bsp.o
                                                  rel/tunnel.o
BSP_updateScreen                                  rel/bsp.o
                                                  rel/tunnel.o
BusFault_Handler                                  rel/startup_efm32pg1b.o
CMU_AUXHFRCOBandGet                               rel/em_cmu.o
CMU_AUXHFRCOBandSet                               rel/em_cmu.o
CMU_Calibrate                                     rel/em_cmu.o
CMU_CalibrateConfig                               rel/em_cmu.o
CMU_CalibrateCountGet                             rel/em_cmu.o
CMU_ClockDivGet                                   rel/em_cmu.o
                                                  rel/udelay.o
CMU_ClockDivSet                                   rel/em_cmu.o
                                                  rel/udelay.o
CMU_ClockEnable                                   rel/em_cmu.o
                                                  rel/displaypalemlib.o
                                                  rel/udelay.o
                                                  rel/bsp.o
CMU_ClockFreqGet                                  rel/em_cmu.o
                                                  rel/displaypalemlib.o
                                                  rel/em_usart.o
CMU_ClockPrescGet                                 rel/em_cmu.o
CMU_ClockPrescSet                                 rel/em_cmu.o
CMU_ClockSelectGet                                rel/em_cmu.o
                                                  rel/udelay.o
CMU_ClockSelectSet                                rel/em_cmu.o
                                                  rel/displaypalemlib.o
                                                  rel/udelay.o
CMU_FreezeEnable                                  rel/em_cmu.o
CMU_HFRCOBandGet                                  rel/em_cmu.o
CMU_HFRCOBandSet                                  rel/em_cmu.o
CMU_HFXOInit                                      rel/em_cmu.o
CMU_IRQHandler                                    rel/startup_efm32pg1b.o
CMU_LCDClkFDIVGet                                 rel/em_cmu.o
CMU_LCDClkFDIVSet                                 rel/em_cmu.o
CMU_LFXOInit                                      rel/em_cmu.o
CMU_OscillatorEnable                              rel/em_cmu.o
                                                  rel/udelay.o
CMU_OscillatorTuningGet                           rel/em_cmu.o
CMU_OscillatorTuningSet                           rel/em_cmu.o
CMU_PCNTClockExternalGet                          rel/em_cmu.o
CMU_PCNTClockExternalSet                          rel/em_cmu.o
CRYOTIMER_IRQHandler                              rel/startup_efm32pg1b.o
CRYPTO_IRQHandler                                 rel/startup_efm32pg1b.o
DebugMon_Handler                                  rel/startup_efm32pg1b.o
Default_Handler                                   rel/startup_efm32pg1b.o
Display_clear                                     rel/display_ls013b7dh03.o
Display_enable                                    rel/display_ls013b7dh03.o
                                                  rel/bsp.o
Display_init                                      rel/display_ls013b7dh03.o
                                                  rel/bsp.o
Display_refresh                                   rel/display_ls013b7dh03.o
Display_sendPA                                    rel/display_ls013b7dh03.o
                                                  rel/bsp.o
EMU_DCDCInit                                      rel/em_emu.o
EMU_DCDCLnRcoBandSet                              rel/em_emu.o
EMU_DCDCModeSet                                   rel/em_emu.o
EMU_DCDCOptimizeSlice                             rel/em_emu.o
EMU_DCDCOutputVoltageSet                          rel/em_emu.o
EMU_DCDCPowerOff                                  rel/em_emu.o
EMU_EM23Init                                      rel/em_emu.o
EMU_EM4Init                                       rel/em_emu.o
EMU_EnterEM2                                      rel/em_emu.o
EMU_EnterEM3                                      rel/em_emu.o
EMU_EnterEM4                                      rel/em_emu.o
EMU_IRQHandler                                    rel/startup_efm32pg1b.o
EMU_MemPwrDown                                    rel/em_emu.o
EMU_UpdateOscConfig                               rel/em_emu.o
                                                  rel/em_cmu.o
EMU_VmonChannelStatusGet                          rel/em_emu.o
EMU_VmonEnable                                    rel/em_emu.o
EMU_VmonHystInit                                  rel/em_emu.o
EMU_VmonInit                                      rel/em_emu.o
FPUEH_IRQHandler                                  rel/startup_efm32pg1b.o
GPIO_DbgLocationSet                               rel/em_gpio.o
GPIO_DriveStrengthSet                             rel/em_gpio.o
GPIO_EM4EnablePinWakeup                           rel/em_gpio.o
GPIO_EVEN_IRQHandler                              rel/bsp.o
GPIO_ExtIntConfig                                 rel/em_gpio.o
GPIO_ODD_IRQHandler                               rel/startup_efm32pg1b.o
GPIO_PinModeGet                                   rel/em_gpio.o
GPIO_PinModeSet                                   rel/em_gpio.o
                                                  rel/displaypalemlib.o
                                                  rel/bsp.o
HardFault_Handler                                 rel/startup_efm32pg1b.o
I2C0_IRQHandler                                   rel/startup_efm32pg1b.o
IDAC0_IRQHandler                                  rel/startup_efm32pg1b.o
INT_LockCnt                                       rel/em_int.o
                                                  rel/udelay.o
LDMA_IRQHandler                                   rel/startup_efm32pg1b.o
LETIMER0_IRQHandler                               rel/startup_efm32pg1b.o
LEUART0_IRQHandler                                rel/startup_efm32pg1b.o
MSC_IRQHandler                                    rel/startup_efm32pg1b.o
MemManage_Handler                                 rel/startup_efm32pg1b.o
Mine1_ctor_call                                   rel/mine1.o
                                                  rel/tunnel.o
Mine1_inst                                        rel/mine1.o
Mine2_ctor_call                                   rel/mine2.o
                                                  rel/tunnel.o
Mine2_inst                                        rel/mine2.o
Missile_ctor_call                                 rel/missile.o
                                                  rel/main.o
Missile_inst                                      rel/missile.o
NMI_Handler                                       rel/startup_efm32pg1b.o
PAL_GpioInit                                      rel/displaypalemlib.o
                                                  rel/display_ls013b7dh03.o
PAL_GpioPinAutoToggle                             rel/displaypalemlib.o
                                                  rel/display_ls013b7dh03.o
PAL_GpioPinModeSet                                rel/displaypalemlib.o
                                                  rel/display_ls013b7dh03.o
PAL_GpioPinOutClear                               rel/displaypalemlib.o
                                                  rel/display_ls013b7dh03.o
PAL_GpioPinOutSet                                 rel/displaypalemlib.o
                                                  rel/display_ls013b7dh03.o
PAL_GpioPinOutToggle                              rel/displaypalemlib.o
PAL_GpioShutdown                                  rel/displaypalemlib.o
PAL_SpiInit                                       rel/displaypalemlib.o
                                                  rel/display_ls013b7dh03.o
PAL_SpiShutdown                                   rel/displaypalemlib.o
PAL_SpiTransmit                                   rel/displaypalemlib.o
                                                  rel/display_ls013b7dh03.o
PAL_TimerInit                                     rel/displaypalemlib.o
                                                  rel/display_ls013b7dh03.o
PAL_TimerMicroSecondsDelay                        rel/displaypalemlib.o
                                                  rel/display_ls013b7dh03.o
PAL_TimerShutdown                                 rel/displaypalemlib.o
PCNT0_IRQHandler                                  rel/startup_efm32pg1b.o
PRS_SourceAsyncSignalSet                          rel/em_prs.o
                                                  rel/displaypalemlib.o
PRS_SourceSignalSet                               rel/em_prs.o
PendSV_Handler                                    rel/startup_efm32pg1b.o
QActive_ctor                                      rel/qf_qact.o
                                                  rel/qf_actq.o
                                                  rel/tunnel.o
                                                  rel/ship.o
                                                  rel/missile.o
QActive_defer                                     rel/qf_defer.o
QActive_flushDeferred                             rel/qf_defer.o
QActive_get_                                      rel/qf_actq.o
                                                  rel/qv.o
QActive_maxPubSignal_                             rel/qf_ps.o
QActive_postLIFO_                                 rel/qf_actq.o
                                                  rel/qf_qmact.o
                                                  rel/qf_qact.o
QActive_post_                                     rel/qf_actq.o
                                                  rel/qf_qmact.o
                                                  rel/qf_qact.o
QActive_psInit                                    rel/qf_ps.o
                                                  rel/main.o
QActive_publish_                                  rel/qf_ps.o
                                                  rel/bsp.o
QActive_recall                                    rel/qf_defer.o
QActive_register_                                 rel/qf_qact.o
                                                  rel/qv.o
QActive_registry_                                 rel/qf_qact.o
                                                  rel/qv.o
                                                  rel/qf_ps.o
                                                  rel/qf_actq.o
QActive_start_                                    rel/qv.o
                                                  rel/qf_qmact.o
                                                  rel/qf_qact.o
                                                  rel/qf_actq.o
QActive_subscrList_                               rel/qf_ps.o
QActive_subscribe                                 rel/qf_ps.o
                                                  rel/tunnel.o
                                                  rel/ship.o
                                                  rel/missile.o
QActive_unregister_                               rel/qf_qact.o
QActive_unsubscribe                               rel/qf_ps.o
QActive_unsubscribeAll                            rel/qf_ps.o
QEQueue_get                                       rel/qf_qeq.o
                                                  rel/qf_defer.o
QEQueue_init                                      rel/qf_qeq.o
                                                  rel/qv.o
QEQueue_post                                      rel/qf_qeq.o
                                                  rel/qf_defer.o
QEQueue_postLIFO                                  rel/qf_qeq.o
QF_bzero                                          rel/qf_qact.o
                                                  rel/qv.o
                                                  rel/qf_qmact.o
                                                  rel/qf_ps.o
QF_deleteRef_                                     rel/qf_dyn.o
QF_ePool_                                         rel/qf_dyn.o
QF_gc                                             rel/qf_dyn.o
                                                  rel/qv.o
                                                  rel/qf_ps.o
                                                  rel/qf_defer.o
                                                  rel/qf_actq.o
QF_getPoolMin                                     rel/qf_dyn.o
QF_getQueueMin                                    rel/qf_actq.o
QF_init                                           rel/qv.o
                                                  rel/main.o
QF_intLock_                                       rel/qf_qact.o
QF_intNest_                                       rel/qf_qact.o
QF_maxPool_                                       rel/qf_dyn.o
                                                  rel/qv.o
QF_newRef_                                        rel/qf_dyn.o
QF_newX_                                          rel/qf_dyn.o
                                                  rel/ship.o
                                                  rel/missile.o
                                                  rel/mine2.o
                                                  rel/mine1.o
                                                  rel/bsp.o
QF_onCleanup                                      rel/bsp.o
                                                  rel/qv.o
QF_onStartup                                      rel/bsp.o
                                                  rel/qv.o
QF_poolGetMaxBlockSize                            rel/qf_dyn.o
QF_poolInit                                       rel/qf_dyn.o
                                                  rel/main.o
QF_readySet_                                      rel/qf_qact.o
                                                  rel/qv.o
                                                  rel/qf_actq.o
QF_run                                            rel/qv.o
                                                  rel/main.o
QF_stop                                           rel/qv.o
                                                  rel/tunnel.o
QHsm_childState                                   rel/qep_hsm.o
QHsm_ctor                                         rel/qep_hsm.o
                                                  rel/qf_qact.o
                                                  rel/mine2.o
                                                  rel/mine1.o
QHsm_dispatch_                                    rel/qep_hsm.o
                                                  rel/qf_qact.o
QHsm_init_                                        rel/qep_hsm.o
                                                  rel/qf_qact.o
QHsm_isIn                                         rel/qep_hsm.o
QHsm_state_entry_                                 rel/qep_hsm.o
QHsm_state_exit_                                  rel/qep_hsm.o
QHsm_top                                          rel/qep_hsm.o
                                                  rel/tunnel.o
                                                  rel/ship.o
                                                  rel/missile.o
                                                  rel/mine2.o
                                                  rel/mine1.o
QHsm_tran_                                        rel/qep_hsm.o
QMActive_ctor                                     rel/qf_qmact.o
QMPool_get                                        rel/qf_mem.o
                                                  rel/qf_dyn.o
QMPool_init                                       rel/qf_mem.o
                                                  rel/qf_dyn.o
QMPool_put                                        rel/qf_mem.o
                                                  rel/qf_dyn.o
QMsm_childStateObj                                rel/qep_msm.o
QMsm_ctor                                         rel/qep_msm.o
                                                  rel/qf_qmact.o
QMsm_dispatch_                                    rel/qep_msm.o
                                                  rel/qf_qmact.o
QMsm_enterHistory_                                rel/qep_msm.o
QMsm_execTatbl_                                   rel/qep_msm.o
QMsm_exitToTranSource_                            rel/qep_msm.o
QMsm_init_                                        rel/qep_msm.o
                                                  rel/qf_qmact.o
QMsm_isInState                                    rel/qep_msm.o
QMsm_stateObj                                     rel/qep_msm.o
QP_versionStr                                     rel/qep_hsm.o
QTicker_ctor                                      rel/qf_actq.o
                                                  rel/main.o
QTicker_dispatch_                                 rel/qf_actq.o
QTicker_init_                                     rel/qf_actq.o
QTicker_postLIFO_                                 rel/qf_actq.o
QTicker_post_                                     rel/qf_actq.o
QTimeEvt_armX                                     rel/qf_time.o
                                                  rel/tunnel.o
QTimeEvt_ctorX                                    rel/qf_time.o
                                                  rel/tunnel.o
QTimeEvt_currCtr                                  rel/qf_time.o
QTimeEvt_disarm                                   rel/qf_time.o
                                                  rel/tunnel.o
QTimeEvt_noActive                                 rel/qf_time.o
QTimeEvt_rearm                                    rel/qf_time.o
QTimeEvt_tick_                                    rel/qf_time.o
                                                  rel/qf_actq.o
QTimeEvt_timeEvtHead_                             rel/qf_time.o
                                                  rel/qv.o
QTimeEvt_wasDisarmed                              rel/qf_time.o
QV_init                                           rel/qv_port.o
                                                  rel/qv.o
QV_onIdle                                         rel/bsp.o
                                                  rel/qv.o
Q_BUILD_DATE                                      rel/qstamp.o
Q_BUILD_TIME                                      rel/qstamp.o
Q_onAssert                                        rel/bsp.o
                                                  rel/qv.o
                                                  rel/qf_time.o
                                                  rel/qf_qeq.o
                                                  rel/qf_qact.o
                                                  rel/qf_ps.o
                                                  rel/qf_mem.o
                                                  rel/qf_dyn.o
                                                  rel/qf_defer.o
                                                  rel/qf_actq.o
                                                  rel/qep_msm.o
                                                  rel/qep_hsm.o
                                                  rel/startup_efm32pg1b.o
                                                  rel/tunnel.o
                                                  rel/mine2.o
                                                  rel/mine1.o
                                                  rel/main.o
RTCC_ChannelInit                                  rel/em_rtcc.o
                                                  rel/displaypalemlib.o
RTCC_Enable                                       rel/em_rtcc.o
                                                  rel/displaypalemlib.o
                                                  rel/udelay.o
RTCC_IRQHandler                                   rel/startup_efm32pg1b.o
RTCC_Init                                         rel/em_rtcc.o
                                                  rel/displaypalemlib.o
                                                  rel/udelay.o
RTCC_Reset                                        rel/em_rtcc.o
RTCC_StatusClear                                  rel/em_rtcc.o
Reset_Handler                                     rel/startup_efm32pg1b.o
SVC_Handler                                       rel/startup_efm32pg1b.o
SYSTEM_ChipRevisionGet                            rel/em_system.o
                                                  rel/em_emu.o
Ship_ctor_call                                    rel/ship.o
                                                  rel/main.o
Ship_inst                                         rel/ship.o
SysTick_Handler                                   rel/bsp.o
SystemCoreClock                                   rel/system_efm32pg1b.o
                                                  rel/bsp.o
SystemCoreClockGet                                rel/system_efm32pg1b.o
                                                  rel/em_emu.o
                                                  rel/em_cmu.o
                                                  rel/bsp.o
SystemHFClockGet                                  rel/system_efm32pg1b.o
                                                  rel/em_cmu.o
SystemHFXOClockGet                                rel/system_efm32pg1b.o
SystemHFXOClockSet                                rel/system_efm32pg1b.o
SystemHfrcoFreq                                   rel/system_efm32pg1b.o
                                                  rel/em_cmu.o
SystemInit                                        rel/system_efm32pg1b.o
                                                  rel/startup_efm32pg1b.o
SystemLFRCOClockGet                               rel/system_efm32pg1b.o
                                                  rel/em_cmu.o
SystemLFXOClockGet                                rel/system_efm32pg1b.o
                                                  rel/em_cmu.o
SystemLFXOClockSet                                rel/system_efm32pg1b.o
SystemMaxCoreClockGet                             rel/system_efm32pg1b.o
                                                  rel/em_cmu.o
SystemULFRCOClockGet                              rel/system_efm32pg1b.o
                                                  rel/em_cmu.o
TIMER0_IRQHandler                                 rel/startup_efm32pg1b.o
TIMER1_IRQHandler                                 rel/startup_efm32pg1b.o
Tunnel_ctor_call                                  rel/tunnel.o
                                                  rel/main.o
Tunnel_inst                                       rel/tunnel.o
UDELAY_Calibrate                                  rel/udelay.o
                                                  rel/displaypalemlib.o
UDELAY_Delay                                      rel/udelay.o
                                                  rel/displaypalemlib.o
USART0_RX_IRQHandler                              rel/bsp.o
USART0_TX_IRQHandler                              rel/startup_efm32pg1b.o
USART1_RX_IRQHandler                              rel/startup_efm32pg1b.o
USART1_TX_IRQHandler                              rel/startup_efm32pg1b.o
USART_BaudrateAsyncSet                            rel/em_usart.o
USART_BaudrateCalc                                rel/em_usart.o
USART_BaudrateGet                                 rel/em_usart.o
USART_BaudrateSyncSet                             rel/em_usart.o
USART_Enable                                      rel/em_usart.o
                                                  rel/displaypalemlib.o
USART_InitAsync                                   rel/em_usart.o
USART_InitI2s                                     rel/em_usart.o
USART_InitPrsTrigger                              rel/em_usart.o
USART_InitSync                                    rel/em_usart.o
                                                  rel/displaypalemlib.o
USART_Reset                                       rel/em_usart.o
USART_Rx                                          rel/em_usart.o
USART_RxDouble                                    rel/em_usart.o
USART_RxDoubleExt                                 rel/em_usart.o
USART_RxExt                                       rel/em_usart.o
USART_SpiTransfer                                 rel/em_usart.o
USART_Tx                                          rel/em_usart.o
                                                  rel/displaypalemlib.o
USART_TxDouble                                    rel/em_usart.o
                                                  rel/displaypalemlib.o
USART_TxDoubleExt                                 rel/em_usart.o
USART_TxExt                                       rel/em_usart.o
USARTn_InitIrDA                                   rel/em_usart.o
UsageFault_Handler                                rel/startup_efm32pg1b.o
WDOG0_IRQHandler                                  rel/startup_efm32pg1b.o
__aeabi_idiv0                                     d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_dvmd_tls.o)
__aeabi_ldiv0                                     d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_dvmd_tls.o)
                                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_aeabi_uldivmod.o)
__aeabi_uldivmod                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_aeabi_uldivmod.o)
                                                  rel/em_usart.o
__bss_end__                                       rel/startup_efm32pg1b.o
                                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
__bss_start__                                     rel/startup_efm32pg1b.o
                                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
__call_exitprocs                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o)
__data_end__                                      rel/startup_efm32pg1b.o
__data_load                                       rel/startup_efm32pg1b.o
__data_start                                      rel/startup_efm32pg1b.o
__deregister_frame_info                           d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
__dso_handle                                      d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
__init_array_end                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)
__init_array_start                                d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)
__libc_fini_array                                 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
__libc_init_array                                 d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)
                                                  rel/startup_efm32pg1b.o
                                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
__preinit_array_end                               d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)
__preinit_array_start                             d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)
__register_frame_info                             d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crtbegin.o
__sf_fake_stderr                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
__sf_fake_stdin                                   d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
__sf_fake_stdout                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
__stack                                           d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
__stack_end__                                     rel/startup_efm32pg1b.o
__udivmoddi4                                      d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_udivmoddi4.o)
                                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp\libgcc.a(_aeabi_uldivmod.o)
_exit                                             d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libnosys.a(_exit.o)
                                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o)
_fini                                             d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crti.o
_global_impure_ptr                                d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
                                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o)
_impure_ptr                                       d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-impure.o)
_init                                             d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/thumb/v7e-m+dp/softfp/crti.o
                                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-init.o)
_mainCRTStartup                                   d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
_stack_init                                       d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
_start                                            d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
assert_failed                                     rel/startup_efm32pg1b.o
atexit                                            d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
dummy                                             rel/qf_act.o
errataFixDcdcHsState                              rel/em_emu.o
exit                                              d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-exit.o)
                                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
g_pfnVectors                                      rel/startup_efm32pg1b.o
hardware_init_hook                                d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
loops_per_jiffy                                   rel/udelay.o
main                                              rel/main.o
                                                  rel/startup_efm32pg1b.o
                                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
memset                                            d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp\libc_nano.a(lib_a-memset.o)
                                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
software_init_hook                                rel/startup_efm32pg1b.o
                                                  d:/qp/qtools/gnu_arm-none-eabi/bin/../lib/gcc/arm-none-eabi/10.3.1/../../../../arm-none-eabi/lib/thumb/v7e-m+dp/softfp/crt0.o
the_Ticker0                                       rel/main.o
                                                  rel/bsp.o
```

## 参考

- [ROM, FLASH 和 RAM 的区别](https://zhuanlan.zhihu.com/p/38339306)
- [闪存 - 维基百科，自由的百科全书](https://zh.wikipedia.org/zh-cn/%E9%97%AA%E5%AD%98)
- [(深入理解计算机系统) bss 段，data 段、text 段、堆(heap)和栈(stack)](https://www.cnblogs.com/yanghong-hnu/p/4705755.html)
- [数据段（BSS 段、DATA 段）、代码段（.RODATA）、堆栈段的区别](https://www.cnblogs.com/-gebi-laowang/p/7325412.html)
- [C 语言函数内 static 关键字详解](https://blog.csdn.net/liutgnukernel/article/details/51472176)
- [.bss - wikipedia](https://en.wikipedia.org/wiki/.bss)
- [XIP 技术总结](https://zhuanlan.zhihu.com/p/368276428)
- [Static storage union and named members initialization in C language - Stack Overflow](https://stackoverflow.com/questions/54307858/static-storage-union-and-named-members-initialization-in-c-language)
- [充分理解 Linux GCC 链接生成的 Map 文件](https://zhuanlan.zhihu.com/p/502051758)
