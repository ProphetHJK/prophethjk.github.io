---
title: "Linux内核学习笔记之设备和模块"
author: Jinkai
date: 2023-03-15 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [kernel, Linux]
---

## 设备类型

在 Linux 以及所有 Unix 系统中，设备被分为以下三种类型：

- 块设备
- 字符设备
- 网络设备

前两个设备在[设备的分类](/posts/linux-kernel-block-io/#%E8%AE%BE%E5%A4%87%E7%9A%84%E5%88%86%E7%B1%BB)中有提到

网络设备最常见的类型有时也以以太网设备(ethernet devices)来称呼，它提供了对网络(例如 Internet)的访问，这是通过一个物理适配器(如你的笔记本电脑的 802.11 卡)和一种特定的协议(如 IP 协议)进行的。网络设备打破了 Unix 的“所有东西都是文件”的设计原则，它不是通过设备节点来访问，而是通过套接字 API 这样的特殊接口来访问。

### 伪设备

有些设备驱动是**虚拟的**，仅提供访问内核功能而已。我们称为“`伪设备`”(pseudo device)，最常见的如:

- **内核随机数发生器**(通过`/dev/random` 和 `/dev/urandom` 访问)
- **空设备**(通过 `/dev/null` 访问)
- **零设备**(通过 `/dev/zero` 访问)
- **满设备**(通过 `/dev/full` 访问)
- **内存设备**(通过 `/dev/mem` 访问)

### 杂项设备

“杂项设备”(miscellaneous device)，通常简写为`miscdev`，它实际上是对字符设备的封装，方便使用。杂项设备使驱动程序开发者能够很容易地表示一个简单设备。

## 模块

尽管 Linux 是“**宏内核**”(monolithic)的操作系统，但是 Linux 内核是模块化组成的，它允许内核在运行时**动态**地向其中插入或从中删除代码（当然模块也运行在内核空间，其实和内核是一个整体）。

> **宏内核和微内核**
>
> 宏内核是指整个内核运行在同一个空间中，也就是内核空间，所有资源都能直接共享，可以理解为是一个进程。而微内核是指将各个功能模块分散在不同的进程中，功能模块之间需要通过进程间通信的方式交流信息，windows NT 属于微内核。
>
> 微内核的优点是模块化带来的高可扩展性和隔离安全性，每个模块可以单独更新或裁剪，不同模块之间不会因为漏洞或 bug 干扰彼此，但缺点就是进程间通信效率远不如直接的内存共享。

这些代码(包括相关的子例程、数据、函数和入口和函数出口)被一并组合在一个单独的二进制镜像中，即所谓的可装载内核模块中，或简称为**模块**。

支持模块的好处是基本**内核镜像**可以尽可能地小，因为可选的功能和驱动程序可以利用模块形式再提供。模块允许我们方便地删除和重新载入内核代码，也方便了调试工作。而且当**热播拔**新设备时，可通过命令载入新的驱动程序。

### Hello，World 模块示例

```c
/*
 * hello.c – The Hello, World! Kernel Module
 */
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
/*
 * hello_init – the init function, called when the module is loaded.
 * Returns zero if successfully loaded, nonzero otherwise.
 */
static int hello_init(void)
{
	printk(KERN_ALERT "I bear a charmed life.\n");
	return 0;
}
/*
 * hello_exit – the exit function, called when the module is removed.
 */
static void hello_exit(void)
{
	printk(KERN_ALERT "Out, out, brief candle!\n");
}
module_init(hello_init); // 注册 模块初始化函数，当模块被装载时会调用
module_exit(hello_exit); // 注册 模块退出函数，当模块被卸载时会调用
module_param(helloarg, bool, 0644); // 声明模块所需参数，可在模块装载时传入
MODULE_LICENSE("GPL"); // 模块版权
MODULE_AUTHOR("Shakespeare"); // 作者
MODULE_DESCRIPTION("A Hello, World Module"); // 描述
```

### 构建模块

模块相关的代码可以防止内核源码树中也可以放在外面。

#### 放在内核源代码树中

- **字符设备**存在于`drivers/char/`目录下
- **块设备**存放在`drivers/block/`目录下
- **USB 设备**则存放在`drivers/usb/`目录下

以字符设备`fishing`为例，编辑 `drivers/char/Makefile` 并加入:

```makefile
obj-m += fishing/
# 如果使用自定义的编译选项如CONFIG_FISHING_POLE，则使用下面的命令
# obj-$(CONFIG_FISHING_POLE) += fishing/
```

在`drivers/char/fishing/`下，需要添加一个新`Makefile`文件:

```makefile
obj-m += fishing.o
# 如果使用自定义的编译选项如CONFIG_FISHING_POLE，则使用下面的命令
# obj-$(CONFIG_FISHING_POLE) += fishing.o
```

如果后续新增功能，可以把相关源文件都放在`drivers/char/fishing/`目录下，这样它们会一起被编译和连接到`fishing.o`，修改`drivers/char/fishing/Makefile`：

```makefile
obj-m += fishing.o
fishing-objs := fishing-main.o fishing-line.o
```

这样编译内核时，也会自动编译该模块，最终编译编译连接完的文件名为`fishing.ko`

#### 放在内核代码外

其实基本和[放在内核源代码树中](#放在内核源代码树中)差不多，假设放在`/home/dev/fishing/`目录中，那么修改`/home/dev/fishing/Makefile`:

```makefile
obj-m += fishing.o
fishing-objs := fishing-main.o fishing-line.o
```

编译时需要在`/home/dev/fishing/`目录下，然后执行：

```shell
make -C /mnt/disk/kernelsrc/ SUBDIRS=$PWD modules
```

这里的`/mnt/disk/kernelsrc/`就是内核源码目录，由于模块代码放在内核源码目录外，make 的时候需要手动指定一下

### 安装模块

使用下面命令安装编译的模块到合适的目录：

```shell
make modules_install
```

通常需要以 root 权限运行。

正常情况下模块将被安装在**宿主机**(host)的`/lib/modules/{version}/kernel`下:

```console
root@racknerd-ae2d96:/lib/modules# ls -lh
total 20K
drwxr-xr-x 2 root root 4.0K Jul 20  2021 4.15.0-99-generic
drwxr-xr-x 2 root root 4.0K Feb  7 22:21 5.13.0-41-generic
drwxr-xr-x 5 root root 4.0K May 23  2022 5.15.0-30-generic
drwxr-xr-x 5 root root 4.0K Feb  7 22:19 5.15.0-58-generic
drwxr-xr-x 2 root root 4.0K May 23  2022 5.8.0-59-generic
```

比如源码为 2.6.34 版本，则模块路径为 `/lib/modules/2.6.34/kernel/drivers/char/fishing.ko`

TODO：关于交叉编译怎么实现，后续再补充

### 模块依赖性

Linux 模块之间存在依赖性

模块依赖关系信息存放在`/ibmodules/{version}/modules.dep` 文件中。

使用 `depmod` 命令产生依赖信息， `-A` 参数表示仅更新新模块的依赖信息。

### 载入模块

载入模块：

```shell
insmod fishing.ko
```

卸载模块：

```shell
rmmod fishing.ko
```

载入模块，自动载入依赖项：

```shell
modprobe modules
```

卸载模块，自动卸载未使用的依赖项：

```shell
modprobe -r modules
```

### 管理配置选项

2.6 内核新引入了 kbuild 系统，让编译选项的配置更简单。

比如之前提到的 `CONFIG_FISHING_POLE` 编译选项，只需编辑 `drivers/char/fishing/Kconfig`，加入以下内容：

```plaintext
config FISHING_POLE
	tristate "Fish Master 3000 support"
	default n
	depends on BLK_DEV_INITRD && !RD_LZO
	help
	  If you say Y here, support for the Fish Master 3000 with computer
	  interface will be compiled into the kernel and accessible via a
	  device node. You can also say M here and the driver will be built as a
	  module named fishing.ko.

	  If unsure, say N.
```

- 第一行是配置名称
- 第二行的 `tristate`表示该模块代码能直接编译进内核(Y)，或编译成模块(M)，或不编译(N)。后面的文字是在`menuconfig`中的显示名称
- 第三行是默认选项，这里是 n，也就是不编译
- 第四行的 depends 是可选的，表示依赖的配置选项，这里表示`CONFIG_BLK_DEV_INITRD`必须启用且`CONFIG_RD_LZO`被禁用，才能启用本配置
- 第五行的 help 是帮助信息

### 模块参数

Linux 允许驱动程序声明参数，从而用户可以在系统启动或者模块装载时再指定参数值，这些参数对于驱动程序属于全局变量。

模块参数将会载入 sysfs 文件系统中，变为文件。

```c
module_param(name, type, perm);
```

- name:变量名，非字符串，而是 C 语言变量，需要在外部先定义好
- type:参数类型，比如 int,bool 等
- perm:变量进入 sysfs 后的权限，如`0644`

### 导出符号(symbol)表

模块被载入后，就会被动态地连接(link)到内核，连接过程需要借助内核导出的符号表来访问内核函数。

只有被**显式导出**的内核函数，才能被模块调用（类似动态链接库）。

使用 `EXPORT_SYMBOL()`和`EXPORT_SYMBOL_GPL()` 可以在内核源码中显式导出内核函数：

```c
/*
 * get_pirate_beard_color - return the color of the current pirate's beard.
 * @pirate is a pointer to a pirate structure
 * the color is defined in <linux/beard_colors.h>.
 */
int get_pirate_beard_color(struct pirate *p)
{
	return p->beard.color;
}
EXPORT_SYMBOL(get_pirate_beard_color);
```

导出的**内核符号表**被看做导出的内核接口，称为内核 API。

## 设备模型

2.6 内核增加了一个引入注目的新特性——**统一设备模型**(device model)。设备模型提供了一个独立的机制专门来表示设备，并描述其在系统中的拓扑结构，从而使得系统具有以下优点:

- 代码重复最小化。
- 提供诸如引用计数这样的统一机制。
- 可以列举系统中所有的设备，观察它们的状态，并且查看它们连接的总线。
- 可以将系统中的全部设备结构以树的形式完整、有效地展现出来——包括所有的总线和内部连接。
- 可以将设备和其对应的驱动联系起来，反之亦然。
- 可以将设备按照类型加以归类，比如分类为输入设备，而无需理解物理设备的拓扑结构。
- 可以沿**设备树**的叶子向其根的方向依次遍历，以保证能以正确顺序关闭各设备的电源。

在实现中运用了面向对象的思想

### kobject

kobject 其实类似于面向对象中的**基类**，设备类继承该类

```c
// include/linux/kobject.h
struct kobject {
	const char		*name;
	struct list_head	entry;
	struct kobject		*parent;// 父对象指针，用于表达设备树中的层次关系
	struct kset		*kset;
	struct kobj_type	*ktype;
	struct sysfs_dirent	*sd; // sysfs的dirent对象指针，指向本对象(本对象在sysfs中其实是一个文件)
	struct kref		kref;// 引用计数
	unsigned int state_initialized:1;
	unsigned int state_in_sysfs:1;
	unsigned int state_add_uevent_sent:1;
	unsigned int state_remove_uevent_sent:1;
	unsigned int uevent_suppress:1;
};
```

实例：cdev 是 kobject 的一个派生类，表示字符设备：

```c
// include/linux/cdev.h
/* cdev structure - 该对象表示一个字符设备 */
struct cdev
{
	struct kobject kobj; // 嵌入kobject表示继承，必须放在结构体开头实现多态
	// 后面为该类的特有成员
	struct module *owner;
	const struct file_operations *ops;
	struct list_head list;
	dev_t dev;
	unsigned int count;
};
```

### ktype

kobject 的成员 ktype 表示本 kobject 的**类型**，多个 kobject 可以关联同一个 ktype，描述一类 kobject 所具有的普遍特性。

```c
// include/linux/kobject.h
struct kobj_type {
	void (*release)(struct kobject *kobj); // 引用计数归0时的析构函数，也就是同类kobject通用
	const struct sysfs_ops *sysfs_ops; // sysfs 的操作方法
	struct attribute **default_attrs; // 属性，是个数组
	const struct kobj_ns_type_operations *(*child_ns_type)(struct kobject *kobj);
	const void *(*namespace)(struct kobject *kobj);
};
```

ktype 定义了一些 kobject 相关的默认特性:析构行为、sysfs 行为(sysfs 的操作表)以及别的一些默认属性。同一类 kobject 共享这些默认特性，按面向对象的方式说就是继承了这些方法。

### kset

kset 用于对诸多 kobject 及其派生类对象进行分组（分组和 ktype 无关，即使 ktype 相同的也能分到不同组中）。分组依据比如“全部的块设备”，kset 的存在让分组更灵活，而不受限于相同或是不同的 ktype。

kset 的存在是为了将 kobject 分组映射为 sysfs 中的目录关系信息，详见[sysfs](#sysfs)

```c
// include/linux/kobject.h
struct kset {
	struct list_head list; // 链表，连接该kset管理的所有组内kobj，指向kobj链表上的第一个节点
	spinlock_t list_lock; // 保护链表的自旋锁
	struct kobject kobj; // 作为组内的所有kobject的基类,这是kset的一大功能
	const struct kset_uevent_ops *uevent_ops; // 用于处理集合中kobject对象的热插拔操作
};
```

kset 对象作为链表头连接一组 kobject（kobj 之间通过 kobject 内的 entry 成员连接）：

![f17.1](/assets/img/2023-03-15-linux-kernel-devices-modules/f17.1.jpg)

### 管理和操作 kobject

_kobject 默认构造函数：_

```c
// include/linux/kobject.h
extern void kobject_init(struct kobject *kobj, struct kobj_type *ktype);
```

> 调用前需要保证 kobj 为空，比如用 memset 或者通过 kzalloc 新分配。

示例：

```c
dir = kzalloc(sizeof(*dir), GFP_KERNEL);
if (!dir)
	return NULL;

dir->class = class;
kobject_init(&dir->kobj, &class_dir_ktype);
```

_kobject 默认创建函数（分配+构造）：_

```c
// include/linux/kobject.h
extern struct kobject * __must_check kobject_create(void);
extern struct kobject * __must_check kobject_create_and_add(const char *name,
						struct kobject *parent);
```

示例（源码中并没有直接使用 kobject_create 的地方）：

```c
dev_kobj = kobject_create_and_add("dev", NULL);
```

### 引用计数

类似于高级语言中的内存自动回收（gc）机制，当引用数为 0 时回收对象。

kref 结构:

```c
// include/linux/kref.h
struct kref {
	atomic_t refcount;
};
```

递增引用计数:

```c
// include/linux/kobject.h
extern struct kobject *kobject_get(struct kobject *kobj);
```

递减引用计数:

```c
// include/linux/kobject.h
extern void kobject_put(struct kobject *kobj);
```

## sysfs

sysfs 文件系统是一个处于内存中的**虚拟文件系统**，它为我们提供了 kobject 对象**层次结构**的视图。kobject 被映射为**目录**（非文件），通过 `sd` 成员映射[目录项](/posts/linux-kernel-vfs/#目录项对象-dentry)。

sysfs 取代了原来 `ioctl()` 操作**设备节点**和 `procfs` 文件系统操作**内核变量**的方式。只需在 sysfs 的目录中创建一个文件并关联设备，就能直接通过文件接口操作设备。

要实现 sysfs 的映射，需要扫描所有 kobject 的 parent 和 kset 成员：

- 如果 parent 为另一个 kobject，则本 kobject 就是其 parent 的子节点，在 sysfs 中也就是子目录（直接的 kobj 树，依赖 parent 构成的树）
- 如果 parent 为 NULL, kset 成员有值，则该 kobject 对应的 sysfs 目录是 kset->kobj 的子目录（kobj 不在直接的 kobj 树中，而是在[kset](#kset)下构成的树中）
- 如果 parent 为 NULL，keset 也为 NULL，则说明其为 root，在 sysfs 中对应根级目录

扫描完成后即可确定文件系统目录树。

`/sys`目录：

```console
|-- block
| |-- loop0 -> ../devices/virtual/block/loop0
| |-- md0 -> ../devices/virtual/block/md0
| |-- nbd0 -> ../devices/virtual/block/nbd0
| |-- ram0 -> ../devices/virtual/block/ram0
| `-- xvda -> ../devices/vbd-51712/block/xvda
|-- bus
| |-- platform
| |-- serio
|-- class
| |-- bdi
| |-- block
| |-- input
| |-- mem
| |-- misc
| |-- net
| |-- ppp
| |-- rtc
| |-- tty
| |-- vc
| `-- vtconsole
|-- dev
| |-- block
| `-- char
|-- devices
| |-- console-0
| |-- platform
| |-- system
| |-- vbd-51712
| |-- vbd-51728
| |-- vif-0
| `-- virtual
|-- firmware
|-- fs
| |-- ecryptfs
| |-- ext4
| |-- fuse
| `-- gfs2
|-- kernel
| |-- config
| |-- dlm
| |-- mm
| |-- notes
| |-- uevent_helper
| |-- uevent_seqnum
| `-- uids
`-- module
	|-- ext4
	|-- i8042
	|-- kernel
	|-- keyboard
	|-- mousedev
	|-- nbd
	|-- printk
	|-- psmouse
	|-- sch_htb
	|-- tcp_cubic
	|-- vt
	`-- xt_recent
```

[HAL](https://www.freedesktop.org/wiki/Software/hal/)基于 sysfs 中的数据建立起了一个内存数据库，将 class 概念、设备概念和驱动概念联系到一起。在这些数据之上，HAL 提供了丰富的 API 以使得应用程序更灵活。

### sysfs 中添加和删除 kobject

kobject 默认初始化后并不关联到 sysfs，需要使用`kobject_add()`:

```c
// include/linux/kobject.h
// 对象(或者叫目录)名称使用printf()风格的格式化字符串
int kobject_add(struct kobject *kobj, struct kobject *parent,
		const char *fmt, ...);
```

可以使用 `kobject_create_and_add()` 将 `kobject_create()` 和 `kobject_add()` 合并执行，之前介绍了。

### 向 sysfs 中添加文件（attr）

之前提到 kobject 对象对应的是 sysfs 中的**目录**，而**文件**则是由 kobject 对象中的成员 `default_attrs 数组`对应，该数组负责将**内核数据**映射成 sysfs 中的**文件**。

#### 默认文件

kobject 对象中的成员 `default_attrs 数组` 表示目录下的默认文件，在 kobject 初始化后就存在。

```c
// include/linux/sysfs.h
// 内核数据映射成 sysfs 中的文件
struct attribute {
	const char		*name; // 属性名称，对应sysfs文件名
	umode_t			mode; // 权限，对应sysfs文件权限
#ifdef CONFIG_DEBUG_LOCK_ALLOC
	bool			ignore_lockdep:1;
	struct lock_class_key	*key;
	struct lock_class_key	skey;
#endif
};
```

kobject 中的**sysfs_ops 成员**（在 ktype 中）则描述了如何使用这些文件（内核数据）:

```c
// include/linux/sysfs.h
struct sysfs_ops {
	// 读取文件,从kobj（表示目录）和attr（表示文件）中，读取数据到buf中
	ssize_t	(*show)(struct kobject *kobj, struct attribute *attr,char *buf);
	// 写入文件
	ssize_t	(*store)(struct kobject *,struct attribute *,const char *, size_t);
	const void *(*namespace)(struct kobject *, const struct attribute *);
};
```

回忆一下[ktype](#ktype)，相同 ktype 的 kobject 拥有相同的 sysfs_ops。

#### 创建新文件(attr)

一般而言，相同 ktype 的 kobject 的 default_attrs 都是相同的，也就是这些目录下的文件组织结构(文件名，权限)都相同。

但有时候会希望为某个 kobject 增加一个文件(也就是 attr):

```c
int sysfs_create_file(struct kobject *kobj, const struct attribute tattr);
```

还可创建符号链接(目录)：

```c
int sysfs_create_link(struct kobject *kobj, struct kobject *target, char *name);
```

#### 删除新文件(attr)

```c
void sysfs_remove_file(struct kobject *kobj, const struct attribute *attr);
```

删除符号链接：

```c
void sysfs_remove_link(struct kobject *kobj, char *name) ;
```

#### sysfs 约定

- 一值一文件：sysfs 属性应该保证每个文件只导出一个值，该值应该是文本形式而且映射为简单 C 类型。避免文件内容过于复杂，这样使用 shell 或 C 语言读取写入该文件就会简单得多。
- 清晰的层次组织数据
- sysfs 提供内核到用户空间的服务
- sysfs 已经取代 `ioctl()` 和 `procfs`，尽可能得使用 sysfs 操作内核变量

### 内核事件层

内核事件层实现了内核到用户的**消息通知**系统（通过 kobject 和 sysfs）

事件是实现异步操作的必要组成部分，常见事件如硬盘满了，处理器过热了，分区挂载了。

每个事件源都是一个 sysfs 路径，比如一个硬盘通知事件源为 `/sys/block/hda`。

内核事件由内核空间传递到用户空间需要经过`netlink`（netlink 是一个用于传送网络信息的多点传送套接字）。使用示例：在用户空间实现一个系统后台服务用于监听套接字(socket)，处理任何读到的信息，并将事件传送到系统栈里，通过该方法也能实现将事件整合入 `D-BUS`。

在内核代码中向用户空间发送信号使用函数`kobject_uevent()`:

```c
// lib/kobject_uevent.c
int kobject_uevent(struct kobject *kobj, enum kobject_action action);
```

- **kobj**: 发送事件的 kobject，最终发出的事件中将会包含 kobject 对应的 sysfs 路径**字符串**
- **action**: 信号(枚举型)。最终发出的内核事件将包含该**枚举**类型`kobject_action`映射成的**字符串**(枚举型保证了可重用性和类型安全性)。该枚举变量定义于文件`<linux/kobject_uevent.c>`中，其形式为`kOBJ_foo`。当前值包含 kOBJ_MOUNT,kOBJ_UNMOUNT,kOBJ_ADD,kOBJ_REMOVE 和 kOBJ_CHANGE 等，这些值分别映射为字符串"mount","unmount","add","remove"和"change"等。

所以最终事件就是包含 kobject 对应的 sysfs 路径和信号动作的**字符串**。

## 参考

- [Linux 内核设计与实现（第三版）第十七章](https://www.amazon.com/Linux-Kernel-Development-Robert-Love/dp/0672329468/ref=as_li_ss_tl?ie=UTF8&tag=roblov-20)
- [Robert Love](https://rlove.org/)
