---
title: "Linux内核学习笔记之调试"
author: Jinkai
date: 2023-03-21 09:00:00 +0800
published: false
categories: [学习笔记]
tags: [kernel, Linux]
---

## 内核调试配置选项

```kconfig
CONFIG_PREEMPT=y
CONFIG_DEBUG_KERNEL=y
CONFIG_KALLSYMS=y
CONFIG_DEBUG_SPINOCK_SLEEP=y
```

## 神奇系统请求键

神奇系统请求键(Magic SysRq key)可以通过定义`CONFIG_MAGIC_SYSRQ`配置选项来启用。

当该功能被启用的时候，无论内核处于什么状态（比如**无响应**或卡死），都可以通过特殊的组合键跟内核进行通信。

除了配置选项外，还需要运行时的配置：

```shell
echo 1 > /proc/sys/kernel/sysrq
```

具体组合键见`Documentation/sysrq.txt`，下面截取一部分做预览:

```plaintext
*  How do I use the magic SysRq key?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
On x86   - You press the key combo 'ALT-SysRq-<command key>'. Note - Some
           keyboards may not have a key labeled 'SysRq'. The 'SysRq' key is
           also known as the 'Print Screen' key. Also some keyboards cannot
	   handle so many keys being pressed at the same time, so you might
	   have better luck with "press Alt", "press SysRq", "release SysRq",
	   "press <command key>", release everything.

On SPARC - You press 'ALT-STOP-<command key>', I believe.
```

```plaintext
*  What are the 'command' keys?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'b'     - Will immediately reboot the system without syncing or unmounting
          your disks.

'c'	- Will perform a system crash by a NULL pointer dereference.
          A crashdump will be taken if configured.

'd'	- Shows all locks that are held.

'e'     - Send a SIGTERM to all processes, except for init.

'f'	- Will call oom_kill to kill a memory hog process.

```

## gdb 调试器

使用 gdb 调试器调试内核和调试进程不太一样，只能进行基础操作，不能**修改内核数据**、单步调试、打断点等。

打开内核文件：

```shell
gdb vmlinux /proc/kcore
```

vmlinux 是未经压缩的内核镜像（非 zImage 或 bzImage）

打印一个变量的值:

```shell
p global_variable
```

反汇编一个函数:

```shell
disassemble function
```

如果在内核编译时使用 `-g` 参数，可以打印更多信息

### kgdb

可以在被调试内核上打上**kgdb 调试补丁**，运行在**被调试机**上，然后通过**串口**连接到**调试机**上，调试机就能用 gdb 连接被调试机上的内核并使用所有 gdb 的功能。

## 参考

- [Linux 内核设计与实现（第三版）第十八章](https://www.amazon.com/Linux-Kernel-Development-Robert-Love/dp/0672329468/ref=as_li_ss_tl?ie=UTF8&tag=roblov-20)
- [Robert Love](https://rlove.org/)
