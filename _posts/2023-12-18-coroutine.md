---
title: "什么是协程？"
author: Jinkai
date: 2023-12-18 08:00:00 +0800
published: true
categories: [教程]
tags: [coroutine]
---

## 协程介绍

协程(coroutine)是计算机程序的一类组件，类似于线程，是一种用于处理**协作式多任务**的方式。

协程适合于用来实现**彼此熟悉**的程序组件，如协作式多任务、异常处理、事件循环、迭代器、无限列表和管道。

协作意味着由拥有控制权的任务决定什么时候交出控制权，且交给哪个任务，而不是由操作系统的调度内核决定。

## 和线程的区别

线程使用通用的多任务执行方式，其依赖于**操作系统内核**的实现**并行和并发**(看上去同时执行，且实际可在多个 CPU 同时运行)的多任务处理，而协程是**应用/语言级别**（在协程之间的切换不需要涉及任何系统调用或任何阻塞调用）的多任务处理，无需依赖操作系统，这意味着协程提供**并发性**(看上去是同时执行，实际为交替执行)而非并行性。

协程不需要用来守卫关键区块的同步性原语(primitive)比如互斥锁、信号量等，并且不需要来自操作系统的支持。协程是语言层级的构造，可看作一种形式的**控制流**，而线程是系统层级的构造。

## 协程示例

```console
var q := new 队列

coroutine 生产者
    loop
        while q 不满载
            建立某些新产品
            向 q 增加这些产品
        yield 消费者

coroutine 消费者
    loop
        while q 不空载
            从 q 移除某些产品
            使用这些产品
        yield 生产者
```

协程可以通过 `yield`（理解为**让步**）来主动让出执行流控制权并调用其它协程，接下来的每次协程被调用时，从协程上次 yield 返回的位置接着执行。

通过 yield 方式转移执行权的协程之间不是调用者与被调用者的关系，而是彼此**对称、平等**的。

## 协程实例

在[《UML 状态图的实用 C/C++设计》(QP 状态机)学习笔记](/posts/quantum-platform-1/#原生合作式-vanilla-内核)中提到的合作式 QV 内核就是类似协程的概念，其不依赖于操作系统，即使在裸机环境也可执行。每个任务执行一定步骤主动交出控制权来实现并发处理，对于 QP 这种事件驱动型状态机来说，这种调度方式非常合适。

### 生成器generator

生成器函数看起来和普通函数类似，但它使用 yield 而不是 return 来返回值。每次调用生成器的 `__next__()` 方法（或者通过 next() 函数），它会从上次离开的地方继续执行，直到遇到下一个 yield。

```python
def my_generator():
    yield 1
    yield 2
    yield 3

# 使用生成器
gen = my_generator()

print(next(gen))  # 输出 1
print(next(gen))  # 输出 2
print(next(gen))  # 输出 3
```

生成器是迭代器的一种，所以它实现了迭代器的协议，即 `__iter__()` 和 `__next__()` 方法。你可以使用 for 循环来遍历生成器。

`yield` 是生成器的核心。每次执行 yield 时，生成器会暂停其状态，保留局部变量的值、当前的执行位置等信息。下一次调用 `__next__()` 或 `next()` 时，生成器会从暂停的地方继续执行。

python:

```python
def fibonacci(limit):
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b

# 生成 10 以内的 Fibonacci 数列
for value in fibonacci(10):
    print(value)
```

C++ 23:

```cpp
#include <generator>
#include <utility>
#include <iostream>
std::generator<uint64_t> fib(int max) {
    auto a = 0, b = 1;
    for (auto n = 0; n < max; n++) {
        co_yield std::exchange(a, std::exchange(b, a + b));
    }
}

int main(){
    for(auto&& i: fib(10)) { // 输出fibonacci数列的前十个
        std::cout<<i<<"\n";
    }
}
```

C++ 20:

```cpp
#include <coroutine>
#include <iostream>
#include <utility>

template <typename T> struct Generator {
  // 实现一个协程需要一个 promise_type 用于状态管理。名字必须叫promise_type
  struct promise_type {
    T value_;

    // 返回一个协程对象，它持有协程的句柄。编译器会自动调用
    Generator get_return_object() {
      return Generator{
          std::coroutine_handle<promise_type>::from_promise(*this)};
    }
    // 定义协程的初始挂起行为。通常返回
    // std::suspend_always，表示协程初始时会挂起。
    static std::suspend_always initial_suspend() { return {}; }
    // 定义协程的最终挂起行为。通常返回
    // std::suspend_always，表示协程结束时会挂起，以便进行清理。
    static std::suspend_always final_suspend() noexcept { return {}; }
    // 用于返回一个值并挂起协程。
    template <std::convertible_to<T> From> // C++20 concept
    std::suspend_always yield_value(From &&from) {
      value_ = std::forward<From>(from); // caching the result in promise
      return {};
    }
    // 用于协程正常结束时的处理。
    void return_void() {}
    void unhandled_exception() { std::terminate(); }
  };

  // 用于恢复协程的执行、检查协程的状态等。它是一个轻量级的对象，提供了协程的生命周期管理。
  std::coroutine_handle<promise_type> coro;

  Generator(std::coroutine_handle<promise_type> h) : coro(h) {}
  ~Generator() {
    if (coro)
      coro.destroy();
  }

  bool move_next() {
    coro.resume();
    return !coro.done();
  }

  T current_value() const { return coro.promise().value_; }
};

Generator<int> fibonacci() {
  int a = 0, b = 1;
  while (true) {
    // 相当于co_await promise.yield_value(expr)。
    // 第一次调用时，会调用Generator构造函数，找到该类中名为promise_type的内部类并构造，然后调用其get_return_object
    // 生成一个std::coroutine_handle<promise_type>作为Generator的参数
    co_yield std::exchange(a, std::exchange(b, a + b));
  }
}

int main() {
  auto fib = fibonacci();
  for (int i = 0; i < 10; ++i) { // 生成前 10 个斐波那契数
    fib.move_next();
    std::cout << fib.current_value() << " ";
  }
}
```

## 参考

- [协程 - 维基百科，自由的百科全书](https://zh.wikipedia.org/wiki/%E5%8D%8F%E7%A8%8B)
