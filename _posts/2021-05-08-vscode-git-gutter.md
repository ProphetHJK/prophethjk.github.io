---
title: "关于VSCode使用Remote SSH时git gutter(代码差异装饰器)无法显示的问题"
author: Jinkai
date: 2021-05-08 09:00:00 +0800
published: false
categories: [技术]
tags: [vscode, git, gutter]
---

## diff decorations gutter介绍

`diff decorations gutter`中文翻译为代码差异装饰器，就是在使用git或svn插件时代码编辑器序号旁边显示的彩色装饰条，点击可以看到改动后的内容和HEAD内容的差异

![diff-gutter](/assets/img/2021-05-08-vscode-git-gutter/diff-gutter.jpg)

## 无法显示问题

在使用Remote SSH进行远程开发时发现代码差异装饰器无法显示，通过查找发现是`软链接`的问题，就是打开的文件夹是软链接后的文件夹，导致VSCode无法识别。

## 解决方法

不要打开软链接文件夹，直接打开软链接指向的目录，问题解决
