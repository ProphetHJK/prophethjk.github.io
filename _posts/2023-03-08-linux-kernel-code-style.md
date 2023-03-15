---
title: "Linux内核学习笔记之编码风格"
author: Jinkai
date: 2023-03-08 16:00:00 +0800
published: true
categories: [学习笔记]
tags: [kernel, Linux]
---

几个推荐的网站或邮件列表：

- <http://vger.kernel.org/majordomo-info.html>，内核邮件列表(Linux Kernel Mailing List,lkml)是对内核进行发布、讨论的主战场。在做任何实际的动作之前，新特性会在此处被讨论，新代码的大部分也会在此处张贴。
- <https://lkml.org/>，对 lkml 的归档（非官方），官方的应该是<https://lore.kernel.org/lkml/>。
- <https://kernelnewbies.org/>，是一方适合内核开发初级黑客的乐土——该网站几乎能够满足所有磨刀霍替向内核的新手的需求。
- <https://www.lwn.net>，Linux 新闻周刊，它有一个专区报道有关内核的重要新闻。

Linux 的编码风格记录在源码树的 `<Documentation/CodingStyle>` 中

## 缩进

缩进风格是用**制表符**(Tab)每次缩进**8 个字符**长度。

```c
static void get_new_ship(const char *name)
{
	if (!name)
		name = DEPAULT_SHIP_NAME;
	get_new_ship with_name(name);
}
```

8 个字符长度的缩进能让不同的代码块看起来一目了然，特别是在连续几个小时的开发之后，效果更加明显。

随着缩进层数的增加，8 字符制表位的左侧可用空间就所剩不多了。所以 Linus Torvalds 要求代码中的缩进不应超过三层。如果层级较多，需要重构你的代码，把复杂的层次关系(为此形成多层缩进)分解为独立的功能。

Linux 内核的核心代码（非驱动或体系特定代码）中几乎没有超过三层(3 个 tab)的代码。

## switch 语句

case 与 switch 齐平来减少缩进层次。如果 case 内不使用 break 离开，而是继续进入下一个 case 则需要**注释说明**。

```c
switch (animal){
case ANIMAL_CAT:
	handle_cats();
	break;
case ANIMAL_WOLF:
	handle_wolves();
	/* fall through */
case ANIMAL_DOG:
	handle_dogs();
	break;
default:
	printk(KERN_WARNING "Unknown animal %d!\n", animal);
}
```

## 空格

**关键字**和左圆括号间加空格:

```c
if (foo)

while (foo)

for (i = 0; i < NR_CPUS; i++)

switch (foo)
```

**函数**、**宏**以及与**函数相像的关键字**(例如 sizeof、typeof 以及 alignof)在关键字和圆括号之间没有空格:

```c
wake_up_process(task);
size_t nlongs = BITS_TO_LONG(nbits);
int len = sizeof(struct task_struct);
typeof(*p)
__alignof__(struct sockaddr *)
__attribute__((packed))
```

对于大多数二元或者三元**操作符**(+,-,?,&)，在操作符的两边加上空格:

```c
int sum = a + b;
int product = a * b;
int mod = a % b;
int ret = (bar) ? bar : 0;
return (ret ? 0 : size);
int nr = nr ? : 1; /* allowed shortcut, same as "nr ? nr: 1" */
if (x < y)
if (tsk->flags & PF_SUPERPRIV)
mask = POLLIN | POLLRDNORM;
```

对于大多数**一元操作符**(++,--,!,&,~)，在操作符和操作数之间不加空格:

```c
if (!foo)
int len = foo.len;
struct work_struct *work = &dwork->work;
foo++;
--bar;
unsigned long inverted = ~mask;
```

提领运算符(\*)应该贴近变量，而不是类型（TODO:有待商榷，个人还是比较喜欢贴近类型）：

```c
char *strcpy(char *dest，const char *src)
```

## 花括号

左花括号和标识符放在同一行；如果右花括号后还有同一语句块的另一个标识符，则都放在同一行：

```c
if (ret) {
	sysctl_sched_xt_period = old_period;
	sysctl_sched_rt_runtime = old_runtime;
} else {
	def_rt_bandwidth.rt_runtime = global_rt_runtime();
	def_rt_bandwidth.rt_period = ns_to_ktime(global_rt_period());
}
```

```c
do {
	percpu_counter_add(&ca->cpustat[idx], val); ca = ca->parent;
} while (ca);
```

## 每行代码的长度

每行代码的长度不超过 80 个字符。

圆括号内参数可以分行，一般会让参数对齐，但没有明确规定(如果使用 tab 制表符无法对齐，可以使用空格来微调)：

```c
static void get_new_parrot(const char *name,
			   unsigned long disposition,
			   unsigned long feather_quality)
```

## 命名规范

不允许大小写混合，如驼峰命名 theLoopIndex。

变量和函数使用小写字母，必要时使用下划线(`_`)区分单词。而且尽量要表达含义(如`get_active_tty()`)，不要使用难以理解的缩写(如`atty()`)

## 函数

函数的代码长度不应该超过两屏(按照 80x24 的标准终端，应该是 48 行)，局部变量不应超过 10 个。

一个函数应该功能单一并且实现精准，如果功能过于复杂，可以将一个函数分解成一些更短小的函数的组合。

如果你担心函数调用导致的开销，可以使用`inline`关键字。

## 注释

注释的话只要按照 C 风格就行(`/* */`)，具体的内部定义可以按自己喜好

多行注释示例：

```c
/*
 * get_ship_speed() - return the current speed of the pirate ship
 * We need this to calculate the ship coordinates.As this function can sleep,
 * do not call while holding a spinlock
 */
```

## typedef

内核开发者们强烈反对使用 typedef 语句。他们的理由是:

- typedef 掩盖了数据的真实类型。
- 由于数据类型隐藏起来了，所以很容易因此而犯错误，比如以传值的方式向栈中推入结构（本应该是指针，如果结构较大，传值的方式会导致栈溢出）。
- 使用 typedef 往往是因为想要偷懒

尽量少用 typedef ，必要的时候再用，内核在 `<linux/types.h>` 中使用了 typedef。对于 struct 的定义，不使用 typedef：

```c
struct completion {
	unsigned int done;
	wait_queue_head_t wait;
};
```

## 多用现成的东西

对于已有的功能不要自己造轮子。内核本身就提供了字符串操作函数、压缩函数和一个链表接口，所以请使用它们。

不要为了让接口通用化而封装内核提供的接口。隐藏实现有时不一定是好事，特别是操作系统级别的编程时。

## 在源码中减少使用 ifdef

我们不赞成在源码中使用 `ifdef` 预处理指令。(TODO:实际上用的还挺多的)

## 结构初始化

使用C99风格，允许不明确定义初值，使用默认值(如指针被设为NULL，整型被设为0，浮点数被设置为0.0)

```c
struct foo {
	int a;
	char b;
	long c;
}

// C99 风格
struct foo my_foo = {
	.a = INITIAL_A,
	.b = INITIAL_B
};

// GNU 风格
struct foo my_foo = {INITIAL_A, INITIAL_B};
```

本例中 c 未被明确赋予初值，使用默认值 0。

## 代码格式化工具

可以使用各种工具，比如 indent:

```console
indent -kr -i8 -ts8 -sob -180 -ss -bs -psl <file>
```

也可以直接使用源码目录中的 `scripts/Lindent` 脚本

## 参考

- [Linux 内核设计与实现（第三版）第二十章](https://www.amazon.com/Linux-Kernel-Development-Robert-Love/dp/0672329468/ref=as_li_ss_tl?ie=UTF8&tag=roblov-20)
- [Robert Love](https://rlove.org/)
