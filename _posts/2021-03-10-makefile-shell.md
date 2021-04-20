---
title: Makefile和SHELL中$及$$的区别
author: Jinkai
date: 2021-03-10 09:00:00 +0800
published: true
categories: [技术]
tags: [Makefile, shell]
---

最近在看linux内核代码时看到在Makefile中用到了`$$()`的使用方式，虽然能猜到什么意思，但不知道使用方法和具体含义，于是查找资料，在此写一个总结

## SHELL中的$说明

-------

在shell中，`$`的一种用法是引用shell变量，执行脚本时，`$`引用的变量会被替换为相应的字符串。

当然shell中`$`的用法远不止于此，此处就不多做展开，想要了解更多，可以阅读[Linux Shell中'$'符号的N种用法](<https://www.caosh.me/linux/dollar-in-linux-shell/>)

## Makefile中的$说明

-------

Makefile中的`$`用法和shell中的大体类似，只不过在Makefile中，`$`仅能用于引用Makefile声明的变量，无法引用shell的变量。

这里要注意下，使用make命令执行Makefile时并不是shell环境，当执行到Makefile的某个操作时才会执行shell，例：

```makefile
checkstack:
	$(OBJDUMP) -d vmlinux $$(find . -name '*.ko') | \
	$(PERL) $(src)/scripts/checkstack.pl $(CHECKSTACK_ARCH)

kernelrelease:
	@echo "$(KERNELVERSION)$$($(CONFIG_SHELL) $(srctree)/scripts/setlocalversion $(srctree))"

kernelversion:
	@echo $(KERNELVERSION)
```

> 注：makefile中对变量的引用需要使用`$()`这种带括号的方式，否则只会识别`$`后的一个字母

只有执行对应的Makefile命令的shell语句时才会进入shell环境，每行命令独立，每行都是单独的shell，所以上一行定义的shell变量并不适用于下一行。当然如果是使用了`\`来合并行就可以摆脱这个限制了，比如例子中的`checkstack`命令下的shell命令虽然是两行但在同一个shell环境中执行

## Makefile中的$$说明

-------

Makefile命令中的shell语句也并非直接用于shell环境，make会对该语句进行预处理，如果想要引用shell中的变量，就要使用`$`号来把Makefile变量转换成shell变量

`$$`的用法就是把Makefile引用转化为shell引用，可以理解为此时的`$`是一个转义符，**也可以理解为去掉一个`$`后直接带入shell脚本中**

### 例1

```makefile
LIST = one two three
all:
	for i in $(LIST); do \
        echo $i; \
    done
```

通过make预处理后转化为shell:

```shell
for i in one two three; do \
        echo ; \
    done

# 输出为空
```

本例中，`$i`和`$(LIST)`会被先当成Makefile变量，`LIST`变量在Makefile中有定义，被转换为了`one two three`，由于`i`变量未在Makefile中定义，所以转化为了空。

### 例2

```makefile
LIST = one two three
all:
	for i in $(LIST); do \
        echo $$i; \
    done
```

通过make预处理后转化为shell:

```shell
for i in one two three; do \
        echo $i; \
    done

# 输出为
# one
# two
# three
```

例2中，`$$i`命令被make翻译成了shell命令中的`$i`，此时shell脚本可以正常执行，输出正确结果

### 例3

```makefile
help:
	@echo  '                    (default: $$(INSTALL_MOD_PATH)/lib/firmware)'
```

输出结果为：

```txt
                    (default: $(INSTALL_MOD_PATH)/lib/firmware)
```

> 注：Makefile中的`@`符号表示该行shell命令不回显，否则执行时make会把转化后的shell脚本打印一遍

> 注：`单引号`在shell中表示不执行转义或引用，按照原样字符串输出，此处`$(INSTALL_MOD_PATH)`不会被理解为变量

例3中，`$$(INSTALL_MOD_PATH)`被翻译成`$(INSTALL_MOD_PATH)`，但由于存在`单引号`，导致shell变量不会被引用

### 例4

```makefile
VERSION = 3
PATCHLEVEL = 10
SUBLEVEL = 108
EXTRAVERSION =
# kernel 版本号，为四个版本号的组合
KERNELVERSION = $(VERSION)$(if $(PATCHLEVEL),.$(PATCHLEVEL)$(if $(SUBLEVEL),.$(SUBLEVEL)))$(EXTRAVERSION)
# 从shell环境变量中提取shell的执行环境
CONFIG_SHELL := $(shell if [ -x "$$BASH" ]; then echo $$BASH; \
	  else if [ -x /bin/bash ]; then echo /bin/bash; \
	  else echo sh; fi ; fi)
# 选取脚本的目录，如果KBUILD_SRC未定义，则选择$(CURDIR)，$(CURDIR)表示当前目录绝对路径
srctree		:= $(if $(KBUILD_SRC),$(KBUILD_SRC),$(CURDIR))
KBUILD_VERBOSE = 1
# 是否在控制台回显，如果有@则不回显
ifeq ($(KBUILD_VERBOSE),1)
  quiet =
  Q =
else
  quiet=quiet_
  Q = @
endif

version:
	$(Q)echo "$(KERNELVERSION)$$($(CONFIG_SHELL) $(srctree)/scripts/setlocalversion $(srctree))" > $@

```

转化后的shell为：

```shell
echo "3.10.108$(/bin/bash /root/repo/makefile_test/scripts/setlocalversion /root/repo/makefile_test)" > version

# 假定setlocalversion脚本存在，且会输出一个'+'号，输出结果为：
# 3.10.108+
# 该值会被写入version文件
```

例4为比较实际的例子，选自linux kernel的makefile中，相关变量的注释已经添加，结合前三个例子应该很好理解

## 总结

-------

Makefile中的`$`用于引用Makefile变量，shell中的`$`用于引用shell变量，Makefile中的`$$`用于把Makefile引用转化为shell引用

## 参考

- [Makefile中$$使用](<https://blog.csdn.net/weixin_34255055/article/details/92069010>)
