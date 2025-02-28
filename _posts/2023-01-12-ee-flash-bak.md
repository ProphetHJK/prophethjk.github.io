---
title: "基于页的eeprom备份至flash方案"
author: Jinkai
date: 2023-01-12 09:00:00 +0800
published: true
math: true
categories: [平台设计]
tags: [嵌入式, 文件系统]
---

本文介绍了一种将基于页的 eeprom 数据备份至 flash 内的方案

## flash 划分

flash 使用和 eeprom 相同的页大小，为 64Bytes。一个 sector 为 4096Bytes，包含了 4096/64 = 64 个页。

对于 32KB 的 eeprom，共有 512 页需要备份，对应 flash 至少需要 512/64 = 8 个 sector，为了实现 flash 的擦写要求和备份策略，实际可能会更多，取决于具体的备份策略和擦写均衡算法。

![page](/assets/img/2023-01-12-ee-flash-bak/page.png)

## 备份策略

备份策略不使用整体完全备份，基于消耗的时间过长以及数据备份不及时考虑。

为了实现数据的及时备份，每次对 eeprom 的页的修改都会将其备份至 flash。由于 flash 的只写一次特性，所以备份时采用追加写入的方式，按顺序依次写入要备份的页。

比如依次修改了 eeprom 中的页 1、页 2、页 1，则在 flash 的页 0、页 1、页 2 依次备份 eeprom 的页 1、页 2、页 1，则 flash 内的存储情况如下：

| flash 页 | eeprom 页    |
| :------- | :----------- |
| 0        | 1(version 1) |
| 1        | 2(version 1) |
| 2        | 1(version 2) |
| 3        | null         |
| 4        | null         |
| ...      | ...          |

### flash-eeprom 映射表

为了实现追加备份的策略，需要维护一张映射表，用于表示 flash 页和被备份的 eeprom 页间的关系，映射表示例如下:

| flash 页 | eeprom 页 |
| :------- | :-------- |
| 0        | 1         |
| 1        | 2         |
| 2        | 1         |
| 3        | null      |
| ...      | ...       |

映射表存储在单独的 flash 区域，我们称其为日志区。日志由记录构成，记录的结构如下：

```plaintext
[--  sector id（2 Bytes） --][---  映射数组（128 Bytes）  ---]
```

- **sector id**：2 Bytes，用于表示本条记录对应的 sector 编号
- **映射数组**：128 Bytes，表示本 sector 内的页和备份的 eeprom 的页的映射关系。包含 64 个元素的数组，每个元素为 2 字节，数组索引表示 flash 页编号，元素内容表示备份的 eeprom 页编号。默认为 0xFF 表示未写入数据，每次追加备份页时先在 flash 对应页写入备份页内容，再在映射数组的对应位置写入备份页编号。

  映射数组示例如下：

  | 数组索引 | 元素内容(2 Bytes) |
  | :------- | :---------------- |
  | 0        | 0x0001            |
  | 1        | 0x0002            |
  | 2        | 0x0001            |
  | 3        | 0xFFFF            |
  | ...      | 0xFFFF            |
  | 63       | 0xFFFF            |

当一条记录内的映射数组的所有元素都被填充时，需要在日志区追加一条记录，同时需要一个新的被完全擦除的 sector，该记录的 sector id 写为这个新 sector 的 id，映射数组默认全为 0xFFFF。

### eeprom-flash 映射表

为了快速找到 eeprom 页对应备份在 flash 中的位置，可以在 RAM 中维护一张 eeprom-flash 映射表

映射表示例如下：

| eeprom 页 | flash 页 |
| :-------- | :------- |
| 0         | 10       |
| 1         | 2        |
| 2         | 1        |
| ...       | ...      |
| 511       | ...      |

此处的 flash 页编号可以使用 sector id 和 sector 内页编号换算。

在系统启动时可以通过 flash-eeprom 映射表来生成 eeprom-flash 映射表，通过遍历 flash-eeprom 映射表的所有项，找出每个 eeprom 的最新的备份版本对应的 flash 页。

生成示例如下：

| eeprom 页 | flash 页       |
| :-------- | :------------- |
| 0         | null -> 10     |
| 1         | null -> 0 -> 2 |
| 2         | null -> 1      |
| ...       | ...            |
| 511       | ...            |

比如 eeprom 中的页 1 在 flash-eeprom 映射表中有两条记录，其中最新一条记录对应的 flash 页编号为 2，则最终生成的 eeprom-flash 映射表中的 eeprom 页 1 对应 flash 页 2

映射表的数据结构类似于 flash-eeprom 映射表的映射数组，其中索引表示 eeprom 页编号，元素内容表示 flash 页编号，示例如下：

| 数组索引 | 元素内容(2 Bytes) |
| :------- | :---------------- |
| 0        | 0x000A            |
| 1        | 0x0002            |
| 2        | 0x0001            |
| 3        | 0xFFFF            |
| ...      | 0xFFFF            |
| 511      | 0xFFFF            |

## 旧版本数据处理

由于采用了追加备份的策略，对同一个 eeprom 页的备份会存在多个版本，一般我们只关注最新的版本，所有旧版本的数据可以视为垃圾数据。

### 检测垃圾数据

检查垃圾数据的方法是遍历 flash-eeprom 映射表，如果发现对应的记录不在 eeprom-flash 映射表中或存在更新的版本时，该数据就是垃圾数据，反之就是有效数据。

### 垃圾回收

旧版本的垃圾数据会占用备份区的空间，需要在适当的时机进行清理以腾出空间用于备份新的数据。由于 flash 的最小可擦除单元为一个 sector，所以对垃圾数据所在的 sector 擦除前需要将有效数据移动到其他位置防止被一起擦除。

当某个 sector 内只有少数的有效数据时，可以把这些有效数据所为新记录追加到最新的备份位置，这样就让整个 sector 内的所有页都变为了垃圾数据，可以对其进行擦除来释放空间，之后该区域可以作为新的备份区。

![gc](/assets/img/2023-01-12-ee-flash-bak/gc.png)
