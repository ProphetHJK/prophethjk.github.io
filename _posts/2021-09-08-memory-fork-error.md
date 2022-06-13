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

首先是分析日志，对于还可以正常通信的设备的日志进行分析，发现升级失败原因为升级包**校验失败**，升级包的传输应该是不会有问题的，校验失败应该另有隐情。

仔细分析了报错信息后，发现频繁打印"script execute error."，这个是应用里对system的一个封装函数的打印，发生条件是`system()`函数返回非0值。所以可以初步确定校验失败的原因就是**校验脚本执行失败**。

实际上 `system` 函数内部干了三件事情：

1. `fork` 创建一个子进程
2. 在子进程中调用 `exec` 函数去执行 command
3. 在父进程中调用 `waitpid` 去等待子进程结束

关于fork的详细介绍，在我之前写的[《Operating Systems: Three Easy Pieces》学习笔记(三) 插叙：进程 API](/posts/operating-systems-3/)一文里有介绍

问题很有可能发生在`fork`阶段，从这方面入手进行了模拟测试，终于发现在**系统内存占用较高**时fork会有失败的现象。

那又是什么导致现场占用内存这么高呢？问题肯定和**校验脚本**有关，因为每次发生问题都是在校验脚本开始执行之后。仔细检查了**校验脚本**，发现该脚本会解压一次升级文件并放在/tmp分区，tmp分区时**tmpfs格式分区**，也就是内存分区，将内存当作磁盘使用。tmpfs分区是动态分配的，做法是有多少占多少。当tmpfs分区占用太大时会导致**内存不足**。

## 分析结果

至此，问题已经明确，升级校验过程中执行的校验脚本在tmpfs分区解压了升级包，导致tmpfs分区占用过高，**占用了部分内存**。

同时由于该设备是边缘网关，现场子节点较多，导致采集程序也占用了较高的内存，以上两者共同作用，**导致了内存不足**。

**内存不足引发fork失败，后续的升级脚本无法执行，通信模块复位也无法进行，导致升级失败和无法通信的现象**

## 解决方案

1. 分析发现校验脚本不需要解压升级包，因为升级脚本会做这件事，把这步删了，可以省下很多内存
2. 封装所有system()和fork()函数，对于调用失败的情况，复位设备，如果出现异常，统计到达一定次数后触发异常保护，比如关闭进程或重启系统

下面是封装函数的源码：

```c
/**
 * @brief system函数封装
 * 
 * @param szCmd 
 * @return int -1：执行失败; 0:执行成功; 其他:exit code
 */
int systemcmd(const char *szCmd)
{
    Log::Inf("systemcmd:");
    Log::Inf("%s", szCmd);
    pid_t status;
    status = pox_system(szCmd);
    if (time(NULL) - first_error_time > 3600)
    {
        system_exec_error = 0;
    }
    if (-1 == status)
    {
        Log::Err("system cmd exec error: -1");
        if (system_exec_error == 0)
        {
            first_error_time = time(NULL);
        }
        system_exec_error++;
        Log::Err("system cmd exec error times: %d", system_exec_error);
        if (system_exec_error >= MAX_EXEC_ERROR)
        {
            Log::Err("too many exec error, reboot dcu:%d", system_exec_error);
            saveErrorLog();
            exit(0);
        }
        return -1;
    }
    else
    {
        Log::Inf("exit status value = [0x%x]", status);
        if (WIFEXITED(status))
        {
            if (WEXITSTATUS(status) == 0)
            {
                Log::Inf("run shell script successfully.");
            }
            else
            {
                Log::Err("run shell script fail, script exit code: %d", WEXITSTATUS(status));
            }
            return WEXITSTATUS(status);
        }
        else
        {
            Log::Err("exit status = [%d]", WIFEXITED(status));
            return -1;
        }
    }
}
```

## 感想

分析这个问题的过程其实走了很多弯路，比如还考虑过SIGCHLD信号的问题。在日志信息不全，时间紧迫的情况下，也能把问题分析出来，从这件事也印证出没有什么问题是解决不了的，遇到问题不要慌，按部就班一个个分析，总能有头绪的。

当然还有程序设计上，对于系统函数要做一下封装，比如system()或者fork()函数，一是在执行异常时可以通过复位解决问题，二是防止分析日志的时候抓瞎。

## 参考

- [fork之后父子进程的内存关系_Shreck66的专栏-CSDN博客](https://blog.csdn.net/Shreck66/article/details/47039937)
- [Linux 中 popen 函数与 system 函数的区别_胡小哲的博客-CSDN博客](https://blog.csdn.net/hudazhe/article/details/79434111)
