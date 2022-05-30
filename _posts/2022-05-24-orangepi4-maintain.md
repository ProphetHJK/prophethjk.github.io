---
title: "Orangepi4维护指南"
author: Jinkai
date: 2022-05-30 09:00:00 +0800
published: true
categories: [教程]
tags: [orangepi4, maintain, shell]
---

## 固件

使用 Armbian focal cli 版本，基于 Ubuntu server 20.04

[armbian 官网](https://www.armbian.com/orange-pi-4/)

## 存储

### 外置 USB 硬盘

#### 自动休眠

修改 etc 配置

```conf
# /etc/hdparm.conf
/dev/sda {
    write_cache = on
    spindown_time = 120
}
```

#### 立刻休眠

```bash
# 省电standby
hdparm -y /dev/sda
# 休眠sleep
hdparm -Y /dev/sda
```

#### 测速

```bash
# 非缓存
hdparm -t /dev/sda
# 缓存
hdparm -T /dev/sda
```

#### 空间占用

```bash
# 总使用情况
df -h
# 具体目录和一级子目录使用情况
du -d 1 -h
# 具体目录，不包含子目录使用情况
du -s -h
```

#### smart 健康状态查询

```bash
smartctl -a /dev/sda
```

### 查看目录被进程占用

```bash
# fuser
fuser -aumv /mnt/disk3

# 递归查找某个目录中被打开的文件信息
lsof +D /var/log/nginx
```

### 查看进程 IO 情况

iotop 实时统计：

```bash
iotop -oP
```

pidstat 连续统计：

```bash
pidstat -d 1
```

## 代理

启动 udp2raw_arm

启动 v2ray

## 状态查看

```bash
htop
```

## videomanage

### 生成缩略图

1. 进入/home/dev/videomanager/vcsithumb/
2. 修改 config.ini
3. 执行 python3 vcsithumb.py(root 用户)

### 更新数据库

1. 进入/home/dev/videomanager/videodb/
2. 修改 config.ini
3. 备份 videodb.db
4. 执行 python3 videodb.py(dev 用户)

### 编译 web

1. 进入/home/dev/videomanager/videoweb/
2. 执行 npm run build(dev 用户)

## 参考

- [linux 查看哪个进程占用磁盘 IO\_带鱼兄的博客-CSDN 博客\_linux 查看磁盘被哪个进程占用](https://blog.csdn.net/daiyudong2020/article/details/53863314)
- [Linux hdparm 命令 | 菜鸟教程](https://www.runoob.com/linux/linux-comm-hdparm.html)
- [fuser 与 lsof -- 查看文件被哪些进程占用 - 常四 - 博客园](https://www.cnblogs.com/ccbloom/p/11301159.html)
