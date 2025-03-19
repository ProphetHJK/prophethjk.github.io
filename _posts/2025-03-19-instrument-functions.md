---
title: "GCC -finstrument-functions 选项介绍"
date: 2025-03-19 09:00:00 +0800
published: true
categories: [教程]
tags: [GCC]
---

## 介绍

开启 `-finstrument-functions` 选项后，编译器会在所有函数的进入和退出位置插入检测函数：

```c
void __cyg_profile_func_enter (void *this_fn,
                               void *call_site);
void __cyg_profile_func_exit  (void *this_fn,
                               void *call_site);
```

## 使用

编译时使用 `-finstrument-functions` 参数，链接时不需要。

`__cyg_profile_func_enter` 和 `__cyg_profile_func_exit` 这两个函数必须被声明并定义

```cpp
extern "C" {
// 必须为其添加 no_instrument_function 说明，防止其自身发生嵌套
void __cyg_profile_func_enter(void *func, void *caller)
    __attribute__((no_instrument_function));
void __cyg_profile_func_exit(void *func, void *caller)
    __attribute__((no_instrument_function));
}

// 功能示例：进入函数时判断 SP 位置是否超出界限
void __cyg_profile_func_enter(void *func, void *caller) {
  __asm__ volatile(
      "MOV   R2, %0       \n\t"    // 加载 currPoolTop 的值到 R0
      "LDR   R0, [R2]     \n\t"  // 加载 currPoolTop 的值到 R0
      "CMP   R0, SP       \n\t" // 比较 currPoolTop (R0) 与 SP
      "BLS   1f    \n\t" // 如果 currPoolTop > SP，异常处理；否则直接返回
      "B .         \n\t"  // 无限循环
      "1:          \n\t"
      :
      : "r"(&currPoolTop) // 输入参数：currPoolTop 的地址
      : "r0", "r2"        // 使用 R0 和 R2，所以要指定它们为修改过的寄存器
  );
}

// 可以使用空的实现
void __cyg_profile_func_exit(void *func, void *caller) {}
```

## 注意事项

- 该编译选项将在所有函数中插入这两个函数，如果不希望某个函数被插入，使用 `__attribute__((no_instrument_function))` 说明符
- 这两个函数实现的时候要足够简单，必要时最好使用汇编来实现
- 该功能最好仅用于调试而不是生产，因为会带来较大的性能损耗
- 开启 LTO 后这两个函数可能被内联，如果是空实现就不会体现在最终二进制文件中了

## 参考

- [GCC options](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html#index-finstrument-functions)
