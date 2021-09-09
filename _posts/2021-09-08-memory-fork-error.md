---
title: "Linux系统中内存不足导致system()执行失败的问题"
author: Jinkai
date: 2021-09-08 09:00:00 +0800
published: true
categories: [技术]
tags: [linux, system, fork]
---

在实际项目中遇到了现场大量设备升级后无法上线的问题，经过几天的分析发现是升级占用了大量内存导致system()函数执行失败，也就是无法通过C程序执行shell脚本，造成了设备异常。本文将对问题原因与解决方案做详细介绍

## 问题简介

现场设备挂网时间有1年多了，打算进行远程升级以支持更多功能与提高稳定性。首次选择了200个设备进行小批量验证，但升级成功率很低，有将近3/4的设备升级失败，且升级失败后大部分进入异常状态，无法进行通信，也就是处于离线状态。

两天后离线的设备陆续上线，推测原因可能是异常时间较长导致主进程崩溃，随即触发了硬件看门狗复位设备，且重新上线后设备各项功能都正常。

## 原因分析

首先是分析日志，对于还可以正常通信的设备的日志进行分析，发现升级失败原因为升级包校验失败，升级包的传输应该是不会有问题的，校验失败应该另有隐情，

## 参考

- [DHCPv6基础-曹世宏的博客](https://cshihong.github.io/2018/02/01/DHCPv6%E5%9F%BA%E7%A1%80/)
- [RFC3315](https://datatracker.ietf.org/doc/html/rfc3315)
- [RFC8415](https://datatracker.ietf.org/doc/html/rfc8415)
- [Ubuntu Manpage:dhcp6relay—DHCPv6 relay agent](https://manpages.ubuntu.com/manpages/bionic/man8/dhcp6relay.8.html)
