---
title: "Git 常用操作"
author: Jinkai
date: 2023-11-16 08:00:00 +0800
published: true
categories: [教程]
tags: [Git]
---

## 前言

vscode 的 Git 和 GitLens 插件已经能完成大部分的工作，本文介绍只能在命令行下实现的常用操作

## 合并多条提交

合并最后 2 条记录：

```c
git rebase -i HEAD~2
```

打印如下：

```console
GNU nano 3.2
git-rebase-todo

pick f9fb267 feat: 提交1
pick 88ede48 feat: 提交2

# 变基 86de2ed..88ede48 到 86de2ed（2 个提交）
#
# 命令:
# p, pick <提交> = 使用提交
# r, reword <提交> = 使用提交，但编辑提交说明
# e, edit <提交> = 使用提交，但停止以便在 shell 中修补提交
# s, squash <提交> = 使用提交，但挤压到前一个提交
# f, fixup [-C | -c] <提交> = 类似于 "squash"，但只保留前一个提交
#                    的提交说明，除非使用了 -C 参数，此情况下则只
#                    保留本提交说明。使用 -c 和 -C 类似，但会打开
#                    编辑器修改提交说明
# x, exec <命令> = 使用 shell 运行命令（此行剩余部分）
# b, break = 在此处停止（使用 'git rebase --continue' 继续变基）
# d, drop <提交> = 删除提交
# l, label <label> = 为当前 HEAD 打上标记
# t, reset <label> = 重置 HEAD 到该标记
# m, merge [-C <commit> | -c <commit>] <label> [# <oneline>]
# .       创建一个合并提交，并使用原始的合并提交说明（如果没有指定
# .       原始提交，使用注释部分的 oneline 作为提交说明）。使用
# .       -c <提交> 可以编辑提交说明。
#
# 可以对这些行重新排序，将从上至下执行。
#
# 如果您在这里删除一行，对应的提交将会丢失。
#
# 然而，如果您删除全部内容，变基操作将会终止。
#
```

除第一个`pick`外将其他`pick`修改为`squash`（简写为`s`）：

```console
GNU nano 3.2
git-rebase-todo

pick f9fb267 feat: 提交1
s 88ede48 feat: 提交2
```

使用 nano 编辑器保存后退出，那之后会提示修改提交记录，如果不想更改直接保存即可。

## 子模块

克隆包含子模块的项目：

```console
git clone --recurse-submodules http://xxxx.git
```

添加子模块，注意要在需要添加到的子目录下执行：

```console
git submodule add https://xxxx.git
```

## 参考

- [git 里如何将多次 commit 合并为一次？](https://www.jianshu.com/p/66cece71b41d)
