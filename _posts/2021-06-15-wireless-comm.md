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

1. 发送端的原始电信号通常具有`频率很低`的频谱分量，一般不适宜直接在信道中进行传输。
2. 通过调制可以将多个基带信号搬移到`高频载波`，实现频谱搬移。

![modulation](/assets/img/2021-06-15-wireless-comm/modulation.png)

### 数字调制

![digital-modulation](/assets/img/2021-06-15-wireless-comm/digital-modulation.png)

1. **幅移键控 ASK**：

   `有幅度`表示 1，`无幅度`表示 0

2. **频移键控 FSK**：

   `频率高`表示 1，`频率低`表示 0

3. **相移键控 PSK**：

   用不同`相位`表示不同信息

4. **二进制相移键控 BPSK**：

   ![bpsk](/assets/img/2021-06-15-wireless-comm/bpsk.png)

   相移键控的特殊形式，只能用两个特定的`相位`表示 0 和 1 两个数字

5. **正交相移键控 QPSK**：

   ![qpsk](/assets/img/2021-06-15-wireless-comm/qpsk.png)

   相移键控的特殊形式，可以使用 4 种`相位`，表示 4 种信息（两个比特），抗干扰能力减弱但速率提升

6. **8 相移键控 8PSK**：

   ![8psk](/assets/img/2021-06-15-wireless-comm/8psk.png)

   相移键控的特殊形式，可以使用 8 种`相位`，表示 8 种信息（3 个比特），抗干扰能力进一步减弱但速率进一步提升

7. **正交振幅调制 QAM**：

   ![qam](/assets/img/2021-06-15-wireless-comm/qam.png)

   如果期望混合后的信号的幅度和相位都能发生变化，用`幅度`和`相位`一起区分来区分不同波形，这就是 QAM 调制。当多进制调制中 N>=4, 不再采用 PSK 调制仅仅控制相位，而采用 QAM 调制控制相位与幅度，QAM 调制又称为高阶调制。

   ![qam2](/assets/img/2021-06-15-wireless-comm/qam2.png)

### 不同调制方式的比较

1. BPSK：2 进制相位调制，每个子载波携带 `1` 个比特的二进制数据，主要用于信道质量非常差的场景以及用于物联网应用的场景。
2. QPSK：4 进制相位调制, 每个子载波携带 `2` 个比特的二进制数据。
3. 16QAM：16 进制相位幅度调制, 每个子载波携带 `4` 个比特的二进制数据。
4. 64QAM：64 进制相位幅度调制, 每个子载波携带 `6` 个比特的二进制数据。
5. 256QAM：256 进制相位幅度调制, 每个子载波携带 `8` 个比特的二进制数据。
6. 1024QAM：1024 进制相位幅度调制, 每个子载波携带 `10` 个比特的二进制数据。主要应用在 `5G`.

## 多址技术

`多址技术`是用来区分用户的技术，先进的`多址技术`能让一个基站为更多用户服务

`移动通信是以多址技术来划分时代的`

![multiple-access](/assets/img/2021-06-15-wireless-comm/multiple-access.png)

### FDMA-频分多址

![fdam1](/assets/img/2021-06-15-wireless-comm/fdam1.png)

![fdam2](/assets/img/2021-06-15-wireless-comm/fdam2.png)

`模拟信号(1G)`是通过`频率`的不同来区分不同的用户（每个用户专属一段频率）

### TDMA-时分多址

![tdma1](/assets/img/2021-06-15-wireless-comm/tdma1.png)

![tdma1](/assets/img/2021-06-15-wireless-comm/tdma2.png)

`GSM(2G)` 是通过及其`微小的时隙`来区别不同的用户（每个用户专属一段时间），类似于 CPU 调度策略中的时间片轮转(RR)

### CDMA-码分多址

![cdma](/assets/img/2021-06-15-wireless-comm/cdma.png)

码分多址是指利用`码序列相关性`实现的多址通信;码分多址(CDMA)的基本思想是靠不同的`地址码`来区分的地址。每个配有不同的地址码，用户所发射的载波(为同一载波)既受基带数字信号调制，又受地址码调制。(类似于广播机制，同一频段客户端的都能收到，但只有属于自己的报文才会处理)

接收时，只有确知其配给`地址码`的接收机，才能解调出相应的基带信号，而其他接收机因`地址码不同`，`无法解调出信号`。划分是根据码型结构不同来实现和识别的。

一般选择伪随机码(PN 码)作地址码。由于 PN 码的码元宽度远小于 PCM 信号码元宽度(通常为整数倍)，这就使得加了伪随机码的信号频谱远大于原基带信号的频谱，因此，码分多址也称为扩频多址。

| 运营商        | 编码                           |
| :------------ | :----------------------------- |
| 联通 CDMA2000 | Walsh 码（同步正交码）         |
| 移动 TD-SCDMA | OVSF 码                        |
| 电信 WCDMA    | OVSF 码 （正交可变扩频因子码） |

虽然已有正交频分复用（`OFDM`） 的技术，但仍发展`CDMA`的原因主要为调制/解调并不需要太`精确的频谱分析`。而`OFDM`使用`DFT`需做复数运算，较`CDMA`使用`Walsh Transform`复杂。 CDMA 的`优点`条列如下：

- 运算量相对于频分多工减少很多
- 可以减少噪声及干涉的影响
- 可以应用在保密和安全传输上
- 就算只接收部分的信号，也有可能把原来的信号还原回来
- 相邻的区域的干扰问题可以减少

### OFDM-正交频分复用

`正交频分复用`，英文原称 Orthogonal Frequency Division Multiplexing，缩写为`OFDM`，实际上是 MCM Multi-CarrierModulation 多载波调制的一种。其主要思想是：将信道分成若干`正交子信道`，将高速数据信号转换成并行的低速子数据流，调制到在每个子信道上进行传输。正交信号可以通过在接收端采用相关技术来分开，这样可以减少子信道之间的`相互干扰 ICI`。每个子信道上的信号带宽小于信道的相关带宽，因此每个子信道上的可以看成平坦性衰落，从而可以消除符号间干扰。而且由于每个子信道的带宽仅仅是原信道带宽的一小部分，信道均衡变得相对容易。

在过去的频分复用（FDM）系统中，整个带宽分成 N 个子频带，子频带之间不重叠，为了避免子频带间相互干扰，频带间通常加保护带宽，但这会使频谱利用率下降。为了克服这个缺点，OFDM 采用 N 个重叠的子频带，`子频带间正交`，因而在接收端`无需分离频谱`就可将信号接收下来。OFDM 系统的一个主要优点是正交的子载波可以利用`快速傅利叶变换（FFT/IFFT）`实现调制和解调。

![ofdm](/assets/img/2021-06-15-wireless-comm/ofdm.png)

![ofdm2](/assets/img/2021-06-15-wireless-comm/ofdm2.png)

### OFDMA-正交频分多址

正交频分多址 Orthogonal Frequency Division Multiple Access(OFDMA):OFDMA 是 OFDM 技术的演进，将 OFDM 和 FDMA 技术结合。在利用 OFDM 对信道进行副载波化后，在部分子载波上加载传输数据的传输技术。

OFDM 是一种调制方式；OFDMA 是一种多址接入技术，用户通过 OFDMA 共享频带资源，接入系统。

OFDMA 又分为`子信道`（Subchannel）OFDMA 和`跳频` OFDMA。

OFDMA技术与OFDM技术相比，用户可以选择条件较好的子载波进行数据传输，而不像OFDM技术那样，一个用户在整个频带内发送，从而保证了子载波都被对应信道条件较优的用户使用，获得了频率上的分集增益。在OFDMA中，一组用户可以同时接入到某一子载波。

目前使用OFDMA的无线通信技术有：IEEE 802.16、Wi-Fi 6。

![ofdma](/assets/img/2021-06-15-wireless-comm/ofdma.png)

## 参考

- [OFDMA-百度百科](https://baike.baidu.com/item/OFDMA/1652530)
- [正交频分复用-百度百科](https://baike.baidu.com/item/%E6%AD%A3%E4%BA%A4%E9%A2%91%E5%88%86%E5%A4%8D%E7%94%A8/7626724)
