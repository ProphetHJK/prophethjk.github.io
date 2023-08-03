---
title: "使用clang-format进行C语言代码格式化"
author: Jinkai
date: 2023-08-03 09:00:00 +0800
published: true
categories: [教程]
tags: [c, format]
---

## clang-format 介绍

官网：<https://clang.llvm.org/docs/ClangFormat.html>

Clang-Format 是一个由 LLVM 项目提供的开源工具，用于对 C、C++、Objective-C、Java（非原生代码）和 JavaScript 进行源代码格式化。

Clang-Format 使用 Clang 编译器的解析引擎来理解代码结构，它的目标是根据预定义的代码样式规则，自动调整源代码的布局，使其符合一致的代码风格。这样可以提高代码的可读性，减少不必要的代码审查问题，并帮助团队在开发过程中保持一致的代码风格。

Clang-Format 支持的一些常见的格式化选项包括：

- 缩进：定义代码块的缩进大小，如制表符或空格。
- 对齐：定义二元操作符、赋值等在一行上的对齐方式。
- 行宽限制：设置每行代码的最大字符数，超过该限制时会自动换行。
- 空格：定义函数参数、括号、逗号等周围的空格规则。
- 换行：定义 if、for、while 等语句的换行方式。
- 排序包含语句：按照一定的规则对包含的头文件进行排序。

## clang-format 安装

建议以下两种安装方式：

1. 安装 Linux 发行版仓库内的版本

   - 以 debian 系为例：

     ```shell
     apt install clang-format
     ```

   > 但该版本更新较慢，一般都是过时的，不关心新特性的话建议用这种方式

2. 安装 LLVM，其中集成了 clang-format

   - 在 LLVM 的 Github[发布页面](https://github.com/llvm/llvm-project/releases)下载对应平台的版本，如 Windows 下载 LLVM-16.0.6-win64.exe。对于 Linux，也可以去下载 ARM 提供的[交叉编译工具链](https://github.com/ARM-software/LLVM-embedded-toolchain-for-Arm/releases)，其中也附带了 clang-format，这也是我使用的版本。
   - 安装对应版本，或者解压后手动添加环境变量

通过命令行查看版本确认安装成功：

```console
dev@dev-PC:~$ clang-format --version
clang-format version 16.0.0
```

## clang-format 使用

首先要在项目根目录放入`.clang-format`配置文件，编写规则见[clang-format 规则](#clang-format-规则)

### 脚本

通过脚本的方式调用 clang-format

1. 首先编写一个配置文件`config.ini`：

   ```toml
   [codestyle]
   src_dirs=examples/app/test_app1
           examples/app/test_app2
   ```

   > 指定需要检查的路径，可以递归搜索

2. 编写格式化的脚本`format.py`：

   ```python
   import os
   import subprocess
   import sys
   import configparser

   def format_code_style():
       config = configparser.ConfigParser()
       config.read("config.ini")

       src_paths = config.get("codestyle", "src_dirs")
       src_paths = src_paths.splitlines()
       print("检查路径:{}".format(src_paths))

       # 获取所有的.c和.h文件
       files_to_format = []
       for src_dir in src_paths:
           for root, _, files in os.walk(src_dir):
               for file in files:
                   if file.endswith((".c", ".h")):
                       files_to_format.append(os.path.join(root, file))

       # 构建clang-format命令
       command = ["clang-format", "-i"] + files_to_format

       # 执行clang-format命令并将输出重定向到format_output.txt
       result = subprocess.run(command, stderr=subprocess.PIPE)

       # 输出错误信息（如果有的话）
       if result.returncode == 0:
           print("代码格式调整成功")
       else:
           print("代码格式调整失败")
           print(result.stderr.decode())
           sys.exit(1)

   if __name__ == "__main__":
       format_code_style()
   ```

3. 执行脚本即可实现格式化

   ```console
   dev@dev-PC:~$ python3 format.py
   检查路径:['examples/app/test_app1', 'examples/app/test_app1']
   代码格式调整成功
   ```

### visual studio code

在 vscode 中有两种方式使用 clang-format:

- 使用[C/C++插件](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools)(这个应该是 C 程序员必备的插件)，使用`格式化文档`操作时默认就会调用 clang-format 进行格式化。
- 编写`.vscode/tasks.json`配置，添加一个 task，结合[上一节](#脚本)提到的脚本：

  ```json
  {
    "version": "2.0.0",
    "tasks": [
      {
        "label": "codeformat",
        "type": "shell",
        "command": "python3 format.py"
      }
    ]
  }
  ```

  之后就能使用 vscode 的`运行任务`功能自动调用脚本了。

## clang-format 规则

详细规则可以在此处查看：<https://clang.llvm.org/docs/ClangFormatStyleOptions.html>

可以选择自己感兴趣的配置项跳着看，不会花太长时间。注意版本兼容问题，每个配置项后都有最低版本要求，低版本的 clang-format 不能使用高版本新增的配置项。

这里提供一个我使用的针对 C 语言的示例：

```yaml
---
# https://clang.llvm.org/docs/ClangFormatStyleOptions.html
Language: Cpp
BasedOnStyle: LLVM
UseTab: Never # 使用空格而不是制表符。
IndentWidth: 4 # 缩进宽度为4个空格。
TabWidth: 4 # Tab长度
ColumnLimit: 80 # 单行的长度不超过80字符
IndentPPDirectives: BeforeHash # 嵌套宏缩进风格为‘#’前缩进
PPIndentWidth: -1 # 嵌套宏的缩进，使用IndentWidth

BreakBeforeBraces: Custom # 使用自定义风格的大括号排列
BraceWrapping:
  AfterCaseLabel: false # case语句左大括号不换行
  AfterEnum: false
  AfterFunction: true # 函数大括号另起一行
  AfterStruct: false
  AfterUnion: false
  AfterExternBlock: false # extern 的左大括号不换行
  BeforeElse: true # else另起一行
  BeforeWhile: false # do..while中while不另起一行
  AfterControlStatement: MultiLine # 仅在控制语句有多行判断条件的情况下为左大括号换行
  SplitEmptyFunction: false

AllowShortIfStatementsOnASingleLine: false # 不允许将if控制语句和语句放在同一行
IndentCaseLabels: true # 对case标签进行额外的缩进。
BreakBeforeBinaryOperators: NonAssignment # 在除了赋值运算符（如"="、"+="、"-="等）之外的二元运算符(如 &&)之前换行。
SortIncludes: Never # 不要排序#include
SpaceAroundPointerQualifiers: Both # 保证指针限定符(const)左右都有空格
PointerAlignment: Right # 指针符靠右
# QualifierAlignment: Right # 限定符(const)靠右，根据官方文档介绍该操作有风险，不强制规定
# QualifierOrder: ['static', 'inline', 'type', 'const', 'volatile' ] # 限定符顺序，同上，不强制规定

AlignConsecutiveMacros: Consecutive # 对齐define宏,不跨空行不跨注释
AlignConsecutiveBitFields: Consecutive # 对齐位域,不跨空行不跨注释
AlignConsecutiveAssignments: Consecutive # 对齐赋值,不跨空行不跨注释
BitFieldColonSpacing: None # 位域前没有空格
AlignEscapedNewlines: Left # 分行符靠左对齐
# AlignConsecutiveDeclarations: Consecutive # 对齐定义，用处不大，不启用
---
```
