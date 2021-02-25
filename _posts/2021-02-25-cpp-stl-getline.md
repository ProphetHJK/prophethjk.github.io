---
title: STL getline读入\r问题
author: Jinkai
date: 2021-02-25 09:00:00 +0800
published: true
categories: [技术]
tags: [stl, c++, getline]
---

## getline说明

- basic_istream& getline( char_type* s, std::streamsize count );
- basic_istream& getline( char_type* s, std::streamsize count, char_type delim );

从流释出字符，直至`行尾`或指定的`分隔符` delim 。

第一版本等价于 `getline(s, count, widen('\n'))` 。

表现为无格式输入函数 (UnformattedInputFunction) 。构造并检查 sentry 对象后，从 *this 释出字符并存储它们于首元素为 s 所指向的数组的相继位置，直至出现任何下列条件（按出示顺序测试）：

- 输入序列中出现文件尾条件（该情况下执行 setstate(eofbit) ）
- 下个可用字符 c 是以 `Traits::eq(c, delim)` 确定的分隔符。释出该分隔符（不同于 `basic_istream::get()` ）并计入 gcount() ，但不存储它。
- 已经释出 `count-1` 个字符（该情况下执行 `setstate(failbit)` ）。

若函数未释出字符（即 `count < 1` ），则执行 `setstate(failbit)` 。

任何情况下，若 `count>0` ，则它存储空字符 CharT() 到数组的下个相继位置，并更新 gcount() 。

### 注意

因为条件 #2 在条件 #3 前测试，故准确适合缓冲区的输入行不会触发 failbit 。

因为终止字符计为释出的字符，故空输入行不触发 failbit 。

### 参数

- s-指向要存储字符到的字符串的指针
- count-s 所指向的字符串的大小
- delim-释出所终止于的分隔字符。释出但不存储它。

### 返回值

*this

### 异常

若出现错误（错误状态标志不是 goodbit ）并且设置了 exceptions() 为对该状态抛出则为 failure 。

若内部操作抛出异常，则捕获它并设置 badbit 。若对 badbit 设置了 exceptions() ，则重抛该异常。

## 出现的错误

使用vscode编辑txt格式文件时，默认的换行符为`CRLF`，即`\r\n`，而getline的默认分隔符为`\n`，导致`\r`也被读入string，造成乱码
