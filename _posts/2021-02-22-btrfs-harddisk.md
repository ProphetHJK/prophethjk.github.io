---
title: 在移动硬盘上使用btrfs文件系统
author: Jinkai
date: 2021-02-22 09:00:00 +0800
published: true
categories: [技术]
tags: [btrfs, linux, 文件系统]
---

>参考：
>
>- [Linux使用fdisk创建分区详解](<https://www.jianshu.com/p/520b3a405014>)

## 前言

--------

对于移动硬盘，在空间和便携性上取舍是个比较麻烦的问题，即想要便携又要大的存储空间时怎么办？这时就要考虑带有透明压缩的文件系统，btrfs就是个很好的选择，在拥有诸多现代文件系统特性的基础上增加了透明压缩功能，压缩率能达到50%以上，让移动硬盘能塞下更多文件

但同时btrfs也是有缺陷的，就是主流的操作系统支持性并不好，Windows和Macos需要安装驱动，Linux4.14后的版本才可支持zstd压缩算法。

## 介绍

--------

`Btrfs`（B-tree文件系统，通常念成Butter FS，Better FS或B-tree FS），一种支持写入时复制（COW）的文件系统，运行在Linux操作系统，采用GPL授权。Oracle于2007年对外宣布这项计划，并发布源代码，在2014年8月发布稳定版。目标是取代Linux目前的ext3文件系统，改善ext3的限制，特别是单个文件的大小，总文件系统大小或文件检查和加入ext3未支持的功能，像是可写快照（writable snapshots）、快照的快照（snapshots of snapshots）、内建磁盘阵列（RAID），以及子卷（subvolumes）。Btrfs也宣称专注在“`容错、修复及易于管理`”。

## btrfs特性

--------

- 联机碎片整理
- 联机卷生长和收缩
- 联机块设备增加和删除
- 联机负载均衡（块设备间的对象移动以达到平衡）
- 文件系统级的镜像（类RAID-1）、条带（类RAID-0）
- 子卷（一个或多个单独可挂载基于每个物流分区）
- 透明压缩（目前支持zlib、LZO和ZSTD (从 4.14 开始支持)）
- 快照（只读和可写，写复制，子卷复制）
- 文件克隆
- 数据和元数据的校验和（目前是CRC-32C）
- 就地转换（带回滚）ext3/4
- 文件系统种子
- 用户定义的事务
- 块丢弃支持

## 分区

--------

```console
fdisk /dev/sdb

>Command (m for help): n

>Command action #这里可以选择是作为扩展分区还是主分区。这里作为主分区，则选择p
e   extended
p   primary partition (1-4)
p

>Partition number (1-4): 1  #做第一块主分区

>First cylinder (1-130, default 1):
Using default value 1

>Last cylinder, +cylinders or +size{K,M,G} (1-130, default 130): +500M  #分区大小为K，M，G。制作分区的大小，这里选择第一块分区大小为500M

>Command (m for help): p    #输入p可以查看刚才分区的情况

Disk /dev/sdb: 1073 MB, 1073741824 bytes
255 heads, 63 sectors/track, 130 cylinders
Units = cylinders of 16065 * 512 = 8225280 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0x06194404
Device Boot      Start         End      Blocks   Id  System
/dev/sdb1          1            65      522081   83  Linux

>Command (m for help): w    # 最好输入w 保存我们刚才从sdb分区出来的sdb1

The partition table has been altered!

Calling ioctl() to re-read partition table.
Syncing disks.
```

## 格式化

--------

使用`mkfs.btrfs`命令格式化分区:

```console
mkfs.btrfs /dev/sdb1
```

## 挂载

--------

获取UUID:

```console
lsblk -f
```

修改/etc/fstab:

```console
UUID=f4f459e9-48df-445e-94f1-96c98a68e78e               /mnt/btrfs      btrfs   defaults,noauto,nofail,noatime,compress-force=zstd:1  0       0
```

- noatime已经包含了nodiratime，不用同时指定
- zstd:1表示使用level1的zstd压缩算法，较为快速，不同level压缩率差距很小，详见[BTRFS ZSTD level compression benchmark](<https://docs.google.com/spreadsheets/d/1x9-3OQF4ev1fOCrYuYWt1QmxYRmPilw_nLik5H_2_qA/edit#gid=0>)

使用`mount`命令挂载:

```console
mount /mnt/btrfs
```

## compress-force与compress

--------

1. 使用compress-force可以带来更高的压缩比，但会影响性能
2. compress的采样算法在4.15有优化，但没有实质变化
3. 经过实测，19092520KB的原始数据在两种策略下的压缩率实际表现如下:

| raw      | compress  | compress-force |
| :------: |  :------: | :------:       |
|19092520  | 11827572  |  11532752      |

## 压缩算法

--------

Btrfs文件系统目前支持`ZLIB`、`LZO`、`ZSTD`(从 4.14 开始支持)算法，ZSTD是目前btrfs最好的压缩策略
