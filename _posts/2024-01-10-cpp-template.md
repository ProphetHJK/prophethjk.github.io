---
title: "C++ template详解"
author: Jinkai
date: 2024-01-10 08:00:00 +0800
published: true
categories: [教程]
tags: [constexpr, cpp]
---

## template 的初衷

模板被设计之初的用法是用于实现**泛型**。在加入模板之前，常常使用**宏**来实现泛型：

```cpp
#define add(T) _ADD_IMPL_##T

#define ADD_IMPL(T) \
T _ADD_IMPL_##T (T a, T b) { \
    return a + b; \
}

ADD_IMPL(int); // 必须显式实例化
ADD_IMPL(float);

int main()
{
    add(int)(1, 2); // 不能自动推导类型
    add(float)(1.0f, 2.0f);
}
```

主要问题：

1. 必须显式实例化
2. 不能自动推导类型

可以通过使用 template 解决问题：

```cpp
template<typename T>
T add(T a, T b)
{
    return a + b;
}

// template int add<>(int, int); // 无需显式实例化(函数)

int main()
{
    add<int>(1, 2); // 显式指名模板参数T
    add(1, 2);      // 支持自动推导模板参数T
    add(1.0f, 2.0f); // 自动推导并且隐式实例化(函数)
}
```

## 基本概念

### typename 用法

关键字 typename 在 C++ 标准化过程中被引入进来，用来澄清模板内部的一个标识符代表的是某种类型，而不是数据成员。

```cpp
template<typename T>
class MyClass {
  public:
    // ...
    void foo() {
    // 此处的typename表示SubType是一个类型，
    // 且ptr是一个SubType类型指针。
    typename T::SubType* ptr;
  }
};
```

因为 T 是类型(type)而不是类(class)，所以也不能将 SubType 理解为 T 类中的一个 static 变量，这样这个表达式就变成了 T::SubType 和 ptr 的乘法：

```cpp
T::SubType * ptr;
```

正确使用方法需要配合 typedef 或 using 在 T 类中定义一个 SubType 类：

```cpp
class MyClass2 {
  public:
    using SubType = int;
}

int main()
{
  MyClass<MyClass2> obj;
  obj.foo();
}
```

### 零初始化

对于**基础类型**，比如 int，double 以及指针类型，由于它们没有默认构造函数，因此它们不会被默认初始化成一个有意义的值。比如任何未被初始化的局部变量的值都是未定义的：

```cpp
template<typename T>
void foo()
{
  T x; // x has undefined value if T is built-in type
}
```

一种初始化的方法被称为“**值初始化**（value initialization）”，它要么调用一个对象已有的构造函数，要么就用零来初始化这个对象。通过下面你的写法就可以保证即使是内置类型也可以得到适当的初始化（内置类型被初始化为 0）：

```cpp
void foo()
{
  T x{}; // x is zero (or false) if T is a built-in type
}
```

对于自定义类模板，需要在默认构造函数初始化成员(值初始化)：

```cpp
template <typename T> class MyClass {
private:
  T x;

public:
  MyClass() : x{} { // ensures that x is initialized even for built-in types
  }
};
```

也可以在定义成员时直接初始化(值初始化)：

```cpp
template <typename T> class MyClass {
private:
  T x{}; // zero-initialize x unless otherwise specified
};
```

## 类型萃取

类型萃取（Type Traits）是在编译时获取或判断类型信息的一种技术。C++标准库中提供了 `<type_traits>` 头文件，其中包含一系列类模板和函数，用于进行类型特性检查。

类型萃取的目的是使程序能够根据类型信息进行编译时决策，而不是在运行时进行。这有助于提高代码的性能和安全性。

1. is_same： 判断两个类型是否相同。

   ```cpp
   #include <type_traits>

   template <typename T>
   void exampleFunction(T value) {
       static_assert(std::is_same<T, int>::value, "T must be int");
       // 其他操作
   }
   ```

2. is_pointer： 判断类型是否为指针类型。

   ```cpp
   #include <type_traits>

   template <typename T>
   void exampleFunction(T value) {
       static_assert(std::is_pointer<T>::value, "T must be a pointer");
       // 其他操作
   }
   ```

3. conditional： 根据条件选择类型。

   ```cpp
   #include <type_traits>

   template <bool Condition, typename T, typename U>
   using conditional_type = typename std::conditional<Condition, T, U>::type;

   using result_type = conditional_type<sizeof(int) == 4, int, long>;
   ```

4. remove_reference： 移除引用。

   ```cpp
   #include <type_traits>

   template <typename T>
   void exampleFunction(T value) {
       using ValueType = typename std::remove_reference<T>::type;
       // ValueType 是没有引用的 T 类型
   }
   ```

5. enable_if： 根据条件启用函数模板的重载。

   ```cpp
   #include <type_traits>

   template <typename T>
   typename std::enable_if<std::is_integral<T>::value, T>::type
   exampleFunction(T value) {
       // 只有当 T 是整数类型时才启用该模板
   }
   ```

## 模板分类

模块可分为**函数模板**和**类模板**两类。

### 函数模板（Function Templates）

```cpp
#include <type_traits>
template<typename T1, typename T2, typename RT =
std::common_type_t<T1,T2>>
RT max (T1 a, T2 b)
{
    return b < a ? a : b;
}
```

本例中包含了多个模板参数，其中 RT 为一个复合类（本质是一个类模板），其中 T1 和 T2 可以选择不指定而自动推导，随后如果 RT 不指定会默认为这个复合类，然后再根据返回值自动推导为复合类包含的类型中的一个(T1 或 T2)。

#### 缩写函数模板（C++20）

C++20 引入了 auto 关键字的新用法：当 auto 关键字在普通函数中用作参数类型时，编译器会自动将该函数转换为函数模板，每个自动参数成为独立的模板类型参数。这种创建函数模板的方法称为缩写函数模板。

```cpp
auto max(auto x, auto y)
{
    return (x < y) ? y : x;
}
```

用来代替：

```cpp
template <typename T, typename U>
auto max(T x, U y)
{
    return (x < y) ? y : x;
}
```

这仅在两个参数类型不强制要求相同的情况下有效，否则不能使用缩写函数模板

### 类模板（Class Templates）

```cpp
#include <cassert>
#include <vector>
template <typename T> class Stack {
private:
  std::vector<T> elems; // elements
public:
  void push(T const &elem); // push element
  void pop();               // pop element
  T const &top() const;     // return top element
  bool empty() const {      // return whether the stack is empty
    return elems.empty();
  }
};
template <typename T> void Stack<T>::push(T const &elem) {
  elems.push_back(elem); // append copy of passed elem
}
template <typename T> void Stack<T>::pop() {
  assert(!elems.empty());
  elems.pop_back(); // remove last element
}
template <typename T> T const &Stack<T>::top() const {
  assert(!elems.empty());
  return elems.back(); // return copy of last element
}
```

## 非类型模板参数

对于之前介绍的**函数模板**和**类模板**，其模板参数不一定非得是某种具体的类型(typename)，也可以是常规数值(实参应该要是常量)。

```cpp
#include <array>
#include <cassert>
template <typename T, std::size_t Maxsize> class Stack {
private:
  std::array<T, Maxsize> elems; // elements
  std::size_t numElems;         // current number of elements
public:
  Stack();                  // constructor
  void push(T const &elem); // push element
  void pop();               // pop element
  T const &top() const;     // return top element
  bool empty() const {      // return whether the stack is empty
    return numElems == 0;
  }
  std::size_t size() const { // return current number of elements
    return numElems;
  }
};
template <typename T, std::size_t Maxsize>
Stack<T, Maxsize>::Stack()
    : numElems(0) // start with no elements
{
  // nothing else to do
}
template <typename T, std::size_t Maxsize>
void Stack<T, Maxsize>::push(T const &elem) {
  assert(numElems < Maxsize);
  elems[numElems] = elem; // append element
  ++numElems;             // increment number of elements
}
template <typename T, std::size_t Maxsize> void Stack<T, Maxsize>::pop() {
  assert(!elems.empty());
  --numElems; // decrement number of elements
}
template <typename T, std::size_t Maxsize>
T const &Stack<T, Maxsize>::top() const {
  assert(!elems.empty());
  return elems[numElems - 1]; // return last element
}
```

实例化方式：

```cpp
Stack<int,20> int20Stack; // stack of up to 20 int
Stack<std::string,40> stringStack;
```

从 C++17 开始，可以使用 auto 类型作为模板参数的类型：

```cpp
template <typename T, auto Maxsize> class Stack {}
```

且可以在类定义的内部获取其类型：

```cpp
// 可以使用新版的using
using size_type = decltype(Maxsize);
// 或使用C风格的typedef
typedef decltype(Maxsize) size_type;
```

## 变参模板

从 C++11 开始，模板可以接受一组数量可变的参数。这样就可以在参数数量和参数类型都不确定的情况下使用模板。

一般需要用递归方式使用这些参数：

```cpp
#include <iostream>
void print (){}
template<typename T, typename... Types>
void print (T firstArg, Types... args)
{
  std::cout << firstArg << '\n'; //print first argument
  std::cout << sizeof...(Types) << '\n'; // 可用sizeof获取类型数量
  std::cout << sizeof...(args) << '\n'; //可用sizeof获取参数数量
  print(args...); // call print() for remaining arguments
}
```

### 扩展：C++ 实现可变参数的三个方法

1. C 方法：va_list

   ```cpp
   #include <stdarg.h>
   int f(int n,...) {
      va_list myarg;
      va_start(myarg, 10);

      int ans(0);
      for (int i(0);i<n;i++) ans += va_arg(myarg, int); //仅支持int
      va_end(myarg);
      return ans;
   }
   ```

2. C++方法：使用 initializer_list

   ```cpp
   #include <initializer_list>

   int max(std::initializer_list<int> li) {
      int ans = 1 << 31;
      for (auto x: li) ans = ans>x ? ans : x;
      return ans;
   }

   main() {
     printf("%d\n", max({1, 2, 3})); //加上大括号，作为整体调用
   }
   ```

3. C++方法：使用可变参数模板

   ```cpp
   template<typename T, typename... Types> // Args：“模板参数包”
   void foo(const T &t, const Types&... args); // args：“一个参数包（含有0或多个参数）”

   foo(i, s, 42, d); // 包中有三个参数
   foo(s, 42, "hi"); // 包中有两个参数
   foo(d, s); // 包中有一个参数
   foo("hi"); // 空包
   ```

## 推断指引（Deduction Guides）

C++17 引入了自动类型推断，如果情况较为复杂导致编译器难以进行自动推断，可以通过提供“推断指引”来提供额外的模板参数推断规则，或者修正已有的模板参数推断规则。

```cpp
Stack(char const*) -> Stack<std::string>;
```

该语句表示，当类模板参数类型为 `char const *` 时，将其推断为 `std::string` 类型。

其实推断指引相当于为该类模板实例化了一个 string 类型的类实例并重载了一个简单的构造函数，构造函数参数为 `char const *`(默认构造函数的参数为 string)。

```cpp
Stack stack("hello");
// 等价于
Stack<std::string> stack("hello");
```

### 变参推断指引

推断指引也可以是变参的。比如在 C++标准库中，为 std::array 定义了如下推
断指引：

```cpp
namespace std {
  template<typename T, typename... U> array(T, U...)
    -> array<enable_if_t<(is_same_v<T, U> && ...), T>, (1 + sizeof...(U))>;
}
```

推断过程：

```cpp
std::array a{42,45,77};
// 推断为
std::array<int, 3> a{42,45,77};
```

其中的折叠表达式：

```cpp
is_same_v<T, U> && ...
// 展开后为
is_same_v<T, U1> && is_same_v<T, U2> && is_same_v<T, U3> ...
```

如果结果是 false（也就是说 array 中元素不是同一种类型），推断指引会被弃用，总的类型推断失败。这样标准库就可以确保在推断指引成功的情况下，所有元素都是同一种类型。

## 按值传递还是按引用传递？

C++ 提供了按值传递（call-by-value）和按引用传递（call-by-reference）两种参数传递方式

### 按值传递

当按值传递参数时，原则上所有的参数都会被拷贝。因此每一个参数都会是被传递实参的一份拷贝（深拷贝）。对于 class 的对象，参数会通过 class 的拷贝构造函数来做初始化。

调用拷贝构造函数的成本可能很高。但是有多种方法可以避免按值传递的高昂成本：事实上编译器可以通过**移动语义**（move semantics）来优化掉对象的拷贝，这样即使是对复杂类型的拷贝，其成本也不会很高。

```cpp
std::string returnString();
std::string s = "hi";
printV(s); // 参数为左值，会调用构造函数
printV(std::string("hi")); // 参数为右值，使用移动语义
printV(returnString()); // 参数为右值，使用移动语义
printV(std::move(s)); // 参数为右值，无需重新构造
```

不过由于编译器的优化能力较强，可以有效避免传递成本，还是建议在函数模板中应该优先使用**按值传递**，除非遇到以下情况：

- 对象不允许被 copy。
- 参数被用于返回数据。
- 参数以及其所有属性需要被模板转发到别的地方。
- 可以获得明显的性能提升

另外按值传递会导致**类型退化**（decay），也就是裸数组类型会退化为指针，const 和 volatile 等限制符会被删除，这是从 C 语言中继承下来的特性:

```cpp
template <typename T> void printV(T arg) {
  // ...
}
std::string const c = "hi";
printV(c);    // 退化，const被删除
printV("hi"); // 退化为指针，T 被推断为char const*，而不是string
int arr[4];
printV(arr);  // 退化为指针，丢失数组大小信息
```

### 按引用传递

C++11 引入了移动语义（move semantics）后，共有三种**按引用传递**方式：

1. X const &（const 左值引用）
   参数引用了被传递的对象，并且参数不能被更改。
2. X &（非 const 左值引用）
   参数引用了被传递的对象，并且参数可以被更改。
3. X &&（右值引用）
   参数通过移动语义引用了被传递的对象，并且参数值可以被更改或者被“窃取”。一般不会为右值引用增加 const 修饰符，因为右值引用的用途就是为了修改

以下模板永远不会拷贝被传递对象（不管拷贝成本是高还是低）：

```cpp
template <typename T> void printR(T const &arg) {
  // ...
}

std::string returnString();
std::string s = "hi";
printR(s);                 // no copy
printR(std::string("hi")); // no copy
printR(returnString());    // no copy
printR(std::move(s));      // no copy
```

按引用传递参数时，其类型不会退化（decay）。也就是说不会把裸数组转换为指针，也不会移除 const 和 volatile 等限制符。而且由于调用参数被声明为 T const &，被推断出来的模板参数 T 的类型将不包含 const。比如：

```cpp
template<typename T>
void printR (T const& arg) {
  ...
}
std::string const c = "hi";
printR(c); // T deduced as std::string, arg is std::string const&
printR("hi"); // T deduced as char[3], arg is char const(&)[3]
int arr[4];
printR(arr); // T deduced as int[4], arg
```

### 使用 std::ref()和 std::cref()

从 C++11 开始，可以让调用者自行决定向函数模板传递参数的方式。如果模板参数被声明成按值传递的，调用者可以使用定义在头文件`<functional>`中的 std::ref() 和 std::cref() 将参数**按引用传递**给函数模板。比如：

```cpp
template<typename T>
void printT (T arg) {
  ...
}
std::string s = "hello";
printT(s); //pass s By value，T 被推断为std::string
printT(std::cref(s)); // pass s “as if by reference”，T 被推断为std::string&
```

### 关于字符串常量和裸数组的特殊实现

有时候可能必须要对数组参数和指针参数做不同的实现，当然也不能退化数组的类型:

```cpp
template<typename T, std::size_t L1, std::size_t L2>
void foo(T (&arg1)[L1], T (&arg2)[L2])
{
  T* pa = arg1; // decay arg1
  T* pb = arg2; // decay arg2
  if (compareArrays(pa, L1, pb, L2)) {
    ...
  }
}
```

## 模板实战

### 包含模式

常规的代码结构存在问题：

```c
/* myfirst.hpp */
#ifndef MYFIRST_HPP
#define MYFIRST_HPP
// declaration of template
template<typename T>
void printTypeof (T const&);
#endif //MYFIRST_HP

/* myfirst.cpp */
#include <iostream>
#include <typeinfo>
#include "myfirst.hpp"
// implementation/definition of template
template<typename T>
void printTypeof (T const& x)
{
  std::cout << typeid(x).name() << ’\n’;
}

/* main.cpp */
#include "myfirst.hpp"
// use of the template
int main()
{
  double ice = 3.0;
  printTypeof(ice); // call function template for type double
}
```

以上代码在编译时不会有问题，但在链接时很有可能提示找不到 printTypeof() 的定义。这是因为在编译 myfirst.cpp 时，由于编译器它不知道和 main.cpp 之间的关联，所以不会实例化 T 为 double 时的函数模板，因此链接器无法找到对应的函数定义。

因此，要将模板的定义放在和声明相同的文件中：

```c
/* myfirst.hpp */
#ifndef MYFIRST_HPP
#define MYFIRST_HPP
#include <iostream>
#include <typeinfo>
// declaration of templat
template<typename T>
void printTypeof (T const&);
// implementation/definition of template
template<typename T>
void printTypeof (T const& x)
{
  std::cout << typeid(x).name() << ’\n’;
}
#endif //MYFIRST_HPP
```

这种组织模板相关代码的方法被称为“包含模式”。但这种方式会让头文件变得臃肿，增加了 include 时的成本和编译时间，不过目前没有更好的解决办法（非官方的预编译头文件特性可能可以缓解该问题）。

## 基本术语

### 类模板和模板类

一般叫类模板

### 声明和定义

对于声明，如果其细节已知，或者是需要申请相关变量的存储空间，那么声明就变成了定义。

```c
/* 声明 */
class C; // a declaration of C as a class
void f(int p); // a declaration of f() as a function and p as a named parameter
extern int v; // a declaration of v as a variabl

/* 定义 */
class C {}; // definition (and declaration) of class C
void f(int p) { //definition (and declaration) of function f()
  std::cout << p << '\n';
}
extern int v = 1; // an initializer makes this a definition for v
int w; // global variable declarations not preceded by extern are also definitions
```

#### 完整类型和非完整类型（complete versus incomplete types）

非完整类型是以下情况之一：

- 一个被声明但是还没有被定义的 class 类型。
- 一个没有指定边界的数组。
- 一个存储非完整类型的数组。
- Void 类型。
- 一个底层类型未定义或者枚举值未定义的枚举类型。
- 任何一个被 const 或者 volatile 修饰的以上某种类型。其它所有类型都是完整类型。

比如：

```c
class C; // C is an incomplete type
extern int arr[]; // arr has an incomplete type…c
extern C elems[10]; // elems has an incomplete type
C const* cp; // cp is a pointer to an incomplete type
class C { }; // C now is a complete type (and therefore elems数组
// no longer refer to an incomplete type)
int arr[10]; // arr now has a complete type
```

### 替换，实例化，和特例化

在处理模板相关的代码时，C++编译器必须经常去用模板实参**替换**模板参数。

用实际参数替换模板参数，以从一个模板创建一个常规类、类型别名、函数、成员函数或者变量的过程，被称为“**模板实例化**”。

通过实例化或者不完全实例化产生的实体通常被称为**特例化**（specialization）

- 显式特例化

  ```c
  template<typename T1, typename T2> // 主模板
  class MyClass {
  };
  template<> // 没有未特例化部分
  class MyClass<std::string,float> {
  };
  ```

- 部分特例化

  ```c
  template<typename T> // 主模板
  class MyClass<T,T> {
  };
  template<typename T> // 还有未特例化部分
  class MyClass<bool,T> {
  };
  ```

特例化之前的模板成为**主模板**

### 唯一定义法则

C++语言中对实体的重复定义做了限制。这一限制就是“唯一定义法则（one-definition rule, ODR）”。

- 常规（比如非模板）非 inline 函数和成员函数，以及非 inline 的全局变量和静态数据成员，在整个程序中只能被定义一次（和 C 语言相同）。
- Class 类型（包含 struct 和 union），模板（包含部分特例化，但不能是全特例化），以及 inline 函数和变量，在**一个编译单元中**只能被定义一次，而且不同编译单元间的定义应该相同(重复定义)。

## 元组

它采用了类似于 class 和 struct 的方式来组织数据。比如，一个包含 int，double 和 std::string 的 tuple，和一个包含 int，double 以及 std::string 类型的成员的 struct 类似，只不过 tuple 中的元素是用**位置信息**（比如 0，1，2）索引的，而不是通过名字。元组的位置接口，以及能够容易地从 typelist 构建 tuple 的特性，使得其相比于 struct 更适用于模板元编程技术。

元组的一种用途是可以作为返回值从而实现类似 python 中的多返回值（使用此方法无需定义一个结构体，比较简单）：

```c
#include <tuple>
#include <string>

std::tuple<int, double, std::string> getPerson() {
    // 假设这是从数据库或某个API中获取的数据
    int age = 30;
    double height = 5.11;
    std::string name = "John Doe";
    return std::make_tuple(age, height, name);
}

int main()
{
    auto person = getPerson();
    // 使用序号索引
    std::cout << "Age: " << std::get<0>(person) << ", Height: "
    << std::get<1>(person) << ", Name: " << std::get<2>(person) << std::endl;
}
```

## 引用

- [雾里看花：真正意义上的理解 C++ 模板(Template) - 知乎](https://zhuanlan.zhihu.com/p/655902377)
- [CPP-Templates-2nd--](https://github.com/Walton1128/CPP-Templates-2nd--)
