---
title: "《UML 状态图的实用 C/C++设计》(QP状态机)学习笔记"
author: Jinkai
date: 2022-07-27 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [quantum platform, QP状态机]
---

- [架构](#架构)
- [UML 状态图](#uml-状态图)
  - [状态机分类](#状态机分类)
  - [正交区域](#正交区域)
  - [转换的执行次序](#转换的执行次序)
  - [本地转换和外部转换的对比](#本地转换和外部转换的对比)
  - [UML 实例](#uml-实例)
  - [计算器设计实例](#计算器设计实例)
    - [高层设计](#高层设计)
    - [寻找重用 (Reuse)](#寻找重用-reuse)
    - [operandX 状态设计](#operandx-状态设计)
    - [处理负号的两种情况](#处理负号的两种情况)
    - [最终状态图](#最终状态图)
- [状态模式](#状态模式)
  - [延迟的事件](#延迟的事件)
    - [目的](#目的)
    - [问题](#问题)
    - [解决](#解决)
- [标准状态机的实现方法](#标准状态机的实现方法)
  - [嵌套的 switch 语句](#嵌套的-switch-语句)
  - [状态表 (State Table)](#状态表-state-table)
  - [面向对象的状态设计模式](#面向对象的状态设计模式)
    - [增加进入退出状态操作](#增加进入退出状态操作)
    - [封装事件处理](#封装事件处理)
  - [QEP FSM 实现方法](#qep-fsm-实现方法)
  - [状态机实现技术的一般性讨论](#状态机实现技术的一般性讨论)
- [层次式事件处理器的实现](#层次式事件处理器的实现)
  - [层次式状态处理函数](#层次式状态处理函数)
  - [层次式状态机的类](#层次式状态机的类)
    - [顶状态和初始伪状态](#顶状态和初始伪状态)
    - [进入 / 退出动作和嵌套的初始转换](#进入--退出动作和嵌套的初始转换)
    - [最顶层初始转换 (QHsm_init())](#最顶层初始转换-qhsm_init)
    - [分派事件（ QHsm_dispatch(), 通用结构）](#分派事件-qhsm_dispatch-通用结构)
    - [在状态机里实施一个转换（ QHsm_dispatch(), 转换）](#在状态机里实施一个转换-qhsm_dispatch-转换)
  - [使用 QEP 实现 HSM 步骤的概要](#使用-qep-实现-hsm-步骤的概要)
  - [常见问题](#常见问题)
- [实时框架的概念](#实时框架的概念)
  - [CPU 管理](#cpu-管理)
  - [活动对象计算模式](#活动对象计算模式)
    - [系统结构](#系统结构)
    - [异步通讯](#异步通讯)
    - [运行 - 到 - 完成 RTC](#运行---到---完成-rtc)
    - [封装](#封装)
  - [事件派发机制](#事件派发机制)
    - [直接事件发送](#直接事件发送)
    - [订阅派发机制](#订阅派发机制)
  - [事件内存管理](#事件内存管理)
    - [零复制的事件派发](#零复制的事件派发)
    - [静态和动态的事件](#静态和动态的事件)
    - [多路传输事件和引用计数器算法](#多路传输事件和引用计数器算法)
    - [事件的所有权](#事件的所有权)
    - [内存池](#内存池)
    - [时间管理](#时间管理)
    - [系统时钟节拍](#系统时钟节拍)
  - [错误和例外的处理](#错误和例外的处理)
  - [基于框架的软件追踪](#基于框架的软件追踪)
- [实时框架的实现](#实时框架的实现)
  - [QF 实时框架的关键特征](#qf-实时框架的关键特征)
  - [QF 的结构](#qf-的结构)
    - [QF 源代码的组织](#qf-源代码的组织)
  - [QF 里的临界区](#qf-里的临界区)
    - [保存和恢复中断状态](#保存和恢复中断状态)
    - [无条件上锁和解锁中断](#无条件上锁和解锁中断)
    - [中断上锁/解锁的内部 QF 宏](#中断上锁解锁的内部-qf-宏)
  - [主动对象](#主动对象)
    - [活动对象的内部状态机](#活动对象的内部状态机)
    - [活动对象的事件队列](#活动对象的事件队列)
    - [执行线程和活动对象优先级](#执行线程和活动对象优先级)
  - [QF 的事件管理](#qf-的事件管理)
    - [事件的结构](#事件的结构)
    - [动态事件分配](#动态事件分配)
    - [自动垃圾收集](#自动垃圾收集)
    - [延迟和恢复事件](#延迟和恢复事件)
  - [QF 的事件派发机制](#qf-的事件派发机制)
    - [直接事件发送](#直接事件发送-1)
    - [发行-订阅事件发送](#发行-订阅事件发送)
  - [时间管理](#时间管理-1)
    - [时间事件结构和接口](#时间事件结构和接口)
    - [系统时钟节拍和 QF_tick() 函数](#系统时钟节拍和-qf_tick-函数)
    - [arming 和 disarm 一个时间事件](#arming-和-disarm-一个时间事件)
  - [原生 QF 事件队列](#原生-qf-事件队列)
    - [QEQueue 结构](#qequeue-结构)
    - [QEQueue 的初始化](#qequeue-的初始化)
    - [原生 QF 活动对象队列](#原生-qf-活动对象队列)
    - [“ 原始的”线程安全的队列](#-原始的线程安全的队列)
  - [原生 QF 内存池](#原生-qf-内存池)
    - [原生 QF 内存池的初始化](#原生-qf-内存池的初始化)
    - [从池里获得一个内存块](#从池里获得一个内存块)
    - [把一个内存块回收到池内](#把一个内存块回收到池内)
  - [原生 QF 优先级集合](#原生-qf-优先级集合)
  - [原生合作式 vanilla 内核](#原生合作式-vanilla-内核)
    - [qvanilla.c 源文件](#qvanillac-源文件)
    - [qvanilla.h 头文件](#qvanillah-头文件)
- [可抢占式“运行-到-完成”内核](#可抢占式运行-到-完成内核)
  - [选择一个可抢占式内核的理由](#选择一个可抢占式内核的理由)
  - [RTC 内核简介](#rtc-内核简介)
    - [使用单堆栈的可抢占式多任务处理](#使用单堆栈的可抢占式多任务处理)
    - [非阻塞型内核](#非阻塞型内核)
    - [同步抢占和异步抢占](#同步抢占和异步抢占)
    - [堆栈的利用](#堆栈的利用)
    - [和传统可抢占式内核的比较](#和传统可抢占式内核的比较)
- [移植和配置 QF](#移植和配置-qf)
  - [QP 平台抽象层](#qp-平台抽象层)
    - [生成 QP 应用程序](#生成-qp-应用程序)
    - [创建 QP 库](#创建-qp-库)
- [开发 QP 应用程序](#开发-qp-应用程序)
  - [开发 QP 应用程序的准则](#开发-qp-应用程序的准则)
    - [准则](#准则)
    - [启发式](#启发式)
  - [哲学家就餐问题](#哲学家就餐问题)
    - [第一步：需求](#第一步需求)
    - [第二步：顺序图](#第二步顺序图)
    - [第三步：信号，事件和活动对象](#第三步信号事件和活动对象)
    - [第四步：状态机](#第四步状态机)
    - [第五步：初始化并启动应用程序](#第五步初始化并启动应用程序)
    - [第六步：优雅的结束应用程序](#第六步优雅的结束应用程序)
  - [在不同的平台运行 DPP](#在不同的平台运行-dpp)
    - [在 DOS 上的 Vanilla 内核](#在-dos-上的-vanilla-内核)
    - [在 Cortex-M3 上的 Vanilla 内核](#在-cortex-m3-上的-vanilla-内核)
    - [uC/OS-II](#ucos-ii)
    - [Linux](#linux)
  - [调整事件队列和事件池的大小](#调整事件队列和事件池的大小)
    - [调整事件队列的大小](#调整事件队列的大小)
    - [调整事件池的大小](#调整事件池的大小)
    - [系统集成](#系统集成)
- [事件驱动型系统的软件追踪](#事件驱动型系统的软件追踪)
  - [QS 目标系统驻留构件](#qs-目标系统驻留构件)
    - [QS 源代码的组织](#qs-源代码的组织)
    - [QS 的平台无关头文件 qs.h 和 qs_dummy.h](#qs-的平台无关头文件-qsh-和-qs_dummyh)
    - [QS 的临界区](#qs-的临界区)
    - [QS 记录的一般结构](#qs-记录的一般结构)
    - [QS 的过滤器](#qs-的过滤器)
      - [全局开/关过滤器](#全局开关过滤器)
      - [本地过滤器](#本地过滤器)
    - [QS 数据协议](#qs-数据协议)
      - [透明](#透明)
      - [大小端](#大小端)
    - [QS 追踪缓存区](#qs-追踪缓存区)
      - [初始化 QS 追踪缓存区 QS_initBuf()](#初始化-qs-追踪缓存区-qs_initbuf)
    - [面向字节的接口： QS_getByte()](#面向字节的接口-qs_getbyte)
    - [面向块的接口： QS_getBlock()](#面向块的接口-qs_getblock)
    - [字典追踪记录](#字典追踪记录)
    - [应用程序相关的 QS 追踪记录](#应用程序相关的-qs-追踪记录)
    - [移植和配置 QS](#移植和配置-qs)
  - [QSPY 主机应用程序](#qspy-主机应用程序)
  - [向 MATLAB 输出追踪数据](#向-matlab-输出追踪数据)
  - [向 QP 应用程序添加 QS 软件追踪](#向-qp-应用程序添加-qs-软件追踪)
    - [定义平台相关的 QS 回调函数](#定义平台相关的-qs-回调函数)
    - [使用回调函数 QS_onGetTime() 产生 QS 时间戳](#使用回调函数-qs_ongettime-产生-qs-时间戳)
    - [从主动对象产生 QS 字典](#从主动对象产生-qs-字典)
    - [添加应用程序相关的追踪记录](#添加应用程序相关的追踪记录)
- [问题](#问题-1)
- [参考](#参考)

## 架构

![qp1](/assets/img/2022-07-27-quantum-platform-1/qp1.jpg)

`QF` 是一个轻量级`实时框架`，是 `QP事件驱动平台`的核心构件， QP 也包括了 `QEP层次式事件处理器`（在本书第一部分描叙），可抢占的`RTC内核(QK)`，和`软件追踪装置(QS)`。

## UML 状态图

### 状态机分类

有限状态机 (FSM)
: 行为的改变（例如，响应`任何事件`的改变）对应着`状态改变`，被称为状态转换。

扩展状态机(ESM)
: 事件的发生并不意味着状态改变，通过`定量`的方式，让事件发生达到`一定条件`（如次数）才`改变状态`。

层次式状态机(HSM)
: 子状态没有对应事件处理方法时，寻找父状态处理方法

包含其他状态的状态被称为复合状态 (composite state) ，相对的，没有内部结构的状态被称为简单状态 (simple state)。一个嵌套的状态当它没有被其他状态包含时被称为直接子状态 (direct substate)，否则，它被归类于过渡性嵌套子状态 (transitively nested substate) 。

### 正交区域

计算机键盘的两个正交区域（主键区和数字键区）。

![zhenjiao](/assets/img/2022-07-27-quantum-platform-1/zhenjiao.jpg)

当一个系统的行为被分解为独立的`并发性`的主动部分时，状态数目组合性增加，正交区域解决了这个常常碰到的问题。例如，除`主键区`外，一个计算机键盘有一个独立的`数字键区`。

尽管正交区域意味着执行时的`独立性`（也就是说有一些并发性）， UML 规范没有要求为每一个正交区域分配一个独立的执行线程（尽管可以这样做）。事实上最普通的情况是，这些正交区域在同一个线程里执行。 UML 规范仅要求设计者在一个事件被派发到一些相关的正交区域时，不要依赖于任何特定的次序。

### 转换的执行次序

![zhuanhuanlliuchen](/assets/img/2022-07-27-quantum-platform-1/zhuanhuanlliuchen.jpg)

在 UML ，一个`状态转换`能直接连接任何两个状态。这两个状态也许是复合的状态，它们被定名一个转换的`主源` (main source) 和`主目标` (main target)。图 2.9 展示了一个简单的转换实例，并解释了在这个转换里的状态的角色。 UML 规范描叙了执行一个状态转换需要牵涉到以下的动作 [OMG07, 15.3.13 节]:

1. 评估和转换联合的监护条件，如果监护条件为真则执行以下的步骤。
2. 退出源状态配置。
3. 执行和转换联合的动作。
4. 进入到目的状态配置。

在这个简单的实例里，主源和主目标在相同的层嵌套，因此这个转换序列很容易解释。例如，图 2.9 所示的转换 T1 引起监护条件 g() 的评估，假设监护条件 g( ) 被评估为真，后面是动作的执行序列： a( ) ； b( ) ； t( ) ； c( ) ； d( ) ； e( ) 。

**本书改动**：

本书描叙的 `HSM实现`（见第四章）通过进入到目标状态配置来维持必要的退出源结构的次序，但是完全在`源状态的上下文`里去执行和转换联合的动作。也就是说，在`退出`源状态配置`之前`执行。所实现的具体的转换序列如下：

1. 评估和转换联合的监护条件，仅当监护条件为真，执行以下的步骤。
2. 执行和转换联合的动作。
3. 退出源状态配置并进入到目标状态配置。

例如，图 2.9 所示的转换 T1 会引发对监护条件 g( ) 的评估；然后当对监护条件 g( ) 为真时是`动作序列`： t( ) ；a( ) ； b( ) ； c( ) ； d( ) ； e( ) 。

就是先进行转换和对应动作，再退出源状态，因为退出源状态意味着清空了上下文，不退出就可以利用`源状态的上下文`信息做些事情

### 本地转换和外部转换的对比

![transitions](/assets/img/2022-07-27-quantum-platform-1/transitions.jpg)

本地转换在主目标状态是`主源状态`的一个`子状态`时，并不会导致从主源状态的退出。

本地转换在主目标状态是`主源状态`的一个`超状态`时，不会导致退出和重新进入目标状态。

### UML 实例

对应 p74

假想的 `4 层嵌套状态机`，包含了所有可能的状态转换拓扑，初始 me->foo 为 0：

![SM_of_QHsmTst](/assets/img/2022-07-27-quantum-platform-1/SM_of_QHsmTst.png)

> **勘误**：s11 的 D 事件处理应该是内部转换，也就是不退出 s1，不然和后面的命令图对不上
> ![SM_of_QHsmTst2](/assets/img/2022-07-27-quantum-platform-1/SM_of_QHsmTst2.jpg)

`状态切换`，QHSMTST.EXE 实例程序运行在命令窗口。 在括号里的是供参照的行序号：

![qhsmtst](/assets/img/2022-07-27-quantum-platform-1/qhsmtst.jpg)

- 如果状态里包含大黑点（初始伪状态 ）和无条件的箭头，表示会自动进入箭头指向的状态，但首先要执行该状态自带的 init，不论是否之前 EXIT 过或是 ENTER 过（见 2.3.12 伪状态 (Pseudostates)）

  - 如（5）中，因为要处理 D 退出到了 s 状态，此时就需要执行 s 状态自带的 init，再根据无条件箭头指向的 s11，先进入 s1 再是 s11

- 伪状态

  - 初始伪装态 (initial pseudostate)( 显示为一个黑点）
  - 选择伪装态 (choice pseudostate)( 显示为一个菱形或空心圈 )
  - 浅历史伪装态 (shallow-history pseudostate)
  - 深历史伪状态 (deep-history pseudostate)
  - 连接点伪装态 (junction pseudostate)
  - 结合伪装态 (join pseudostate)
  - 分支伪装态 (fork pseudostate)

- 事件的表示

  - 事件名称(类型)
  - (可选)菱形分割
  - 监护条件(判断条件，`[]`包裹)
  - 分割号`/`
  - 动作
  - 源状态(超状态有个黑点表示本状态，表示进入此状态时无条件自动进入目标状态，状态机不能处于超状态下)
  - 目标状态

  示例 1：`I[me->foo]/me->foo=0`，`I`为事件名称，`[me->foo]`为监护条件，分割号`/`分割了事件信息和动作，`me->foo=0`为动作。

  示例 2：`e/`，`e`表示 enter 事件，没有对应的动作和监护条件；`x/`，`x`表示 exit 事件，没有对应的动作和监护条件

- `满足监护条件`才会执行对应的`状态转换`和`动作`。

- 子状态之间的状态转换需要源状态依次退出到双方的`最小共同父状态`(如 s11 和 s211 的最小共同父状态为 s，书中叫最少共同祖先 least common ancestor(LCA)，我觉得不太好理解)，再依次进入到目的标态

### 计算器设计实例

计算器（见图 2.13）总的来说操作如下：用户输入一个操作数 (operand) ，然后一个操作符 (operator)，然后另一个操作数，最后点击等号按钮得到一个结果。从编程的角度看，意味着这个计算器需要对由下面 BNF 语法定义的数字表达式进行语法分析

```plaintext
expression ::= operand1 operator operand2 '='
operand1   ::= expression | ['+' | '-'] number
operand2   ::= ['+' | '-'] number
number     ::= {'0' | '1' | ... '9'}* ['.' {'0' | '1' | ... '9'}*]
operator   ::= '+' | '-' | '*' | '/'
```

#### 高层设计

![calculater1](/assets/img/2022-07-27-quantum-platform-1/calculater1.jpg)

(a)没有结果显示状态，(b)就可以在开始下一次输入 operand1 前清空屏幕，还可以将结果作为下一次的 operand1

> 把信号 PLUS ，MINUS， MULTIPLY 和 DIVIDE `合并`成一个高级的信号 `OPER` （操作数）。这个变换避免了在两个转换（从 operand1 到 opEntered，和从 result 到 opEntered）上重复相同的触发。

#### 寻找重用 (Reuse)

![calculater2](/assets/img/2022-07-27-quantum-platform-1/calculater2.jpg)

为了保证能在任意状态执行 Clear 初始化和关机，需要很多状态转换。

此时可以提取一个超状态，初始化操作和关机操作放到超状态，让子状态重用该操作

#### operandX 状态设计

![calculater3](/assets/img/2022-07-27-quantum-platform-1/calculater3.jpg)

三个入口：

- 输入 0 事件 -- zeroX 状态
- 输入 1-9 事件 -- intX 状态
- 输入小数点事件 -- fracX 状态

三个状态：

- zeroX

  - 忽略输入 0 事件
  - 其他事件产生状态切换

- intX

  - 处理输入 0-9 事件
  - 输入小数点事件产生状态切换

- fracX

  - 处理输入 0-9 事件
  - 忽略输入小数点事件

#### 处理负号的两种情况

如表达式 -2 \* -2 =

![calculater4](/assets/img/2022-07-27-quantum-platform-1/calculater4.jpg)

添加两个和 operandX 同级的状态 negated1 和 negated2 用于处理数字前的负号，和 zeroX 状态类似

#### 最终状态图

![calculater5](/assets/img/2022-07-27-quantum-platform-1/calculater5.jpg)

## 状态模式

状态机面向对象的设计模式，设计模式就是用于解决实际问题的最佳实践

### 延迟的事件

#### 目的

通过改变事件的顺序来简化状态机。

#### 问题

有时候一个事件在某个`不方便`的时刻到达，这时刻系统正在某个`复杂的事件队列`的中间。

> `复杂的事件队列`指一系列不应该被打断的事件，如发送请求、等待收到回复事件后处理回复，两个事件不是同时发生，但中间也不希望被插入新事件打断

实例：服务器程序处理业务（如从 ATM 终端）的案例。一旦业务开始了，它典型地要走完一个处理序列，从一个远距离终端接受数据开始，然后是业务的授权。这几个事件被视为`连续事件`，虽然事件产生有一定时间间隔，但希望它们能连续执行而不应该被新到达的业务打断。（可以理解为中断，中断的话需要保存上下文，退出中断后恢复，同理状态机处理“中断”也要保存当前状态和上下文，等新事件处理完恢复，太麻烦了）

#### 解决

添加一个`等待队列`，当新业务事件到达时加入这个队列而不是事件队列，在 idle 时再去读取等待队列，把等待队列里的事件加入事件队列

![deferevent](/assets/img/2022-07-27-quantum-platform-1/deferevent.jpg)

![deferevent2](/assets/img/2022-07-27-quantum-platform-1/deferevent2.jpg)

处于 busy 状态的子状态(receiving 和 authorizing)时，收到新的请求事件，处理方法为不执行并加入等待队列，然后该事件会被移除出事件队列，原业务得以继续正常执行。

## 标准状态机的实现方法

定时炸弹状态机的 UML 状态图:

![bomb](/assets/img/2022-07-27-quantum-platform-1/bomb.jpg)

### 嵌套的 switch 语句

```c
void Bomb1_dispatch(Bomb1 *me, Event const *e) { /* dispatching */
  switch (me->state) {
    case SETTING_STATE: {
      switch (e->sig) {
        case UP_SIG: { /* internal transition with a guard */
        ...}
      }
      ...
    }
    case TIMING_STATE: {
      switch (e->sig) {
        case UP_SIG: {
          me->code <<= 1;
          me->code |= 1;
          break;
        }
        ...
      }
      ...
    }
    ...
  }
}
```

### 状态表 (State Table)

![bomb_statetable](/assets/img/2022-07-27-quantum-platform-1/bomb_statetable.jpg)

| 当前状态 | 事件 ( 参数 )   | [ 监护条件 ]             | 下一状态 | 动作                                    |
| :------- | :-------------- | :----------------------- | :------- | :-------------------------------------- |
| setting  | UP              | [me->timeout < 60]       | setting  | ++me->timeout;BSP_display(me->timeout); |
|          | DOWN            | [me->timeout > 1]        | setting  | --me->timeout;BSP_display(me->timeout); |
|          | ARM             |                          | timing   | me->code = 0;                           |
|          | TICK            |                          | setting  |                                         |
| timing   | UP              |                          | timing   | me->code <<=1;me->code = 1;             |
|          | DOWN            |                          | timing   | me->code <<= 1;                         |
|          | ARM             | [me->code == me->defuse] | setting  |                                         |
|          | TICK(fine_time) | [e->fine_time == 0]      | choice   | --me->timeout;BSP_display(me->timeout); |
|          |                 | [me->timeout == 0]       | final    | BSP_boom();                             |
|          |                 | [else]                   | timing   |                                         |

### 面向对象的状态设计模式

![bomb_oob](/assets/img/2022-07-27-quantum-platform-1/bomb_oob.jpg)

用到了多态，使用 C++实现更为简单

正常来说 BombState 被定义为`抽象类`，应该包含至少一个`纯虚函数`，不过此处没有，应该是为了让子类继承父类中虚函数的空实现。

#### 增加进入退出状态操作

![bomb_oob2](/assets/img/2022-07-27-quantum-platform-1/bomb_oob2.jpg)

Bomb 类的 onTick()操作不仅调用了 BombState 状态或是子状态的 onTick 事件处理，还检测了状态是否切换，并执行对应的退出和进入动作

#### 封装事件处理

![bomb_oob3](/assets/img/2022-07-27-quantum-platform-1/bomb_oob3.jpg)

封装了状态中的事件处理函数，这就导致需要在封装函数内使用`switch`区分事件并执行操作。

坏处是失去了 C++提供的多态性

好处是在添加新事件时只需修改函数内内容，无需增加函数定义

### QEP FSM 实现方法

在前面的几节里，提供了实现 FSM 的三种最流行的技术。可是从我的经验来说，单独使用它们时没有一个是最优的

本章只介绍 FSM 的实现，HSM 层次式状态机的在下一章

通用的 QEP 事件处理器：

QEP（事件处理器）设计的创新性来自于把`状态`直接映射成`状态处理函数`，处理在状态里它们表示的全部事件

![qep](/assets/img/2022-07-27-quantum-platform-1/qep.jpg)

```c
/* qevent.h ----------------------------------------------------------------*/
typedef struct QEventTag
{                     /* the event structure */
    // 一个整数，相当于事件唯一标识，方便switch...case...区分事件
    QSignal sig;      /* signal of the event */
    uint8_t dynamic_; /* dynamic attribute of the event (0 for static) */
} QEvent; // 事件，可派生添加参数

/* qep.h -------------------------------------------------------------------*/
// 事件处理对事件处理的状态
typedef uint8_t QState;          /* status returned from a state-handler function */
// 状态处理函数指针，本设计中状态处理函数就表示状态，有typedef表示指定它的类型为QState，
// 相当于一种声明，而非定义产生实例
typedef                          /* pointer to function type definition */
    QState                       /* return type */
    (*QStateHandler)             /* name of the pointer-to-function type */
    (void *me, QEvent const *e); /* argument list */ // 一个通用状态机的指针和一个 QEvent指针

typedef struct QFsmTag
{                        /* Finite State Machine */
    // 当前处于的状态，指向状态处理函数
    QStateHandler state; /* current active state */
} QFsm; // 派生各个状态机结构的基本类

#define QFsm_ctor(me_, initial_) ((me_)->state = (initial_))
// 触发状态机的初始转换
void QFsm_init(QFsm *me, QEvent const *e);
// 派发一个事件给状态机
void QFsm_dispatch(QFsm *me, QEvent const *e);

// 从状态处理函数到事件处理器的返回状态
#define Q_RET_HANDLED ((QState)0)
#define Q_RET_IGNORED ((QState)1)
#define Q_RET_TRAN ((QState)2)

// 一个状态处理函数，每当它处理了当前的事件时，返回宏 Q_HANDLED( ) 。
#define Q_HANDLED() (Q_RET_HANDLED)
// 一个状态处理函数，每当它忽略（不处理）当前的事件时，返回宏 Q_IGNORED( )
#define Q_IGNORED() (Q_RET_IGNORED)
// 逗号表达式表示执行逗号前语句，但整个表达式的值为逗号后变量，优先级比'='更低，
// 先执行((QFsm *)me)->state = (QStateHandler)(target_)，但Q_TRAN(target_)值为Q_RET_TRAN
// 这里可以用(QFsm *)强制转换me是因为派生类me的第一个成员变量就是它的父类QFsm实例，内存起始位置和me一样
#define Q_TRAN(target_) \
    (((QFsm *)me)->state = (QStateHandler)(target_), Q_RET_TRAN)

// 内部使用的信号
// QEP内部维护一个不变的保留事件数组 QEP_reservedEvt_[ ]。用于保存信号对应的事件
enum QReservedSignals
{
    Q_ENTRY_SIG = 1, /* signal for coding entry actions */
    Q_EXIT_SIG,      /* signal for coding exit actions */
    Q_INIT_SIG,      /* signal for coding initial transitions */
    Q_USER_SIG       /* first signal that can be used in user applications */
};
```

QEP FSM 事件处理器的实现:

```c
/* file qfsm_ini.c ---------------------------------------------------------*/
#include "qep_port.h" /* the port of the QEP event processor */
#include "qassert.h"  /* embedded systems-friendly assertions */
void QFsm_init(QFsm *me, QEvent const *e)
{
    // 执行QFsm超状态的状态处理函数，就是init
    (*me->state)(me, e); /* execute the top-most initial transition */
    // 进入目的状态，手动指定状态切换事件(用信号Q_ENTRY_SIG指定)，并处理状态切换事件
    // QEP内部维护一个不变的保留事件数组 QEP_reservedEvt_[ ]。用于保存信号对应的事件
    (void)(*me->state)(me, &QEP_reservedEvt_[Q_ENTRY_SIG]);/* enter the target */
}
/* file qfsm_dis.c ---------------------------------------------------------*/
// 事件生成函数
void QFsm_dispatch(QFsm *me, QEvent const *e)
{
    // 在栈空间中临时保存，防止执行事件处理函数切换状态后丢失源状态
    QStateHandler s = me->state; /* save the current state */
    // 调用当前状态中对应的事件处理函数
    QState r = (*s)(me, e);      /* call the event handler */
    if (r == Q_RET_TRAN) // 执行事件处理函数后发生了状态转换
    {                                                           /* transition taken? */
        // 退出源状态，调用源状态的事件处理函数（发送信号Q_EXIT_SIG）
        (void)(*s)(me, &QEP_reservedEvt_[Q_EXIT_SIG]);          /* exit the source */
        // 进入目的状态，调用目的状态的事件处理函数（发送信号Q_ENTRY_SIG）
        (void)(*me->state)(me, &QEP_reservedEvt_[Q_ENTRY_SIG]); /*enter target*/
    }
}
```

应用程序相关的代码(定时炸弹实例):

```c
#include "qep_port.h" /* the port of the QEP event processor */
#include "bsp.h"      /* board support package */
// 内部使用的信号
enum BombSignals
{ /* all signals for the Bomb FSM */
  UP_SIG = Q_USER_SIG,
  DOWN_SIG,
  ARM_SIG,
  TICK_SIG
};
// 继承自QEvent的Tick事件
typedef struct TickEvtTag
{
    QEvent super;      /* derive from the QEvent structure */
    uint8_t fine_time; /* the fine 1/10 s counter */
} TickEvt;
// 继承自QFsm的状态机，增加了自定义的一些参数
typedef struct Bomb4Tag
{
    QFsm super;      /* derive from QFsm */
    uint8_t timeout; /* number of seconds till explosion */ //倒计时
    uint8_t code;    /* currently entered code to disarm the bomb */ //密码输入值
    uint8_t defuse;  /* secret defuse code to disarm the bomb */ //密码
} Bomb4;
// 后面是不是就是检测到事件时调用me->state(me,e)就行
void Bomb4_ctor(Bomb4 *me, uint8_t defuse); // 初始化（类似C++的构造函数）
QState Bomb4_initial(Bomb4 *me, QEvent const *e); // 入口
QState Bomb4_setting(Bomb4 *me, QEvent const *e); // setting状态事件处理函数
QState Bomb4_timing(Bomb4 *me, QEvent const *e); // timing状态事件处理函数
/*--------------------------------------------------------------------------*/
/* the initial value of the timeout */
#define INIT_TIMEOUT 10
/*..........................................................................*/
void Bomb4_ctor(Bomb4 *me, uint8_t defuse)
{
    QFsm_ctor_(&me->super, (QStateHandler)&Bomb4_initial);
    me->defuse = defuse; /* the defuse code is assigned at instantiation */
}
/*..........................................................................*/
QState Bomb4_initial(Bomb4 *me, QEvent const *e)
{
    (void)e;
    me->timeout = INIT_TIMEOUT;
    return Q_TRAN(&Bomb4_setting); //切换到setting
}
/*..........................................................................*/
QState Bomb4_setting(Bomb4 *me, QEvent const *e)
{
    // 使用switch区分事件，这里是用了QEvent中的一个整数变量sig，相当于事件唯一标识，
    // 因为switch只支持int整数，不支持结构体
    switch (e->sig)
    {
    case UP_SIG:
    {
        if (me->timeout < 60)
        {
            ++me->timeout;
            BSP_display(me->timeout);
        }
        return Q_HANDLED();// 不切换状态就返回Q_HANDLED()
    }
    case DOWN_SIG:
    {
        if (me->timeout > 1)
        {
            --me->timeout;
            BSP_display(me->timeout);
        }
        return Q_HANDLED();
    }
    case ARM_SIG:
    {
        // 需要切换状态就使用Q_TRAN
        return Q_TRAN(&Bomb4_timing); /* transition to "timing" */
    }
    }
    return Q_IGNORED();// 没有对应事件就返回Q_IGNORED()
}
/*..........................................................................*/
void Bomb4_timing(Bomb4 *me, QEvent const *e)
{
    switch (e->sig)
    {
    case Q_ENTRY_SIG:
    {
        me->code = 0; /* clear the defuse code */
        return Q_HANDLED();
    }
    case UP_SIG:
    {
        me->code <<= 1;
        me->code |= 1;
        return Q_HANDLED();
    }
    case DOWN_SIG:
    {
        me->code <<= 1;
        return Q_HANDLED();
    }
    case ARM_SIG:
    {
        if (me->code == me->defuse)
        {
            return Q_TRAN(&Bomb4_setting);
        }
        return Q_HANDLED();
    }
    case TICK_SIG:
    {
        // 拿派生事件的自定义参数也没问题
        if (((TickEvt const *)e)->fine_time == 0)
        {
            --me->timeout;
            BSP_display(me->timeout);
            if (me->timeout == 0)
            {
                BSP_boom(); /* destroy the bomb */
            }
        }
        return Q_HANDLED();
    }
    }
    return Q_IGNORED();
}
```

### 状态机实现技术的一般性讨论

- `函数指针`是使用 C/C++ 实现状态机时最快的途径。状态函数可以放在 ROM 里，RAM 里只需存指针。
- C++语言里，`异常抛出和捕捉`例外和状态机的`运行到完成` (RTC) 语义基本上`不相容`。因为破坏了事件处理的原子性
- `监护条件`和`选择伪状态`的实现就是把`return Q_TRAN()`改为条件判断函数，将切换状态的任务交给该函数
- `QFsm_dispatch`实现状态切换的方式是发送`EXIT`和`ENTER`事件(信号)给对应状态，这样状态可以在进入和退出时做一些事情，如初始化某些值，相关状态只需要在事件处理函数中实现对这类事件的处理。

## 层次式事件处理器的实现

![qep_hsm](/assets/img/2022-07-27-quantum-platform-1/qep_hsm.jpg)

下面只介绍和 FSM 实现不同的地方

### 层次式状态处理函数

一个层次式状态处理函数`QStateHandler`必须特别通知事件处理器有关状态`嵌套层次`的信息。

当一个层次式状态处理函数不处理当前的事件，它返回一个宏 `Q_SUPER()`给事件处理器，定义如下:

```c
#define Q_RET_SUPER ((QState)3)
#define Q_SUPER(super_) \
  (((QHsm *)me)->state = (QStateHandler)(super_), Q_RET_SUPER)
```

FSM 里不处理是返回`Q_RET_IGNORED`，因为没有超状态去处理它，HSM 里就需要返回`Q_RET_SUPER`

```c
QState Calc_int1(Calc *me, QEvent const *e)
{
    switch (e->sig)
    {
    case DIGIT_0_SIG: /* intentionally fall through */
    case DIGIT_1_9_SIG:
    {
        BSP_insert(((CalcEvt const *)e)->key_code);
        return Q_HANDLED();
    }
    case POINT_SIG:
    {
        BSP_insert(((CalcEvt const *)e)->key_code);
        return Q_TRAN(&Calc_frac1);
    }
    }
    return Q_SUPER(&Calc_operand1);
}
```

### 层次式状态机的类

QHsm 类

**C 语言版本**：

```c
typedef struct QHsmTag
{
    QStateHandler state; /* current active state (state-variable) */
} QHsm; // 这里和FSM一样，事件处理函数的指针
#define QHsm_ctor(me_, initial_) ((me_)->state = (initial_))
void QHsm_init(QHsm *me, QEvent const *e);
// 分派事件
void QHsm_dispatch(QHsm *me, QEvent const *e);
// 测试HSM是否“在”一个给定的状态内，超状态包括子状态
uint8_t QHsm_isIn(QHsm *me, QHsmState state);
/**
 * 函数QHsm_top( )是顶状态的层次式状态处理函数。
 * 顶状态是 UML 的概念，表示状态层次的最终根。
 * 顶状态处理函数对每一个事件的处理方法是静静的忽略它，
 * 这是 UML 的默认方法
 */
QState QHsm_top(QHsm *me, QEvent const *e);
```

c 语言版本的不太直观，没有反应出继承关系，建议看 C++版本的

**C++版本**：

```cpp
class QHsm
{
protected:
    QStateHandler m_state; // current active state (state-variable)

public:
    void init(QEvent const *e = (QEvent const *)0);
    void dispatch(QEvent const *e);
    uint8_t isIn(QHsmState state);

protected:
    QHsm(QStateHandler initial) : m_state(initial) {} // protected ctor
    static QState top(QHsm *me, QEvent const *e);
};
```

其中`top`函数就是 C 版本中的`QHsm_top`，这里用了`静态类型`，这样子类继承后所有对象共享相同的 top 函数，也可以`防止被重载`。且 static 成员变量或函数在基类和派生类中是`共用空间`的，可以节省空间

除此之外的其他成员函数都是需要`重载`的

#### 顶状态和初始伪状态

每一个 HSM 都有（典型的是隐含）`顶状态` top，它围绕着整个状态机的全部其他元素

![qep_hsm2](/assets/img/2022-07-27-quantum-platform-1/qep_hsm2.jpg)

QHsm 类通过提供 `QHsm_top()` 层次式状态处理函数，然后由`子类`来继承它，从而确保顶状态对每一个`派生`的状态机都是可用的。 `QHsm_top()` 层次式状态处理函数定义如下：

```c
// protected型的静态成员函数，子类都可调用，一般在子类处理事件时如果没有找到对应处理方式时调用
QState QHsm_top(QHsm *me, QEvent const *e)
{
    // 避免编译器报未使用参数的警告，空引用一下
    (void)me;           /* avoid the compiler warning about unused parameter */
    (void)e;            /* avoid the compiler warning about unused parameter */
    // 顶状态可以理解为一个虚状态，不做任何事，所以忽略掉事件
    return Q_IGNORED(); /* the top state ignores all events */
}
```

状态机的初始化被特意分为 2 步。 QHsm `构造函数`仅仅把状态变量初始化成`初始伪状态`。然后，应用程序代码必须通过调用`QHsm_init()`明确的触发初始转换。这个设计分割了状态机的实例化和初始化，让用户程序对系统的初始化顺序有完全的控制。

下一节有详细描述

以下代码展示了计算器状态机的一个初始伪状态处理函数的例子：

```c
QState Calc_initial(Calc *me, QEvent const *e)
{
    (void)e;                 /* avoid the compiler warning about unused parameter */
    BSP_clear();             /* clear the calculator display */
    // 初始化后必须转换到默认子状态的操作
    return Q_TRAN(&Calc_on); /* designate the default state */
}
```

`非叶子`状态才有`初始伪状态`，离开状态再次进入会触发初始化

#### 进入 / 退出动作和嵌套的初始转换

```c
enum QReservedSignals {
    Q_ENTRY_SIG = 1, /* signal for coding entry actions */
    Q_EXIT_SIG, /* signal for coding exit actions */
    Q_INIT_SIG, /* signal for coding initial transitions */
    Q_USER_SIG /* first signal that can be used in user code */
};
```

状态处理函数能够通过把它们放在在 switch 语句的 case 后作为标签来处理它们。

状态处理函数可以任意执行任何动作去响应这些信号

限制条件：

- `进入动作Q_ENTRY_SIG`和`退出动作Q_EXIT_SIG`中不能做任何`状态转换`
- `初始化动作Q_INIT_SIG`必须包括 `Q_TRAN()` 宏来转换到当前状态的`默认子状态`。

嵌套的初始转换必须“钻进”状态层次(直接或间接的子状态)，但是不能“上升” 到目标超状态，或“绕道”到同级状态。

```c
QState Calc_on(Calc *me, QEvent const *e)
{
    switch (e->sig)
    {
        case Q_ENTRY_SIG:
        { /* entry action */
            BSP_message("on-ENTRY;");
            return Q_HANDLED();
        }
        case Q_EXIT_SIG:
        { /* exit action */
            BSP_message("on-EXIT;");
            return Q_HANDLED();
        }
        case Q_INIT_SIG:
        { /* nested initial transition */
            BSP_message("on-INIT;");
            // 初始化后必须转换到子状态
            return Q_TRAN(&Calc_ready);
        }
        case C_SIG:
        {
            BSP_clear();
            return Q_TRAN(&Calc_on);
        }
        case OFF_SIG:
        {
            return Q_TRAN(&Calc_final);
        }
    }
    // 无法处理时使用超状态处理
    return Q_SUPER(&QHsm_top);
}
```

`保留`的信号占用最低的信号值（ 0...3,进入退出和初始化），它们不能被`应用程序`使用。为了方便，公开的 HSM 接口包含了信号 `Q_USER_SIG` ，这是用户可以使用的`第一个信号值`。一个典型的定义应用程序级信号的方法是使用一个新的`枚举值`。这样 Q_USER_SIG 能被用于`偏移`全部新的枚举量

#### 最顶层初始转换 (QHsm_init())

![qep_hsm3](/assets/img/2022-07-27-quantum-platform-1/qep_hsm3.jpg)

1. 执行和最顶层转换关联的动作
2. 执行进入动作到达默认子状态 `on`
3. 执行由状态 `on` 定义的和`初始`转换关联的动作
4. 执行进入动作到达默认子状态 `ready`
5. 执行由状态 `ready` 定义的和`初始`转换关联的动作，进入 `begin`
6. 执行和状态 `begin` 关联的进入动作。在这一刻，转换已经完成，因为 `begin` 是没有嵌套的初始转换的`叶状态`。

树状继承结构的优势是从叶节点`返回`到上层节点(如 top)很容易，但从上层节点`进入`到指定的目的节点却很复杂，因为要`遍历`寻找叶节点的父节点

QEP 里的解决方法是使用一个临时的数组 `path[]` 记录从初始状态的目标状态开始的`退出路径`而不执行任何动作（见图 4.4 ）。通过使用保留的 `QEP_EMPTY_SIG_` 信号来调用状态处理函数，令每一个状态处理函数不执行任何动作就立刻返回超状态。返回的路径被保存在 path[] 数组。在到达当前的状态后， path[] 数组被回访，精确的沿着它被退出的`相反次序`进入目标状态

使用 path[] 数组沿着正确的次序进入目标状态配置:

![qep_hsm4](/assets/img/2022-07-27-quantum-platform-1/qep_hsm4.jpg)

```c
#define QEP_TRIG_(state_, sig_) \
    ((*(state_))(me, &QEP_reservedEvt_[sig_]))

#define QEP_EXIT_(state_) \
    if (QEP_TRIG_(state_, Q_EXIT_SIG) == Q_RET_HANDLED) { \
        /* QS software tracing instrumentation for state entry */\
    }

#define QEP_ENTER_(state_) \
    if (QEP_TRIG_(state_, Q_ENTRY_SIG) == Q_RET_HANDLED) { \
        /* QS software tracing instrumentation for state exit */\
    }
void QHsm_init(QHsm *me, QEvent const *e)
{
    QStateHandler t;
    /* the top-most initial transition must be taken */
    // 初始伪状态产生的初始转换（只改了state没有执行对应进入动作）
    Q_ALLEGE((*me->state)(me, e) == Q_RET_TRAN);
    // 临时保存源状态t（第一次为top）
    t = (QStateHandler)&QHsm_top; /* HSM starts in the top state */
    do
    { /* drill into the target... */
        QStateHandler path[QEP_MAX_NEST_DEPTH_];
        int8_t ip = (int8_t)0; /* transition entry path index */
        // 临时存下目的状态，同时作为路径起点，前面做过状态转换，me->state已经是目的状态了
        path[0] = me->state;   /* save the target of the initial transition */
        // 返回到超状态，利用QEP_EMPTY_SIG_信号
        (void)QEP_TRIG_(me->state, QEP_EMPTY_SIG_);
        // 直到回退到源状态t，这里都只是修改state没有触发进入退出动作
        while (me->state != t)
        {
            // 保存路径
            path[++ip] = me->state;
            // 不断返回超状态，直到到达源状态
            (void)QEP_TRIG_(me->state, QEP_EMPTY_SIG_);
        }
        // 路径记录完把状态恢复为目的状态(只改了state没有执行对应进入动作)
        me->state = path[0]; /* restore the target of the initial tran. */
                             /* entry path must not overflow */
        Q_ASSERT(ip < (int8_t)QEP_MAX_NEST_DEPTH_);
        do
        {/* retrace the entry path in reverse (desired) order... */
            // 反向遍历路径，从源状态一层层进入目的状态（处理ENTER信号）
            QEP_ENTER_(path[ip]); /* enter path[ip] */
        } while ((--ip) >= (int8_t)0);
        // 临时保存源状态t（就是本循环一开始的目的状态，在下个循环里就是源状态了）
        // 现在来看是等于me->state的，因为上面也给me->state赋值了
        t = path[0]; /* current state becomes the new source */
    // 如果本次循环抵达的目的状态不是叶状态，还要继续深入
    } while (QEP_TRIG_(t, Q_INIT_SIG) == Q_RET_TRAN);
    // 直到当前状态为叶状态
    me->state = t;
}
```

> QEP 内定义的断言宏：
>
> - Q_REQUIRE()，断言一个前置条件
> - Q_ENSURE() ，断言一个后置条件
> - Q_INVARIANT() ，断言一个不变量
> - Q_ASSERT() ，断言一个其他类型的一般性契约
> - Q_ALLEGE，断言一个一般性的契约，而且即使在编译时间断言被禁止了也评估当前的情况。

#### 分派事件（ QHsm_dispatch(), 通用结构）

```c
void QHsm_dispatch(QHsm *me, QEvent const *e)
{
    QStateHandler path[QEP_MAX_NEST_DEPTH_];
    QStateHandler s;// source源状态
    QStateHandler t;// target目的状态
    QState r;
    // 临时保存当前状态，后面作为源状态
    t = me->state; /* save the current state */
    // 执行对应状态事件处理函数，如果返回Q_RET_SUPER说明交给了超状态处理，
    // 此时继续执行，直到某个超状态处理了该事件
    do
    { /* process the event hierarchically... */
        s = me->state;
        r = (*s)(me, e); /* invoke state handler s */
    } while (r == Q_RET_SUPER);
    // 当需要转换状态时，源状态必须为处理该事件的状态，
    // 所以如果处理事件的状态为超状态而非当前状态，
    // 当前状态必须切换为该超状态，也就是返回到该超状态
    if (r == Q_RET_TRAN)
    {                             /* transition taken? */
        int8_t ip = (int8_t)(-1); /* transition entry path index */
        int8_t iq;                /* helper transition entry path index */
        // 路径0赋值为目的状态
        path[0] = me->state;      /* save the target of the transition */
        // 路径1赋值为源状态
        path[1] = t;
        // s状态就是实际处理了该事件的状态
        // s状态可能是源状态，也可能是源状态的某个超状态
        // 如果当前状态不为s状态时，当前状态退出直到s状态
        while (t != s)
        { /* exit current state to transition source s... */
            // 退出源状态
            if (QEP_TRIG_(t, Q_EXIT_SIG) == Q_RET_HANDLED)
            {                                       /*exit handled? */
                // 退出成功时返回到超状态
                (void)QEP_TRIG_(t, QEP_EMPTY_SIG_); /* find superstate of t */
            }
            // t赋值为该超状态
            t = me->state; /* me->state holds the superstate */
        }
        // 最后t==s，执行状态切换动作（下一节讲）
        ...
    }
    me->state = t; /* set new state or restore the current state */
}
```

对`if (r == Q_RET_TRAN)`的解释：当需要转换状态时，源状态必须为处理该事件的状态，所以如果处理事件的状态为超状态而非当前状态，当前状态必须切换为该超状态，也就是返回到该超状态

![qep_hsm5](/assets/img/2022-07-27-quantum-platform-1/qep_hsm5.jpg)

本图中 result 收到的 OPER 事件被交给 ready 处理，ready 对事件的处理需要转换状态到 opEntered，所以必须将当前状态转变为 ready，也就是退出 result(此时不触发 ready 的 init，可以不把这个操作理解成标准的状态切换，因为本身 ready 也是临时状态，马上要切换成其他状态了)，然后触发状态切换从 ready 到 opEntered

#### 在状态机里实施一个转换（ QHsm_dispatch(), 转换）

上一节是找路径，这一节是沿着路径做转换

在 HSM 里执行一个通用的`状态转换`，到目前为止是 QEP 实现的`最复杂`的部分。挑战是最快的找到源状态和目标状态的`最少共同祖先` (`LCA`) 状态。 (LCA 是同时源状态和目标状态的超状态里的最低层次的状态 ) 。

然后转换序列牵涉到所有状态的`退出`动作，向上到达`LCA`（但是`不退出 LCA`本身），然后是递归的进入到目标状态，然后使用初始转换“`钻入`”到目标状态配置，直到到达一个`叶状态`为止。

![qep_hsm6](/assets/img/2022-07-27-quantum-platform-1/qep_hsm6.jpg)

> h: 子状态到超状态的超状态

```c
/* NOTE: 上一节代码省略部分 */
// 路径0保存了目的状态，给t赋值，t等于me->state
t = path[0]; /* target of the transition */
// 如果源状态等于目的状态，相当于自转换，情况(a)适用
if (s == t)
{                   /* (a) check source==target (transition to self) */
    QEP_EXIT_(s)    /* exit the source */
    ip = (int8_t)0; /* enter the target */
}
else
{
    // t(等于当前状态me->state)退出到超状态
    // 使用t作为参数，会忽略me->state原有值，执行后强制赋值，
    // 如此处给空信号返回超状态，me->state强制赋值为t的超状态
    (void)QEP_TRIG_(t, QEP_EMPTY_SIG_); /* superstate of target */
    // 为t赋值当前状态（目的状态的超状态）
    t = me->state;
    // 情况(b)，目的状态的超状态为源状态，超状态进入子状态（源状态不用退出）
    if (s == t)
    {                   /* (b) check source==target->super */
        ip = (int8_t)0; /* enter the target */
    }
    else
    {
        // 退出到s的超状态，为me->state强制赋值
        (void)QEP_TRIG_(s, QEP_EMPTY_SIG_); /* superstate of src */
                                            /* (c) check source->super==target->super */
        // 情况(c)，源状态的超状态等于目的状态的超状态
        if (me->state == t)
        {
            QEP_EXIT_(s)    /* exit the source */
            ip = (int8_t)0; /* enter the target */
        }
        else
        {
            /* (d) check source->super==target */
            // 情况(d)，源超状态等于目的状态
            if (me->state == path[0])
            {
                QEP_EXIT_(s) /* exit the source */
            }
            else
            {                   /* (e) check rest of source==target->super->super..
                                 * and store the entry path along the way
                                 */
                iq = (int8_t)0; /* indicate that LCA not found */
                ip = (int8_t)1; /* enter target and its superstate */
                path[1] = t;    /* save the superstate of target */
                t = me->state;  /* save source->super */
                /* find target->super->super */
                r = QEP_TRIG_(path[1], QEP_EMPTY_SIG_);
                while (r == Q_RET_SUPER)
                {
                    path[++ip] = me->state; /* store the entry path */
                    if (me->state == s)
                    {                   /* is it the source? */
                        iq = (int8_t)1; /* indicate that LCA found */
                        /* entry path must not overflow */
                        Q_ASSERT(ip < (int8_t)QEP_MAX_NEST_DEPTH_);
                        --ip;              /* do not enter the source */
                        r = Q_RET_HANDLED; /* terminate the loop */
                    }
                    else
                    { /* it is not the source, keep going up */
                        r = QEP_TRIG_(me->state, QEP_EMPTY_SIG_);
                    }
                }
                if (iq == (int8_t)0)
                { /* the LCA not found yet? */
                    /* entry path must not overflow */
                    Q_ASSERT(ip < (int8_t)QEP_MAX_NEST_DEPTH_);
                    QEP_EXIT_(s) /* exit the source */
                    /* (f) check the rest of source->super
                     * == target->super->super...
                     */
                    iq = ip;
                    r = Q_RET_IGNORED; /* indicate LCA NOT found */
                    do
                    {
                        if (t == path[iq])
                        {                          /* is this the LCA? */
                            r = Q_RET_HANDLED;     /* indicate LCA found */
                            ip = (int8_t)(iq - 1); /*do not enter LCA*/
                            iq = (int8_t)(-1);     /* terminate the loop */
                        }
                        else
                        {
                            --iq; /* try lower superstate of target */
                        }
                    } while (iq >= (int8_t)0);
                    if (r != Q_RET_HANDLED)
                    { /* LCA not found yet? */
                        /* (g) check each source->super->...
                         * for each target->super...
                         */
                        r = Q_RET_IGNORED; /* keep looping */
                        do
                        {
                            /* exit t unhandled? */
                            if (QEP_TRIG_(t, Q_EXIT_SIG) == Q_RET_HANDLED)
                            {
                                (void)QEP_TRIG_(t, QEP_EMPTY_SIG_);
                            }
                            t = me->state; /* set to super of t */
                            iq = ip;
                            do
                            {
                                if (t == path[iq])
                                { /* is this LCA? */
                                    /* do not enter LCA */
                                    ip = (int8_t)(iq - 1);
                                    iq = (int8_t)(-1); /*break inner */
                                    r = Q_RET_HANDLED; /*break outer */
                                }
                                else
                                {
                                    --iq;
                                }
                            } while (iq >= (int8_t)0);
                        } while (r != Q_RET_HANDLED);
                    }
                }
            }
        }
    }
}
/* retrace the entry path in reverse (desired) order... */
for (; ip >= (int8_t)0; --ip)
{
    QEP_ENTER_(path[ip]) /* enter path[ip] */
}
t = path[0];   /* stick the target into register */
me->state = t; /* update the current state */
               /* drill into the target hierarchy... */
while (QEP_TRIG_(t, Q_INIT_SIG) == Q_RET_TRAN)
{
    ip = (int8_t)0;
    path[0] = me->state;
    (void)QEP_TRIG_(me->state, QEP_EMPTY_SIG_); /* find superstate */
    while (me->state != t)
    {
        path[++ip] = me->state;
        (void)QEP_TRIG_(me->state, QEP_EMPTY_SIG_); /*find superstate*/
    }
    me->state = path[0];
    /* entry path must not overflow */
    Q_ASSERT(ip < (int8_t)QEP_MAX_NEST_DEPTH_);
    do
    {                        /* retrace the entry path in reverse (correct) order... */
        QEP_ENTER_(path[ip]) /* enter path[ip] */
    } while ((--ip) >= (int8_t)0);
    t = path[0];
}
```

### 使用 QEP 实现 HSM 步骤的概要

计算器认识的按键是： 0 ， 1-9 ， . ， + ， - ， \* ， / ， = ， C 和 E(cancel entry CE) 。ESC 按键终止程序。其他别的按键会被忽略。

- 枚举信号，如 C， CE ， DIGIT_0 ， DIGIT_1_9 等待
- 定义事件，如`OPER_SIG`信号对应按下+ ， - ， \* ， / 的四个事件，事件参数在 key_code 变量中

  ```c
  struct CalcEvt : public QEvent {
    uint8_t key_code;
  };
  ```

- 派生特定的状态机

  ```c
  class Calc : public QHsm
  {
  private:
      double m_operand1;  // the value of operand 1 (extended state variable)
      uint8_t m_operator; // operator key entered (extended state variable)
  public:
      Calc() : QHsm((QStateHandler)&Calc::initial)
      { // ctor
      }

  protected:
      // 声明为静态,如果有扩展派生类也能共享
      static QState initial(Calc *me, QEvent const *e);   // initial pseudostate
      static QState on(Calc *me, QEvent const *e);        // state handler
      static QState error(Calc *me, QEvent const *e);     // state handler
      static QState ready(Calc *me, QEvent const *e);     // state handler
      static QState result(Calc *me, QEvent const *e);    // state handler
      static QState begin(Calc *me, QEvent const *e);     // state handler
      static QState negated1(Calc *me, QEvent const *e);  // state handler
      static QState operand1(Calc *me, QEvent const *e);  // state handler
      static QState zero1(Calc *me, QEvent const *e);     // state handler
      static QState int1(Calc *me, QEvent const *e);      // state handler
      static QState frac1(Calc *me, QEvent const *e);     // state handler
      static QState opEntered(Calc *me, QEvent const *e); // state handler
      static QState negated2(Calc *me, QEvent const *e);  // state handler
      static QState operand2(Calc *me, QEvent const *e);  // state handler
      static QState zero2(Calc *me, QEvent const *e);     // state handler
      static QState int2(Calc *me, QEvent const *e);      // state handler
      static QState frac2(Calc *me, QEvent const *e);     // state handler
      static QState final(Calc *me, QEvent const *e);     // state handler
  };
  ```

- 定义初始伪状态，作用是执行一些初始化操作，还有转换到默认状态 on

  ```c
  QState Calc::initial(Calc *me, QEvent const * /* e */)
  {
      BSP_clear();
      return Q_TRAN(&Calc::on);
  }
  ```

- 定义状态处理函数

  用 switch 处理信号，避免`switch外`的处理代码

  - Q_ENTRY_SIG 和 Q_EXIT_SIG：进入动作和退出动作，总是返回 Q_HANDLED()，`不允许`状态切换
  - Q_INIT_SIG：每个`组合状态`（带有子状态的状态）能有它自己的`初始转换`，初始转换不能有监护条件，初始转换只能以自己的子状态作为目的状态
  - 内部转换：内部转换是对事件的简单反应，并从`不导致`状态的转换，因此也从不导致进入动作，退出动作或初始转换的执行，总是返回 Q_HANDLED()
  - 常规转换：执行动作，返回 Q_TRAN()
  - 监护条件：根据事件参数的值和 / 或和状态机联合的变量（扩展状态变量）来`动态的评估`。条件为 false 相当于没处理，需要抛给超状态处理

### 常见问题

- 不完整的状态处理函数

  ```c
  QState Calc_on(Calc *me, QEvent const *e)
  {
      switch (e->sig)
      {
          ...case C_SIG:
          {
              // case里应该return一个预定义的QState值，如Q_HANDLED()，
              // 这里却是一个自定义函数，虽然结果相同，但代码不直观，违反了设计规范
              return Calc_onClear(me); /* handle the Clear event */
          }
          ...
      }
      return Q_SUPER(&QHsm_top);
  }
  ...QState Calc_onClear(Calc *me)
  {
      BSP_clear();
      return Q_TRAN(&Calc_on); /* transition to "on" */
  }
  ```

- 在进入 / 退出动作或初始转换内访问事件参数

  处理 Q_ENTRY_SIG 信号时不应该访问 QEvent 参数，需要在切换时传递的参数可以定义为该状态机的全局变量（如上面的`m_operand1`），这样状态机里所有状态都能共享

- 不够优化的信号粒度

  计算器状态图把数字 1 到 9 的群表示为一个 信号 `IDC_1_9_SIG`，而不是每个数字一个信号，这样增加了一步读取事件参数获得实际值的操作，但减少了信号数量，总体上增大了信号粒度，避免过细的信号粒度带来的复杂性

  过大的信号粒度会导致一个 case 里写的条件判断过多（switch 套 switch），让代码变成意大利面条

## 实时框架的概念

### CPU 管理

传统的事件驱动型架构对实时框架不是非常适合。最起码在三个方面存在问题：

1. **响应性**：单一事件队列不允许对工作的任何合理的`优先次序`。每个事件，无论优先级，必
   须等待直到它前面的全部事件被处理完后才能被处理。
2. **不支持对应用程序上下文的管理**：流行的`事件 - 动作范型`在响应事件时忽略应用程序的
   上下文，这样应用程序员就即兴发挥，到最后搞出“面条”代码。不幸的是，事件 - 动作
   范型和状态机不兼容。
3. **全局数据**：在传统的事件架构里，全部的事件处理函数存取一样的全局数据。这阻碍了对问
   题的`分区`，并为任何形式的多任务带来了`并发性`危机。

### 活动对象计算模式

![room](/assets/img/2022-07-27-quantum-platform-1/room.jpg)

**活动对象** = （控制的线程 + 事件队列 + 状态机）

应用程序包含了多个`活动对象`，每个都封装了一个`控制线程（事件循环）`，一个私有的`事件队列`和一个`状态机`。

- `控制线程（事件循环）`: 图(a)中为一个环形标记（方框右下角），具体见图(b)，事件循环调用和这个活动对象联合的 dispatch()函数。 dispatch()函数执行调度和处理事件的工作， 类似于在传统事件驱动型架构的事件处理函数。
- `事件队列`：(a)中的 event queue
- `状态机`：(a)中的 internal state machine

#### 系统结构

![kernelosapp](/assets/img/2022-07-27-quantum-platform-1/kernelosapp.jpg)

`RTOS` 层在底部提供多任务和基本服务，比如`消息队列`，为存储事件确定内存分区等等。基于这些服务， `QF` 实时框架提供 `QActive` 类用于活动对象的`派生`。 `QActive` 类是从 QHsm 基础类派生而来，这意味着活动对象是状态机，并且继承了在 QHsm 基础类（见第四章）定义的`dispatch()`操作。另外， `QActive` 包含了一个`执行线程`和一个`事件队列`，它基于底层 RTOS 上的消息队列。应用程序通过从 QActive 基础类派生`活动对象`以及从 QEvent 类派生带有参数的`事件`，从而扩展了实时框架。

#### 异步通讯

活动对象专门的通过它们的`事件队列`接收事件。所以事件都被`异步`投递，意味着一个事件生产者仅发送一个事件给接收者活动对象的事件队列，但是`不会原地等待`这个事件的实际处理过程。

活动对象之间也可以通过这种方式传递事件，而不只局限于内部。

#### 运行 - 到 - 完成 RTC

每一个活动对象用运行到完成（ run-to-completion）方式来处理事件，它是通过活动对象的事件循环的结构来保证的。

#### 封装

封装意味着活动对象`不共享数据`和任何其他资源。

数据通过`消息`机制传递

### 事件派发机制

两类事件派发机制:

- `简单的事件直接发送机制`：一个事件的生产者直接发送这个事件到消费者活动对象的`事件队列`。
- `订阅派发机制`，这里一个生产者“发行”一个事件给框架，框架然后把这个事件派发给所有已经“`订阅`”了这个事件的活动对象。发行-订阅机制提供了在事件产生者和消费者之间较低的耦合。

#### 直接事件发送

例如，QF 实时框架提供了操作 QActive_postFIFO()

这个事件传递的方式需要事件产生者密切的“`知道`”接收者。这种知识，散布在参与应用程序的组件中，使组件之间的`耦合`非常强烈和在运行时不灵活。

#### 订阅派发机制

- 事件的产生者和消费者不需要互相了解对方（`松耦合`）。
- 通过这个机制的事件交换必须被公开的了解，全部参与者必须有`相同的语义`。
- 需要一个`介质`去接收所发行的事件，再把它们派发给感兴趣的订阅者。
- `多对多`交互作用（对象-到-对象）被`一对多`交互作用（对象-到-介质）所取代

### 事件内存管理

事件频繁产生消耗，内存重用很重要

#### 零复制的事件派发

`复制`整个事件到消息队列的蛮力方法是一个传统的 RTOS 能做的最好方法，因为一个 RTOS 在事件离开队列后`不能够控制`它们。另一方面，一个`实时框架`可以更加有效，因为由于控制的倒置，框架实际在管理一个事件的全部`生命周期`。

![eventgc](/assets/img/2022-07-27-quantum-platform-1/eventgc.jpg)

![eventgc2](/assets/img/2022-07-27-quantum-platform-1/eventgc2.jpg)

一个事件的生命周期开始于框架分配`事件内存`并返回一个指向这个内存的`指针`给事件生产者，如图(1)，生产者然后`填充`事件`参数`，执行写入所提供的事件指针。然后，事件生产者发送这个事件`指针`给接收者活动对象的`队列`，如图(2)

稍后，活动对象开始`处理`事件。活动对象读取通过指针从队列里`提取`的事件数据。最后，框架在垃圾收集步骤自动的`回收`事件。请注意**事件从来没有被复制**。同时框架确信事件没有被过早回收。当然，框架必须也保证用一个`线程安全`的方式执行全部操作。

#### 静态和动态的事件

- **静态事件**：没有参数或参数不会变的事件，可以静态分配，永远不变，如上图(3)
- **动态事件**：参数会变的事件，需要事件池动态分配

#### 多路传输事件和引用计数器算法

使用订阅分发机制时也可以使用`零复制`派发事件指针。但该指针被`多个`活动对象使用，问题是如何知道`最后一个`活动对象完成了对这个给定事件的处理，这样它占用的空间可以被`回收`。

一个简便的方法是使用标准的`引用计数器算法`，每个动态事件有个计数器，开始为 0，每次发生事件加 1，每次被回收时减 1，到 0 删除事件内存

#### 事件的所有权

![eventowner](/assets/img/2022-07-27-quantum-platform-1/eventowner.jpg)

`生产者`仅能通过调用 `new_()` 操作来获得一个新事件的所有权。但是最后生产者必须把所有权`转让`给框架，如生产者发送或发行事件，主动要求删除不完整事件

`消费者`活动对象在`框架`调用 `dispatch(e)` 操作时获得当前事件 e 的所有权(只读)。当 dispatch()操作返回到框架时，所有权被终止。

#### 内存池

`堆`一般有碎片化、泄露、悬空指针、难以预测、无法重入、空间浪费（管理信息）等问题

内存池会有一定优势，QF 实时框架，可以管理多达 3 个拥有不同块尺寸（`小，中，大`）的事件池。

#### 时间管理

![timeevt](/assets/img/2022-07-27-quantum-platform-1/timeevt.jpg)

当活动对象需要安排一个超时服务，它准备它的某个`时间事件`以便在未来的某时刻发送给自己。

时间事件为这个目的提供的公共操作：为`一次性`超时提供`postIn()`，为`周期性`超时提供 `postEvery()` 。

应用程序可以明确的使用 `disarm()` 操作在任何时刻`解除` (disarm) 任何（周期性的或一次性的）时间事件，之后该事件空间可以`重用`。

可以通过 `rearm()` 操作`重新设定` (rearmed)，如刷新看门狗

#### 系统时钟节拍

系统时钟节拍典型地是一个以预先确定的速率发生的`周期性中断`，典型的速率在 10 和 100Hz 之间。

下图用某种夸张的方式展示了在一个节拍间隔内一个周期性时间事件的不同的延迟：

![systemtick](/assets/img/2022-07-27-quantum-platform-1/systemtick.jpg)

`高优先级`的任务能更`及时`获得节拍，且跳动(jitter)较少。

一个仅为了一个节拍而准备的时间事件会立刻过期，比如上图第 3 个节拍处理时已经在第 4 个节拍之后了，因为还在处理第 3 个节拍对应的的事件动作，可能会导致第 4 个节拍事件`没有产生`(类似中断丢失)，导致第 4 个节拍对应的动作无法执行。解决方法是事件要对应两个节拍，也就是原来指定第 4 个节拍发生的动作应该指定为 4 和 5 都能发生。

### 错误和例外的处理

契约式设计 Design by Contract, DbC 方法
: 通过`断言assertion`来保证程序正常，它们既`不预防`错误也实际上`不处理`错误
: 更适合小型系统，正常状态不应该有错误，有错误就复位，不允许跑飞的程序继续运行

防御式编程
: 通过接收`更宽范围`的输入或允许操作的次序不必定符合对象的状态，让操作对错误更加`强壮`。
: 适合大型系统，尽可能规避错误，即使有错误也要尝试处理和恢复，不能退出进程或重启。因为大型系统运行有很高的不确定性，比如用户的输入无法预测。

QF 框架规定了一些`断言宏`来处理错误

### 基于框架的软件追踪

简单的讲，软件追踪类似于在代码里安排一些 printf()语句，它被称为`检测代码`，记录并分析以后从目标系统取回来的所感兴趣的分立事件。当然，一个好的软件追踪检测设备可以做到比简单的 printf()更少的侵入并更有效。

从框架自身得到的软件追踪数据，允许你为全部系统里的活动对象生成完整的，带有时间戳的顺序图和详细的状态机活动图。

使用 QS 构件(Q-Spy)实现

## 实时框架的实现

QF 框架的代码实现详解，对上一章的补充

### QF 实时框架的关键特征

- 可移植性

  所以 QF 源代码使用可移植的 ANSI-C ，或者[`嵌入式 C++子集`](http://www.caravan.net/ec2plus/)（wiki 上说这个项目从 2002 年开始就停止了，而且 C++之父也不看好）编写，所有处理器相关的，编译器相关的，或操作系统相关的代码被抽象成一个清楚定义的平台抽象层 PAL（ platform abstraction layer）。

- 可伸缩性

  QF 被设计用于一个`细粒度`的对象库的部署，你可以静态的把它链接到你的应用程序。这个策略把责任交给链接器，让它在链接时自动排除任何没用到的代码，应用程序员不需为每个应用程序在编译时刻去配置 QF 代码。

- 对现代状态机的支持

  QF 实时框架被设计为和 QEP 层次式事件处理紧密的工作，QEP 提供了 UML 兼容的直接实现，而 QF 提了并发执行这类状态机的基础设施。

- 直接事件发送和发布 - 订阅式事件派发

  QF 实时框架支持使用 FIFO 和 LIFO 策略对特点活动对象进行直接事件发送。QF 也支持更加先进的发行 - 订阅事件派发机制。

- 零复制的事件内存管理

  QF 支持 事件的基于引用计数算法的多路发送，对事件的`自动垃圾收集`，`高效`的静态事件，“`零复制`”事件延迟， 和可多多达 3 个为了最佳内存使用而拥有`不同块尺寸`的`事件池`。

- 开放式序号的时间事件

  每个时间事件可以被作为一个一次性或周期性超时发生器而被激活。只有被激活（ active ） 的时间事件才消耗 CPU 周期。

- 原生的事件队列

  QF 提供原生事件队列的 2 个版本。

  第一个版本是为活动对象优化的，包含一个可移植的可以为`阻塞型内核`、`简单的合作式 vanilla 内核`或 `QK 可抢占型内核`而做修改的层。

  第二个版本是一个简单的“线程安全的”队列，它不能阻塞，被设计为给中断发送事件和存储延迟的事件。

- 原生的内存池

  QF 提供了一个快的，可确定的，和线程安全的内场池。 QF 在内部把内存池作为管理动态事件的事件池，但是你也可以为了在你系统中分配任何其他对象而使用内存池。

- 内置 Vanilla 调度器

  QF 实时框架包含了一个可移植的，合作式 vanilla 内核

- 和 QK 可抢占式内核的紧密集成

  QF 实时框架也可以和可确定的，可抢占的，非阻塞 QK 内核工作。

- 低功耗构架

  绝大多数嵌入式微处理器 MCU 提供了一个低功耗睡眠模式的选择，用来通过调节给 CPU 和其他外设的时钟来节省能量。睡眠模式通过软件控制进入，在某个外部中断时退出。

- 基于断言的错误处理

  契约式设计（ DbC）哲学

- 内置软件追踪测试设备

  一个实时框架可以使用软件追踪技术提供比任何传统的 RTOS 更广泛和更详细的，关于运行中应用系统的信息。关闭 Q_SPY 宏时不产生空间和性能开销

### QF 的结构

![qf](/assets/img/2022-07-27-quantum-platform-1/qf.jpg)

QF 提供了核心基本类 `QActive` ，用于活动对象类的派生。 `QActive` 类是`抽象`的，意味着它不是打算用于被直接实例化，而是为了派生具体的活动对象类，比如图内的`Ship`，`Missile`和 `Tunnel` 。

QActive 类默认是从在 `QEP`事件处理器的 `QHsm` 层次式状态机类`派生`。这意味着，凭借着继承，`活动对象`是 HSM，并继承了 init() 和 dispatch() 状态机接口。 QActive 也包含了一个`执行线程`和一个`事件队列`，它可以是原生的 QF 类，或者由底层 RTOS 提供。

和`QEP`事件处理器一样， QF 使用同样的 `QEvent` 类来表示事件。另外，框架提供了时间事件类 `QTimeEvt`，应用程序使用它来产生超时请求。

QF 也提供了几个服务给应用程序，它们没有在图的类图展示出来。这些额外的 QF 服务包括`生成新的动态事件` (Q_NEW()) ，`发行事件`（ QF_publish()），`原生 QF 事件队列类` (QEQueue) ，`原生 QF 内存池类`（ QMPool ），和内建的`合作式 vanilla 内核`

#### QF 源代码的组织

QF 源代码文件典型地每个文件`只包含`一个函数或一个数据结构的定义。这个设计是为了把 QF 当作一个`细粒度`的库来部署，你可以静态的把它和你的应用程序链接。

这个策略把负担交给`链接器`，让它去在链接时排除任何没用的代码，而不是让程序员为每个应用程序在编译时配置 QF 代码。

TODO:新版本还是这样的吗，感觉整合了不少

### QF 里的临界区

QF 和其他任何系统层软件一样，必须保护某些指令的顺序不被破坏从而担保线程安全的操作。这个必须被`不可分割`地执行的代码区被称为`临界区`。

`嵌入式`系统可以在进入临界区时`关中断`，在从临界区退出时`解锁中断`。

在不允许锁中断的系统里， QF 可以采用其他的由底层`操作系统`支持的机制，比如`互斥体`（ mutex ）

QF 平台抽象层包含 了 2 个宏 QF_INT_LOCK()和 QF_INT_UNLOCK() ，分别用来`进入临界区`和`退出临界区`。

#### 保存和恢复中断状态

一种临界区实现方式：

```c
{
  unsigned int lock_key;
  . . .
  // 关中断前保存当前中断状态，用于后面恢复
  lock_key = get_int_status();
  // 关闭中断，功能由编译器提供
  int_lock();
  . . .
  /* critical section of code */
  . . .
  // 恢复中断状态，相当于开中断
  set_int_status(lock_key);
  . . .
}
```

用于实现这个功能的宏定义：

```c
// 这个宏用于在预编译时告诉QF框架是否使用“保存和恢复中断状态”策略(该宏定义)，
// 还是下一节的“无条件锁住和解锁中断”策略(该宏不定义)
#define QF_INT_KEY_TYPE unsigned int
#define QF_INT_LOCK(key_)          \
    do                             \
    {                              \
        (key_) = get_int_status(); \
        int_lock();                \
    } while (0)
#define QF_INT_UNLOCK(key_) set_int_status(key_)
```

> QF_INT_LOCK()宏的 do {…} while (0) 循环是语法正确的用来`组合指令`的`标准做法`。你确信这个宏可以被安全的用于 `if-else` 语句（在宏后加分号），而不会造成[“悬吊 if”（ dangling-if ）](https://en.wikipedia.org/wiki/Dangling_else)问题。
{: .prompt-tip }

“保存和恢复中断状态”政策的主要优点是可以`嵌套临界区`的能力。当 QF 函数从一个已经建立的临界段比如 ISR 里调用时，且`部分处理器`在进入 ISR 后自动关中断(进临界区)，需要在 ISR 内部先解锁中断才能使用 QF 函数(详见下节例子)，如果做不到就需要使用上述的办法`嵌套临界区`。

> 为什么要解锁中断才能调用 QF 函数，见下一节

#### 无条件上锁和解锁中断

```c
/* QF_INT_LOCK_KEY not defined */
#define QF_INT_LOCK(key_) int_lock()
#define QF_INT_UNLOCK(key_) int_unlock()
```

“无条件上锁和解锁”策略是简单和快捷的，但是`不允许`临界区的`嵌套`，理由见上节

使用一个`基于优先级`的中断控制器时一个 ISR 的常规结构：

```c
// 这是个ISR中断处理程序
// 绝大多数控制器在进入 ISR 时，中断被硬件上锁。中断控制器被关闭，所有中断被关闭，不论优先级
// 不能嵌套临界区并不意味着你不能嵌套中断。许多处理器拥有基于优先级的中断控制器
void interrupt ISR(void) { /* entered with interrupts locked in hardware */
    // 中断控制器必须被通知要进入这个中断。这个通知常在定向（跳转）到 ISR 之前自动在硬件层发生。
    Acknowledge the interrupt to the interrupt controller (optional)
    // 如果中断源是电平触发的，你需要明确的清除它，以便触发下一次该中断。
    // 因为这里同优先级的中断也被关闭了，本来就不能触发，所以之后清除也没关系
    Clear the interrupt source, if level triggered
    // 如果之前被关中断了就执行开中断，使能中断控制器，这样高优先级的中断可以执行，
    // 更低或相同优先级的中断依旧不能执行。此时临界区结束
    QF_INT_UNLOCK(dummy); /* unlock the interrupts at the processor level */
    // 主 ISR 代码在临界区外执行，因此 QF 可以被安全的调用而不需嵌套临界区。
    Handle the interrupt, use QF calls, e.g., QF_tick(), Q_NEW or QF_publish()
    // 中断被锁住，为中断的离开建立临界区。
    QF_INT_LOCK(dummy); /* lock the interrupts at the processor level */
    // EOI (end of interrupt) 指令被发往中断控制器，停止这个中断的优先权
    Write End-Of-Interrupt (EOI) instruction to the Interrupt Controller
    // 由编译器提供的中断退出步骤，从堆栈恢复 CPU寄存器，包括 CPU状态寄存器。典型地这个步骤会解锁中断。
}
```

> `基于优先级`的中断控制器`记忆`当前所服务的中断的优先级，并仅允许比当前优先级高的中断抢占这个 ISR 。`较低`的或`相同`优先级的中断在中断控制器层次被`锁住`，`即使`这些中断在处理器层次`被解锁`。中断优先排序发生在中断控制器硬件层，直到中断控制器接受到中断结束 EOI 指令为止。

> TODO: 开中断是为了什么？是不是为了防止执行主 ISR 代码(QF 函数)的过程太长导致临界区时间太长。还是为了主 ISR 代码执行时需要用到某些中断
>
> 解答：QF 函数执行部分`内部`有些也使用的`关开中断`创建临界区的部分，为了防止`中断嵌套`，也就是`外面`关了中断，进了函数`内部`又关一次就会造成阻塞，也就是`死锁`。

#### 中断上锁/解锁的内部 QF 宏

QF 平台抽象层 (platform abstraction layer)PAL 使用中断上锁/解锁宏`QF_INT_LOCK()`， `QF_INT_UNLOCK()` ，和 `QF_INT_KEY_TYPE` 。

中断上锁 / 解锁的内部宏:

```c
#ifndef QF_INT_KEY_TYPE /* simple unconditional interrupt locking/unlocking */
    #define QF_INT_LOCK_KEY_
    #define QF_INT_LOCK_() QF_INT_LOCK(ignore)
    #define QF_INT_UNLOCK_() QF_INT_UNLOCK(ignore)
#else /* policy of saving and restoring interrupt status */
    #define QF_INT_LOCK_KEY_ QF_INT_KEY_TYPE intLockKey_;
    #define QF_INT_LOCK_() QF_INT_LOCK(intLockKey_)
    #define QF_INT_UNLOCK_() QF_INT_UNLOCK(intLockKey_)
#endif
```

末尾带下划线的宏保持使用两种不同策略时的`一致性`（自动选择）

示例：

```c
void QF_service_xyz(arguments)
{
    QF_INT_LOCK_KEY_
    ...
    QF_INT_LOCK_();
    ...
    /* critical section of code */
    ...
    QF_INT_UNLOCK_();
}
```

### 主动对象

QF 实时框架提供了基础结构 QActive 用于派生应用程序的特定好的对象。 QActive 结合了后面三个基本要素：

1. 它是一个`状态机`（从 QHsm 或其他拥有兼容接口的类派生）
2. 它是一个`事件队列`
3. 它有一个带有唯一优先级的`执行线程`

```c
// 可以自定义基础类，只要实现了状态机接口，也就是可以不用QEP框架里的QHsm
#ifndef QF_ACTIVE_SUPER_
    // 基础类默认为QEP提供的QHsm类
    #define QF_ACTIVE_SUPER_ QHsm
    // 基础类构造函数名字
    #define QF_ACTIVE_CTOR_(me_, initial_) QHsm_ctor((me_), (initial_))
    // 基础类init初始化函数的名字
    #define QF_ACTIVE_INIT_(me_, e_) QHsm_init((me_), (e_))
    // 基础类dispatch()函数的名字
    #define QF_ACTIVE_DISPATCH_(me_, e_) QHsm_dispatch((me_), (e_))
    // 基础类构造函数的参数的类型
    #define QF_ACTIVE_STATE_ QState
#endif
typedef struct QActiveTag
{
    /// QActive 的基础类(继承)
    QF_ACTIVE_SUPER_ super; /* derives from QF_ACTIVE_SUPER_ */
    // 事件队列，可自定义
    QF_EQUEUE_TYPE eQueue;  /* event queue of active object */
    // TODO:这个osObject在 #[POSIX的 QF 移植] 中会提到
#ifdef QF_OS_OBJECT_TYPE
    QF_OS_OBJECT_TYPE osObject; /* OS-object for blocking the queue */
#endif
    // 线程处理
#ifdef QF_THREAD_TYPE
    QF_THREAD_TYPE thread; /* execution thread of the active object */
#endif
    // 每个主动对象有唯一的优先级，最大为63，0是特殊的休眠优先级，也就是最大支持63个主动对象
    uint8_t prio;    /* QF priority of the active object */
    // 用于一些移植，写入0会终止活动对象
    uint8_t running; /* flag indicating if the AO is running */
} QActive;

// 开始执行
void QActive_start(QActive *me, uint8_t prio,
                   QEvent const *qSto[], uint32_t qLen,
                   void *stkSto, uint32_t stkSize,
                   QEvent const *ie);
// FIFO方式发送到活动对象的事件队列
void QActive_postFIFO(QActive *me, QEvent const *e);
// LIFO方式发送到活动对象的事件队列
void QActive_postLIFO(QActive *me, QEvent const *e);
// 构造函数
void QActive_ctor(QActive *me, QState initial);
// 停止活动对象执行线程
void QActive_stop(QActive *me);
// 和事件订阅相关
void QActive_subscribe(QActive const *me, QSignal sig);
void QActive_unsubscribe(QActive const *me, QSignal sig);
void QActive_unsubscribeAll(QActive const *me);
// 用于高效的（“零复制”）事件延迟和事件恢复
void QActive_defer(QActive *me, QEQueue *eq, QEvent const *e);
QEvent const *QActive_recall(QActive *me, QEQueue *eq);
// 从活动对象的事件队列每次移除一个事件,这个函数仅被用在 QF 内部，并且从不用于应用程序层
QEvent const *QActive_get_(QActive *me);
```

通过把宏 `QF_ACTIVE_XXX_` 定义到你`自己的类`，你可以排除在 `QF` 框架和 `QEP` 事件处理器之间的`依赖性`。

自定义示例：

```c
#define QF_ACTIVE_SUPER_ MyClass
#define QF_ACTIVE_CTOR_(me_, ini_) MyClass_ctor((me_), (ini_))
#define QF_ACTIVE_INIT_(me_, e_) MyClass_init((me_), (e_))
#define QF_ACTIVE_DISPATCH_(me_, e_) MyClass_dispatch((me_), (e_))
#define QF_ACTIVE_STATE_ void*
```

#### 活动对象的内部状态机

每个`活动对象`都是一个`状态机`，如飞行和射击”游戏例子里的 Ship，Missile，或 Tunnel

活动对象由 QHsm 派生，利用`多态`特性可以使用`QHsm指针`使用派生活动对象的`状态机函数`(QEP 层)，所以无论活动对象添加了多少自定义的变量，都可以当作状态机使用。

#### 活动对象的事件队列

QF 的事件队列需要“`多写单读`”的存取权限，可以从其他地方(不同线程)发送事件到活动对象，活动对象线程每次取一个使用。所以需要`读写互斥锁`和`写者互斥锁`

"`零复制`"事件队列不存储实际事件，仅存储执行`事件实例`的`指针`。

可以使用操作系统提供的消息队列，尽管有点大材小用

#### 执行线程和活动对象优先级

活动对象线程的步骤：

```c
// 从事件队列获取事件，没事件时可以阻塞让线程休眠。
QEvent const *e = QActive_get_(a);  /* get the next event for AO 'a' */
// 利用多态使用基类函数和基类指针作为参数执行派生后的函数实现
QF_ACTIVE_DISPATCH_(&a->super, e)   /* dispatch to the AO 'a' */
// QF垃圾回收器回收无用的事件
QF_gc(e);   /* determine if event 'e' is garbage and collect it if so */
```

QF 应用程序需要`代表`系统里的每个活动对象调用`QActive_start()`函数(启动活动对象)

```c
void QActive_start(QActive *me,
                   uint8_t prio,                        /* 唯一优先级，the unique priority */
                   QEvent const *qSto[], uint32_t qLen, /* 事件队列空间，event queue */
                   void *stkSto, uint32_t stkSize,      /* 栈空间，per-task stack */
                   QEvent const *ie)                    /* 初始事件，the initialization event */
{
    me->prio = prio;         /* set the QF priority */
    // 注册到QF
    QF_add(me);              /* make QF aware of this active object */
    // 执行在活动对象里的状态机的最顶初始转换,需要配合ie提供的信息
    QF_ACTIVE_INIT_(me, ie); /* execute the initial transition */
    // 初始化事件队列
    Initialize the event queue object 'me->eQueue' using qSto and qLen
    // 创建活动对象线程
    Create and start the thread 'me->thread' of the underlying kernel
}
```

> “`初始事件`” ie 让你有机会提供一些信息给活动对象，这个活动对象(这里原文用的`which`，是指代上一句的`一些信息`还是`活动对象`？)在后面的初始化过程才被知道（比如，在 GUI 系统里的一个窗口处理句柄）。请注意，（在 C++里）活动对象的构造函数在 main() 之前运行，这时你没有所有的信息来初始化一个活动对象的全部方面。

### QF 的事件管理

“零复制”事件派发方案

1. 被框架管理的`动态`事件
2. 其他不被 QF 管理的（`静态`分配的）事件

#### 事件的结构

```c
typedef struct QEventTag { /* QEvent base structure */
    QSignal sig; /* public signal of the event instance */
    // 动态还是静态事件
    uint8_t dynamic_; /* attributes of a dynamic event (0 for static event) */
} QEvent;
```

![qeventdyn](/assets/img/2022-07-27-quantum-platform-1/qeventdyn.jpg)

7,6 表示事件池 id(大、中、小、静态 0)，5-0 表示事件引用计数器，引用计数器归 0 才回收

#### 动态事件分配

大中小三个事件池，事件用完空间可回收

```c
/* Package-scope objects ---------------------------------------------------*/
// 事件池管理信息，不包含实际空间
QF_EPOOL_TYPE_ QF_pool_[3]; /* allocate 3 event pools */
// 实际使用的池的数量
uint8_t QF_maxPool_;        /* number of initialized event pools */
/*..........................................................................*/
// poolSto参数才是分配的实际事件空间
void QF_poolInit(void *poolSto, uint32_t poolSize, QEventSize evtSize)
{
    /* cannot exceed the number of available memory pools */
    // 合法性检查
    Q_REQUIRE(QF_maxPool_ < (uint8_t)Q_DIM(QF_pool_));
    /* please initialize event pools in ascending order of evtSize: */
    Q_REQUIRE((QF_maxPool_ == (uint8_t)0) ||
                (QF_EPOOL_EVENT_SIZE_(QF_pool_[QF_maxPool_ - 1]) < evtSize));
    /* perfom the platform-dependent initialization of the pool */
    // 所有框架操作需要的内存由应用程序提供给框架。这里实际分配空间为poolSto指向的内存
    // 这个宏默认提供QMPool_init（就是QF原生内存池）的分配功能
    QF_EPOOL_INIT_(QF_pool_[QF_maxPool_], poolSto, poolSize, evtSize);
    // 变量 QF_maxPool_ 被增加，表示多个池已被初始化
    ++QF_maxPool_; /* one more pool */
}
```

> 所有 QP 构件，包括 QF 框架，一致地假设，在`系统开始`时，没有明确初始值的变量被`初始化为 0` ，这是 ANSI-C 标准的要求。在嵌入式系统，这个初始化步骤对应于`清除.BSS段`(用来放`全局变量`)。你应该确信在你的系统里，在 main() 被调用前 .BSS 段确实被清除了。

_从最小事件尺寸池分配一个事件的简单策略_:

```c
QEvent *QF_new_(QEventSize evtSize, QSignal sig)
{
    QEvent *e;
    /* find the pool id that fits the requested event size ... */
    uint8_t idx = (uint8_t)0;
    // 从小到大找到合适的池
    while (evtSize > QF_EPOOL_EVENT_SIZE_(QF_pool_[idx]))
    {
        ++idx;
        Q_ASSERT(idx < QF_maxPool_); /* cannot run out of registered pools */
    }
    // 从池中获取e（分配空间）
    QF_EPOOL_GET_(QF_pool_[idx], e); /* get e -- platform-dependent */
    // 断言池未枯竭
    Q_ASSERT(e != (QEvent *)0);      /* pool must not run out of events */
    // 设置信号
    e->sig = sig;                    /* set signal for this event */
    /* store the dynamic attributes of the event:
     * the pool ID and the reference counter == 0
     */
    // 设置池标记(高两位)
    e->dynamic_ = (uint8_t)((idx + 1) << 6);
    return e;
}
```

#### 自动垃圾收集

动态事件的引用计数器被存储在事件属性 dynamic\_的`低 6 位` LSB 里，发送事件时递增，`归 0` 由 QF 自动检测`回收`

```c
void QF_gc(QEvent const *e)
{
    // 判断是否动态事件
    if (e->dynamic_ != (uint8_t)0)
    { /* is it a dynamic event? */
        QF_INT_LOCK_KEY_
        // 中断上锁,操作引用计数器需要临界区
        QF_INT_LOCK_();
        if ((e->dynamic_ & 0x3F) > 1)
        {                              /* isn't this the last reference? */
            // 大于1，递减
            --((QEvent *)e)->dynamic_; /* decrement the reference counter */
            QF_INT_UNLOCK_();
        }
        else
        { /* this is the last reference to this event, recycle it */
            // 小于1，回收，先从高2位获取index索引，找到对应池，然后归还空间
            uint8_t idx = (uint8_t)((e->dynamic_ >> 6) - 1);
            QF_INT_UNLOCK_();
            Q_ASSERT(idx < QF_maxPool_); /* index must be in range */
            QF_EPOOL_PUT_(QF_pool_[idx], (QEvent *)e);
        }
    }
}
```

#### 延迟和恢复事件

QF 分别通过 QActive 的类函数 QActive_defer() 和 QActive_recall() 实现明确的事件延迟和恢复。见[延迟的事件](#延迟的事件)

当事件在某个特别`不方便的时刻`到达时，可以被`延迟`一些时间直到系统有一个比较好的状态去处理这个事件，事件的延迟是很方便的

```c
void QActive_defer(QActive *me, QEQueue *eq, QEvent const *e)
{
    (void)me;                /* avoid compiler warning about 'me' not used */
    // 发送给等待队列，这里计数器会被加1，防止被回收
    // 因为事件被处理后即使不执行操作放入等待队列，计数器也会被减1
    QEQueue_postFIFO(eq, e); /* increments ref-count of a dynamic event */
}
/*..........................................................................*/
QEvent const *QActive_recall(QActive *me, QEQueue *eq)
{
    // 从等待队列取一个事件
    QEvent const *e = QEQueue_get(eq); /* get an event from deferred queue */
    if (e != (QEvent *)0)
    { /* event available? */
        QF_INT_LOCK_KEY_
        // 发送到事件队列，用LIFO插队到第一个，引用计数器会被加1
        QActive_postLIFO(me, e); /* post it to the front of the AO's queue */
        QF_INT_LOCK_();
        if (e->dynamic_ != (uint8_t)0)
        { /* is it a dynamic event? */
            Q_ASSERT((e->dynamic_ & 0x3F) > 1);
            // 从等待队列里拿出来了，引用计数器要减1(事件队列里的处理后会自动减)
            --((QEvent *)e)->dynamic_; /* decrement the reference counter */
        }
        QF_INT_UNLOCK_();
    }
    return e; /*pass the recalled event to the caller (NULL if not recalled) */
}
```

### QF 的事件派发机制

QF 仅支持异步事件交换，发送者不等待事件处理

派发机制：

- **直接事件发送的简单机制** -- 一个事件的生产者直接发送这个事件给消费者活动对象的事件队列。
- **订阅事件发送机制** -- 事件的生产者把事件发行给框架，框架然后把事件发行给所有订阅了这个事件的活动对象。

#### 直接事件发送

QF 通过 `QActive_postFIFO()` 和 `QActive_postLIFO()` 函数支持直接事件发送

```c
QActive_postFIFO(AO_ship, (QEvent *)e); /* post event 'e' to the Ship AO */
```

这里参数 `AO_ship` 是 `QActive` 基类类型，利用了多态

```c
extern QActive * const AO_Ship; /* opaque pointer to the Ship AO */
```

#### 发行-订阅事件发送

- 初始化`发行-订阅`机制: QF_psInit()
- 订阅：QActive_subscribe(), QActive_unsubscribe(), QActive_unsubscribeAll()
- 发行：QF_publish()

_管理订阅信息的数据结构_：

```c
typedef struct QSubscrListTag {
    // QF_MAX_ACTIVE - 1表示需要的位数
    // 除以8向上取整，表示需要的字节数
    uint8_t bits[((QF_MAX_ACTIVE - 1) / 8) + 1];
} QSubscrList;
```

![subscriberbitmap](/assets/img/2022-07-27-quantum-platform-1/subscriberbitmap.jpg)

每类信号为一行，每行中的每一位对应一个主动对象，因为优先级和主动对象一一对应，所以通过优先级(1-63)对应位唯一标识，置位表示该事件被对应的主动对象订阅。如图中 bit15 对应优先级 16 的主动对象。

上图例子中每行 bit 为 64 个(目前 QF_MAX_ACTIVE 的范围是 1 到 63)，这也是[主动对象](#主动对象)提到的优先级上限为 63 的原因

- 初始化

  ```c
  QSubscrList *QF_subscrList_; /* initialized to zero per C-standard */
  QSignal QF_maxSignal_;
  /* initialized to zero per C-standard */
  void QF_psInit(QSubscrList *subscrSto, QSignal maxSignal)
  {
      QF_subscrList_ = subscrSto;
      QF_maxSignal_ = maxSignal;
  }
  ```

- 订阅

  ```c
  // me: 本对象，sig：要订阅的信号
  void QActive_subscribe(QActive const *me, QSignal sig)
  {

      uint8_t p = me->prio;
      // 字节索引，QF_div8Lkup[p] = (p – 1)/8，
      // 可以每次算也可以用预生成在ROM的查找表
      uint8_t i = Q_ROM_BYTE(QF_div8Lkup[p]);
      QF_INT_LOCK_KEY_
      Q_REQUIRE(((QSignal)Q_USER_SIG <= sig) && (sig < QF_maxSignal_)
                  && ((uint8_t)0 < p)
                  && (p <= (uint8_t)QF_MAX_ACTIVE)
                  && (QF_active_[p] == me));
      QF_INT_LOCK_();
      // 找到字节内偏移，QF_pwr2Lkup[p] = 1 << ((p – 1) % 8)，
      // 可以每次算也可以用预生成在ROM的查找表
      QF_subscrList_[sig].bits[i] |= Q_ROM_BYTE(QF_pwr2Lkup[p]);
      QF_INT_UNLOCK_();
  }
  ```

- 发行

  ```c
  // 给所有订阅者发行一个给定事件 e
  void QF_publish(QEvent const *e)
  {
      QF_INT_LOCK_KEY_
      /* make sure that the published signal is within the configured range */
      Q_REQUIRE(e->sig < QF_maxSignal_);
      // 读取加修改，典型的临界区
      QF_INT_LOCK_();
      if (e->dynamic_ != (uint8_t)0)
      { /* is it a dynamic event? */
        // e->dynamic_为0说明是高2位也是0，就是静态事件
          /*lint -e1773 Attempt to cast away const */
          // 增加一次引用计数器，防止刚发送给一个活动对象事件立刻被处理了的情况下，
          // 引用计数器直接归0，事件被回收，无法给其他活动对象发事件
          // QF_publish执行到最后给所有订阅的活动对象发完，应该要减1
          ++((QEvent *)e)->dynamic_; /* increment reference counter, NOTE01 */
      }
      QF_INT_UNLOCK_();
  #if (QF_MAX_ACTIVE <= 8)
      { // 只有一个字节
          // 赋给临时变量，后面能随便修改
          uint8_t tmp = QF_subscrList_[e->sig].bits[0];
          while (tmp != (uint8_t)0)
          { // 不为0表示有订阅
              // 找最高优先级的活动对象，也就是从高到低第一个为1的位，
              // 以 2 为底的对数查找快捷的确定在bitmask的MSB位
              uint8_t p = Q_ROM_BYTE(QF_log2Lkup[tmp]);
              // 清掉该位
              tmp &= Q_ROM_BYTE(QF_invPwr2Lkup[p]);    /* clear subscriber bit */
              Q_ASSERT(QF_active_[p] != (QActive *)0); /* must be registered */
              /* internally asserts if the queue overflows */
              // 向对应活动对象发送
              QActive_postFIFO(QF_active_[p], e);
          }
      }
  #else

      {
          // Q_DIM获取字节数sizeof(array_) / sizeof((array_)[0U]
          uint8_t i = Q_DIM(QF_subscrList_[0].bits);
          do
          { /* go through all bytes in the subscription list */
            // 遍历该事件信号对应的订阅清单里的所有字节
              uint8_t tmp;
              // 从高到低遍历
              --i;
              // 这里开始和上面单字节的一样了
              tmp = QF_subscrList_[e->sig].bits[i];
              while (tmp != (uint8_t)0)
              {
                  uint8_t p = Q_ROM_BYTE(QF_log2Lkup[tmp]);
                  tmp &= Q_ROM_BYTE(QF_invPwr2Lkup[p]);    /*clear subscriber bit */
                  // 这里和上面不一样，要移位一下
                  p = (uint8_t)(p + (i << 3));             /* adjust the priority */
                  Q_ASSERT(QF_active_[p] != (QActive *)0); /*must be registered*/
                  /* internally asserts if the queue overflows */
                  QActive_postFIFO(QF_active_[p], e);
              }
          } while (i != (uint8_t)0);
      }
  #endif
      // 执行一次垃圾回收，将引用计数器减1，这里就是对应开头那里的增加1
      QF_gc(e); /* run the garbage collector, see NOTE01 */
  }
  ```

  > 为什么加锁，见[比较并交换](/posts/operating-systems-22/#比较并交换)

  二进制算法查找表 `QF_log2Lkup[]` 映射`字节值`到 MSB 的 bit`数字` (找一个字节里的`最高有效位`所在的位置 1-8，可以通过表一一对应)：

  ![log2Lkup](/assets/img/2022-07-27-quantum-platform-1/log2Lkup.jpg)

  > 注意：横坐标有部分缩放，是不等距的
  {: .prompt-warning }

  如果不用这个表，`运行时`用$log_2(x)$算也可以，这会造成重复计算开销，嵌入式系统可以使用这种预配置的表，缺点是`占用空间`，比如这个表是 256 个单字节数组，占用 256 Bytes

### 时间管理

时间事件只能是`静态`的

一个时间事件在实例化时（在`构造`函数里）必须被分配一个`信号`，这个信号在后面`不能被改变`。后一个约束防止了时间事件在还被某个事件队列持有时，被意外的改变。

#### 时间事件结构和接口

```c
typedef struct QTimeEvtTag
{
    // 从QEvent派生
    QEvent super;             /* derives from QEvent */
    // 双向链表前后指针
    struct QTimeEvtTag *prev; /* link to the previous time event in the list */
    struct QTimeEvtTag *next; /* link to the next time event in the list */
    // 存储了时间事件的接收者(其他类型的事件好像没有派生这个变量)
    QActive *act;             /* the active object that receives the time event */
    // 每个tick（调用QF_tick()）递减，直到0发送事件
    QTimeEvtCtr ctr;          /* the internal down-counter of the time event */
    // 周期性时间事件的间隔，单次为0
    QTimeEvtCtr interval;     /* the interval for the periodic time event */
} QTimeEvt;
// 构造函数，里面会给事件一个信号，该事件可重用但不应修改它的信号
// 因为改了以后会导致原来接收这个事件的活动对象无法使用该事件
void QTimeEvt_ctor(QTimeEvt *me, QSignal sig);
// 为什么用do{...}while (0)之前提到过了，为了在宏里安全包裹多步操作
// 设置定时器，用于一次性时间事件
#define QTimeEvt_postIn(me_, act_, nTicks_)      \
    do                                           \
    {                                            \
        (me_)->interval = (QTimeEvtCtr)0;        \
        QTimeEvt_arm_((me_), (act_), (nTicks_)); \
    } while (0)
// 设置定时器，周期性时间事件
#define QTimeEvt_postEvery(me_, act_, nTicks_)   \
    do                                           \
    {                                            \
        (me_)->interval = (nTicks_);             \
        QTimeEvt_arm_((me_), (act_), (nTicks_)); \
    } while (0)
// 解除定时器
uint8_t QTimeEvt_disarm(QTimeEvt *me);
// 重设定时器
uint8_t QTimeEvt_rearm(QTimeEvt *me, QTimeEvtCtr nTicks);
/* private helper function */
// 把时间事件插入已设定的定时器的链接表内
void QTimeEvt_arm_(QTimeEvt *me, QActive *act, QTimeEvtCtr nTicks);
```

![timeevtlist](/assets/img/2022-07-27-quantum-platform-1/timeevtlist.jpg)

已被设定的时间事件放于链表中，已解除的不在链表中

#### 系统时钟节拍和 QF_tick() 函数

QF 需要获取节拍管理时间事件，一般就是在 `ISR` 中调用自己的 `QF_tick()`

```c
void QF_tick(void)
{ /* see NOTE01 */
  QTimeEvt *t;
  QF_INT_LOCK_KEY_
  QF_INT_LOCK_();
  // 从链表头开始
  t = QF_timeEvtListHead_; /* start scanning the list from the head */
  while (t != (QTimeEvt *)0)
  {//t = t->next;遍历
    // 每次调用减1
    if (--t->ctr == (QTimeEvtCtr)0)
    { /* is time evt about to expire? */
      // 到达倒计时
      // 判断是否是周期性事件
      if (t->interval != (QTimeEvtCtr)0)
      {                       /* is it periodic timeout? */
        t->ctr = t->interval; /* rearm the time event */
      }
      else // 不是周期性事件
      { /* one-shot timeout, disarm by removing it from the list */
        if (t == QF_timeEvtListHead_)
        {
          // 当前指针是头指针时，头指针直接指向next，即使next是空也没关系
          QF_timeEvtListHead_ = t->next;
        }
        else
        {
          // 把定时器对象节点从链表中删除
          if (t->next != (QTimeEvt *)0)
          { /* not the last event? */
            t->next->prev = t->prev;
          }
          t->prev->next = t->next;
        }
        // 标记该节点为未使用状态
        t->prev = (QTimeEvt *)0; /* mark the event disarmed */
      }
      QF_INT_UNLOCK_(); /* unlock interrupts before calling QF service */
      /* postFIFO() asserts internally that the event was accepted */
      // 发送事件
      QActive_postFIFO(t->act, (QEvent *)t);
    }
    else
    {
      static uint8_t volatile dummy;
      QF_INT_UNLOCK_();
      // 在许多 CPU 里，中断解锁仅在下个机器指令后才生效,
      // 对 dummy 变量的赋值需要几个机器指令，这是编译器没办法优化掉的。这确保中断被实际解锁
      // 防止QF_INT_UNLOCK_和下一个QF_INT_LOCK_挨在一起，CPU要等一段时间才能重新上锁
      dummy = (uint8_t)0; /* execute a few instructions, see NOTE02 */
    }
    // 为了下一次循环上锁
    QF_INT_LOCK_(); /* lock interrupts again to advance the link */
    t = t->next;
  }
  QF_INT_UNLOCK_();
}
```

#### arming 和 disarm 一个时间事件

QTimeEvt*arm*()用于把`时间事件`插入已设定的定时器的`链接`表内

```c
void QTimeEvt_arm_(QTimeEvt *me, QActive *act, QTimeEvtCtr nTicks)
{
  QF_INT_LOCK_KEY_
  Q_REQUIRE((nTicks > (QTimeEvtCtr)0)                       /* cannot arm a timer with 0 ticks */
            && (((QEvent *)me)->sig >= (QSignal)Q_USER_SIG) /*valid signal */
            && (me->prev == (QTimeEvt *)0)                  /* time evt must NOT be used */
            && (act != (QActive *)0));                      /* active object must be provided */
  me->ctr = nTicks;
  // Q_REQUIRE判断了me->prev == (QTimeEvt *)0，表示该节点未使用，
  // 所以这里赋值一下（不是0就行，这里指向了自己），表示该节点对应的计时器已启用
  // 后面会利用这个值判断该节点是否
  me->prev = me; /* mark the timer in use */
  me->act = act;

  // 对链表的操作要加锁
  QF_INT_LOCK_();
  // 放到链表头部
  me->next = QF_timeEvtListHead_;
  if (QF_timeEvtListHead_ != (QTimeEvt *)0)
  {
    QF_timeEvtListHead_->prev = me;
  }
  QF_timeEvtListHead_ = me;
  QF_INT_UNLOCK_();
}
```

QTimeEvt_disarm()用于`关闭`已经设定的`定时器`：

```c
uint8_t QTimeEvt_disarm(QTimeEvt *me)
{
  uint8_t wasArmed;
  QF_INT_LOCK_KEY_
  QF_INT_LOCK_();
  if (me->prev != (QTimeEvt *)0)
  { /* is the time event actually armed? */
    // prev指针不为0表示已经被插入定时器链表了，但事件还没被发出去
    // 返回1向调用者保证， 这个时间事件还没有被发送也不会被发送，仅对单次定时器有效，
    // 因为多次的话即使事件发出去了，节点也还在链表内
    wasArmed = (uint8_t)1;
    // 从链表里删除
    if (me == QF_timeEvtListHead_)
    {
      QF_timeEvtListHead_ = me->next;
    }
    else
    {
      if (me->next != (QTimeEvt *)0)
      { /* not the last in the list? */
        me->next->prev = me->prev;
      }
      me->prev->next = me->next;
    }
    // 设定为未使用
    me->prev = (QTimeEvt *)0; /* mark the time event as disarmed */
  }
  else
  { /* the time event was not armed */
    // 定时器未启用，可能是从未启用，也有可能是事件已经发出去后被关闭了
    wasArmed = (uint8_t)0;
  }
  QF_INT_UNLOCK_();
  return wasArmed;
}
```

![oneshottimeevent](/assets/img/2022-07-27-quantum-platform-1/oneshottimeevent.jpg)

当状态机处于 A 状态时设置了一个定时事件，但在定时器生效前发生了状态切换到 B（图中触发的 BUTTON_PRESS 事件），此时 A 设定的定时事件还存在，QF 框架还会给当前状态机发事件，当 B 收到该事件后用`自己的处理方式`处理，就会有问题，因为这个是状态 A 设定的，B 没设定过，不同状态的对`同一信号`的处理是`不同`的。

这时需要 A 在退出前`关闭定时器`（利用在 exit()中执行 QTimeEvt_disarm()），且用一个`全局变量`通知其他状态不要用已经在事件队列里的属于状态 A 的定时事件

### 原生 QF 事件队列

使用 QEQueue 数据结构管理，有两种类型：

- 第一个变体是特别为活动对象设计和优化的事件队列

  原生 QF 事件队列放弃的功能：

  - 比如可变尺寸的消息（原生 QF 事件队列是固定`等长`的，仅存储指向事件的指针）
  - 阻塞在一个满队列（原生 QF 事件队列在`插入`时不能被阻塞，即使队列已满，不能处理满的情况）
  - 定时阻塞在空队列（原生 QF 事件队列永远阻塞在空队列，意味着该线程不会在超时后去做其他事情）

- 另一个更简单的 QF 事件队列的变体，是一个通用的“原始的”`线程安全`的`不能阻塞`的队列

#### QEQueue 结构

![qequeuering](/assets/img/2022-07-27-quantum-platform-1/qequeuering.jpg)

> 这个图片好像画错了

QEQueue 环形队列里存放的是`事件指针`(QEvent\*)，在 32 位机里就是`等长`的 4 个字节，指向事件实例

```c
#ifndef QF_EQUEUE_CTR_SIZE
    #define QF_EQUEUE_CTR_SIZE 1
#endif
#if (QF_EQUEUE_CTR_SIZE == 1)
    typedef uint8_t QEQueueCtr;
#elif (QF_EQUEUE_CTR_SIZE == 2)
    typedef uint16_t QEQueueCtr;
#elif (QF_EQUEUE_CTR_SIZE == 4)
    typedef uint32_t QEQueueCtr;
#else
    #error "QF_EQUEUE_CTR_SIZE defined incorrectly, expected 1, 2, or 4"
#endif
typedef struct QEQueueTag
{
    // 该值和tail位置的值相同，指向下一个要被使用的事件，frontEvt为空表示队列为空队列
    QEvent const *frontEvt; /* pointer to event at the front of the queue */
    // 环形队列起始位置指针
    QEvent const **ring;    /* pointer to the start of the ring buffer */
    // 环形队列结束偏移
    QEQueueCtr end;         /* offset of the end of the ring buffer from the start */
    // 事件队列头(入队位置，FIFO)
    QEQueueCtr head;        /* offset to where next event will be inserted */
    // 事件队列尾(出队位置；入队位置，LIFO)
    QEQueueCtr tail;        /* offset of where next event will be extracted */
    // 环形队列空闲数量
    QEQueueCtr nFree;       /* number of free events in the ring buffer */
    // 最小空闲事件数，跟踪队列使用的最差情况，用于微调环形缓存的尺寸
    QEQueueCtr nMin;        /* minimum number of free events ever in the buffer */
} QEQueue;
```

#### QEQueue 的初始化

```c
// 参数qSto为预分配空间
void QEQueue_init(QEQueue *me, QEvent const *qSto[], QEQueueCtr qLen)
{
  me->frontEvt = (QEvent *)0; /* no events in the queue */
  me->ring = &qSto[0];
  me->end = qLen;
  me->head = (QEQueueCtr)0;
  me->tail = (QEQueueCtr)0;
  me->nFree = qLen; /* all events are free */
  me->nMin = qLen;  /* the minimum so far */
}
```

qSto==NULL 和 qLen=0 将队列设置为仅 1 个容量，因为 fromtEvt 也算一个

#### 原生 QF 活动对象队列

活动对象事件队列的接口包含 3 个函数： `QActive_postFIFO()`，`QActive_postLIFO()`和 `QActive_get_()`

```c
// 返回一个指向静态QEvent的指针
QEvent const *QActive_get_(QActive *me)
{
  QEvent const *e;
  QF_INT_LOCK_KEY_
  QF_INT_LOCK_();
  // 阻塞直到队列不为空（视实现而定，非抢占式的可能不阻塞）
  QACTIVE_EQUEUE_WAIT_(me); /* wait for event queue to get an event */
  // 取frontEvt的值，而不是找ring内的tail
  e = me->eQueue.frontEvt;
  // end初始化赋值为qLen，可以表示ring总长，这里判断是否全空
  if (me->eQueue.nFree != me->eQueue.end)
  { /* any events in the buffer? */
    /* remove event from the tail */
    // 从tail取到frontEvt
    me->eQueue.frontEvt = me->eQueue.ring[me->eQueue.tail];
    // index为0表示绕尾
    if (me->eQueue.tail == (QEQueueCtr)0)
    {                                   /* need to wrap the tail? */
      // 绕尾就要把值从0直接变成尾部的qLen，然后减1就是绕尾后的index
      me->eQueue.tail = me->eQueue.end; /* wrap around */
    }
    // 从tail取出，tail递减
    --me->eQueue.tail;
    // 空闲数增加
    ++me->eQueue.nFree; /* one more free event in the ring buffer */
  }
  else // 如果全空
  {
    me->eQueue.frontEvt = (QEvent *)0; /* queue becomes empty */
    // 队列为空信号
    QACTIVE_EQUEUE_ONEMPTY_(me);
  }
  QF_INT_UNLOCK_();
  return e;
}
```

```c
void QActive_postFIFO(QActive *me, QEvent const *e)
{
  QF_INT_LOCK_KEY_
  QF_INT_LOCK_();
  if (e->dynamic_ != (uint8_t)0)
  {                            /* is it a dynamic event? */
    ++((QEvent *)e)->dynamic_; /* increment the reference counter */
  }
  if (me->eQueue.frontEvt == (QEvent *)0) // 为空
  {                             /* empty queue? */
    // 如果为空就直接赋值给frontEvt，不需要插入head再赋值给frontEvt
    me->eQueue.frontEvt = e;    /* deliver event directly */
    // 队列非空信号，给QActive_get_()的QACTIVE_EQUEUE_WAIT_()
    QACTIVE_EQUEUE_SIGNAL_(me); /* signal the event queue */
  }
  else // 不为空
  { /* queue is not empty, insert event into the ring-buffer */
    /* the queue must be able to accept the event (cannot overflow) */
    // 事件队列不能满，满的情况不能处理，用断言退出
    Q_ASSERT(me->eQueue.nFree != (QEQueueCtr)0);
    /* insert event into the ring buffer (FIFO) */
    // head位置插入
    me->eQueue.ring[me->eQueue.head] = e;
    // 绕尾
    if (me->eQueue.head == (QEQueueCtr)0)
    {                                   /* need to wrap the head? */
      // 绕尾就要把值从0直接变成尾部的qLen，然后减1就是绕尾后的index
      me->eQueue.head = me->eQueue.end; /* wrap around */
    }
    // 递减head
    --me->eQueue.head;
    // 递减free
    --me->eQueue.nFree; /* update number of free events */
    if (me->eQueue.nMin > me->eQueue.nFree)
    {
      // nFree更小时，更新nMin
      me->eQueue.nMin = me->eQueue.nFree; /* update min so far */
    }
  }
  QF_INT_UNLOCK_();
}
```

#### “ 原始的”线程安全的队列

```c
/* Application header file -----------------------------------------------*/
#include "qequeue.h"
extern QEQueue APP_isrQueue; /* global “raw” queue */
typedef struct IsrEvtTag
{ /* event with parameters to be passed to the ISR */
  QEvent super;
  ...
} IsrEvt;
/* ISR module ------------------------------------------------------------*/
QEQueue APP_isrQueue; /* definition of the “raw” queue */
// 自定义ISR中断处理程序
void interrupt myISR()
{
  QEvent const *e;
  // 取一个事件，这里的QEQueue_get()即使队列为空也不阻塞
  ... e = QEQueue_get(&APP_isrQueue); /* get an event from the “raw” queue */
  /* event available? */
  if (e != (QEvent *)0)
  {// 执行事件
    Process the event e(could be dispatching to a state machine)
    ...
    // 因为是ISR管理事件，不是QF框架，要记得回收空间
    QF_gc(e); /* explicitly recycle the event */
  }
  ...
}
/* Active object module --------------------------------------------------*/
QState MyAO_stateB(MyAO *me, QEvent const *e)
{
  switch (e->sig)
  {
    ...
    case SOMETHING_INTERESTING_SIG:
    {
      IsrEvt *pe = Q_NEW(IsrEvt, ISR_SIG);
      pe->... = ... /* set the event attributes */
      // 发送事件
      QEQueue_postFIFO(&APP_isrQueue, (QEvent *)pe);
      return (QSTATE)0;
    }
    ...
  }
  return (QState)&MyAO_stateA;
}
/* main module -----------------------------------------------------------*/
static QEvent *l_isrQueueSto[10]; /* allocate a buffer for the “raw” queue */
main()
{
  ...
  /* initialize the “raw” queue */
  // 初始化事件队列
  QEQueue_init(&APP_isrQueue, l_isrQueueSto, Q_DIM(l_isrQueueSto));
  ...
}
```

QEQueue 函数 QEQueue_postFIFO() ， QEQueue_postLIFO() 和 QEQueue_get()的实现是非常直接的，因为不需要平台相关的宏。所有这些函数都是`可重入`的(多线程安全)，因为它们使用`临界区`代码维护队列的完整性。

### 原生 QF 内存池

![qmpool](/assets/img/2022-07-27-quantum-platform-1/qmpool.jpg)

图中`粗黑线`框起来的是一个块，`细黑线`分割了一个块，`左边`为下一空闲块`指针`。通过这种方法重用了`空闲块`的空间，不需要单独找地方存一张`空闲表`了

```c
typedef struct QMPoolTag
{
  // 空闲表表头，即首个空闲块的地址
  void *free;           /* the head of the linked list of free blocks */
  // 池开始块地址
  void *start;          /* the start of the original pool buffer */
  // 池结束块地址
  void *end;            /* the last block in this pool */
  // 块大小
  QMPoolSize blockSize; /* maximum block size (in bytes) */
  // 块数量
  QMPoolCtr nTot;       /* total number of blocks */
  // 空闲块数量
  QMPoolCtr nFree;      /* number of free blocks remaining */
  // 空闲块曾经出现过的最小数量，用于分析使用情况
  QMPoolCtr nMin;       /* minimum number of free blocks ever in this pool */
} QMPool
```

#### 原生 QF 内存池的初始化

_QFreeBlock 结构用于对不同架构 CPU 实现内存对齐_：

```c
// 空闲链表节点，里面就一个指针
typedef struct QFreeBlockTag {
    struct QFreeBlockTag *next;
} QFreeBlock;
```

```c
void QMPool_init(QMPool *me, void *poolSto,
                 uint32_t poolSize, QMPoolSize blockSize)
{
  // 空闲链表
  QFreeBlock *fb;
  uint32_t corr;
  uint32_t nblocks;
  /* The memory block must be valid
   * and the poolSize must fit at least one free block
   * and the blockSize must not be too close to the top of the dynamic range
   */
  Q_REQUIRE((poolSto != (void *)0) // 预分配空间不能为空
            && (poolSize >= (uint32_t)sizeof(QFreeBlock)) // 池大小必须能够至少放入一个空闲块，后面有断言poolSize >= (uint32_t)blockSize，这里只是一种判断条件
            && ((QMPoolSize)(blockSize + (QMPoolSize)sizeof(QFreeBlock))
            > blockSize));  // blockSize值不应该接近QMPoolSize类型值上限，比如QMPoolSize是uint16，
                            // blockSize不应该接近65535，如果blockSize为65532，
                            // 这里加上QFreeBlock指针的4，就会溢出回绕，最终比blockSize小。
  /*lint -e923 ignore MISRA Rule 45 in this expression */
  // (uint32_t)sizeof(QFreeBlock) - (uint32_t)1得到非对齐mask，如4-1=3=0x0011，如果是对齐地址，&操作后应该为0(相当于除以4的余数)，非对齐则不为0
  corr = ((uint32_t)poolSto & ((uint32_t)sizeof(QFreeBlock) - (uint32_t)1));
  if (corr != (uint32_t)0) // 未对齐
  {                                             /* alignment needed? */
    // 算对齐误差
    corr = (uint32_t)sizeof(QFreeBlock) - corr; /*amount to align poolSto*/
    // poolSize相应缩小，放弃未对齐部分
    poolSize -= corr;                           /* reduce the available pool size */
  }
  /*lint -e826 align the head of free list at the free block-size boundary*/
  // 开始给QPool赋值，强制对齐下，会丢弃未对齐部分，从对齐地址开始使用
  me->free = (void *)((uint8_t *)poolSto + corr);
  /* round up the blockSize to fit an integer # free blocks, no division */
  // me->blockSize通过运算变为blockSize
  me->blockSize = (QMPoolSize)sizeof(QFreeBlock); /* start with just one */
  // nblocks的计算避免用到除法，而是用while做加法计算
  // nBlocks = (blockSize + sizeof(QFreeBlock) – 1)/sizeof(QFreeBlock + 1)
  nblocks = (uint32_t)1;   /* # free blocks that fit in one memory block */
  // 加法增加，也能保证me->blockSize是sizeof(QFreeBlock)的整数倍，保证了每个块的地址也是对齐的
  while (me->blockSize < blockSize)
  {
    me->blockSize += (QMPoolSize)sizeof(QFreeBlock);
    ++nblocks;
  }
  blockSize = me->blockSize; /* use the rounded-up value from now on */
                             /* the pool buffer must fit at least one rounded-up block */
  Q_ASSERT(poolSize >= (uint32_t)blockSize);
  /* chain all blocks together in a free-list... */
  // 第一个直接减掉，因为已经加进链表了，见下面的while循环
  poolSize -= (uint32_t)blockSize; /*don’t link the last block to the next */
  // 不是从0开始，因为第一个就是me->free，已经在了，见下面while循环
  me->nTot = (QMPoolCtr)1;         /* the last block already in the pool */
  // 空闲队列指针赋值
  fb = (QFreeBlock *)me->free;     /*start at the head of the free list */
  while (poolSize >= (uint32_t)blockSize)
  {                                  /* can fit another block? */
    // TODO:这里的nblocks应该是me->nTot吧
    fb->next = &fb[nblocks];         /* point the next link to the next block */
    // 链表生成
    fb = fb->next;                   /* advance to the next block */
    poolSize -= (uint32_t)blockSize; /* reduce the available pool size */
    ++me->nTot;                      /* increment the number of blocks so far */
  }
  fb->next = (QFreeBlock *)0; /* the last link points to NULL */
  me->nFree = me->nTot;       /* all blocks are free */
  me->nMin = me->nTot;        /* the minimum number of free blocks */
  me->start = poolSto;        /* the original start this pool buffer */
  me->end = fb;               /* the last block in this pool */
}
```

> 许多 CPU 架构对指针的正确`对齐`有特别的要求。例如， `ARM` 处理器需要一个指针被分配在一个可以`被 4 整除`的地址。其他的 CPU，比如 `Pentium` ，可以接受分配在`奇数地址`的指针，但是当指针在可被 4 整除的地址对齐时，`执行性能`会更加好。

#### 从池里获得一个内存块

使用 `QMPool_get()` 从内存池获取一个块，支持耗尽，耗尽返回 `NULL`。

> 之前在[动态事件分配](#动态事件分配)中提到如果是内存池用于动态事件队列，由于 QF 不支持`满队列`（耗尽），所以用完`无法插入`队列时会直接断言`报错`。

```c
void *QMPool_get(QMPool *me)
{
  QFreeBlock *fb;
  QF_INT_LOCK_KEY_
  QF_INT_LOCK_();
  fb = (QFreeBlock *)me->free; /* get a free block or NULL */
  if (fb != (QFreeBlock *)0)
  {                      /* free block available? */
    me->free = fb->next; /* adjust list head to the next free block */
    --me->nFree;         /* one less free block */
    if (me->nMin > me->nFree)
    {
      me->nMin = me->nFree; /* remember the minimum so far */
    }
  }
  QF_INT_UNLOCK_();
  return fb; /* return the block or NULL pointer to the caller */
}
```

#### 把一个内存块回收到池内

`QMPool_put()` 用来把块回收到池内

```c
// b是要回收的块的地址
void QMPool_put(QMPool *me, void *b)
{
  QF_INT_LOCK_KEY_
  Q_REQUIRE((me->start <= b) && (b <= me->end) /* must be in range */
  // TODO: 这里应该是小于不是小于等于，等于说明全空闲，就不能再释放了
            && (me->nFree <= me->nTot));       /* # free blocks must be < total */
  QF_INT_LOCK_();
  ((QFreeBlock *)b)->next = (QFreeBlock *)me->free; /* link into free list */
  me->free = b;   /* set as new head of the free list */
  ++me->nFree;    /* one more free block in this pool */
  QF_INT_UNLOCK_();
}
```

### 原生 QF 优先级集合

可以用来表示活动对象优先级，此时每一位对应一个活动对象

```c
typedef struct QPSet64Tag
{
  uint8_t bytes;   /* condensed representation of the priority set */
  uint8_t bits[8]; /* bitmasks representing elements in the set */
} QPSet64;
```

![qpset](/assets/img/2022-07-27-quantum-platform-1/qpset.jpg)

`uint8_t bits[8]`一共是 8 个 1 字节共 64 位，对应图上的 8x8 矩阵(bitmask)，`bits[0]`表示第 1 行,`bits[7]`表示第 8 行

`uint8_t bytes`用于加快 bitmask `查找`，用来指示对应行的位中是否有`至少一个 1`(字节值大于等于 1)。如`bytes`的`第0位`指示`bits[0]`是否大于等于 1，如大于等于 1 则为 1。bytes 为`0x10010001`表示`bytes[0]`、`bytes[4]`、`bytes[7]`大于等于 1。

_判断集合是否为空_:

```c
#define QPSet64_notEmpty(me_) ((me_)->bytes != (uint8_t)0)
```

_找出集合里最大的元素_:

```c
// 先找bytes最高位，在找最高位对应的bits的最高位，bytes移位算偏移后相加
#define QPSet64_findMax(me_, n_)                                  \
  do                                                              \
  {                                                               \
    (n_) = (uint8_t)(QF_log2Lkup[(me_)->bytes] - 1);              \
    (n_) = (uint8_t)(((n_) << 3) + QF_log2Lkup[(me_)->bits[n_]]); \
  } while (0)
```

> 二进制对数查找表 `QF_log2Lkup` 见[发行-订阅事件发送](#发行-订阅事件发送)的`订阅`一节

_插入一个值_:

```c
#define QPSet64_insert(me_, n_)                       \
  do                                                  \
  {                                                   \
    (me_)->bits[QF_div8Lkup[n_]] |= QF_pwr2Lkup[n_];  \
    (me_)->bytes |= QF_pwr2Lkup[QF_div8Lkup[n_] + 1]; \
  } while (0)
```

> 字节索引 `QF_div8Lkup[p] = (p – 1)/8`（把值转为 bits 的索引），找字节内偏移 `QF_pwr2Lkup[p] = 1 << ((p – 1) % 8)`（p-1 是因为偏移和索引都是从 0 开始，参数 p 是从 1 开始）

先给 bits 赋值，再给 bytes 赋值

_移除一个值_:

```c
#define QPSet64_remove(me_, n_)                            \
  do                                                       \
  {                                                        \
    (me_)->bits[QF_div8Lkup[n_]] &= QF_invPwr2Lkup[n_];    \
    if ((me_)->bits[QF_div8Lkup[n_]] == (uint8_t)0)        \
    {                                                      \
      (me_)->bytes &= QF_invPwr2Lkup[QF_div8Lkup[n_] + 1]; \
    }                                                      \
} while(0)
```

> `QF_invPwr2Lkup[p]` 清除对应位

### 原生合作式 vanilla 内核

QF 包含了一个简单的合作式 `vanilla` 内核

> 在计算机科学领域，`香草vanilla`是一个用于表示“一个事物没有经过自定义的改动而仍然保留着它们`默认`的形式”的术语。这个术语已经广为流传并成为事实标准。香草一词来自于传统冰淇淋的`标准口味`，香草味。根据 Eric S. Raymond 的《The New Hacker's Dictionary》一书记载，香草一词在感觉上比普通一词更能表达“`默认`”的含义。[维基百科:香草软件](https://zh.m.wikipedia.org/zh-hans/%E9%A6%99%E8%8D%89%E8%BD%AF%E4%BB%B6)

vanilla 内核通过在一个`无限循环`内不断查询所有活动对象的事件队列来工作。内核总是挑选`最高优先级`的`预备运行`(非空事件队列)的`活动对象`

![readyset](/assets/img/2022-07-27-quantum-platform-1/readyset.jpg)

图中所示 QPSet64 类型的 QF*readySet* 优先级集合用于表示系统内所有`非空事件队列`的“`预备集合`”，每一位对应一个活动对象。活动对象的事件队列为非空时对应位置 1 ，为空时置 0

#### qvanilla.c 源文件

```c
#include "qf_pkg.h"
#include "qassert.h"
/* Package-scope objects -----------------------------------------------*/
// 禁止优化，因为可能在中断中改变
QPSet64 volatile QF_readySet_; /* QF-ready set of active objects */
/*.....................................................................*/
void QF_init(void)
{
  /* nothing to do for the “vanilla” kernel */
}
/*.....................................................................*/
void QF_stop(void)
{
  /* nothing to cleanup for the “vanilla” kernel */
  QF_onCleanup(); /* cleanup callback */
}
/*.....................................................................*/
// main()中调用QF_run()，把控制权转让给QF框架，也就是运行 vanilla 内核
void QF_run(void)
{ /* see NOTE01 */
  uint8_t p;
  QActive *a;
  QEvent const *e;
  QF_INT_LOCK_KEY_
  // 配置回调函数并启动中断
  QF_onStartup(); /* invoke the QF startup callback */
  for (;;)
  { /* the background loop */
    QF_INT_LOCK_();// 处理QF_readySet_上锁
    // 是否有事件要处理
    if (QPSet64_notEmpty(&QF_readySet_))
    { // 获取有事件的最高优先级的活动对象
      QPSet64_findMax(&QF_readySet_, p);
      a = QF_active_[p];
      QF_INT_UNLOCK_(); // 中断上锁是为了处理QF_readySet_，现在可以解锁了
      // 找这个活动对象的第一个待处理事件
      e = QActive_get_(a);               /* get the next event for this AO */
      // 执行状态函数
      QF_ACTIVE_DISPATCH_(&a->super, e); /* dispatch to the AO */
      QF_gc(e);                          /* determine if event is garbage and collect it if so */
    }
    else // 没有事件的话不阻塞，要做其他事情，比如进入低功耗模式
         // 进入Idle函数前必须上锁，进入后在开启低功耗模式前必须解锁中断，防止死锁
    { /* all active object queues are empty */
#ifndef QF_INT_KEY_TYPE // QF_onIdle是否有参数取决于临界区机制
      QF_onIdle(); /* see NOTE02 */
#else
      QF_onIdle(intLockKey_); /* see NOTE02 */
#endif /* QF_INT_KEY_TYPE */
    }
  }
}
/*.....................................................................*/
// 启动活动对象线程
void QActive_start(QActive *me, uint8_t prio,
                   QEvent const *qSto[], uint32_t qLen,
                   void *stkSto, uint32_t stkSize,
                   QEvent const *ie)
{
  Q_REQUIRE(((uint8_t)0 < prio) && (prio <= (uint8_t)QF_MAX_ACTIVE)
            && (stkSto == (void *)0)); /* does not need per-actor stack */
  (void)stkSize;                                     /* avoid the “unused parameter” compiler warning */
  QEQueue_init(&me->eQueue, qSto, (QEQueueCtr)qLen); /* initialize QEQueue */
  me->prio = prio;                                   /* set the QF priority of this active object */
  QF_add_(me);                                       /* make QF aware of this active object */
  QF_ACTIVE_INIT_(&me->super, ie);                   /* execute initial transition */
}
/*.....................................................................*/
void QActive_stop(QActive *me)
{
  QF_remove_(me);
}
```

QF_onIdle()是否有参数取决于[QF 里的临界区](#qf-里的临界区)类型，当使用简单的“`无条件中断解锁`”策略时，这个函数没有参数，但是在使用“`保存和恢复中断状态`” 策略时，它需要中断状态参数。

![vanillaidle](/assets/img/2022-07-27-quantum-platform-1/vanillaidle.jpg)

如图，如果进入 `Idle` 函数前`不关中断`，就会产生`竞争`，可能就有`新事件`插入了。然后 Idle 处理进入`低功耗模式`就不能`及时响应`这个事件了。

解决办法就是`进 Idle 前`关中断，然后在`进 Idle 后`且进入`低功耗模式`的`同时`开中断，注意这个“同时”，需要实现`原子操作`，也就是 MCU 的支持。

#### qvanilla.h 头文件

这个头文件最重要的功能是在事件被`发送`到和从活动对象事件队列`移除`时`更新预备集合` (`QF_readySet_`)

```c
#ifndef qvanilla_h
#define qvanilla_h
#include "qequeue.h" /* “Vanilla” kernel uses the native QF event queue */
#include "qmpool.h"  /* “Vanilla” kernel uses the native QF memory pool */
#include "qpset.h"   /* “Vanilla” kernel uses the native QF priority set */
                     /* the event queue and thread types for the “Vanilla” kernel */
#define QF_EQUEUE_TYPE QEQueue // 使用QEQueue作为事件队列
/* native QF event queue operations */
#define QACTIVE_EQUEUE_WAIT_(me_) \  // 不阻塞，仅当它确信事件队列拥有最少一个事件时，它才调用 QActive_get_()
  Q_ASSERT((me_)->eQueue.frontEvt != (QEvent *)0)
#define QACTIVE_EQUEUE_SIGNAL_(me_) \  // 发给空队列时修改优先集合
  QPSet64_insert(&QF_readySet_, (me_)->prio)
#define QACTIVE_EQUEUE_ONEMPTY_(me_) \ // 删除后成空队列时修改优先集合
  QPSet64_remove(&QF_readySet_, (me_)->prio)
/* native QF event pool operations */
#define QF_EPOOL_TYPE_ QMPool // 使用QMPool作为事件池
#define QF_EPOOL_INIT_(p_, poolSto_, poolSize_, evtSize_) \
  QMPool_init(&(p_), poolSto_, poolSize_, evtSize_)
#define QF_EPOOL_EVENT_SIZE_(p_) ((p_).blockSize)
#define QF_EPOOL_GET_(p_, e_) ((e_) = (QEvent *)QMPool_get(&(p_)))
#define QF_EPOOL_PUT_(p_, e_) (QMPool_put(&(p_), e_))
// 共享变量声明为volatile不允许优化
extern QPSet64 volatile QF_readySet_; /** QF-ready set of active objects */
#endif                                /* qvanilla_h */
```

## 可抢占式“运行-到-完成”内核

### 选择一个可抢占式内核的理由

**正常情况并不需要可抢占式内核**：

- 长过程被分割成了`短`的 RTC(run-to-completion) 步骤，不需要内核来`分割`（QP从设计层面就避免了长过程，如果用可抢占式内核就可以通过内核调度分割长过程）
- 活动对象执行线程不会`阻塞`（不阻塞意味着CPU控制权会在RTC步骤执行完成时被让出）
- RTC 步骤足够短，`响应延迟`较低

**需要可抢占式内核的情况**：

需要密集的、对时序有极高要求的任务，且低优先级的任务 RTC 时间较长且不容易分解。

以一个 GPS 接收机系统为例。这个接收机在一个`定点` CPU 上执行大量的`浮点`运算去`计算` GPS 的位置（计算步骤不容易分解，且占用较长 RTC 时间）。同时， GPS 接收机必须`跟踪` GPS 卫星的`信号`，这牵涉到在小于`毫秒级`间隔内的`闭环控制回路`。很明显我们不容易把`位置计算`分解成`足够短`的 RTC 步骤从而允许`可靠的`信号跟踪，即使把信号跟踪定义为最高优先级，低优先级的 RTC 过程过长依然会影响时序。

> 定点和浮点详见[定点vs浮点数字信号处理](https://www.analog.com/cn/technical-articles/fixedpoint-vs-floatingpoint-dsp.html)

### RTC 内核简介

#### 使用单堆栈的可抢占式多任务处理

常规实时内核需要为每个任务配置单独的`堆栈`，还要维护复杂的执行`上下文`。

需要在切换时保存上下文到任务`独立的栈`的原因是调度的`不确定性`，例：

A 切 B, B 切 C, C 切 D, D 切 A，此时 A 的上下文信息如果在全局栈中，必须把 B C D 的上下文全部出栈，这显然是不合理的，**所以必须为每个任务单独配置堆栈，并在切换时把上下文信息保存在任务独立的栈中**。

对于可确定`调度顺序`(基于优先级)而且遵从`运行到完成`规范的任务，就可以把每个任务的上下文信息都保存在`全局栈`中，例：

A 发事件给 B，因为 B 的优先级更高，所以内核立刻调度到 B，并把 A 的上下文保存到全局栈(本来就在全局栈中)中，B 也可以发送事件给更高优先级的任务并执行，这样就形成`嵌套`，因为任务都是运行到完成，所以等栈顶任务执行完可以`有序退出`。

这种调度策略和基于`优先级`的中断控制器逻辑非常像。而且和函数的`嵌套调用`过程也非常像

#### 非阻塞型内核

上面说的 RTC 内核有个局限，就是`不能阻塞`。原因就是虽然看上去是调度，但实际上还是一个`连续执行`的过程，就像函数的嵌套调用一样，不允许中间有阻塞。不过活动对象的设计就是不阻塞的，这也不是问题。

#### 同步抢占和异步抢占

- 同步抢占

  当一个较低优先级任务发送一个事件给一个较高优先级任务时，内核必须立刻暂停较低优先级任务的执行，并启动较高优先级的任务。

- 异步抢占

  在`中断 ISR` 中发送一个事件给一个比被中断的任务更高优先级的任务时，当这个 ISR `完成后`，内核必须启动较高优先级任务的执行，而不是恢复这个较低优先级的任务。(因为中断优先级总是比任务高，必须运行到完成后才运行执行任务)

_同步抢占_：

![highproitask](/assets/img/2022-07-27-quantum-platform-1/highproitask.jpg)

- （2）时低优先级任务发送事件给高优先级任务，且调度器开始调度。
- （5）时高优先级任务发送事件给低优先级任务，调度器不执行调度，
- （7）时高优先级任务运行完成并返回（2）时调用的调度器。
- （8）调度器再一次检查是否有一个较高优先级任务准备运行，但是它没找到。 RTC调度器返回低优先级任务。

_异步抢占_：

![isrhighpriotask](/assets/img/2022-07-27-quantum-platform-1/isrhighpriotask.jpg)

- （3）中断服务程序 (ISR) 执行 `RTC 内核`特定的`进入动作`，它在一个堆栈变量中保存被中断任务的优先级，把 RTC 内核的当前优先级提升到 ISR 层（在任何任务之上）。这一步是为了防止第（4）步产生事件导致的调度，因为此时内核优先级比那个任务优先级高，就不会在 ISR 内部触发调度动作
- （4）ISR 发送了一个事件给高优先级任务，发送事件的动作会让 RTC 调度器工作，它`立即返回`，因为没有任务有比当前的优先级更高的优先级。ISR `继续运行`
- （5）ISR 继续运行，最后执行 RTC 内核相关的`退出动作`
- （6）RTC 内核相关的 ISR 退出，发送 End-Of-Interrupt(`EOI`) 指令给中断控制器，`恢复`被中断任务的被保留的`优先级`，并调用 `RTC 调度器`。

  > 退出中断有 `EOI` 和 `IRET` 两步，EOI 表示停止对当前的中断嵌套层进行优先级排序(此时可以插入任意优先级新中断)，IRET 表示从中断返回。这一步只发 EOI 表示还不想从中断返回
- （7）调度器`开中断`，并开始调度到高优先级任务。此时 RTC 调度器没有返回。
- （9）高优先级任务执行完毕并返回到 RTC 调度器
- （10）IRET 执行，IRET 恢复低优先级任务的上下文，从（2）开始的中断返回

在第 (5) 步 RTC 内核相关的中断退出(执行 EOI 后)里，中断处理在概念上已经`结束`了，即使`中断堆栈帧`(interrupt stack frame) 继续保留在堆栈上并且 `IRET` 指令还没执行。在 EOI 指令之前，`中断控制器`仅允许比当前正在服务的中断更高优先级的中断。在 EOI 指令后，通过调用 RTC 调度器，中断被`解锁`，中断控制器允许所有的级别的中断，这正是在任务层所期望的行为。这样的话在（8）中高优先级任务执行时依旧可以触发中断和异步调度

#### 堆栈的利用

_同步抢占_:

![stacksync](/assets/img/2022-07-27-quantum-platform-1/stacksync.jpg)

- （2）发送事件给高优先级任务，调用了 RTC 调度器，`调度器堆栈帧`(stack frame)`入栈`所以栈增长了
- （3）RTC 调度器调用高优先级任务，`任务堆栈帧`(stack frame)`入栈`，栈再次增长
- （5）高优先级任务发送事件给低优先级任务，调用了 RTC 调度器，调度器堆栈帧(stack frame)`入栈`，随后因为不满足调度条件`立即返回`，调度器堆栈帧(stack frame)`出栈`
- （7）任务堆栈帧(stack frame)`出栈`
- （8）调度器在调度完成后`再次检查`是否有较高优先级的任务要运行，没有就`出栈`

_异步抢占_:

![stackasync](/assets/img/2022-07-27-quantum-platform-1/stackasync.jpg)

- （2）发生中断，由硬件控制将中断堆栈帧压栈，ISR 开始运行，并可能把某些别的上下文压入堆栈 （就是 ISR 程序，虚线所示）
- （4）TODO：应该会发送事件触发一次调度器调用，怎么栈没增加
- （6）RTC 调度器被调用，堆栈帧入栈
- （7）使能中断并调度到高优先级任务，堆栈帧入栈
- （8）高优先级任务运行到结束，出栈
- （9）调度器再次检查，没有就出栈
- （10）ISR 出栈（虚线），硬件执行 IRET 指令，中断出栈

#### 和传统可抢占式内核的比较

通过在`一个堆栈`管理所有的任务和中断的上下文， RTC 内核运行所需的 `RAM` 远比一个典型的阻塞式内核需要的少。

C 编译器生成的 ISR 进入时仅保留可能在 C 函数被使用那些寄存器，而不是全部，比传统的少

## 移植和配置 QF

QF 包含了一个被清楚定义的`平台抽象层 PAL`（ platform abstraction layer ），它封装了所有平台相关的代码，清晰把它和平台无关的代码区分开

### QP 平台抽象层

#### 生成 QP 应用程序

你在使用的 QP 移植由 `qf_port.h` 头文件和 `QF 库文件`所在的目录分支决定。

![qpport](/assets/img/2022-07-27-quantum-platform-1/qpport.jpg)

编译+链接，QP 库允许连接器在链接时消除任何没有被引用的 QP 代码

#### 创建 QP 库

## 开发 QP 应用程序

### 开发 QP 应用程序的准则

#### 准则

- 活动对象应该仅通过某个`异步事件`交换来相互作用，不应该`共享内存`或其他资源。
- 活动对象不应该`阻塞`或者在RTC处理的中间`忙等待`事件。

#### 启发式

- 事件驱动型编程，`非阻塞`，快速返回
- 实现在活动对象之间的`松散耦合`，避免资源共享
- 把较长的处理`分解`成较短的步骤
- 画出`顺序图`

### 哲学家就餐问题

![philosopher](/assets/img/2022-07-27-quantum-platform-1/philosopher.jpg)

#### 第一步：需求

5个哲学家，5个餐叉，吃面需要2个餐叉，吃完会思考，核心是防止死锁和饿死。

#### 第二步：顺序图

![sequencediagram](/assets/img/2022-07-27-quantum-platform-1/sequencediagram.jpg)

`Table` 对象管理餐叉，每个 `Philo` 对象管理一个哲学家

触发 QF 定时事件`Philo[m]`终止思考，开始饥饿，向Table发送事件(HUNGRY(m))请求就餐许可(有足够的叉子)。Table 将就餐许可事件(EAT(m))发送给对应对象。`Philo[m]`进入就餐状态直到下一个定时事件，发送完成事件(DONE(m))归还叉子。

#### 第三步：信号，事件和活动对象

```c
#ifndef dpp_h
#define dpp_h
// 对哲学家就餐问题自定义的事件信号
enum DPPSignals
{
  EAT_SIG = Q_USER_SIG, /* published by Table to let a philosopher eat */
  DONE_SIG,             /* published by Philosopher when done eating */
  TERMINATE_SIG,        /* published by BSP to terminate the application */
  MAX_PUB_SIG,          /* the last published signal */
  // 这个信号是直接发送的
  HUNGRY_SIG,           /* posted directly from hungry Philosopher to Table */
  MAX_SIG               /* the last signal */
};
// 派生自QEvent的事件，增加了一个philoNum变量
typedef struct TableEvtTag
{
  QEvent super;     /* derives from QEvent */
  uint8_t philoNum; /* Philosopher number */
} TableEvt;
enum
{
  N_PHILO = 5
};                     /* number of Philosophers */
// 构造函数，再main开始时调用
void Philo_ctor(void); /* ctor that instantiates all Philosophers */
void Table_ctor(void);
extern QActive *const AO_Philo[N_PHILO]; /* "opaque" pointers to Philo AOs */
extern QActive *const AO_Table;          /* "opaque" pointer to Table AO */
#endif                                   /* dpp_h */
```

#### 第四步：状态机

![ddpstatemachines](/assets/img/2022-07-27-quantum-platform-1/ddpstatemachines.jpg)

这里产生`HUNGRY`事件和`DONE`事件不是由`定时`事件触发而是`进入退出`动作时触发，更`精确`的反应了语义，提高后续的`可维护性`

准则：偏向使用`进入`动作和`退出`动作，而不是`转换`动作。

_哲学家和餐叉编号_：

![philoforknum](/assets/img/2022-07-27-quantum-platform-1/philoforknum.jpg)

```c
#include "qp_port.h"
#include "dpp.h"
#include "bsp.h"
Q_DEFINE_THIS_FILE
/* Active object class -----------------------------------------------------*/
// 活动对象Table从QActive派生，增加了两个变量，管理叉子和饥饿度
typedef struct TableTag
{
  QActive super;             /* derives from QActive */
  uint8_t fork[N_PHILO];     /* states of the forks */
  uint8_t isHungry[N_PHILO]; /* remembers hungry philosophers */
} Table;
static QState Table_initial(Table *me, QEvent const *e); /* pseudostate */
static QState Table_serving(Table *me, QEvent const *e); /* state handler */
// 如上图，n顺时针递增，人和右叉为一组，标记为n，计算左边或右边组的序号
#define RIGHT(n_) ((uint8_t)(((n_) + (N_PHILO - 1)) % N_PHILO))
#define LEFT(n_) ((uint8_t)(((n_) + 1) % N_PHILO))
enum ForkState
{
  FREE,
  USED
};
/* Local objects ----------------------------------------------------------*/
// static让其他文件无法访问
static Table l_table; /* the single instance of the Table active object */
/* Global-scope objects ---------------------------------------------------*/
// 指针设为const不能更改，可以让编译器把该指针分配在ROM里
QActive *const AO_Table = (QActive *)&l_table; /* "opaque" AO pointer */
/*........................................................................*/
// 构造函数，C需要手动调用，C++会自动调用
void Table_ctor(void)
{
  uint8_t n;
  Table *me = &l_table;
  // 实例化超类，为super部分初始化
  QActive_ctor(&me->super, (QStateHandler)&Table_initial);
  for (n = 0; n < N_PHILO; ++n)
  {
    me->fork[n] = FREE;
    me->isHungry[n] = 0;
  }
}
/*.......................................................................*/
// 最顶初始转换
QState Table_initial(Table *me, QEvent const *e)
{
  (void)e; /* avoid the compiler warning about unused parameter */
  // 订阅信号
  QActive_subscribe((QActive *)me, DONE_SIG);
  QActive_subscribe((QActive *)me, TERMINATE_SIG);
  /* signal HUNGRY_SIG is posted directly */
  return Q_TRAN(&Table_serving);
}
/*.......................................................................*/
QState Table_serving(Table *me, QEvent const *e)
{
  uint8_t n, m;
  // Table相关事件，定义见上一节
  TableEvt *pe;
  switch (e->sig)
  {
  case HUNGRY_SIG:
  {
    // 人工延长单RTC处理的时间，方便进行压力测试
    BSP_busyDelay();
    // 提取事件参数
    n = ((TableEvt const *)e)->philoNum;
    /* phil ID must be in range and he must be not hungry */
    Q_ASSERT((n < N_PHILO) && (!me->isHungry[n]));
    // 屏幕打印
    BSP_displyPhilStat(n, "hungry ");
    m = LEFT(n);
    if ((me->fork[m] == FREE) && (me->fork[n] == FREE))
    {// 左右叉都空闲的情况
      me->fork[m] = me->fork[n] = USED;
      // 生成eat事件
      pe = Q_NEW(TableEvt, EAT_SIG);
      pe->philoNum = n;
      QF_publish((QEvent *)pe);
      BSP_displyPhilStat(n, "eating ");
    }
    else
    {
      me->isHungry[n] = 1;
    }
    return Q_HANDLED();
  }
  case DONE_SIG:
  {
    BSP_busyDelay();
    n = ((TableEvt const *)e)->philoNum;
    /* phil ID must be in range and he must be not hungry */
    Q_ASSERT((n < N_PHILO) && (!me->isHungry[n]));
    // 吃完开始思考
    BSP_displyPhilStat(n, "thinking");
    m = LEFT(n);
    /* both forks of Phil [n] must be used */
    Q_ASSERT((me->fork[n] == USED) && (me->fork[m] == USED));
    // 归还叉子
    me->fork[m] = me->fork[n] = FREE;
    // 右边的人是否饥饿
    m = RIGHT(n); /* check the right neighbor */
    if (me->isHungry[m] && (me->fork[m] == FREE))
    {
      me->fork[n] = me->fork[m] = USED;
      me->isHungry[m] = 0;
      pe = Q_NEW(TableEvt, EAT_SIG);
      pe->philoNum = m;
      QF_publish((QEvent *)pe);
      BSP_displyPhilStat(m, "eating ");
    }
    // 左边的左边的人是否饥饿
    m = LEFT(n); /* check the left neighbor */
    n = LEFT(m); /* left fork of the left neighbor */
    if (me->isHungry[m] && (me->fork[n] == FREE))
    {
      me->fork[m] = me->fork[n] = USED;
      me->isHungry[m] = 0;
      pe = Q_NEW(TableEvt, EAT_SIG);
      pe->philoNum = m;
      QF_publish((QEvent *)pe);
      BSP_displyPhilStat(m, "eating ");
    }
    return Q_HANDLED();
  }
  // 终止
  case TERMINATE_SIG:
  {
    QF_stop();
    return Q_HANDLED();
  }
  }
  return Q_SUPER(&QHsm_top);
}
```

#### 第五步：初始化并启动应用程序

注意点：

- 活动对象的相对优先级
- 预先分配的事件队列的尺寸
- 活动对象启动顺序

```c
#include "qp_port.h"
#include "dpp.h"
#include "bsp.h"
/* Local-scope objects ---------------------------------------------------*/
// 所有事件队列的内存缓存被静态分配
static QEvent const *l_tableQueueSto[N_PHILO];
static QEvent const *l_philoQueueSto[N_PHILO][N_PHILO];
// 用于订阅者列表的内存空间也被静态分配，这是个bitmap，之前提到过
static QSubscrList l_subscrSto[MAX_PUB_SIG];
// 使用"小尺寸"事件池
static union SmallEvent
{
  void *min_size;// min_size无意义，这句是为了让SmallEvent至少比一个指针占用空间大
  TableEvt te;
  // 可以添加其他自定义事件
  /* other event types to go into this pool */
} l_smlPoolSto[2 * N_PHILO]; /* storage for the small event pool */
/*.......................................................................*/
int main(int argc, char *argv[])
{
  uint8_t n;
  Philo_ctor();                               /* instantiate all Philosopher active objects */
  Table_ctor();                               /* instantiate the Table active object */
  BSP_init(argc, argv);                       /* initialize the Board Support Package */
  QF_init();                                  /* initialize the framework and the underlying RT kernel */
  // 订阅功能初始化
  QF_psInit(l_subscrSto, Q_DIM(l_subscrSto)); /* init publish-subscribe */
  // 用于动态事件的池，默认使用QF原生内存池管理，
  // 这里用了BSS段空间(static变量)作为原始空间（有些嵌入式没有堆空间，这是标准做法）
  QF_poolInit(l_smlPoolSto, sizeof(l_smlPoolSto), sizeof(l_smlPoolSto[0]));/* initialize event pools... */
  // 先初始化哲学家对象,
  for (n = 0; n < N_PHILO; ++n)
  { /* start the active objects... */
    QActive_start(AO_Philo[n], (uint8_t)(n + 1),
                  l_philoQueueSto[n], Q_DIM(l_philoQueueSto[n]),
                  (void *)0, 0, /* no private stack */
                  (QEvent *)0);
  }
  // 后初始化table管理对象
  QActive_start(AO_Table, (uint8_t)(N_PHILO + 1),
                l_tableQueueSto, Q_DIM(l_tableQueueSto),
                (void *)0, 0, /* no private stack */
                (QEvent *)0);
  QF_run(); /* run the QF application */
  return 0;
}
```

#### 第六步：优雅的结束应用程序

在嵌入式系统中不需要考虑，一般就是无限运行直到复位。

### 在不同的平台运行 DPP

#### 在 DOS 上的 Vanilla 内核

```c
#include "qp_port.h"
#include "dpp.h"
#include "bsp.h"
...

/* Local-scope objects---------------------------------------------------*/
static void interrupt (*l_dosTmrISR)();
static void interrupt (*l_dosKbdISR)();
static uint32_t l_delay = 0UL; /* limit for the loop counter in busyDelay() */
#define TMR_VECTOR 0x08
#define KBD_VECTOR 0x09
/*......................................................................*/
// Turbo C++ 1.01编译器提供了一个扩展关健词 interrupt ，它允许你使用 C/C++ 编写ISR
void interrupt ISR_tmr(void)
{
  // 80x86处理器在进ISR时自动关中断，不过可以在ISR内手动开中断
  // 由8259A可编程中断控制器管理中断优先级
  QF_INT_UNLOCK(dummy); /* unlock interrupts */
  // QF_tick()内部会关中断，且使用了“无条件中断上锁和解锁”策略，
  // 不支持中断嵌套，为了防止死锁，需要提前开中断，在临界区外调用QF_tick()
  QF_tick();            /* call QF_tick() outside of critical section */
  QF_INT_LOCK(dummy);   /* lock interrupts again */
  // 中断结束 end-of-interrupt(EOI)指令被发往主 8259A ，因此它结束这个中断级别的优先级。
  outportb(0x20, 0x20); /* write EOI to the master 8259A PIC */
}
/*......................................................................*/
// 按键中断
void interrupt ISR_kbd(void)
{
  uint8_t key;
  uint8_t kcr;
  QF_INT_UNLOCK(dummy);                  /* unlock interrupts */
  key = inport(0x60);                    /*key scan code from the 8042 kbd controller */
  kcr = inport(0x61);                    /* get keyboard control register */
  outportb(0x61, (uint8_t)(kcr | 0x80)); /* toggle acknowledge bit high */
  outportb(0x61, kcr);                   /* toggle acknowledge bit low */
  if (key == (uint8_t)129)
  {                                          /* ESC key pressed? */
    static QEvent term = {TERMINATE_SIG, 0}; /* static event */
    QF_publish(&term);                       /* publish to all interested AOs */
  }
  QF_INT_LOCK(dummy);   /* lock interrupts again */
  outportb(0x20, 0x20); /* write EOI to the master 8259A PIC */
}
/*.......................................................................*/
void QF_onStartup(void)
{
  /* save the origingal DOS vectors ... */
  // 保存原始中断向量，在最后清理时恢复
  l_dosTmrISR = getvect(TMR_VECTOR);
  l_dosKbdISR = getvect(KBD_VECTOR);
  QF_INT_LOCK(dummy);
  // 配置自定义的中断向量
  setvect(TMR_VECTOR, &ISR_tmr);
  setvect(KBD_VECTOR, &ISR_kbd);
  QF_INT_UNLOCK(dummy);
}
/*.......................................................................*/
void QF_onCleanup(void)
{ /* restore the original DOS vectors ... */
  QF_INT_LOCK(dummy);
  // 恢复中断向量
  setvect(TMR_VECTOR, l_dosTmrISR);
  setvect(KBD_VECTOR, l_dosKbdISR);
  QF_INT_UNLOCK(dummy);
  _exit(0); /* exit to DOS */
}
/*.......................................................................*/
// 见[qvanilla.c 源文件](#qvanillac-源文件)
void QF_onIdle(void)
{                       /* called with interrupts LOCKED */
  QF_INT_UNLOCK(dummy); /* always unlock interrutps */
}
/*.......................................................................*/
void BSP_init(int argc, char *argv[])
{
  // 读取参数
  if (argc > 1)
  {
    // 忙等待时长
    l_delay = atol(argv[1]); /* set the delay counter for busy delay */
  }
  printf("Dining Philosopher Problem example"
         "\nQEP %s\nQF %s\n"
         "Press ESC to quit...\n",
         QEP_getVersion(),
         QF_getVersion());
}
/*......................................................................*/
// 用于手动调用延长RTC执行时间，方便调试
void BSP_busyDelay(void)
{
  uint32_t volatile i = l_delay;
  // 忙等待
  while (i-- > 0UL)
  { /* busy-wait loop */
  }
}
/*......................................................................*/
// 打印执行信息，仅被活动对象 Table 调用
void BSP_displyPhilStat(uint8_t n, char const *stat)
{
  printf("Philosopher %2d is %s\n", (int)n, stat);
}
/*......................................................................*/
void Q_onAssert(char const Q_ROM *const Q_ROM_VAR file, int line)
{ // 断言失败时终止
  QF_INT_LOCK(dummy); /* cut-off all interrupts */
  fprintf(stderr, "Assertion failed in %s, line %d", file, line);
  QF_stop();
}
```

#### 在 Cortex-M3 上的 Vanilla 内核

![vanillacortexm3](/assets/img/2022-07-27-quantum-platform-1/vanillacortexm3.jpg)

t（思考）， e（就餐）和 h（饥饿）

```c
#include "qp_port.h"
#include "dpp.h"
#include "bsp.h"
// 驱动库
#include "hw_ints.h"
.../* other Luminary Micro driver library include files */

/* Local-scope objects ---------------------------------------------------*/
static uint32_t l_delay = 0UL; /* limit for the loop counter in busyDelay() */

/*......................................................................*/
void ISR_SysTick(void)
{
  // Cortex-M3 进入 ISR 时，中断是解锁的，这就有别于80x86
  QF_tick(); /* process all armed time events */
  /* add any application-specific clock-tick processing, as needed */
}
...

/*......................................................................*/
// 板的初始化
void
BSP_init(int argc, char *argv[])
{
  (void)argc; /* unused: avoid the complier warning */
  (void)argv; /* unused: avoid the compiler warning */
              /* Set the clocking to run at 20MHz from the PLL. */
  SysCtlClockSet(SYSCTL_SYSDIV_10 | SYSCTL_USE_PLL | SYSCTL_OSC_MAIN | SYSCTL_XTAL_6MHZ);
  /* Enable the peripherals used by the application. */
  SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
  SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOC);
  /* Configure the LED, push button, and UART GPIOs as required. */
  GPIODirModeSet(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1,
                 GPIO_DIR_MODE_HW);
  GPIODirModeSet(GPIO_PORTC_BASE, PUSH_BUTTON, GPIO_DIR_MODE_IN);
  GPIODirModeSet(GPIO_PORTC_BASE, USER_LED, GPIO_DIR_MODE_OUT);
  GPIOPinWrite(GPIO_PORTC_BASE, USER_LED, 0);
  /* Initialize the OSRAM OLED display. */
  // 初始化显示驱动
  OSRAMInit(1);
  OSRAMStringDraw("Dining Philos", 0, 0);
  OSRAMStringDraw("0 ,1 ,2 ,3 ,4", 0, 1);
}
/*......................................................................*/
void BSP_displyPhilStat(uint8_t n, char const *stat)
{
  char str[2];
  str[0] = stat[0];
  str[1] = '\0';
  OSRAMStringDraw(str, (3 * 6 * n + 6), 1);
}
/*......................................................................*/
void BSP_busyDelay(void)
{
  uint32_t volatile i = l_delay;
  while (i-- > 0UL)
  { /* busy-wait loop */
  }
}
/*......................................................................*/
void QF_onStartup(void)
{
  /* Set up and enable the SysTick timer. It will be used as a reference
   * for delay loops in the interrupt handlers. The SysTick timer period
   * will be set up for BSP_TICKS_PER_SEC.
   */
  // 设置节拍速率
  SysTickPeriodSet(SysCtlClockGet() / BSP_TICKS_PER_SEC);
  SysTickEnable();
  // 配置节拍中断优先级，0xC0为倒数第二低的优先级
  IntPrioritySet(FAULT_SYSTICK, 0xC0); /* set the priority of SysTick */
  SysTickIntEnable();                  /* Enable the SysTick interrupts */
  QF_INT_UNLOCK(dummy);                /* set the interrupt flag in PRIMASK */
}
/*......................................................................*/
// 没有操作系统，不需要清理，退出直接复位
void QF_onCleanup(void)
{
}
/*......................................................................*/
void QF_onIdle(void)
{ /* entered with interrupts LOCKED, see NOTE01 */
  /* toggle the User LED on and then off, see NOTE02 */
  GPIOPinWrite(GPIO_PORTC_BASE, USER_LED, USER_LED); /* User LED on */
  GPIOPinWrite(GPIO_PORTC_BASE, USER_LED, 0);        /* User LED off */
#ifdef NDEBUG
  /* Put the CPU and peripherals to the low-power mode.
   * you might need to customize the clock management for your application,
   * see the datasheet for your particular Cortex-M3 MCU.
   */
  // 低功耗模式
  __asm("WFI"); /* Wait-For-Interrupt */
#endif
  QF_INT_UNLOCK(dummy); /* always unlock the interrupts */
}
/*......................................................................*/
void Q_onAssert(char const Q_ROM *const Q_ROM_VAR file, int line)
{
  (void)file;         /* avoid compiler warning */
  (void)line;         /* avoid compiler warning */
  QF_INT_LOCK(dummy); /* make sure that all interrupts are disabled */
  // 实际使用要去掉这个循环
  for (;;)
  { /* NOTE: replace the loop with reset for the final version */
  }
}
/* error routine that is called if the Luminary library encounters an error */
void __error__(char *pcFilename, unsigned long ulLine)
{
  Q_onAssert(pcFilename, ulLine);
}
```

#### uC/OS-II

![ucos2dpp](/assets/img/2022-07-27-quantum-platform-1/ucos2dpp.jpg)

_main.c_：

```c
#include "qp_port.h"
#include "dpp.h"
#include "bsp.h"
/* Local-scope objects ---------------------------------------------------*/
... 
static OS_STK l_philoStk[N_PHILO][256]; /* stacks for the Philosophers */
static OS_STK l_tableStk[256];              /* stack for the Table */
static OS_STK l_ucosTaskStk[256];           /* stack for the ucosTask */
/*........................................................................*/
int main(int argc, char *argv[])
{
  ... 
  for (n = 0; n < N_PHILO; ++n)
  {
    // 需要为每个活动对象分配私有堆栈
    QActive_start(AO_Philo[n], (uint8_t)(n + 1),
                  l_philoQueueSto[n], Q_DIM(l_philoQueueSto[n]),
                  l_philoStk[n], sizeof(l_philoStk[n]), (QEvent *)0);
  }
  QActive_start(AO_Table, (uint8_t)(N_PHILO + 1),
                l_tableQueueSto, Q_DIM(l_tableQueueSto),
                l_tableStk, sizeof(l_tableStk), (QEvent *)0);
  /* create a uC/OS-II task to start interrupts and poll the keyboard */
  // 比其他系统多加了个任务，见下面的bsp.c
  OSTaskCreate(&ucosTask,
               (void *)0, /* pdata */
               &l_ucosTaskStk[Q_DIM(l_ucosTaskStk) - 1],
               0); /* the highest uC/OS-II priority */
  QF_run();        /* run the QF application */
  return 0;
}
```

_bsp.c_:

```c
#include "qp_port.h"
#include "dpp.h"
#include "bsp.h"
#include "video.h"
/*.......................................................................*/
void ucosTask(void *pdata)
{
  (void)pdata;    /* avoid the compiler warning about unused parameter */
  QF_onStartup(); /* start interrupts including the clock tick, NOTE01 */
  for (;;)
  {
    // for循环里要加阻塞转让控制权
    OSTimeDly(OS_TICKS_PER_SEC / 10); /* sleep for 1/10 s */
    if (kbhit())
    { /* poll for a new keypress */
      uint8_t key = (uint8_t)getch();
      // 检测是否按了 ESC 键
      if (key == 0x1B)
      { /* is this the ESC key? */
        // 发布静态的 TERMINATE 事件
        QF_publish(Q_NEW(QEvent, TERMINATE_SIG));
      }
      else
      { /* other key pressed */
        Video_printNumAt(30, 13 + N_PHILO, VIDEO_FGND_YELLOW, key);
      }
    }
  }
}
/*.......................................................................*/
// 节拍中断，因为使用“保存和恢复中断状态”策略支持中断嵌套，进入ISR后不需要开中断
void OSTimeTickHook(void)
{
  QF_tick();
  /* add any application-specific clock-tick processing, as needed */
}
/*.......................................................................*/
// Idle进入低功耗模式
void OSTaskIdleHook(void){
    /* put the MCU to sleep, if desired */
}
...
```

#### Linux

![linuxddp](/assets/img/2022-07-27-quantum-platform-1/linuxddp.jpg)

_bsp.c_:

```c
#include "qp_port.h"
#include "dpp.h"
#include "bsp.h"
#include <sys/select.h>
... 
Q_DEFINE_THIS_FILE
/* Local objects ---------------------------------------------------------*/
// Linux控制台默认配置不允许异步接收用户按键，需要修改控制台配置，这个变量备份了修改前的配置
static struct termios l_tsav; /* structure with saved terminal attributes */
static uint32_t l_delay;      /* limit for the loop counter in busyDelay() */
/*.......................................................................*/
// 异步监控控制台输入的线程，按下ESC终止应用
static void *idleThread(void *me)
{ /* the expected P-Thread signature */
  for (;;)
  {
    struct timeval timeout = {0}; /* timeout for select() */
    fd_set con;                   /* FD set representing the console */
    FD_ZERO(&con);
    FD_SET(0, &con);
    timeout.tv_usec = 8000;
    /* sleep for the full tick or until a console input arrives */
    // 使用select()作为阻塞机制
    if (0 != select(1, &con, 0, 0, &timeout))
    { /* any descriptor set? */
      char ch;
      read(0, &ch, 1);
      if (ch == '\33')
      { /* ESC pressed? */
        // 按ESC发布退出事件
        QF_publish(Q_NEW(QEvent, TERMINATE_SIG));
      }
    }
  }
  return (void *)0; /* return success */
}
/*.......................................................................*/
void BSP_init(int argc, char *argv[])
{
  printf("Dining Philosopher Problem example"
         "\nQEP %s\nQF %s\n"
         "Press ESC to quit...\n",
         QEP_getVersion(),
         QF_getVersion());
  if (argc > 1)
  {
    l_delay = atol(argv[1]); /* set the delay from the argument */
  }
}
/*.......................................................................*/
void QF_onStartup(void)
{                     /* startup callback */
  struct termios tio; /* modified terminal attributes */
  pthread_attr_t attr;
  struct sched_param param;
  pthread_t idle;
  // 修改前保存终端属性
  tcgetattr(0, &l_tsav);           /* save the current terminal attributes */
  tcgetattr(0, &tio);              /* obtain the current terminal attributes */
  tio.c_lflag &= ~(ICANON | ECHO); /* disable the canonical mode & echo */
  // 关闭终端属性中的不允许异步输入模式
  tcsetattr(0, TCSANOW, &tio);     /* set the new attributes */
  /* SCHED_FIFO corresponds to real-time preemptive priority-based scheduler
   * NOTE: This scheduling policy requires the superuser priviledges
   */
  pthread_attr_init(&attr);
  // 将idle线程配置为SCHED_FIFO调度策略
  pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
  // 将idle线程优先级配置为最低
  param.sched_priority = sched_get_priority_min(SCHED_FIFO);
  pthread_attr_setschedparam(&attr, &param);
  pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
  // 创建idle线程
  if (pthread_create(&idle, &attr, &idleThread, 0) != 0)
  {
    /* Creating the p-thread with the SCHED_FIFO policy failed.
     * Most probably this application has no superuser privileges,
     * so we just fall back to the default SCHED_OTHER policy
     * and priority 0.
     */
    // 如果创建失败就尝试另外的配置重新创建
    pthread_attr_setschedpolicy(&attr, SCHED_OTHER);
    param.sched_priority = 0;
    pthread_attr_setschedparam(&attr, &param);
    Q_ALLEGE(pthread_create(&idle, &attr, &idleThread, 0) == 0);
  }
  pthread_attr_destroy(&attr);
}
/*.......................................................................*/
void QF_onCleanup(void)
{ /* cleanup callback */
  printf("\nBye! Bye!\n");
  tcsetattr(0, TCSANOW, &l_tsav); /* restore the saved terminal attributes */
  QS_EXIT();                      /* perform the QS cleanup */
}
/*.......................................................................*/
void BSP_displyPhilStat(uint8_t n, char const *stat)
{
  printf("Philosopher %2d is %s\n", (int)n, stat);
}
/*.......................................................................*/
void BSP_busyDelay(void)
{
  uint32_t volatile i = l_delay;
  while (i-- > 0UL)
  {
  }
}
/*.......................................................................*/
void Q_onAssert(char const Q_ROM *const Q_ROM_VAR file, int line)
{
  fprintf(stderr, "Assertion failed in %s, line %d", file, line);
  QF_stop();
}
```

> 相关文章：[select()用法](/posts/operating-systems-27/#重要-apiselect或-poll)

### 调整事件队列和事件池的大小

`开发阶段`使用`超大`的队列、池和堆栈，仅在产品开发的`末期`才开始`缩小`它们。

#### 调整事件队列的大小

事件队列的要求：

```plaintext
平均事件产生速率 <P(t)> 不高于平均事件消耗速率 <C(t)>
```
  
一旦 `P(t)` 过大导致事件队列`满`，QP 会视其为`异常`，而不是`阻塞`生产者或`丢弃`事件

**解决方法**：

- 运行时评估：

  - 运行程序一段时间并检查 `nMin` 的值，评估事件队列大小是否合理

- 静态分析

  - 事件队列的大小取决于活动对象的`优先级`

    一般的，`优先级`越高，必需的事件队列越短。因为一旦事件队列被填充，内核会`尽快`调度该活动对象线程运行处理事件

  - 队列大小取决于最长的 `RTC` 步骤持续的`时间`

    处理越快，必需的事件队列越短。理想情况是，某个给定活动对象的所有 RTC 步骤都只需要相同的 CPU 周期来完成。

  - 任何相关的事件生产都能增加队列的大小

    有时候 ISR 或活动对象在一个 RTC 步骤内生产多个事件实例。应该避免短时间内产生较多事件

#### 调整事件池的大小

取决于事件种类，和活动对象数量，事件实例的可重用性，事件池尺寸种类

#### 系统集成

QF 允许你在软件的`任何地方`发送或发行事件，而不限于仅从活动对象。比如可以在设备`驱动程序`中发布事件。

设备应该被视为一个`共享`的资源，对它的存取`限制`到仅一个活动对象内，避免共享资源竞争导致的各种问题。可以用一个活动对象封装多个设备。

## 事件驱动型系统的软件追踪

![tracemodel](/assets/img/2022-07-27-quantum-platform-1/tracemodel.jpg)

上图展示了软件追踪的一个典型设置

嵌入式目标系统在运行被监测的代码，它在目标系统的 RAM 缓存区记录追踪数据。追踪数据通过一个数据连接被从这个缓存区送给一个主机，它存储、显示和分析这些信息。这个配置意味着软件追踪总是需要 2 个构件：

- 用来收集和发送追踪数据的[目标系统驻留构件](#qs-目标系统驻留构件)
- 用来接收，解压，可视化和分析这些数据的[主机驻留构件](#qspy-主机应用程序)。

### QS 目标系统驻留构件

![qstarget](/assets/img/2022-07-27-quantum-platform-1/qstarget.jpg)

- 侵入性小 - 数据格式化工作被从目标系统里移到主机执行
- 数据记录和发送数据给主机是分隔的，例如在目标 CPU 的空闲循环处传输数据。减少了发送数据的开销
- 支持数据压缩，如数据字典
- 带级别过滤器
- 带可配精度时间戳
- 探测传输错误并重传机制（高级数据连接控制协议 [High Level Data Link Control, HLDLC]）
- 轻量级传输 API

#### QS 源代码的组织

```console
<qp>\qpc\ - QP/C root directory (<qp>\qpcpp for QP/C++)
    |
    +-include/ - QP platform-independent header files
    | +-qs.h - QS platform-independent active interface
    | +-qs_dummy.h - QS platform-independent inactive interface
    |
    +-qs/ - QS target component
    | +-source/ - QS platform-independent source code (*.C files)
    | | +-qs_pkg.h - internal, packet-scope interface for QS implementation
    | | +-qs.c - internal ring buffer and formatted output functions
    | | +-qs_.c - definition of basic unformatted output functions
    | | +-qs_blk.c - definition of block-oriented interface QS_getBlock()
    | | +-qs_byte.c - definition of byte-oriented interface QS_getByte()
    | | +-qs_f32.c - definition of 32-bit floating point output QS_f32()
    | | +-qs_f64.c - definition of 64-bit floating point output QS_f64()
    | | +-qs_mem.c - definition of memory-block output
    | | +-qs_str.c - definition of zero-terminated string output
    |
    +-ports\ - Platform-specific QP ports
    | +- . . .
    +-examples\ - Platform-specific QP examples
    | +- . . .<qp>\qpc\ - QP/C root directory (<qp>\qpcpp for QP/C++)
    |
    +-include/ - QP platform-independent header files
    | +-qs.h - QS platform-independent active interface
    | +-qs_dummy.h - QS platform-independent inactive interface
    |
    +-qs/ - QS target component
    | +-source/ - QS platform-independent source code (*.C files)
    | | +-qs_pkg.h - internal, packet-scope interface for QS implementation
    | | +-qs.c - internal ring buffer and formatted output functions
    | | +-qs_.c - definition of basic unformatted output functions
    | | +-qs_blk.c - definition of block-oriented interface QS_getBlock()
    | | +-qs_byte.c - definition of byte-oriented interface QS_getByte()
    | | +-qs_f32.c - definition of 32-bit floating point output QS_f32()
    | | +-qs_f64.c - definition of 64-bit floating point output QS_f64()
    | | +-qs_mem.c - definition of memory-block output
    | | +-qs_str.c - definition of zero-terminated string output
    |
    +-ports\ - Platform-specific QP ports
    | +- . . .
    +-examples\ - Platform-specific QP examples
    | +- . . .
```

QS 源文件通常在`每个文件`里只包含**一个函数**或**一个数据结构**。这种设计的目的在于把 QS 部署成一个`精细粒度`的库，你可以把它静态的和里的应用程序链接。精细粒度意味着 QS 库由许多小的松散耦合的模块（目标文件）组成，而不是由一个包含所有功能的单一模块组成。

#### QS 的平台无关头文件 qs.h 和 qs_dummy.h

- `qs.h` - QS 功能的所有“活动”接口
- `qs_dummy.h` - QS 功能的所有“不活动”接口

_qs.h_:

```c
#ifndef qs_h
#define qs_h
#ifndef Q_SPY
#error "Q_SPY must be defined to include qs.h"
#endif /* Q_SPY */

// 枚举QS记录类型，相当于日志标记
enum QSpyRecords
{
    /* QEP records */
    QS_QEP_STATE_ENTRY, /**< a state was entered */
    QS_QEP_STATE_EXIT,  /**< a state was exited */
    ...
    /* QF records */
    QS_QF_ACTIVE_ADD,         /**< an AO has been added to QF (started) */
    QS_QF_ACTIVE_REMOVE,      /**< an AO has been removed from QF (stopped) */
    QS_QF_ACTIVE_SUBSCRIBE,   /**< an AO subscribed to an event */
    QS_QF_ACTIVE_UNSUBSCRIBE, /**< an AO unsubscribed to an event */
    QS_QF_ACTIVE_POST_FIFO,   /**< an event was posted (FIFO) directly to AO */
    ...
    /* QK records */
    QS_QK_MUTEX_LOCK,   /**< the QK mutex was locked */
    QS_QK_MUTEX_UNLOCK, /**< the QK mutex was unlocked */
    QS_QK_SCHEDULE,     /**< the QK scheduled a new task to execute */
    ...
    /* Miscellaneous QS records */
    QS_SIG_DICTIONARY, /**< signal dictionary entry */
    QS_OBJ_DICTIONARY, /**< object dictionary entry */
    QS_FUN_DICTIONARY, /**< function dictionary entry */
    QS_ASSERT,         /** assertion failed */
    ...
    /* User records */
    QS_USER /**< the first record available for user QS records */
    // 从QS_USER开始可以自定义记录类型
};
...
/* Macros for adding QS instrumentation to the client code .................*/
//所有 QS 服务被定义为预处理器的宏。这样，即使软件追踪被禁止，你也可以把它们留在代码中。
#define QS_INIT(arg_) QS_onStartup(arg_)
#define QS_EXIT() QS_onCleanup()
// 全局 QS 过滤器，它把某个给定 QS 追踪记录打开或关闭。
#define QS_FILTER_ON(rec_) QS_filterOn(rec_)
#define QS_FILTER_OFF(rec_) QS_filterOff(rec_)
// 本地 QS 过滤器。这个过滤器允许你有选择的追踪那些特定的状态机对象。
#define QS_FILTER_SM_OBJ(obj_) (QS_smObj_ = (obj_))
#define QS_FILTER_AO_OBJ(obj_) (QS_aoObj_ = (obj_))
#define QS_FILTER_MP_OBJ(obj_) (QS_mpObj_ = (obj_))
#define QS_FILTER_EQ_OBJ(obj_) (QS_eqObj_ = (obj_))
#define QS_FILTER_TE_OBJ(obj_) (QS_teObj_ = (obj_))
#define QS_FILTER_AP_OBJ(obj_) (QS_apObj_ = (obj_))
/* Macros to generate user QS records (formatted data output) ..............*/
// 互斥锁，BEGIN上锁，END解锁，用于保护QS 追踪缓存
#define QS_BEGIN(rec_, obj_) ...
#define QS_END() ...
// 不上锁（比如在临界区内再调用就不需要关中断了）
#define QS_BEGIN_NOLOCK(rec_, obj_) ...
#define QS_END_NOLOCK() ...
    ...
#define QS_I8 (w_, d_) QS_u8((uint8_t)(((w_) << 4)) | QS_I8_T, (d_))
#define QS_U8 (w_, d_) QS_u8((uint8_t)(((w_) << 4)) | QS_U8_T, (d_))
#define QS_I16(w_, d_) QS_u16((uint8_t)(((w_) << 4)) | QS_I16_T, (d_))
#define QS_U16(w_, d_) QS_u16((uint8_t)(((w_) << 4)) | QS_U16_T, (d_))
#define QS_I32(w_, d_) QS_u32((uint8_t)(((w_) << 4)) | QS_I32_T, (d_))
#define QS_U32(w_, d_) QS_u32((uint8_t)(((w_) << 4)) | QS_U32_T, (d_))
#define QS_F32(w_, d_) QS_f32((uint8_t)(((w_) << 4)) | QS_F32_T, (d_))
#define QS_F64(w_, d_) QS_f64((uint8_t)(((w_) << 4)) | QS_F64_T, (d_))
#define QS_STR(str_) QS_str(str_)
#define QS_STR_ROM(str_) QS_str_ROM(str_)
#define QS_MEM(mem_, size_) QS_mem((mem_), (size_))
#if (QS_OBJ_PTR_SIZE == 1)
#define QS_OBJ(obj_) QS_u8(QS_OBJ_T, (uint8_t)(obj_))
#elif (QS_OBJ_PTR_SIZE == 2)
#define QS_OBJ(obj_) QS_u16(QS_OBJ_T, (uint16_t)(obj_))
#elif (QS_OBJ_PTR_SIZE == 4)
#define QS_OBJ(obj_) QS_u32(QS_OBJ_T, (uint32_t)(obj_))
#else
#define QS_OBJ(obj_) QS_u32(QS_OBJ_T, (uint32_t)(obj_))
#endif
#if (QS_FUN_PTR_SIZE == 1)
#define QS_FUN(fun_) QS_u8(QS_FUN_T, (uint8_t)(fun_))
#elif (QS_FUN_PTR_SIZE == 2)
    ...
#endif
#if (Q_SIGNAL_SIZE == 1)
#define QS_SIG(sig_, obj_)   \
    QS_u8(QS_SIG_T, (sig_)); \
    QS_OBJ_(obj_)
#elif (Q_SIGNAL_SIZE == 2)
    ...
#endif
/* Dictionary records ......................................................*/
#define QS_OBJ_DICTIONARY(obj_) ...
#define QS_FUN_DICTIONARY(fun_) ...
#define QS_SIG_DICTIONARY(sig_, obj_) ...
    ...
/* Macros used only internally in the QP code ..............................*/
#define QS_BEGIN_(rec_, obj_) ...
#define QS_END_() ...
#define QS_BEGIN_NOLOCK_(rec_, obj_) ...
#define QS_END_NOLOCK_() ...
/* QS functions for managing the QS trace buffer ...........................*/
void
QS_initBuf(uint8_t sto[], uint32_t stoSize);
uint16_t QS_getByte(void);                     /* byte-oriented interface */
uint8_t const *QS_getBlock(uint16_t *pNbytes); /* block-oriented interface */
/* QS callback functions, typically implemented in the BSP .................*/
uint8_t QS_onStartup(void const *arg);
void QS_onCleanup(void);
void QS_onFlush(void);
QSTimeCtr QS_onGetTime(void);
#endif /* qs_h */
```

_qs_dummy.h_:

```c
#ifndef qs_dummy_h
#define qs_dummy_h
#ifdef Q_SPY
#error "Q_SPY must NOT be defined to include qs_dummy.h"
#endif
#define QS_INIT(arg_) ((uint8_t)1)
#define QS_EXIT() ((void)0)
#define QS_DUMP() ((void)0)
#define QS_FILTER_ON(rec_) ((void)0)
#define QS_FILTER_OFF(rec_) ((void)0)
#define QS_FILTER_SM_OBJ(obj_) ((void)0)
...
#define QS_GET_BYTE(pByte_) ((uint16_t)0xFFFF)
#define QS_GET_BLOCK(pSize_) ((uint8_t *)0)
#define QS_BEGIN(rec_, obj_) \
    if (0)                   \
    {
#define QS_END() }
#define QS_BEGIN_NOLOCK(rec_, obj_) QS_BEGIN(rec_, obj_)
#define QS_END_NOLOCK() QS_END()
#define QS_I8(width_, data_) ((void)0)
#define QS_U8(width_, data_) ((void)0)
    ...
#define QS_SIG(sig_, obj_) ((void)0)
#define QS_OBJ(obj_) ((void)0)
#define QS_FUN(fun_) ((void)0)
#define QS_SIG_DICTIONARY(sig_, obj_) ((void)0)
#define QS_OBJ_DICTIONARY(obj_) ((void)0)
#define QS_FUN_DICTIONARY(fun_) ((void)0)
#define QS_FLUSH() ((void)0)
    ...
#endif
```

#### QS 的临界区

QS 目标构件必须保护`追踪缓存`的内部完整性，它在并发运行的任务和中断之间被共享，所以需要被视为`临界区`

当 QS 探测 `QF 临界区`的宏 QF_INT_LOCK() ， QF_INT_UNLOCK() 被定义时， QS 使用了**这个定义**作为它自己的临界区。

然而，当你在**没有** QF 实时框架的情况下使用 QS 时，你需要在`qs_port.h`头文件里定义 QS 的`平台相关`的中断上锁 / 解锁策略

> QS_BEGIN 和 QS_END()就是利用的`qs_port.h`里定义的锁宏

自定义的锁*qs_port.h*:

```c
#define QS_INT_KEY_TYPE . . .
    #define QS_INT_LOCK(key_) . . .
    #define QS_INT_UNLOCK(key_) . . .
```

#### QS 记录的一般结构

QS 在分离的被称为 `QS“追踪记录”` 的小块里记录追踪数据。

```c
QS_BEGIN_xxx(record_type) /* trace record begin */
    QS_yyy(data); /* QS data element */
    QS_zzz(data); /* QS data element */
    . . . /* QS data element */
QS_END_xxx() /* trace record end */
```

- `QS_BEGIN/QS_END()`: 在记录的开始处`上锁`中断，在记录的结尾`解锁`中断。
- `QS_BEGIN_NOLOCK()/QS_END_NOLOCK()`: 用来创建应用程序相关的记录而`不需进入`临界区，它们仅能被用于某个`临界区内部`。

> TODO:NOLOCK 有什么意义

#### QS 的过滤器

##### 全局开/关过滤器

预定义的类型就是`qs.h`中的`QSpyRecords`枚举型，通过过滤器启用/禁用对应类型的日志记录

全局开 / 关过滤器使用一个位掩码数据`QS_glbFilter_[]`而高效的实现，这个数组的`每一位`代表一个追踪记录。当前 QS*glbFilter*[]包含 32 字节，总共 32×8 位可以代表 `256` 个不同的追踪记录。其中大约四分之一已经被用于预定义的 QP 追踪记录。剩下四分之三可以用于应用程序。

```c
#define QS_BEGIN(rec_, obj_) \
    if (((QS_glbFilter_[(uint8_t)(rec_) >> 3U] \
        & (1U << ((uint8_t)(rec_) & 7U))) != 0) . . .\
```

`rec_`表示记录类型枚举 id，从 0 到 255，右移三位表示整除 8，因为最后三位被右移掉了，相当于把余数抹除了。这样`QS_glbFilter_[]`就能定位到该 id 对应的字节,如 255 对应第 32 个字节，46 对应第 5 个字节。然后再以上一步余数（和 7 进行与操作）为`mask`找到对应的位，代码中就是将 1 左移余数值生成一个字节 8 位里的某个 mask。如 46 余数是 6，1 左移 6 位，mask 就是 0x40，找到第 5 个字节中的 0x40 mask 对应的位

> 上述表达式中需要重复计算的部分可以作为编译时常数值。 如(QS*glbFilter*[5] & 0x40) != 0)

> 这里将 QS*glbFilter*定义为单字节数组而不是多字节数组是为了兼容性。

- 宏`QS_FILTER_ON(rec_)`: 打开和记录 rec\_ 对应的位
- 宏`QS_FILTER_OFF(rec_)`: 关闭和记录 rec\_ 相对应的位

##### 本地过滤器

以对象为单位管理过滤器。如只开启对某个活动对象的打印，关闭其他的

对象类型有：状态机、活动对象、内存池、事件队列、时间事件、一般的应用程序对象

| 本地过滤器                        | 对象类型           | 例子                                       | 适用的 QS 记录                                                                                                                                                                                        |
| :-------------------------------- | :----------------- | :----------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| QS_FILTER_SM_OBJ()                | 状态机             | QS_FILTER_SM_OBJ(<br>&l_qhsmTst);          | QS_QEP_STATE_EMPTY,<br>QS_QEP_STATE_ENTRY,<br>QS_QEP_STATE_EXIT,<br>QS_QEP_STATE_INIT,<br>QS_QEP_INIT_TRAN,<br>QS_QEP_INTERN_TRAN,<br>QS_QEP_TRAN,<br>QS_QEP_IGNORED                                  |
| QS_FILTER_AO_OBJ()                | 活动对象 t         | QS_FILTER_AO_OBJ(<br>&l_philo[3]);         | QS_QF_ACTIVE_ADD,<br>QS_QF_ACTIVE_REMOVE,<br>QS_QF_ACTIVE_SUBSCRIBE,<br>QS_QF_ACTIVE_UNSUBSCRIBE,<br>QS_QF_ACTIVE_POST_FIFO,<br>QS_QF_ACTIVE_POST_LIFO,<br>QS_QF_ACTIVE_GET,<br>QS_QF_ACTIVE_GET_LAST |
| QS_FILTER_MP_OBJ()<br>( 见注释 1) | 内存池             | QS_FILTER_MP_OBJ(<br>l_regPoolSto);        | QS_QF_MPOOL_INIT,<br>QS_QF_MPOOL_GET<br>QS_QF_MPOOL_PUT                                                                                                                                               |
| QS_FILTER_EQ_OBJ()<br>( 见注释 2) | 事件队列           | QS_FILTER_EQ_OBJ(<br>l_philQueueSto[3]);   | QS_QF_EQUEUE_INIT,<br>QS_QF_EQUEUE_POST_FIFO,<br>QS_QF_EQUEUE_POST_LIFO,<br>QS_QF_EQUEUE_GET,<br>QS_QF_EQUEUE_GET_LAST                                                                                |
| QS_FILTER_TE_OBJ()                | 时间事件           | QS_FILTER_TE_OBJ(<br>&l_philo[3].timeEvt); | QS_QF_TICK,<br>QS_QF_TIMEEVT_ARM,<br>QS_QF_TIMEEVT_AUTO_DISARM,<br>QS_QF_TIMEEVT_DISARM_ATTEMPT,<br>QS_QF_TIMEEVT_DISARM,<br>QS_QF_TIMEEVT_REARM,<br>QS_QF_TIMEEVT_POST,<br>QS_QF_TIMEEVT_PUBLISH     |
| QS_FILTER_AP_OBJ()                | 一般的应用程序对象 | QS_FILTER_AP_OBJ(<br>&myAppObject);        | 以 QS_USER 开始的应用程序相关的记录                                                                                                                                                                   |

#### QS 数据协议

类似 HDLC 协议

QS 协议被特别设计用来简化在目标系统里的数据管理的开销，同时允许探测到任何由于追踪缓存不足造成的`数据丢失`。这个协议不但可以探测到在数据和其他错误之间的缺陷，而且允许在任何错误后立即`重新同步`，把数据丢失减到最小。

![qstransport](/assets/img/2022-07-27-quantum-platform-1/qstransport.jpg)

帧序号+记录类型 ID+数据域+校验码+帧尾标记

##### 透明

就是对帧内出现的帧尾标记字节(0x7E)做`转义`

使用 0x7D 做转义前导符，对 0x7E 做转义，当然 0x7D 本身也要转义，方法为对要转义的字符和 0x20 异或

一个例子也许可以更清楚的说明这点。假设以下的追踪记录需要被插入追踪缓存（透明字节用粗
体字显示）：

```plaintext
Record ID = 0x7D, Record Data = 0x7D 0x08 0x01
```

假设当前的帧顺序号码是 0x7E，校验和通过计算下列字节而得到：

```plaintext
Checksum == (uint8_t)(~(0x7E + 0x7D + 0x7D + 0x08 + 0x01)) == 0x7E
```

实际被插入到 QS 追踪缓存的帧如下：

```plaintext
0x7D 0x5E 0x7D 0x5D 0x7D 0x5D 0x08 0x01 0x7D 0x5E 0x7E
```

##### 大小端

QS 传输协议规定了数据是小端（ little-endian ）

高位高地址，低位低地址，优先传输低位

#### QS 追踪缓存区

追踪缓存区内保存的就是`HDLC`帧

特点：

- 第一，在追踪缓存使用 HDLC 格式的数据，允许把向追踪缓存插入数据和从指针缓存已走数据解除耦合。可以按个数丢弃，**无需考虑边界(自动检测边界)**
- 第二，在缓存里使用格式化的数据能够使用“最后的是最好的”追踪策略。因为`校验码`可以检测**覆盖导致的错误**，自动丢弃被覆盖的数据

##### 初始化 QS 追踪缓存区 QS_initBuf()

需要为 QS 追踪缓存分配`静态存储`，当日志数据量大时，缓存也要大，防止绕尾破坏数据（虽然该错误能被检测和处理，但数据还是丢了）

```c
#ifdef Q_SPY /* define QS callbacks */
uint8_t QS_onStartup(void const *arg)
{
    static uint8_t qsBuf[2 * 1024]; /* buffer for Quantum Spy */
    QS_initBuf(qsBuf, sizeof(qsBuf));

    // Initialize the QS data link
    ...

    return success; /* return 1 for success and 0 for failure */
}
#endif
```

#### 面向字节的接口： QS_getByte()

可以在任何时候从缓存移走一个字节

函数 QS_getByte() 不上锁中断，也不是可重入的。也就是用的时候要应用自己加锁

TODO：为什么要这么设计，函数体内关中断不行吗

```c
QF_INT_LOCK(igonre);
while ((fifo != 0) && ((b = QS_getByte()) != QS_EOD)) /* get the next byte */
{
    QF_INT_UNLOCK(igonre);
    // 从缓存读取(移走)一个字节放入TX发送缓存
    outportb(l_base + 0, (uint8_t)b); /* insert byte into TX FIFO */
    --fifo;

    QF_INT_LOCK(igonre);
}
QF_INT_UNLOCK(igonre);
```

#### 面向块的接口： QS_getBlock()

获取一个块，fifo 入参表示希望获取的长度，出参表示实际获得长度。函数返回块起始指针

需要应用加锁

返回长度小于输入长度时表示缓存读尽或还有回绕，再读一次，如果长度是 0 表示缓存读尽

```c
uint16_t fifo = UART_16550_TXFIFO_DEPTH; /* 16550 Tx FIFO depth */
uint8_t const *block;
QF_INT_LOCK(dummy);
block = QS_getBlock(&fifo); /* try to get next block to transmit */
QF_INT_UNLOCK(dummy);
while (fifo-- != 0) { /* any bytes in the block? */
    outportb(l_uart_base + 0, *block++);
}
```

#### 字典追踪记录

当你编译并把应用程序映像装入目标系统后，关于对象名，函数名和信号名的符号信息被从代码中剥离。

QS 提供了专门的追踪记录，特别被设计用来在追踪记录本身包含目标代码的`符号信息`。用于 QSPY 主机应用程序的包含在追踪记录里的`字典记录`，非常类似传统的`单步调试器`使用的嵌入在目标文件里的`符号信息`。

QS 支持 3 类字典追踪记录：对象字典，函数字典和信号字典。

- 对象字典

  用宏 `QS_OBJ_DICTONARY()` 来生成对象字典，它把对象在内存的`地址`和它的`符号名`联合起来。

  ```c
  // 通过活动对象0的内存地址获取对象的名字
  QS_OBJ_DICTIONARY(&l_philo[0]);
  ```

- 函数字典

  使用宏 `QS_FUN_DICTONARY()` 来生成函数字典，它把`函数`在内存的`地址`和它的`符号名`联系起来。

- 信号字典

  使用宏 `QS_SIG_DICTONARY()` 来生成信号字典，它把事件信号的`数值`和`状态机对象`这两者和信号的`符号名`联系起来。

  同时使用信号的数值和状态对象的理由是，仅使用信号值不能有效的把符号化信号区分出来。只有全局发行的信号在系统范围内才是唯一的。其他信号，仅在本地使用，在系统的不同状态机里有完全不同的意义。

#### 应用程序相关的 QS 追踪记录

应用程序相关的 QS 记录允许你从应用层代码生成追踪信息。你可以把应用相关的记录想像成和 `printf()` 等效的功能，但是它有更少的开销。

```c
QS_BEGIN(MY_QS_RECORD, myObjectPointer) /* trace record begin */
  QS_STR("Hello"); /* string data element */
  QS_U8(3, n); /* uint8_t data, 3-decimal digits format */
  . . . /* QS data */
  QS_MEM(buf, sizeof(buf)); /* memory block of a given size */
QS_END() /* trace record end */
```

由 QS_BEGIN 开始，QS_BEGIN 自带上锁功能，参数为一个 QS 记录类型 MY_QS_RECORD（用于[全局过滤器](#全局开关过滤器)）和一个对象指针 myObjectPointer（用于[本地过滤器](#本地过滤器)）

![qsapp](/assets/img/2022-07-27-quantum-platform-1/qsapp.jpg)

上图是上述示例代码的表示

#### 移植和配置 QS

修改 qs_port.h

### QSPY 主机应用程序

使用 C++实现，它的用途仅是提供 QS 数据语法分析，存储，并把数据输出到其他强大的工具比如 MATLAB。

### 向 MATLAB 输出追踪数据

略

### 向 QP 应用程序添加 QS 软件追踪

```c
#include "qp_port.h"
#include "dpp.h"
#include "bsp.h"
/* Local-scope objects -----------------------------------------------------*/
static QEvent const *l_tableQueueSto[N_PHILO];
static QEvent const *l_philoQueueSto[N_PHILO][N_PHILO];
static QSubscrList l_subscrSto[MAX_PUB_SIG];
static union SmallEvent
{
    void *min_size;
    TableEvt te;
    /* other event types to go into this pool */
} l_smlPoolSto[2 * N_PHILO]; /* storage for the small event pool */
/*..........................................................................*/
int main(int argc, char *argv[])
{
    uint8_t n;
    Philo_ctor();         /* instantiate all Philosopher active objects */
    Table_ctor();         /* instantiate the Table active object */
    BSP_init(argc, argv); /* initialize the BSP (including QS) */
    QF_init();            /* initialize the framework and the underlying RT kernel */
    /* setup the QS filters ... */
    // 全局过滤器默认全禁止，这里全开一下
    QS_FILTER_ON(QS_ALL_RECORDS);
    // 关闭一些打印较频繁的记录类型（全局过滤器）
    QS_FILTER_OFF(QS_QF_INT_LOCK);
    QS_FILTER_OFF(QS_QF_INT_UNLOCK);
    QS_FILTER_OFF(QS_QK_SCHEDULE);
    /* provide object dictionaries... */
    // 创建对象字典
    QS_OBJ_DICTIONARY(l_smlPoolSto);
    QS_OBJ_DICTIONARY(l_tableQueueSto);
    QS_OBJ_DICTIONARY(l_philoQueueSto[0]);
    QS_OBJ_DICTIONARY(l_philoQueueSto[1]);
    QS_OBJ_DICTIONARY(l_philoQueueSto[2]);
    QS_OBJ_DICTIONARY(l_philoQueueSto[3]);
    QS_OBJ_DICTIONARY(l_philoQueueSto[4]);
    QF_psInit(l_subscrSto, Q_DIM(l_subscrSto)); /* init publish-subscribe */
    /* initialize event pools... */
    QF_poolInit(l_smlPoolSto, sizeof(l_smlPoolSto), sizeof(l_smlPoolSto[0]));
    for (n = 0; n < N_PHILO; ++n)
    { /* start the active objects... */
        QActive_start(AO_Philo[n], (uint8_t)(n + 1),
                      l_philoQueueSto[n], Q_DIM(l_philoQueueSto[n]),
                      (void *)0, 0, (QEvent *)0);
    }
    QActive_start(AO_Table, (uint8_t)(N_PHILO + 1),
                  l_tableQueueSto, Q_DIM(l_tableQueueSto),
                  (void *)0, 0, (QEvent *)0);
    QF_run(); /* run the QF application */
    return 0;
}
```

#### 定义平台相关的 QS 回调函数

```c
#include "qp_port.h"
#include "dpp.h"
#include "bsp.h"
...
/* Local-scope objects -----------------------------------------------------*/
#ifdef Q_SPY
    static uint16_t l_uart_base; /* QS data uplink UART base address */
...
#define UART_16550_TXFIFO_DEPTH 16
#endif
...
/*..........................................................................*/
void
BSP_init(int argc, char *argv[])
{
    char const *com = "COM1";
    uint8_t n;
    if (argc > 1)
    {
        l_delay = atol(argv[1]); /* set the delay counter for busy delay */
    }
    if (argc > 2)
    {
        com = argv[2];
        (void)com; /* avoid compiler warning if Q_SPY not defined */
    }
    // QS未启用，QS_INIT()未自定义时，总是返回True
    if (!QS_INIT(com))
    { /* initialize QS */
        // 断言
        Q_ERROR();
    }
    ...
}
/*..........................................................................*/
// 在空闲循环里， QK 可抢占式内核调用 QK_onIdle()回调函数
void QK_onIdle(void)
{
#ifdef Q_SPY
    if ((inportb(l_uart_base + 5) & (1 << 5)) != 0)
    {                                            /* Tx FIFO empty? */
        uint16_t fifo = UART_16550_TXFIFO_DEPTH; /* 16550 Tx FIFO depth */
        uint8_t const *block;
        QF_INT_LOCK(dummy);
        block = QS_getBlock(&fifo); /* try to get next block to transmit */
        QF_INT_UNLOCK(dummy);
        while (fifo-- != 0)
        { /* any bytes in the block? */
            outportb(l_uart_base + 0, *block++);
        }
    }
#endif
}
...
/*--------------------------------------------------------------------------*/
#ifdef Q_SPY /* define QS callbacks */
/*..........................................................................*/
// 配置 80x86 系列 PC 的某个标准 UART （ COM1 到 COM4 ）
static uint8_t
UART_config(char const *comName, uint32_t baud)
{
    switch (comName[3])
    { /* Set the base address of the COMx port */
    case '1':
        l_uart_base = (uint16_t)0x03F8;
        break; /* COM1 */
    case '2':
        l_uart_base = (uint16_t)0x02F8;
        break; /* COM2 */
    case '3':
        l_uart_base = (uint16_t)0x03E8;
        break; /* COM3 */
    case '4':
        l_uart_base = (uint16_t)0x02E8;
        break; /* COM4 */
    default:
        return (uint8_t)0; /* COM port out of range failure */
    }
    baud = (uint16_t)(115200UL / baud);       /* divisor for baud rate */
    outportb(l_uart_base + 3, (1 << 7));      /* Set divisor access bit (DLAB) */
    outportb(l_uart_base + 0, (uint8_t)baud); /* Load divisor */
    outportb(l_uart_base + 1, (uint8_t)(baud >> 8));
    outportb(l_uart_base + 3, (1 << 1) | (1 << 0));            /* LCR:8-bits,no p,1stop */
    outportb(l_uart_base + 4, (1 << 3) | (1 << 1) | (1 << 0)); /*DTR,RTS,Out2*/
    outportb(l_uart_base + 1, 0);                              /* Put UART into the polling FIFO mode */
    outportb(l_uart_base + 2, (1 << 2) | (1 << 0));            /* FCR: enable, TX clear */
    return (uint8_t)1;                                         /* success */
}
/*..........................................................................*/
// 初始化 QS 构件
uint8_t QS_onStartup(void const *arg)
{
    static uint8_t qsBuf[2 * 1024]; /* buffer for Quantum Spy */
    // 初始化 QS 追踪缓存
    QS_initBuf(qsBuf, sizeof(qsBuf));
    return UART_config((char const *)arg, 115200UL);
}
/*..........................................................................*/
// 执行 QS 的清理工作
void QS_onCleanup(void)
{
}
/*..........................................................................*/
// 回调函数 QS_onFlush() 把整个追踪缓存发送给主机。在每个字典追踪记录后调用这个函数， 用来避免在系统初始化时追踪缓存的溢出。
void QS_onFlush(void)
{
    uint16_t fifo = UART_16550_TXFIFO_DEPTH; /* 16550 Tx FIFO depth */
    uint8_t const *block;
    QF_INT_LOCK(dummy);
    while ((block = QS_getBlock(&fifo)) != (uint8_t *)0)
    {
        QF_INT_UNLOCK(dummy);
        /* busy-wait until TX FIFO empty */
        // 忙等待意味着阻塞，所有这个函数仅能在初始化时调用
        while ((inportb(l_uart_base + 5) & (1 << 5)) == 0)
        {
        }

        while (fifo-- != 0)
        { /* any bytes in the block? */
            outportb(l_uart_base + 0, *block++);
        }
        fifo = UART_16550_TXFIFO_DEPTH; /* re-load 16550 Tx FIFO depth */
        QF_INT_LOCK(dummy);
    }
    QF_INT_UNLOCK(dummy);
}
/*..........................................................................*/
// 获取时间戳
QSTimeCtr QS_onGetTime(void)
{ /* see Listing 11.18 */
    ...
}
#endif /* Q_SPY */
/*--------------------------------------------------------------------------*/
```

#### 使用回调函数 QS_onGetTime() 产生 QS 时间戳

![getqstime](/assets/img/2022-07-27-quantum-platform-1/getqstime.jpg)

8254 芯片的计时器 0 是一个 16 位`向下`计数器，它被设置成当它从 0xFFFF `到 0` 下溢，每次到 0 时产生标准的 18.2Hz 时钟`节拍中断`，下一次计数时计数器回绕成 0xFFFF。 计数速率是 1.193182MHz ，大约每个计数是 0.838 微秒。

每次系统节拍中断就记一次 0x10000，精度就是 0x10000，还要获取`更精细`的值就要读上面说的计时器了，它的值会从 0xFFFF 到 0 。中断计数成上 0x10000 加上计数器的值就是完整的值了。

有个问题就是如果系统节拍中断丢失，就会少加 0x10000，需要通过手段规避

```c
/* Local-scope objects -----------------------------------------------------*/
#ifdef Q_SPY
    static QSTimeCtr l_tickTime; /* keeps timestamp at tick */
    static uint32_t l_lastTime;  /* last timestamp */
#endif
...
// 系统时钟节拍中断
void interrupt ISR_tmr(void)
{
    uint8_t pin;
#ifdef Q_SPY
    // 在中断处理程序里加0x10000
    l_tickTime += 0x10000; /* add 16-bit rollover */
#endif
    QK_ISR_ENTRY(pin, TMR_ISR_PRIO); /* inform QK about entering the ISR */
    QF_tick();                       /* call QF_tick() outside of critical section */
    QK_ISR_EXIT(pin);                /* inform QK about exiting the ISR */
}
/*..........................................................................*/
#ifdef Q_SPY /* define QS callbacks */
...
// 总是在代码的某个临界区调用 QS_onGetTime() 函数。
QSTimeCtr QS_onGetTime(void)
{ /* invoked with interrupts locked */
    uint32_t now;
    uint16_t count16; /* 16-bit count from the 8254 */
    if (l_tickTime != 0) // 系统节拍器已使能
    {                                              /* time tick has started? */
        // 8254的计数器 0 被锁住。这样才能安全读取
        outportb(0x43, 0);                         /* latch the 8254's counter-0 count */
        count16 = (uint16_t)inportb(0x40);         /* read the low byte of counter-0 */
        count16 += ((uint16_t)inportb(0x40) << 8); /* add on the hi byte */
        now = l_tickTime + (0x10000 - count16);
        // 说明丢失了一次系统节拍中断（这个检查假设 QS_onGetTime() 在每个回绕周期被调用一次。）
        // 因为假设了每个中断周期内至少调用一次，所以now正常肯定是大于等于l_lastTime的
        // 而且要假设周期内调用的时间是一样的
        if (l_lastTime > now)
        {                   /* are we going "back" in time? */
            // 手动加1
            now += 0x10000; /* assume that there was one rollover */
        }
        l_lastTime = now;
    }
    else // 系统节拍器还未使能
    {
        now = 0;
    }
    return (QSTimeCtr)now;
}
#endif /* Q_SPY */
```

#### 从主动对象产生 QS 字典

_table.c_:

```c
// 这个是哲学家就餐问题，有叉子、饥饿等名词，Table是活动对象类
static Table l_table; /* the single instance of the Table active object */
...
// 初始伪装态比较适合做生成字典操作
void Table_initial(Table *me, QEvent const *e)
{
    (void)e; /* suppress the compiler warning about unused parameter */
    // 这个宏可以获取参数的名字，所以要用l_table而不是me，即使它们的值相同
    QS_OBJ_DICTIONARY(&l_table);
    // 函数字典
    QS_FUN_DICTIONARY(&QHsm_top);
    QS_FUN_DICTIONARY(&Table_initial);
    QS_FUN_DICTIONARY(&Table_serving);
    // 全局发行的信号的信号字典记录必须和系统里所有的状态机相联系。
    // 所以要给这种信号添加额外信息，这里是第二个参数
    // 比如在另一个状态机里是1而不是0
    QS_SIG_DICTIONARY(DONE_SIG, 0); /* global signals */
    QS_SIG_DICTIONARY(EAT_SIG, 0);
    QS_SIG_DICTIONARY(TERMINATE_SIG, 0);
    // 可以直接用me的值(一个地址)作为额外信息，保证不会重复
    QS_SIG_DICTIONARY(HUNGRY_SIG, me); /* signal just for Table */
    /* signal HUNGRY_SIG is posted directly */
    QActive_subscribe((QActive *)me, DONE_SIG);
    QActive_subscribe((QActive *)me, TERMINATE_SIG);

    Q_TRAN(&Table_serving);
}
```

按照[本地过滤器](#本地过滤器)中的对象说明，这个 l_table 应该是`活动对象`

#### 添加应用程序相关的追踪记录

```c
#ifdef Q_SPY
    ...
    enum AppRecords { /* application-specific trace records */
        // 自定义的记录类型需要从QS_USER开始
        PHILO_STAT = QS_USER
    };
#endif
...
/*..........................................................................*/
void
BSP_displyPhilStat(uint8_t n, char const *stat)
{
    Video_printStrAt(17, 12 + n, VIDEO_FGND_YELLOW, stat);
    // 第一个是记录类型，用于全局过滤器，第二个是应用对象，用于本地过滤器，
    // 这里是活动对象类型，表示只记录这个活动对象相关记录
    // QS_BEGIN和QS_END划定临界区
    QS_BEGIN(PHILO_STAT, AO_Philo[n]) /* application-specific record begin */
        QS_U8(1, n);                  /* Philosopher number */
        QS_STR(stat);                 /* Philosopher status */
    QS_END()
}
```

```log
// 笔者注：格式是 时间 记录类型: n stat
 0000525113 User000: 4 eating
 . . .
 0000591471 User000: 3 hungry
 . . .
 0000591596 User000: 2 hungry
 . . .
 0000591730 User000: 0 hungry
 . . .
 0000852276 User000: 4 thinking
 . . .
 0000852387 User000: 3 eating
 . . .
 0000983937 User000: 1 thinking
 . . .
 0000984047 User000: 0 eating
 . . .
 0001246064 User000: 3 thinking
```

## 问题

1. 单过程处理时间，是否在 DMA 时主动让出控制权（时间较短，让出利用率也低，还有一致性问题）
2. 内存分配，由于没有栈空间，需要堆类型的空间（QP 自带的内存池）
3. state local memory，每个 AO 自己的内部变量，即使是临时变量也会占用固定空间，为了退出后下次进入状态时使用，如果是临时变量会浪费空间

## 参考

- [UML 状态图的实用 C/C++设计](https://www.state-machine.com/doc/PSiCC2-CN.pdf)
