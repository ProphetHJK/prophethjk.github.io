---
title: "无线通信技术的变革与详解"
author: Jinkai
date: 2021-06-15 09:00:00 +0800
published: true
categories: [技术]
tags: [5G, QAM]
---

## 无线通信架构

### 声音在无线网络中的传输

![wireless-system](/assets/img/2021-06-15-wireless-comm/wireless-system.png)

这是一张关于无线通信过程的架构图，讲述了声音信号如何从发声人到接收人进行传递。

1. 首先发送者的信号传递到了麦克风，由于人声的频率较低（100Hz 到 10000Hz），而无线通信频率较高（850/900/1800/1900MHz），需要通过调制器，将人声变成高频信号
2. 之后通过功率放大器和发送天线，将信号发送出去
3. 在对端接收到该信号后，通过逆过程，将信号转变为声音信号

### 无线基站架构

![base-station](/assets/img/2021-06-15-wireless-comm/base-station.png)

_The baseband unit (BBU) is the baseband processing unit of telecom systems. The BBU has the advantage of modular design, small size, high integration, low power consumption and easy deployment. A typical wireless base station consists of the baseband processing unit (BBU) and the RF processing unit (remote radio unit - RRU). The BBU is placed in the equipment room and connected with the RRU via optical fiber. The BBU is responsible for communication through the physical interface._

`基带单元`（`BBU`）是电信系统的基带处理单元。 BBU 具有模块化设计、体积小、集成度高、功耗低、部署方便等优点。 一个典型的无线基站由基带处理单元（BBU）和射频处理单元（远程无线电单元-RRU）组成。 BBU 放置在机房内，通过光纤与 RRU 相连。 BBU 负责通过物理接口进行通信。

### 现代无线通信技术总览

| 蜂窝移动通信 | 调制技术(基带信号 → 高频信号) | 通信方式(用来区分用户的技术) |
| :----------: | :---------------------------: | :--------------------------: |
|      1G      |            FM/2FSK            |       FDMA/`频分多址`        |
|      2G      |           FSK/QPSK            |       TDMA/`时分多址`        |
|      3G      |        BPSK/QPSK/8PSK         |       CDMA/`码分多址`        |
|      4G      |        QAM/16QAM/64QAM        |     OFDM/`正交频分多址`      |

## 调制技术

### 介绍

1. 发送端的原始电信号通常具有频率很低的频谱分量，一般不适宜直接在信道中进行传输。
2. 通过调制可以将多个基带信号搬移到高频载波，实现频谱搬移。

![modulation](/assets/img/2021-06-15-wireless-comm/modulation.png)

### 数字调制

数字调制是将数字信号转换为电磁波信号的过程

![digital-modulation](/assets/img/2021-06-15-wireless-comm/digital-modulation.png)

1. **幅移键控 ASK**：

   有幅度表示 1，无幅度表示 0

2. **频移键控 FSK**：

   频率高表示 1，频率低表示 0

3. **相移键控 PSK**：

   用不同相位表示不同信息

4. **二进制相移键控 BPSK**：

   ![bpsk](/assets/img/2021-06-15-wireless-comm/bpsk.png)

   相移键控的特殊形式，只能用两个特定的相位表示 0 和 1 两个数字

5. **正交相移键控 QPSK**：

   ![qpsk](/assets/img/2021-06-15-wireless-comm/qpsk.png)

   相移键控的特殊形式，可以使用 4 种相位，表示 4 种信息（两个比特），抗干扰能力减弱但速率提升

6. **8 相移键控 8PSK**：

   ![8psk](/assets/img/2021-06-15-wireless-comm/8psk.png)

   相移键控的特殊形式，可以使用 8 种相位，表示 8 种信息（3 个比特），抗干扰能力进一步减弱但速率进一步提升

7. **正交振幅调制 QAM**：

   ![qam](/assets/img/2021-06-15-wireless-comm/qam.png)

   如果期望混合后的信号的幅度和相位都能发生变化，用幅度和相位一起区分来区分不同波形，这就是 QAM 调制。当多进制调制中 N>=4, 不再采用 PSK 调制仅仅控制相位，而采用 QAM 调制控制相位与幅度，QAM 调制又称为高阶调制。

   ![qam2](/assets/img/2021-06-15-wireless-comm/qam2.png)

### 不同调制方式的比较

1. BPSK：2 进制相位调制，每个子载波携带 1 个比特的二进制数据，主要用于信道质量非常差的场景以及用于物联网应用的场景。
2. QPSK：4 进制相位调制, 每个子载波携带 2 个比特的二进制数据。
3. 16QAM：16 进制相位幅度调制, 每个子载波携带 4 个比特的二进制数据。
4. 64QAM：64 进制相位幅度调制, 每个子载波携带 6 个比特的二进制数据。
5. 256QAM：256 进制相位幅度调制, 每个子载波携带 8 个比特的二进制数据。
6. 1024QAM：1024 进制相位幅度调制, 每个子载波携带 10 个比特的二进制数据。主要应用在 `5G`.

## 多址技术

多址技术是用来区分用户的技术，越好的多址技术能让一个基站为更多用户服务

`移动通信是以多址技术来划分时代的`

![multiple-access](/assets/img/2021-06-15-wireless-comm/multiple-access.png)

### FDMA-频分多址

![fdam1](/assets/img/2021-06-15-wireless-comm/fdam1.png)

![fdam2](/assets/img/2021-06-15-wireless-comm/fdam2.png)

模拟信号（1G）是通过频率的不同来区分不同的用户（每个用户专属一段频率）
