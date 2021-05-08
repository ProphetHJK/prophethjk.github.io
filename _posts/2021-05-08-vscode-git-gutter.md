---
title: "关于VSCode使用Remote SSH时git gutter(代码差异装饰器)无法显示的问题"
author: Jinkai
date: 2021-05-08 09:00:00 +0800
published: true
categories: [技术]
tags: [vscode, git, gutter]
---

## diff decorations gutter介绍

`diff decorations gutter`中文翻译为代码差异装饰器，就是在使用git或svn插件时代码编辑器序号旁边显示的彩色装饰条，点击可以看到**改动后的内容**和**最后一次提交内容**的差异

![diff-gutter](/assets/img/2021-05-08-vscode-git-gutter/diff-gutter.jpg)

这玩意看似简单，却是版本管理的利器，没有它我都不敢写代码了

## 无法显示问题

在使用Remote SSH进行远程开发时发现代码差异装饰器无法显示，通过查找发现是`软链接`的问题，就是打开的文件夹是软链接后的文件夹，导致VSCode无法识别。

## 解决方法

不要打开软链接文件夹，直接打开软链接指向的目录，问题解决
