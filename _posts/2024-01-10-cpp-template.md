---
title: "C++ template详解"
author: Jinkai
date: 2024-01-10 08:00:00 +0800
published: true
categories: [教程]
tags: [template, cpp]
---

## 查看预处理后代码的工具

<https://cppinsights.io/>

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

主要目的就是为了减少代码的重复书写（由编译器自动生成），降低错误率。

## 函数模板初探

### 定义模板

```cpp
template<typename T>
T max (T a, T b)
{
  // 如果 b < a, 返回 a，否则返回 b
  return b < a ? a : b;
}
```

### 使用模板

```cpp
#include "max1.hpp"
#include <iostream>
#include <string>
int main()
{
  int i = 42;
  std::cout << "max(7,i): " << ::max(7,i) << '\n';
  double f1 = 3.4;
  double f2 = -6.7;
  std::cout << "max(f1,f2): " << ::max(f1,f2) << '\n';
  std::string s1 = "mathematics";
  std::string s2 = "math";
  std::cout << "max(s1,s2): " << ::max(s1,s2) << '\n';
}

// output:
// max(7,i): 42
// max(f1,f2): 3.4
// max(s1,s2): mathematics
```

> 注意在调用 `max()` 模板的时候使用了作用域限制符`::`。这样程序将会在**全局作用域**中查找 `max()` 模板(不会在自定义的命名空间或者 std 命名空间中查找)。如果不使用，在某些情况下标准库中的 `std::max()` 模板将会被调用，就会与预期不符。不过经过实测，即使不加`::`也不会优先调用`std::max()`，就算强制指定 `using namespace std;` ，也会报模板冲突错误：

```cpp
#include "max1.hpp"
#include <iostream>
#include <string>
using namespace std;
int main() {
  int i = 42;
  std::cout << "max(7,i): " << max(7,i) << '\n';
}
// main.cpp:14:35: error: call of overloaded ‘max(int, int&)' is ambiguous
// 14 |   std::cout << "max(7,i): " << max(7,i) << '\n';
```

在编译阶段，模板并不是被编译成一个可以支持多种类型的实体。而是对每一个用于该模板的类型都会产生一个独立的实体。因此在本例中，`max()`会被编译出**三个实体**，因为它被用于三种类型。这个过程就是模板的实例化，就像分别定义了三个函数，这个过程是自动的，无需程序员干涉。

### 两阶段编译检查(Two-Phase Translation)

- 在模板定义阶段，模板的检查并不包含类型参数的检查。只包含下面几个方面：
  - 语法检查。比如少了分号。
  - 使用了未定义的不依赖于模板参数的名称（类型名，函数名，......）。
  - 未使用模板参数的 static assertions。
- 在模板实例化阶段，为确保所有代码都是有效的，模板会再次被检查，尤其是那些依赖于类型参数的部分

```cpp
template<typename T>
void foo(T t)
{
  undeclared(); // 如果 undeclared()未定义，第一阶段就会报错，因为与模板参数无关
  undeclared(t); //如果 undeclared(t)未定义，第二阶段会报错，因为与模板参数有关
  static_assert(sizeof(int) > 10,"int too small"); // 与模板参数无关，总是报错
  static_assert(sizeof(T) > 10, "T too small"); //与模板参数有关，只会在第二阶段报错
}
```

### 模板参数推断

> 在使用模板函数时，编译器会根据实参的类型推断模板函数的模板类型，并自动实例化出对应参数类型的函数，不过这个推断是有条件的，最重要的条件就是不允许类型转换（除了 decay），特别是一个模板类型对应两个参数时：

```cpp
template<typename T>
T max (T a, T b);
max(4, 7.2); // ERROR：编译器可以选择将T推断为int,这样 7.2 这个实参就必须转为int类型来匹配模板，这是不允许的。同理推断为 double 也不行。
```

在**类型推断的过程**中自动的类型转换是受限制的：

- 如果调用参数是按引用传递的，任何类型转换都不被允许。通过模板类型参数 T 定义的两个参数，它们实参的类型必须完全一样。

  ```cpp
  template<typename T>
  auto max (T& a, T& b);
  ```

- 如果调用参数是按值传递的，那么只有退化（decay）这一类简单转换是被允许的：

  - const 和 volatile 限制符会被忽略，
  - 引用被转换成被引用的类型(此时这个引用退化为被其引用的那个变量)
  - raw array 和函数被转换为相应的指针类型。

  通过模板类型参数 T 定义的两个参数，它们实参的类型在退化（decay）后必须一样。

```cpp
template<typename T>
T max (T a, T b);

int const c = 42;
int i = 1;
max(i, c); // OK: T 被推断为 int，c 中的 const 被 decay 掉
max(c, c); // OK: T 被推断为 int
int& ir = i;
max(i, ir); // OK: T 被推断为 int， ir 中的引用被 decay 掉
int arr[4];
foo(&i, arr); // OK: T 被推断为 int*

// 但是像下面这样是错误的：
max(4, 7.2); // ERROR: 不确定 T 该被推断为 int 还是 double
std::string s;
foo("hello", s); //ERROR: 不确定 T 该被推断为 const[6] 还是 std::string
```

对于错误的情况有三种解决办法：

- 对参数做类型转换

  ```cpp
  max(static_cast<double>(4), 7.2); // OK
  ```

- 显式地指出类型参数 T 的类型，这样编译器就不再会去做类型推导。

  ```cpp
  max<double>(4, 7.2); // OK
  ```

- 指明调用参数可能有不同的类型（多个模板参数）。

  ```cpp
  template<typename T,typename T2>
  T max (T a, T2 b);
  ```

#### 对默认调用参数的类型推断

需要注意的是，类型推断并不适用于默认调用参数。例如：

```cpp
template<typename T>
void f(T = "");
...
f(1); // OK: T 被推断为 int, 调用 f<int> (1)
f(); // ERROR: 无法推断 T 的类型
```

为应对这一情况，你需要给模板类型参数也声明一个默认参数：

```cpp
template<typename T = std::string>
void f(T = "");
...
f(); // OK
```

### 函数模板的优先级和重载

```cpp
// maximum of two int values:
int max (int a, int b)
{
  return b < a ? a : b;
}
// maximum of two values of any type:
template<typename T>
T max (T a, T b)
{
  return b < a ? a : b;
}

int main()
{
  ::max(7, 42); // calls the nontemplate for two ints，直接使用非模板的max，模板max<int>不会被使用
  ::max(7.0, 42.0); // calls max<double> (by argument deduction)，当模板实例化后的函数比非模板更接近要求时，优先使用模板实例化后的函数
  ::max('a', 'b'); // calls max<char> (by argument deduction)，同上
  ::max<>(7, 42); // calls max<int> (by argumentdeduction)，强制使用模板，且模板被推断为max<int>
  ::max<double>(7, 42); // calls max<double> (no argumentdeduction)，强制使用模板max<double>
  ::max('a', 42.7); // calls the nontemplate for two ints，模板无法满足要求，因为类型推断过程不允许除了decay外的类型转换，编译器无法实例化该模板，只能使用非模板的max，然后这两个实参都被隐式转换为int。
}
```

一个非模板函数可以和一个与其同名的函数模板共存，并且这个同名的函数模板可以被实例化为与非模板函数具有相同类型的调用参数。在所有其它因素都相同的情况下，模板解析过程将优先选择**非模板函数**，而不是从模板实例化出来的函数。

编程时必须注意到这种优先选择性，选择的函数的不同会影响程序结果：

```cpp
#include <cstring>
// maximum of two values of any type (call-by-reference)
template <typename T> T const &max(T const &a, T const &b) {
  return b < a ? a : b;
}
// maximum of two C-strings (call-by-value)
char const *max(char const *a, char const *b) {
  return std::strcmp(b, a) < 0 ? a : b;
}
// maximum of three values of any type (call-by-reference)
template <typename T> T const &max(T const &a, T const &b, T const &c) {
  return max(max(a, b), c); // error if max(a,b) uses call-by-value
}
int main() {
  auto m1 = ::max(7, 42, 68); // OK
  char const *s1 = "frederic";
  char const *s2 = "anica";
  char const *s3 = "lucas";
  auto m2 = ::max(s1, s2, s3); // run-time ERROR
}
```

上面的例子中，`max(max(a, b), c);`将会优先选用非模板函数。需要注意的是将一个局部变量(作用域在函数块内)通过引用传递出去会导致悬空引用问题，因为当函数返回时该变量就被销毁了，返回值引用将失败，造成运行时错误，见[按引用返回的问题](/posts/cpp-plus/#按引用返回的问题)。这里 `max(max(a, b), c);`语句的返回值是一个临时变量（声明周期和局部变量相同），而 return 时又是按引用返回，就有这个问题。当 `max(max(a, b), c);` 使用的是上面的函数模板生成的函数时，其返回值也是引用，其生命周期就不归属于这个 max()函数(三个参数的这个)，就不会有该问题。

### 缩写函数模板（C++20）

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

## 类模板

```cpp
#include <cassert>
#include <vector>
    template <typename T>
    class Stack {
private:
  std::vector<T> elems; // elements
public:
  void push(T const &elem); // push element
  void pop();               // pop element
  T const &top() const;     // return top element
  bool empty() const {      // return whether the stack is empty
    return elems.empty();
  }
  static int sa;
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

template <typename T>
int Stack<T>::sa = 0; // 静态成员必须在外部定义
```

### 类模板的特例化

我们知道通过类模板生成出来的所有实例化的类都是符合类模板的格式的，因为这是编译器自动替换模板参数的过程。但有时候我们希望对于部分特定的模板参数(类型)，实例化的类是自定义的一套实现，这就要用到模板的特例化。

> 特例化后的模板还是模板，而不是实例，只不过是原模板的一种特殊化的表示形式，依然需要实例化后才能使用(无论隐式还是显式)

```cpp
Stack<std::string> obj; // 使用的是默认的类模板实例
```

我们希望对于 std::string 类型，类模板的实例是自定义的，而不是通过默认的类模板生成的。通过添加一个`template<>`并在类名后显式制定特例化后的类型即可实现特例化：

```cpp
template<>
class Stack<std::string> {
};

Stack<std::string> obj; // 优先使用的是自定义的类模板实例，这就是特例化
```

#### 多模板参数的部分特例化(偏特例化)

上面的例子属于完全特例化，特例化后的模板已经不带有任何模板参数了，下面介绍偏特例化。

```cpp
template<typename T1, typename T2>
class MyClass {
};
```

所谓部分特例化，就是依然保留部分模板参数，而不是直接使用`template<>`的方式：

```cpp
// 依然使用了一个模板参数，原模板T1和T2都是使用这个模板参数
template<typename T>
class MyClass<T,T> {
};

// 依然使用了一个模板参数，原模板T1是使用这个模板参数，T2直接特例化为int
template<typename T>
class MyClass<T,int> {
};

// 模板参数数量还是两个，不过现在变成了指针类型，对于指针类型的模板参数，现在会优先使用本特例化的模板，而不是原模板
template<typename T3, typename T4>
class MyClass<T3*,T4*> {
};
// 和上面的模板等价，特例化模板的模板参数名称也可以随便取，和原模板相同也可以
template<typename T1, typename T2>
class MyClass<T1*,T2*> {
};
```

特例化后的模板会被优先使用：

```cpp
MyClass< int, float> mif; // uses MyClass<T1,T2>
MyClass< float, float> mff; // uses MyClass<T,T>
MyClass< float, int> mfi; // uses MyClass<T,int>
MyClass< int*, float*> mp; // uses MyClass<T1*,T2*>
```

存在歧义的情况：

```cpp
MyClass< int, int> m; // ERROR: matches MyClass<T,T> and MyClass<T,int>
MyClass< int*, int*> m; // ERROR: matches MyClass<T,T> and MyClass<T1*,T2*>

// 为了消除下面一种情况的歧义，需要使用下面的特例化
template<typename T>
class MyClass<T*,T*> {
};
```

下面代码对一个主模板分化出两种特例化(偏特例化)，其中主模板仅用于声明：

```cpp
// primary helper template:
template<int SZ, bool = isPrime(SZ)>
struct Helper;

// implementation if SZ is not a prime number:
template<int SZ>
struct Helper<SZ, false>
{
  // ...
};

// implementation if SZ is a prime number:
template<int SZ>
struct Helper<SZ, true>
{
  // ...
};

int main(){
  Helper<5> helper; // isPrime表示是否为质数
  // 因为5为质数，所以调用的实际是struct Helper<SZ, true>的实例化
}
```

> 函数模板不支持偏特例化，为了避免与重载冲突。但支持完全特例化。

### 默认类模板参数

和函数模板一样，也可以给类模板的模板参数指定默认值。

```cpp
template<typename T1, typename T2 = int>
class MyClass {
};
```

### 类型别名(Type Aliases)

为了简化给类模板定义新名字的过程，可以使用 using 为类型取个别名：

```cpp
using IntStack = Stack <int>; // alias declaration
void foo (IntStack const& s); // s is stack of ints
IntStack istack[10]; // istack is array of
```

给一个已经存在的类型定义新名字的方式，被称为 type alias declaration。新的名字被称为 type alias

#### 别名模板(Alias Templates)

alias declaration 也可以被模板化，这样就可以给一组类型取一个方便的名字。

```cpp
template<typename T>
using DequeStack = Stack<T, std::deque<T>>

// 下面两者等价
DequeStack<int> obj;
Stack<int, std::deque<int>> obj;
```

#### Suffix_t 类型萃取(Type Traits Suffix_t)

从 C++14 开始，标准库使用上面的技术，给标准库中所有返回一个类型的 type trait 定义了快捷方式。比如为了能够使用：

```cpp
std::add_const_t<T> // since C++14
```

而不是：

```cpp
typename std::add_const<T>::type // since C++11
```

标准库做了如下定义，取了一个带后缀(suffix) `_t` 的别名：

```cpp
namespace std {
  template<typename T>
  using add_const_t = typename add_const<T>::type;
}
```

### 类模板的类型推导

#### 类模板对字符串常量参数的类型推断（Class Template Arguments Deduction with String Literals ）

```cpp
template<typename T>
class Stack {
private:
  std::vector<T> elems; // elements
public:
  Stack () = default;
  Stack (T const& elem) // initialize stack with one element
  : elems({elem}) {
  }
};

Stack stringStack = "bottom"; // Stack<char const[7]> deduced since C++17
```

当参数是按照 T 的**引用**传递的时候（上面例子中接受一个参数的构造函数，是按照引用传递的），参数类型不会被 decay（按值传递才会 decay），也就是说一个裸的数组类型不会被转换成裸指针:

```cpp
Stack< char const[7]> // 按引用传递参数时，推断为数组类型
Stack< char const*> // 而不是裸指针
```

在这个场景下，stack 是作为数据容器来保存一组相同类型的数据的（底层使用了 std::vector），如果类型推断为 `char const[7]` 就不能保存其他的长度为 8 或者其他长度的字符串了，这不是我们想要的。

所以我们将构造函数改为按值传递参数，让参数类型 decay 为指针类型：

```cpp
Stack (T elem) // initialize stack with one element by value
: elems({elem}) { // to decay on class tmpl arg deduction
}
```

#### 推断指引（Deduction Guides）

C++17 引入了自动类型推断，如果情况较为复杂导致编译器难以进行自动推断，可以通过提供“推断指引”来提供额外的模板参数推断规则，或者修正已有的模板参数推断规则。

```cpp
Stack(char const*) -> Stack<std::string>;
```

该语句表示，当类模板参数类型为 `char const *` 时，将其推断为 `std::string` 类型。这个指引语句必须出现在和模板类的定义相同的作用域或者命名空间内。通常它紧跟着模板类的定义。`->`后面的类型被称为推断指引的”guided type”。

此时下面表达式可以正常推断：

```cpp
Stack stringStack1{"bottom"}; // TODO：直接列表初始化不是不允许隐式的char const[7]转到string吗
Stack stringStack2("bottom");
```

实例化后的类如下：

```cpp
class Stack {
private:
  std::vector<std::string> elems; // elements
public:
  Stack (std::string const& elem) // initialize stack with one element
  : elems({elem}) {
}
};
```

重要问题：但对于下面的表达式，无法编译通过：

```cpp
Stack stringStack = "bottom"; // Stack<std::string> deduced, but still not valid
```

其实这个方式的初始化称为[复制初始化 Copy initialization](/posts/cpp-plus/#初始化)，其会调用拷贝构造函数进行初始化，此时需要等号右边**隐式的**生成一个临时的 Stack 对象作为拷贝构造函数的参数。生成临时对象的过程可见[转换构造函数](/posts/cpp-plus/#转换构造函数converting-constructors):

```cpp
// 设想的经过隐式的构造后的stringStack构造方式
Stack stringStack(Stack("bottom"));
```

根据编译器的报错：`不存在从 "const char [7]" 转换到 "Stack<std::string>" 的适当构造函数`，发现这个临时对象无法正常构造，问题就出在 C++ 的一个特性：在使用这种隐式的构造函数(转换构造函数)时不允许发生参数类型的隐式转换，也就是参数类型必须是 std::string，而不是 const char[7]。

为了验证这个结论，我们直接使用显式的方式调用临时对象的构造函数，发现就可以正常执行：

```cpp
Stack stringStack(Stack("bottom"));
Stack stringStack = Stack("bottom");
```

## 非类型模板参数

示例在之前的 Stack 类模板的基础上添加了一个非类型的模板参数，用于表示用户指定的栈列表：

```cpp
template<typename T, std::size_t Maxsize>
class Stack {}
```

### 非类型模板参数的限制

非类型模板参数只能是

- `整形常量`（包含枚举）
- 指向 objects/functions/members 的指针
- objects 或者 functions 的左值引用
- std::nullptr_t（类型是 nullptr）。

> 比如 const char \* 就不行。需要使用 const char[]。

```cpp
template <typename T, std::string name> // 错误，不能直接使用objects
class Stack {}

template <typename T, std::string& name> // 正确
class Stack {}


std::string myname{"hello"}; // 保证模板实参必须是编译时可访问到的，不然无法在编译阶段实例化。
int main()
{
  // std::string myname{"hello"}; // ERROR:不能放在此处。
  Stack<int,myname> obj;
}
```

### 用 auto 作为非模板类型参数的类型

```cpp
template<typename T, auto Maxsize>
class Stack {}

Stack<int,20u> int20Stack; // stack of up to 20 ints，type 为 unsigned int
Stack<std::string,40> stringStack; // stack of up to 40 strings，type 为 int
```

使用 decltype(auto) 定义引用类型的 type:

```cpp
template<decltype(auto) N>
class C {}
int i;
C<(i)> x; // N is int&。加了括号后`(i)`就成了一个左值表达式而不是一个变量，对它decltype后type为左值引用`int&`而不是i本身的类型int
C<i> x1; // N is int。
```

- `template<decltype(auto) N>`

C++14 引入：decltype(auto) 是 C++14 引入的一种类型推导方式，它基于表达式的结果类型进行推导。
类型推导：decltype(auto) 可以推导出包括**引用**在内的精确类型。如果传递的是引用，decltype(auto) 会保留引用类型。
复杂表达式：可以处理更复杂的表达式，并推导出表达式的类型。

- `template<auto N>`

C++17 引入：auto 作为模板非类型参数是 C++17 引入的特性。
类型推导：auto 进行类型推导时，会根据传递的**值**进行推导，但不会保留引用的性质。它只推导出值的类型。
简单表达式：通常用于推导基本的值类型，如整数、浮点数、指针等。

## 变参模板（variadic template）

可以将模板参数定义成能够接受任意多个模板参数的情况。这一类模板被称为变参模板（variadic template）

可以通过调用下面代码中的 print()函数来打印一组数量和类型都不确定的参数：

```cpp
#include <iostream>
void print ()
{}
template<typename T, typename... Types>
void print (T firstArg, Types... args)
{
  std::cout << firstArg << '\n'; // print first argument
  print(args...); // call print() for remaining arguments
}
```

一般我们会将模板第一个参数单独声明(`typename T`)，然后将剩余的参数打包为 `typename... Types` 称为模板参数包（templete parameter pack）。将 `Types... args` 成为函数参数包（function parameter pack）。

> 参数包的展开：像上例中`print(args...);`使用了最简单的展开方式，即使用`...`展开前面的表达式，`args...`展开后即为`arg1,arg2,arg3`(假设就这 3 个)，对应到 `print` 中就是 `print(arg1,arg2,arg3)`。`...`前面的也可以是个稍复杂的表达式，比如`(args+1)...`，表达式就是 `args+1`，那么展开后就是`print(arg1+1,arg2+1,arg3+1)`。后面还会提到 C++17 引入的折叠表达式，展开就会相对复杂些。

可以注意到一般变参模板会和**递归**一起使用。

```cpp
std::string s("world");
print(7.5, "hello", s);

// 首先其被扩展为
print<double, char const*, std::string> (7.5, "hello", s);

// 打印第一个double后，print扩展为
print<char const*, std::string> ("hello", s);

// 打印完第二个 "hello" 后，print扩展为：
print<std::string> (s); // 此时 args 就是空了

// 最后调用手动重载的空参数的 print，这里是一个空实现，然后退出递归
```

上述过程一共产生了 3 个函数模板实例。

关于重载：

```cpp
template<typename T>
void print (T arg)
{
  std::cout << arg << '\n'; //print passed argument
}
// 引入一个非变参函数模板后，此时上述例子中的 print<std::string> (s); 优先使用本模板。
```

### sizeof... 运算符

运算符 `sizeof...` 用于计算参数包的大小，既可以用于模板参数包，也可以用于函数参数包。

```cpp
template<typename T, typename... Types>
void print(T firstArg, Types... args)
{
  std::cout << firstArg << '\n'; //print first argument
  std::cout << sizeof...(Types) << '\n'; //print number of remaining types
  std::cout << sizeof...(args) << '\n'; //print number of remaining args...
}
```

### 折叠表达式(Fold expression)

变参模板使用的核心就是如何展开参数包，我们之间介绍了递归方式展开，此外还有简单的变参表达式展开(缺点是无法建立各个参数间的关联，下一节会讲到)。

从 C++17 开始，提供了一种可以用来计算参数包（可以有初始值）中所有参数运算结果的二元运算符。这样就不用通过**提取参数包第一个参数外加递归**的方式来实现部分计算。

```cpp
template<typename... T>
auto foldSum (T... s) {
  return (... + s); // ((s1 + s2) + s3) ...
}
```

C++17 支持的折叠表达式

|     Fold Expression     |                   Evaluation                   |
| :---------------------: | :--------------------------------------------: |
|     ( ... op pack )     | ((( pack1 op pack2 ) op pack3 ) ... op packN ) |
|     ( pack op ... )     |    ( pack1 op ( ... ( packN-1 op packN )))     |
| ( init op ... op pack ) | ((( init op pack1 ) op pack2 ) ... op packN )  |
| ( pack op ... op init ) |      ( pack1 op ( ... ( packN op init )))      |

> op 就是运算符(operator)的意思，这里应该特指二元运算符

```cpp
#include <iostream>
template<typename... Types>
void print (Types const&... args)
{
    (std::cout << ... << args) << '\n';
}
int main()
{
    print(1, 2.5, "Hello", 'c');
}
```

(std::cout << ... << args)展开使用( init op ... op pack ) 规则，展开后如下：

```cpp
std::cout << 1 << 2.5 << "Hello" << 'c';
```

但缺点是不能给每个输出后添加空格或换行。我们可以将这些基本类型封装来解决问题:

```cpp
template<typename T>
class AddSpace
{
private:
  T const& ref; // refer to argument passed in constructor
public:
  AddSpace(T const& r): ref(r) {
  }
  // 重载默认的<<实现
  friend std::ostream& operator<< (std::ostream& os, AddSpace<T> s) {
    return os << s.ref <<' '; // output passed argument and a space
  }
};
template<typename... Args>
void print (Args... args) {
  ( std::cout << ... << AddSpace<Args>(args) ) << '\n';
}
```

通过将原有的类型封装成自定义的 AddSpace 类型并重载 << 运算符，实现折叠表达式的功能扩展。

其实还有更简单的办法，我们利用逗号表达式的特性，逗号表达式表示执行逗号前语句，但整个表达式的值为逗号后变量：

```cpp
template<typename... Args>
void print (Args... args) {
  // std::cout<<args被执行，且(std::cout<<args,' ')表达式的值为' '(一个空格)，
  ( std::cout << ... << (std::cout<<args,' ')) << '\n';
}
```

二叉树例子：

```cpp
// define binary tree structure and traverse helpers:
struct Node {
  int value;
  Node *left;
  Node *right;
  Node(int i = 0) : value(i), left(nullptr), right(nullptr) {}
};
auto left = &Node::left; // 定义一个指向类成员变量的指针
auto right = &Node::right;
// traverse tree, using fold expression:
template <typename T, typename... TP> Node *traverse(T np, TP... paths) {
  // TP的类型是指向类成员变量的指针，而不是Node或Node*类型
  return (np->*...->*paths); // np ->* paths1 ->* paths2 ...
}
int main() {
  // init binary tree structure:
  Node *root = new Node{0};
  root->left = new Node{1};
  root->left->right = new Node{2};
  // traverse binary tree:
  Node *node = traverse(root, left, right); // 查找root的左节点的右节点，这里的left是上面定义的指向类成员变量的指针
}
```

> `auto leftptr = &Node::left;`，定义一个指向类成员变量的指针，这种类型的指针并不包含实际成员变量的内存地址，仅保存了其在类中的相对位置信息，也就是说需要结合一个实际的对象实例才能定位到真正的内存中的位置。需要使用`.*`或`->*`运算符，比如`Node *root = new Node{0};Node* leftNode = root->*leftptr;`等效于`Node* leftNode = root->left;`，优势在于不需要知道 Node 类内的成员变量的名称，且可以单和对象信息分开传递，就像上面的例子中，traverse 传递的后续参数只要这类指针就行，而无需对象信息(或者是实际的成员变量的内存地址)。

### 变参表达式

在 C++17 之前，有简单的变参展开方式，可以对每个参数进行一定的计算(使用一个表达式)，比如 `(args + 1)...` 就是对每个参数都加 1，展开后的结果依然是逗号分隔的参数列表(arg1+1,arg2+1,arg3+1)。

```cpp
template<typename... T>
void printDoubled (T const&... args)
{
  print((args + args)...);
  // print((args + 1)...); // 每个参数都加1
}
```

上述例子中表达式`((args + args)...)`将每个参数都加上自身

```cpp
printDoubled(7.5, std::string("hello"), std::complex<float>(4,2));
// 展开后
print(7.5 + 7.5, std::string("hello") + std::string("hello"), std::complex<float>(4,2) + std::complex<float>(4,2));
```

变参下标（Variadic Indices）：

```cpp
template<typename C, typename... Idx>
void printElems (C const& coll, Idx... idx)
{
  print (coll[idx]...);
}

std::vector<std::string> coll = {"good", "times", "say", "bye"};
printElems(coll,2,0,3);

// 展开后
print (coll[2], coll[0], coll[3]);
```

上面的例子使用了类型模板，也可以将非类型模板参数(size_t)的方式：

```cpp
template<std::size_t... Idx, typename C>
void printIdx (C const& coll)
{
  print(coll[Idx]...);
}
std::vector<std::string> coll = {"good", "times", "say", "bye"};
printIdx<2,0,3>(coll); // 非类型模板参数不能推断，必须显式指定
```

### 变参类模板

tuple:

```cpp
template<typename... Elements>class Tuple;
Tuple<int, std::string, char> t; // t can hold integer, string, and character
```

variant:

```cpp
template<typename... Types>
class Variant;
Variant<int, std::string, char> v; // v can hold integer, string, or character
```

实例(使用变参类模板实现类列表的保存)：

> 使用 c++20 及以上进行编译

```cpp
#include <cassert>
#include <iostream>
#include <tuple>

// 基类Type
class Type {
public:
  virtual void info() const = 0; // 运行时多态
};

// 示例类型
class IntType : public Type {
public:
  consteval IntType() { x = 1; }
  void info() const override { std::cout << "IntType" << std::endl; }
  // 不同的返回值，不能使用运行时多态
  consteval int getValue() const { return x; };

private:
  int x;
};

class DoubleType : public Type {
public:
  consteval DoubleType() { x = 2.1; }
  void info() const override { std::cout << "DoubleType" << std::endl; }
  // 不同的返回值，不能使用运行时多态
  consteval double getValue() const { return x; };

private:
  double x;
};

// 用于编译时多态的 ObjectType 类
template <size_t N>
class ObjectType {
public:
  // 仅构造函数使用变参模板，构造完成后子类信息丢失
  template <typename... Types>
  consteval ObjectType(Types... args)
      : size(sizeof...(Types)), type_list{args...} {
    static_assert(sizeof...(Types) == N, "Number of types must match N");
  }

  // 获取指定索引的类型(运行时)
  const Type *getType(int8_t index) const {
    assert(index >= 0 && index < N); // 确保索引合法
    return type_list[index];
  }

protected:
  size_t size;
  const Type *type_list[N]; // 保存传入的 Type 指针数组
};

// 推断指引，通过构造函数的参数数量推断{变量模板}参数N
template <typename... Types>
ObjectType(Types... args) -> ObjectType<sizeof...(args)>;

// 用于编译时多态的 ObjectTypeConst 类，通过使用<typename... Types>可以在编译时保存子类的信息
template <typename... Types>
class ObjectTypeConst : public ObjectType<sizeof...(Types)> {
public:
  consteval ObjectTypeConst(Types... args)
      : ObjectType<sizeof...(Types)>(args...) {}

  template <size_t index>
  using TypeAt = typename std::tuple_element<index, std::tuple<Types...>>::type;

  // 获取指定索引的类型(编译时)
  template <size_t index>
  consteval auto getType() const {
    static_assert(index < sizeof...(Types), "Index out of bounds");
    return static_cast<TypeAt<index>>(this->type_list[index]);
  }
};

constexpr IntType intType;
constexpr DoubleType doubleType;

// 使用示例
int main() {
  // 初始化ObjectType对象，传入具体的Type指针
  constexpr ObjectType obj1(&intType, &doubleType);
  constexpr ObjectTypeConst obj2(&intType, &doubleType);

  // 测试运行时多态(虚函数)
  obj1.getType(0)->info(); // 输出 "IntType"
  obj1.getType(1)->info(); // 输出 "DoubleType"

  // 测试编译时多态(模板)
  auto value1 = obj2.getType<0>()->getValue();
  auto value2 = obj2.getType<1>()->getValue();

  std::cout << "value1:" << value1 << "\nvalue2:" << value2 << std::endl;

  return 0;
}
```

上述示例还给出了模板的另一个重要用途：编译时多态。

### 变参推断指引

推断指引也可以是变参的。比如在 C++标准库中，为 std::array 定义了如下推断指引：

```cpp
template<typename _Tp, std::size_t _Nm>
  struct array {}

namespace std {
  template<typename T, typename... U>
    array(T, U...)
      -> array<enable_if_t<(is_same_v<T, U> && ...), T>, (1 + sizeof...(U))>;
}
```

推断过程：

```cpp
std::array a{42,45,77};
// 推断为
std::array<int, 3> a{42,45,77};
```

其中对 array 的第一个参数的操作 `std::enable_if<>` 内有一个折叠表达式，展开后如下：

```cpp
is_same_v<T, U> && ...
// 展开后为
is_same_v<T, U1> && is_same_v<T, U2> && is_same_v<T, U3>
```

如果结果是 false（也就是说 array 中元素不是同一种类型），推断指引会被弃用，总的类型推断失败。这样标准库就可以确保在推断指引成功的情况下，所有元素都是同一种类型。

### 变参基类及其使用

在进行多继承时，基类列表也可以是变参的。

阅读下面几个材料来理解下面的例子：

- 关于[仿函数](/posts/cpp-plus/#仿函数functor)
- 关于[隐藏继承的函数](/posts/cpp-plus/#隐藏继承的函数)
- unordered_set 需要 4 个模板参数，其中后面三个有默认的实现：
  - Key: 存储元素的类型。
  - Hash: 哈希函数对象类型，默认是 `std::hash<Key>`。
  - Pred: 相等比较函数对象类型，默认是 `std::equal_to<Key>`。
  - Alloc: 分配器对象类型，默认是 `std::allocator<Key>`。

```cpp
#include <string>
#include <unordered_set>
class Customer {
private:
  std::string name;

public:
  Customer(std::string const &n) : name(n) {}
  std::string getName() const { return name; }
};
// 仿函数，unordered_set需要这样一个相等比较函数对象类型
struct CustomerEq {
  bool operator()(Customer const &c1, Customer const &c2) const {
    return c1.getName() == c2.getName();
  }
};
// 仿函数，unordered_set需要这样一个哈希函数对象类型
struct CustomerHash {
  std::size_t operator()(Customer const &c) const {
    return std::hash<std::string>()(c.getName());
  }
};
// 这里的意图是从多个基类中继承括号运算符重载函数，整合到这一个类中，通过参数数量不同进行重载
template <typename... Bases>
struct Overloader : Bases... { // sturct继承时如果不指定权限，默认使用public继承
  using Bases::operator()...; // OK since C++17，这里using的用法是引入基类的成员函数,防止被隐藏
};
int main() {
  // combine hasher and equality for customers in one type:
  using CustomerOP = Overloader<CustomerHash, CustomerEq>;
  std::unordered_set<Customer, CustomerHash, CustomerEq> coll1;
  // 这个整合后的Overloader类型同时包含了两个仿函数，直接传给unordered_set，其内部会自动做选择
  std::unordered_set<Customer, CustomerOP, CustomerOP> coll2;
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
   void foo(const T &t, const Types&... args); // args：“函数参数包（含有0或多个参数）”

   foo(i, s, 42, d); // 包中有三个参数
   foo(s, 42, "hi"); // 包中有两个参数
   foo(d, s); // 包中有一个参数
   foo("hi"); // 空包
   ```

## 基础技巧

### typename 用法

关键字 `typename` 在 C++ 标准化过程中被引入进来，用来澄清模板内部的一个标识符代表的是某种类型，而不是数据成员。(也可以使用等效的 class 关键字 `template<class T>`，但为了避免歧义，还是尽量用 typename)

```cpp
// class MyClass2 {
//   public:
//     using SubType = int;
// }

template<typename T>
class MyClass {
  public:
    // ...
    void foo() {
    typename T::SubType* ptr;
  }
};
```

上例中`typename T::SubType* ptr;` 中的 typename 用于澄清 SubType 是定义在 class T 内的一个**类型**(而不是成员)，且 ptr 是一个 SubType 类型指针。

如果没有 typename 的话，SubType 会被假设成一个非类型成员（比如 static 成员或者一个枚举常量，亦或者是内部嵌套类或者 using 声明的 public 别名）。这样这个表达式可能就理解为了 T::SubType(static 成员) 和 ptr 变量 的乘法：

```cpp
T::SubType * ptr;
```

### 零初始化

对于**基础类型**，比如 int，double 以及指针类型，由于它们没有默认构造函数，因此它们不会被默认初始化成一个有意义的值。比如任何未被初始化的局部变量的值都是未定义的(直接初始化不适用于基础类型)：

```cpp
template<typename T>
void foo()
{
  T x; // x has undefined value if T is built-in type
}
```

为了在使用模板时让基础类型和自定义 class 都能得到正确初始化，有如下两种办法：

方式一：一种初始化的方法被称为“**值初始化**（value initialization）”，它要么调用一个对象已有的构造函数，要么就用零来初始化这个对象。通过下面你的写法就可以保证即使是内置类型也可以得到适当的初始化（基础类型因为没有构造函数，会被初始化为 0）：

```cpp
template<typename T>
void foo()
{
  T x{}; // x is zero (or false) if T is a built-in type
}
```

方式二：另一种方式是显式的初始化，也能达到将基础类型初始化为 0 的效果：

```cpp
template<typename T>
void foo()
{
  T x = T(); // x is zero (or false) if T is a built-in type
}
```

值得注意的是在 C++17 之前，如果某个类的拷贝初始化对应的构造函数被声明为 explicit，则 `T x = T();` 这种初始化方式将无法使用，因为声明了 explicit 后，该拷贝构造函数只能被显式调用，不能被隐式调用（这里通过把等号的形式转为拷贝构造的方式也算是隐式调用了）。：

```cpp
class MyClass{
  private:
  int a;
  public:
  MyClass()=default;
  explicit MyClass(MyClass& obj){
    a = obj.a;
  }
};

int main()
{
  MyClass x = MyClass(); // error before C++17: no matching function for call to ‘MyClass::MyClass(MyClass)’
}
```

C++17 引入了强制性复制省略（Mandatory Copy Elision）特性，指编译器在某些情况下必须省略对对象的复制或移动操作，从而直接构造对象到其最终位置。所以在 C++17 下编译上述代码时，x 会直接窃取右边的临时对象，根本不会去调用拷贝构造函数，所以即使其被声明为 explicit 也不会编译错误。

> 强制性复制省略（Mandatory Copy Elision）至少包括以下两项内容：
>
> 1. 返回值优化（RVO）：即通过将返回值所占空间的分配地点从被调用端转移至调用端的手段来避免拷贝操作。返回值优化包括具名返回值优化（NRVO）与无名返回值优化（URVO），两者的区别在于返回值是具名的局部变量还是无名的临时对象。
> 2. 右值拷贝优化：当某一个类类型的临时对象被拷贝赋予同一类型的另一个对象时，通过直接利用该临时对象的方法来避免拷贝操作。

所以还是尽可能使用方式一，无论什么 C++ 版本都能使用。

为了满足上面的两种初始化方式，对于自定义类模板，需要在默认构造函数初始化成员(值初始化)：

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

注意不可以对函数的默认参数使用这一方式，比如：

```cpp
template<typename T>
void foo(T p{}) { //ERROR
}
```

正确方式：

```cpp
template<typename T>
void foo(T p = T{}) { //OK (must use T() before C++11)
}
```

### 尽可能使用 this->

对于类模板，如果它的基类也是依赖于模板参数的，对被继承的基类的成员的访问应该使用 `this->` 或 `Base<T>::` 的方式，不要直接使用成员名称，因为这两者不一定等效(尽管不使用类模板时这两者就是等效的)：

```cpp
template<typename T>
class Base {
public:
  void bar();
};
template<typename T>
class Derived : Base<T> {
public:
  void foo() {
    bar(); // calls external bar() or error
    // Option 1: Use 'this->' to explicitly specify that bar() is a member of the base class
    // this->bar();

    // Option 2: Use 'Base<T>::' to explicitly specify that bar() is from the base class
    // Base<T>::bar();
  }
};
```

上面例子中对 bar() 的调用永远不会使用基类中的 bar()，而是会去找其他外部的 bar 定义。这和编译器策略有关，编译器在解析模板类时使用[两阶段编译检查](#两阶段编译检查two-phase-translation)，第一阶段时所有模板都未实例化，所以如果不显式指定 `this->` 或 `Base<T>::`，编译器不会自动假定 bar 函数是基类里的函数，也无法去基类里查找(因为还没有实例化)。

### 使用裸数组或者字符串常量的模板

在[模板参数推断](#模板参数推断)一节已经介绍了如果按引用传递，参数类型不会退化(char const[6])；按值传递会退化(const char\*)。

可以考虑使用处理裸数组的专用模板：

```cpp
template<typename T, int N, int M>
bool less (T(&a)[N], T(&b)[M])
{
  for (int i = 0; i<N && i<M; ++i)
  {
    if (a[i]<b[i]) return true;
    if (b[i]<a[i]) return false;
  }
  return N < M;
}
```

当像下面这样使用该模板的时候：

```cpp
int x[] = {1, 2, 3};
int y[] = {1, 2, 3, 4, 5};
std::cout << less(x,y) << '\n';
```

`less<>`中的 T 会被实例化成 int，N 被实例化成 3，M 被实例化成 5。字符串常量也是一种特殊的裸数组，同理。

下面的代码展示了对数组所做的所有可能的重载：

```cpp
#include <iostream>
template<typename T>
struct MyClass; // 主模板
template<typename T, std::size_t SZ>
struct MyClass<T[SZ]> // partial specialization for arrays of known bounds
{
  static void print()
  {
    std::cout << "print() for T[" << SZ << "]\n";
  }
};
template<typename T, std::size_t SZ>
struct MyClass<T(&)[SZ]> // partial spec. for references to arrays of known bounds
{
  static void print() {
    std::cout << "print() for T(&)[" << SZ <<"]\n";
  }
};
template<typename T>
struct MyClass<T[]> // partial specialization for arrays of unknown bounds
{
  static void print() {
    std::cout << "print() for T[]\n";
  }
};
template<typename T>
struct MyClass<T(&)[]> // partial spec. for references to arrays of unknown bounds
{
  static void print() {
    std::cout << "print() for T(&)[]\n";
  }
};
template<typename T>
struct MyClass<T*> // partial specialization for pointers
{
  static void print() {
    std::cout << "print() for T*\n";
  }
};
```

上面的代码针对以下类型对 MyClass<>做了特化：边界已知和未知的数组，边界已知和未知的数组的引用，以及指针。它们之间互不相同，在各种情况下的调用关系如下:

```cpp
#include "arrays.hpp"
template<typename T1, typename T2, typename T3>
void foo( int a1[7], int a2[], // pointers by language rules
          int (&a3)[42], // reference to array of known bound
          int (&x0)[], // reference to array of unknown bound
          T1 x1, // passing by value decays
          T2& x2, T3&& x3) // passing by reference
{
  MyClass<decltype(a1)>::print(); // uses MyClass<T*>
  MyClass<decltype(a2)>::print(); // uses MyClass<T*> a1, a2 退化成指针
  MyClass<decltype(a3)>::print(); // uses MyClass<T(&)[SZ]>
  MyClass<decltype(x0)>::print(); // uses MyClass<T(&)[]>
  MyClass<decltype(x1)>::print(); // uses MyClass<T*>
  MyClass<decltype(x2)>::print(); // uses MyClass<T(&)[]>
  MyClass<decltype(x3)>::print(); // uses MyClass<T(&)[]>
}

int main()
{
  int a[42];
  MyClass<decltype(a)>::print(); // uses MyClass<T[SZ]>
  extern int x[]; // forward declare array
  MyClass<decltype(x)>::print(); // uses MyClass<T[]>
  foo(a, a, a, x, x, x, x);
}

int x[] = {0, 8, 15}; // define forward-declared array
```

注意，根据语言规则，如果形参被声明为数组的话，那么它的真实类型是指针类型:

```cpp
void foo(int a1[7], int a2[]) // 其实参数类型是指针类型，方括号的数字没有任何意义
// void foo(int* a1,int* a2) // 等效

void foo(int (&a3)[42]) // 按引用传递时，形参不是指针类型，方括号内的边界检查有效
```

而且针对未知边界数组定义的模板，实参可以用于不完整类型，比如：

```cpp
extern int i[]; // 可以作为实参
```

### 成员模板

类的成员也可以是模板，对嵌套类和成员函数都是这样。

我们以之前的 Stack 类模板为例，存在问题：两个不同类型的 Stack 间不能互相赋值：

```cpp
Stack<int> intStack1, intStack2; // stacks for ints
Stack<float> floatStack; // stack for floats

intStack1 = intStack2; // OK: stacks have same type
floatStack = intStack1; // ERROR: stacks have different type
```

默认的赋值运算符要求等号两边的对象类型必须相同，因此如果两个 Stack 之间的元素类型不同的话，这一条件将得不到满足。

- 实现方式一

此时，我们手动重载这个赋值运算符，需要利用到**成员模板**：

```cpp
template <typename T>
class Stack {
private:
  std::deque<T> elems; // elements
public:
  void push(T const &); // push element
  void pop();           // pop element
  T const &top() const; // return top element
  bool empty() const {  // return whether the stack is empty
    return elems.empty();
  }
  // assign stack of elements of type T2
  template <typename T2> // 成员模板
  Stack &operator=(Stack<T2> const &);
};
```

以上代码中有如下两点改动：

1. 赋值运算符的参数是一个元素类型为 T2 的 stack。
2. 新的模板使用 `std::deque<>`作为内部容器。这是为了方便新的赋值运算符的定义。

赋值运算符重载函数的实现如下：

```cpp
template<typename T>
template<typename T2>
Stack<T>& Stack<T>::operator= (Stack<T2> const& op2)
{
  Stack<T2> tmp(op2); // create a copy of the assigned stack
  elems.clear(); // remove existing elements
  while (!tmp.empty()) { // copy all elements
    elems.push_front(tmp.top());
    tmp.pop();
  }
  return *this;
}
```

核心思路就是利用 deque (双向队列)的特性，先拷贝一份 op2 防止影响原来的 op2，将新 op2 的元素从栈顶弹出(队列的尾部弹出)，压入 op1 的栈中(从队列的首部插入)，最终 op1 的布局将和原来的 op2 相同。

- 实现方式二

```cpp
template <typename T>
class Stack {
private:
  std::deque<T> elems; // elements
public:
  Void push(T const &); // push element
  void pop();           // pop element
  T const &top() const; // return top element
  bool empty() const {  // return whether the stack is empty
    return elems.empty();
  }
  // assign stack of elements of type T2
  template <typename T2> Stack &operator=(Stack<T2> const &);
  // to get access to private members of Stack<T2> for any type T2:
  template <typename> friend class Stack;
};
```

> `template <typename> friend class Stack;` 这句中省略了模板名称，一般我们都会用 `<typename T>` 指定一个名称 T，但因为这里不需要，所以可以省略。

首先将所有其他类型的 Stack 声明为友元，这样所有类型的 Stack 间都能互相访问私有的 elems。这样的话等号运算符重载函数的实现会简单很多：

```cpp
template<typename T>
template<typename T2>
Stack<T>& Stack<T>::operator= (Stack<T2> const& op2)
{
  elems.clear(); // remove existing elements
  // 直接使用insert方法批量拷贝
  elems.insert(elems.begin(), // insert at the beginning
  op2.elems.begin(), // all elements from op2
  op2.elems.end());
  return *this;
}
```

使用上述两个方法后，就可以实现不同类型间的赋值了：

```cpp
Stack<int> intStack; // stack for ints
Stack<float> floatStack; // stack for floats

floatStack = intStack; // OK: stacks have different types,
// 但是元素类型还是 float,赋值的时候把int都转换称float了
```

- 实现方式三

将 elems 的类型也模板参数化，从实现方式二可以看出其不一定要是 deque 类型的，甚至是 vector 也行。

```cpp
template <typename T, typename Cont = std::deque<T>>
class Stack {
private:
  Cont elems; // elements
public:
  void push(T const &); // push element
  void pop();           // pop element
  T const &top() const; // return top element
  bool empty() const {  // return whether the stack is empty
    return elems.empty();
  }
  // assign stack of elements of type T2
  template <typename T2, typename Cont2>
  Stack &operator=(Stack<T2, Cont2> const &);
  // to get access to private members of Stack<T2> for any type T2:
  template <typename, typename> friend class Stack;
};
```

赋值运算符实现：

```cpp
template<typename T, typename Cont>
template<typename T2, typename Cont2>
Stack<T,Cont>& Stack<T,Cont>::operator= (Stack<T2,Cont2> const& op2)
{
  elems.clear(); // remove existing elements
  elems.insert(elems.begin(), // insert at the beginning
  op2.elems.begin(), // all elements from op2
  op2.elems.end());
  return *this;
}
```

这样 `Stack<int, std::vector<int>>` 也能正常使用。

#### 成员模板的特例化

成员函数模板也可以被全部或者部分地特例化:

```cpp
class BoolString {
private:
  std::string value;

public:
  BoolString(std::string const &s) : value(s) {}
  template <typename T = std::string>
  T get() const { // get value (converted to T)
    return value;
  }
};
```

完全特例化：

```cpp
template<>
inline bool BoolString::get<bool>() const {
  return value == "true" || value == "1" || value == "on";
}
```

> 因为这个定义要放在头文件中(将模板的定义都放在头文件中是一种最佳实践)，为了避免重复定义错误，需要加上 inline 修饰符。

使用方式：

```cpp
std::cout << std::boolalpha;
BoolString s1("hello");
std::cout << s1.get() << '\n'; //prints hello，未使用特例化版本
std::cout << s1.get<bool>() << '\n'; //prints false
BoolString s2("on");
std::cout << s2.get<bool>() << '\n'; //prints true
```

#### 特殊成员函数的模板

copy 构造函数以及 move 构造函数也可以被模板化。

#### template 的使用

某些情况下，在调用成员模板的时候需要**显式地指定其模板参数的类型**。

但因为模板参数列表开始的这个 `<` 和比较运算符 `<` 很容易混淆。这时候就需要使用关键字 template 来确保符号 `<` 会被理解为模板参数列表的开始，而不是一个比较运算符。

```cpp
template<unsigned long N>
void printBitset (std::bitset<N> const& bs) {
  // bs的to_string()方法是个成员函数模板
  std::cout << bs.template to_string<char,
  std::char_traits<char>,
  std::allocator<char>>();
}
```

#### 泛型 lambdas 和成员模板

在 C++14 中引入的泛型 lambdas，是一种成员模板的简化。对于一个简单的计算两个任意类型参数之和的 lambda：

```cpp
[] (auto x, auto y) {
  return x + y;
}
```

lambdas 本质上就是一个函数对象，泛型 lambdas 无非就是进行了模板化，其实际表现形式是：

```cpp
class SomeCompilerSpecificName {
public:
  SomeCompilerSpecificName(); // constructor only callable by compiler
  template<typename T1, typename T2>
    auto operator() (T1 x, T2 y) const {
    return x + y;
  }
};
```

### 变量模板

> 现在四种模板都介绍到了：class templates, function templates,variable templates,and alias templates

变量模板是 C++14 引入的一个功能，允许开发者为变量定义模板化的版本。

基本语法：

```cpp
template<typename T>
constexpr T pi{3.1415926535897932385};
```

注意，和其它几种模板类似，这个定义最好不要出现在函数内部或者块作用域内部。

其可以有默认参数类型：

```cpp
template<typename T = long double>
constexpr T pi = T{3.1415926535897932385};
```

可以像下面这样使用默认类型或者其它类型：

```cpp
std::cout << pi<> << '\n'; //outputs a long double
std::cout << pi<float> << '\n';
// 但不可以不用尖括号
std::cout << pi << '\n'; //ERROR
```

同样可以用**非类型参数**对变量模板进行参数化，也可以将非类型参数用于参数器的初始化：

```cpp
#include <array>
#include <iostream>
template <int N>
std::array<int, N> arr{}; // array with N elements, zero-initialized
template <typename T, int N>
T arr1[N] = {};
template <auto N>
constexpr decltype(N) dval = N; // type of dval depends on passed value

int main() {
  std::cout << dval<'c'> << '\n'; // N has value

  arr<10>[0] = 42; // sets first element of global arr
  for (std::size_t i = 0; i < arr<10>.size(); ++i) { // uses values set in arr
    std::cout << arr<10>[i] << '\n';
  }
}
```

注意在不同编译单元间初始化或者遍历 arr 的时候，使用的都是同一个全局作用域里的 `std::array<int, 10> arr`，所以相同模板参数的实例只会存在一个。

#### 用于数据成员的变量模板

变量模板的一种应用场景是，用于定义代表类模板成员的变量模板:

```cpp
template<typename T>
class MyClass {
public:
  static constexpr int max = 1000;
};
```

```cpp
template<typename T>
int myMax = MyClass<T>::max;

// 然后这样使用
auto i = myMax<std::string>;

// 取代
auto i = MyClass<std::string>::max;
```

TODO: 看不出有什么用

#### 类型萃取 Suffix_v

> 和 [Suffix_t](#suffix_t-类型萃取type-traits-suffix_t) 区分一下

从 C++17 开始，标准库用变量模板为其用来产生一个值（布尔型）的类型萃取定义了简化方式。比如为了能够使用：

```cpp
std::is_const_v<T> // since C++17
```

而不是：

```cpp
std::is_const<T>::value //since C++11
```

标准库做了如下定义，为它们取了一个带有后缀(suffix) `_v` 的别名：

```cpp
namespace std {
  template<typename T>
  constexpr bool is_const_v = is_const<T>::value;
}
```

### 模板参数模板

模板参数也可以模板化

下面的例子就需要指定两次 int 类型，而且还需要程序员保证这两个类型相同，不能填成 `Stack<int, std::vector<float>>`

```cpp
Stack<int, std::vector<int>> vStack; // integer stack that uses a vector
```

模板参数的模板化：

```cpp
template<typename T,
template<typename Elem> class Cont = std::deque>
class Stack {
private:
  Cont<T> elems; // elements
public:
  void push(T const&); // push element
  void pop(); // pop element
  T const& top() const; // return top element
  bool empty() const { // return whether the stack is empty
    return elems.empty();
  }
};
```

`template<typename Elem> class Cont = std::deque` 这是一个类模板的定义，从 C++17 开始，才可以用 `typename` 取代了这里的 `class`。毕竟这是在尖括号内，使用 typename 也合理，不知道为什么 C++17 才开始支持。因为模板参数 Elem 没有被用到，可以省略：

```cpp
template<typename> class Cont = std::deque
```

成员函数也要做相应的修改，必须将第二个模板参数指定为模板参数模板：

```cpp
template<typename T, template<typename> class Cont>
void Stack<T,Cont>::push (T const& elem)
{
  elems.push_back(elem); // append copy of passed elem
}
```

使用模板参数模板后就能解决开始的问题：

```cpp
Stack<int, std::vector> vStack; // integer stack that uses a vector
```

#### 模板参数模板的参数匹配

上面的例子仅在 C++17 以上才有效，因为 Cont 模板参数个数和 `std::deque` 不同，`std::deque` 实际需要两个参数，只不过一个可以默认。所以在 C++17 也必须仿照 std::deque 声明两个模板参数，第二个参数就置一个默认值：

```cpp
template<typename T, template<typename Elem,
typename Alloc = std::allocator<Elem>> class Cont = std::deque>
class Stack {
private:
  Cont<T> elems; // elements
};
```

### 最终例子

```cpp
#include <cassert>
#include <deque>
#include <memory>
template <typename T, template <typename Elem, typename = std::allocator<Elem>>
                      class Cont = std::deque>
class Stack {
private:
  Cont<T> elems; // elements
public:
  void push(T const &); // push element
  void pop();           // pop element
  T const &top() const; // return top element
  bool empty() const {  // return whether the stack is empty
    return elems.empty();
  }
  // assign stack of elements of type T2
  template <typename T2,
            template <typename Elem2, typename = std::allocator<Elem2>>
            class Cont2>
  Stack<T, Cont> &operator=(Stack<T2, Cont2> const &);
  // to get access to private members of any Stack with elements of type T2 :
  template <typename, template <typename, typename> class>
               friend class Stack;
};

template <typename T, template <typename, typename> class Cont>
void Stack<T, Cont>::push(T const &elem) {
  elems.push_back(elem); // append copy of passed elem
}
template <typename T, template <typename, typename> class Cont>
void Stack<T, Cont>::pop() {
  assert(!elems.empty());
  elems.pop_back(); // remove last element
}
template <typename T, template <typename, typename> class Cont>
T const &Stack<T, Cont>::top() const {
  assert(!elems.empty());
  return elems.back(); // return copy of last element
}
template <typename T, template <typename, typename> class Cont>
template <typename T2, template <typename, typename> class Cont2>
Stack<T, Cont> &Stack<T, Cont>::operator=(Stack<T2, Cont2> const &op2) {
  elems.clear();                  // remove existing elements
  elems.insert(elems.begin(),     // insert at the beginning
               op2.elems.begin(), // all elements from op2
               op2.elems.end());
  return *this;
}
```

```cpp
#include "stack9.hpp"
#include <iostream>
#include <vector>
int main() {
  Stack<int> iStack;   // stack of ints
  Stack<float> fStack; // stack of floats
  // manipulate int stack
  iStack.push(1);
  iStack.push(2);
  std::cout << "iStack.top(): " << iStack.top() << '\n';
  // manipulate float stack:
  fStack.push(3.3);
  std::cout << "fStack.top(): " << fStack.top() << '\n';
  // assign stack of different type and manipulate again
  fStack = iStack;
  fStack.push(4.4);
  std::cout << "fStack.top(): " << fStack.top() << '\n';
  // stack for doubless using a vector as an internal container
  Stack<double, std::vector> vStack;
  vStack.push(5.5);
  vStack.push(6.6);
  std::cout << "vStack.top(): " << vStack.top() << '\n';
  vStack = fStack;
  std::cout << "vStack: ";
  while (!vStack.empty()) {
    std::cout << vStack.top() << ' ';
    vStack.pop();
  }
  std::cout << '\n';
}
```

程序输出如下：

```console
iStack.top(): 2
fStack.top(): 3.3
fStack.top(): 4.4
vStack.top(): 6.6
vStack: 4.4 2 1
```

## 移动语义和 enable_if<>

移动语义（move semantics）是 C++11 引入的一个重要特性。在 copy 或者赋值的时候，可以通过它将源对象中的内部资源 move（“steal”）到目标对象，而不是 copy 这些内容。当然这样做的前提是源对象不在需要这些内部资源或者状态（因为源对象将会被丢弃）。

### 完美转发(Perfect Forwarding)

参数的转发指的是一个函数将自己的参数转发到另一个函数：

```cpp
void g(int a){}
void f(int a)
{
  // f 将自己的参数转发到 g 中
  g(a);
}
```

有时我们希望参数在被转发时保留一些基本特性：

- 可变对象被转发之后依然可变。
- const 对象被转发之后依然是 const 的。
- 可移动对象（可以从中窃取资源的对象）被转发之后依然是可移动的。

```cpp
#include <iostream>
#include <utility>
class X {};

// 定义三个 g 函数用于接收不同类型的参数
void g(X &) { std::cout << "g() for variable\n"; }
void g(X const &) { std::cout << "g() for constant\n"; }
void g(X &&) { std::cout << "g() for movable object\n"; }

// let f() forward argument val to g():
void f(X &val) {
  g(val); // val is non-const lvalue => calls g(X&)
}
void f(X const &val) {
  g(val); // val is const lvalue => calls g(X const&)
}
void f(X &&val) {
  // 虽然这里的 val 看着是右值引用，但实际上val是一个非常量左值
  // 如果不使用 std::move()的话，在第三个 f()中调用的将是 g(X&)而不是 g(X&&)。
  g(std::move(val)); // val is non-const lvalue => needs ::move() to call g(X&&)
}

// 因为定义了3种类型的g()函数，上面三种转发方式会自动选择适合的g()函数，参数的信息得到保留

int main() {
  X v;       // create variable
  X const c; // create constant
  f(v);      // f() for nonconstant object calls f(X&) => calls g(X&)
  f(c);      // f() for constant object calls f(X const&) => calls g(X const&)
  f(X());    // f() for temporary calls f(X&&) => calls g(X&&)
  f(std::move(v)); // f() for movable variable calls f(X&&) => calls g(X&&)
}
```

现在我们尝试将三个 f() 函数用模板统一起来：

```cpp
template<typename T>
void f (T val) {
  g(val);
}
```

因为没有主动使用 `std::move()`，就会出现无法转发右值引用的问题。

基于这一原因，C++11 引入了特殊的规则(std::forward)对参数进行完美转发（perfect forwarding）。实现这一目的的惯用方法如下：

```cpp
template<typename T>
void f (T&& val) { // 使用模板参数特有的万能引用
  g(std::forward<T>(val)); // perfect forward val to g()
}
```

注意 `std::move` 没有模板参数，并且会无条件地移动其参数；而 `std::forward<>` 会跟据被传递参数的具体情况决定是否“转发”其潜在的移动语义(只有当形参要求为右值引用时才将实参转为右值)。

还要注意 `X &&`(如 int &&) 和 `T &&` 虽然语法类似，但是两个完全不同的概念：

- 具体类型 X 的 `X&&` 声明了一个**右值引用**参数。只能被绑定到一个可移动对象上（一个 prvalue，比如临时对象，一个 xvalue，比如通过 std::move()传递的参数）。它的值总是可变的，而且总是可以被“窃取”。
- 模板参数 T 的 `T&&` 声明了一个转发引用（亦称**万能引用**）。可以被绑定到可变、不可变（比如 const）或者可移动对象上(实例化后对于不同的参数类型有不同的实例)。在函数内部这个参数也可以是可变、不可变或者指向一个可以被窃取内部数据的值。

### 特殊成员函数模板

特殊成员函数也可以是模板，比如构造函数(特殊成员函数就是那种没有返回值的函数)

```cpp
#include <iostream>
#include <string>
#include <utility>
class Person {
private:
  std::string name;

public:
  // constructor for passed initial name:
  // 接受一个左值的构造函数
  explicit Person(std::string const &n) : name(n) {
    std::cout << "copying string-CONSTR for ’" << name << "’\n";
  }
  // 接受一个右值的构造函数
  explicit Person(std::string &&n) : name(std::move(n)) {
    std::cout << "moving string-CONSTR for ’" << name << "’\n";
  }
  // copy and move constructor:
  // 拷贝构造函数
  Person(Person const &p) : name(p.name) {
    std::cout << "COPY-CONSTR Person ’" << name << "’\n";
  }
  // 移动构造函数
  Person(Person &&p) : name(std::move(p.name)) {
    std::cout << "MOVE-CONSTR Person ’" << name << "’\n";
  }
};

int main() {
  std::string s = "sname";
  Person p1(s);     // init with string object => calls copying string-CONSTR
  Person p2("tmp"); // init with string literal => calls moving string-CONSTR
  Person p3(p1);    // copy Person => calls COPY-CONSTR
  Person p4(std::move(p1)); // move Person => calls MOVE-CONST
}
```

从[完美转发](#完美转发perfect-forwarding)一节中，我们知道可以用模板整合前两个构造函数：

```cpp
template<typename T>
explicit Person(T&& n) : name(std::forward<T>(n)) {
    std::cout << "TMPL-CONSTR for ’" << name << "’\n";
  }
```

注意该方式带来了一个问题：

```cpp
std::string s = "sname";
Person p1(s);
Person p3(p1); // ERROR
```

原因是 `Person p3(p1);` 匹配了模板生成的 `Person (Person& p)` 而不是上面的正确的拷贝构造函数，name 不能赋值为一个 Person 对象，所以报错。我们可以通过手动定义一个 `Person (Person& p)` 这样的拷贝构造函数，防止模板生成该实例。当然还有马上提到 `std::enable_if<>` 也可以。

### 通过 std::enable_if<> 禁用模板

从 C++11 开始，通过 C++标准库提供的辅助模板 std::enable_if<>，可以在某些编译期条件下忽略掉函数模板。

`std::enable_if<>`是一种**类型萃取**（type trait），它会根据一个作为其（第一个）模板参数的编译期表达式决定其行为：

- 如果这个表达式结果为 true，它的 type 成员会返回一个类型：

  - 如果没有第二个模板参数，返回类型是 void。

    ```cpp
    template<typename T>
    typename std::enable_if<(sizeof(T) > 4)>::type
    foo() {
    }
    // 比如如果 sizeof(T) > 4 时，因为没有第二个参数，实例化后类型就为 void
    void foo() {}
    ```

  - 否则，返回类型是其第二个参数的类型。(上面的例子就是)

    ```cpp
    template<typename T>
    typename std::enable_if<(sizeof(T) > 4), T>::type
    foo() {
    }

    // 使用 suffix_t 简化
    template<typename T>
    std::enable_if_t<(sizeof(T) > 4), T>
    foo() {
    }
    ```

- 如果表达式结果 false，则其成员类型是未定义的。根据模板的一个叫做 SFINAE（substitute failure is not an error，替换失败不是错误，TODO:后面介绍）的规则，这会导致包含 `std::enable_if<>` 表达式的函数模板被忽略掉。

更加优雅的方式是单独为这个判断定义一个模板参数：

```cpp
template<typename T, typename = std::enable_if_t<(sizeof(T) > 4)>>
void foo() {
}
```

这样的话后面这个模板参数是默认的，也不用手动填，只是用来判断该模板是否生效。当无效时忽略该模板的实例化。

再更进一步就是利用别名模板起个别名：

```cpp
template<typename T>
using EnableIfSizeGreater4 = std::enable_if_t<(sizeof(T) > 4)>;

template<typename T, typename = EnableIfSizeGreater4<T>>
void foo() {
}
```

### 使用 enable_if<>

现在解决[特殊成员函数模板](#特殊成员函数模板)最后遗留的问题：

```cpp
template<typename T, typename =
std::enable_if_t<std::is_convertible_v<T, std::string>>>
Person(T&& n);
```

这样当推断出来的 T 类型不为 `std::string` 时，该模板不会实例化。

### 禁用某些成员函数

成员函数模板一般不能用来实例化 copy/move 构造函数，类总是优先使用自定义构造函数或默认构造函数:

```cpp
class C {
public:
  template<typename T>
  C (T const&) {
    std::cout << "tmpl copy constructor\n";
  }
};
```

上例中这个模板实例化后确实可以实现 copy 构造函数的功能，但是实际在执行拷贝构造时永远不会调用这个实例。

```cpp
C x;
C y{x}; // still uses the predefined copy constructor (not the member template)
```

就算删掉 copy 构造函数也不行，这样只会报错说 copy 构造函数被删除了。

原因就是通过 `C(C const &) = delete;` 删除 copy 构造函数并不彻底，声明还在，要通过 `C(C const volatile&) = delete;` 把声明也彻底删除。

```cpp
class C
{
public:
  // user-define the predefined copy constructor as deleted
  // (with conversion to volatile to enable better matches)
  C(C const volatile&) = delete;
  // implement copy constructor template with better match:
  template<typename T>
  C (T const&) {
    std::cout << "tmpl copy constructor\n";
  }
};
```

通过上面这种方式，就可以实现用成员函数模板实例出 copy 构造函数的功能。

### 使用 concept 简化 enable_if<>表达式

上面我们用 `enable_if<>` 的用途就是限制成员函数模板的实例化，这种方式其实并不优雅，且含义模糊。现在有了新的 concept 特性，专门用于定义实例化规则：

```cpp
template<typename STR>
requires std::is_convertible_v<STR,std::string>
  Person(STR&& n) : name(std::forward<STR>(n)) {
}
```

可以单独定义一个通用的 concept：

```cpp
template<typename T>
concept ConvertibleToString = std::is_convertible_v<T,std::string>;

// 这样使用一个已经定义过的 concept
template<typename STR>
requires ConvertibleToString<STR>
Person(STR&& n) : name(std::forward<STR>(n)) {
}
// 或这样使用
template<ConvertibleToString STR>
Person(STR&& n) : name(std::forward<STR>(n)) {
}
```

## 按值传递还是按引用传递？

见[按值传递和按引用传递参数](/posts/cpp-plus/#按值传递和按引用传递参数)

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

## 模板实战

### 包含模式

常规的代码结构存在问题：

```cpp
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
  std::cout << typeid(x).name() << '\n';
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

```cpp
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
  std::cout << typeid(x).name() << '\n';
}
#endif //MYFIRST_HPP
```

这种组织模板相关代码的方法被称为“包含模式”。但这种方式会让头文件变得臃肿，增加了 include 时的成本和编译时间，不过目前没有更好的解决办法（非官方的预编译头文件特性可能可以缓解该问题）。

## 基本术语

### 类模板和模板类

一般叫类模板

### 声明和定义

“声明”是一个 C++概念，它将一个名称**引入**或者再次引入到一个 C++作用域内:

```cpp
class C; // a declaration of C as a class
void f(int p); // a declaration of f() as a function and p as a named parameter
extern int v; // a declaration of v as a variable
```

注意，在 C++中虽然宏和 goto 标签也都有名字，但是它们并不是声明。

对于声明，如果其细节已知，或者是需要申请相关变量的存储空间，那么声明就变成了定义。对于 class 类型的定义和函数定义，意味着需要提供一个包含在{}中的主体，或者是对函数使用了=default/=delete。对于变量，如果进行了**初始化**或者**没有使用 extern**，那么声明也会变成定义:

```cpp
class C {}; // definition (and declaration) of class C
void f(int p) { //definition (and declaration) of function f()
  std::cout << p << '\n';
}
extern int v = 1; // an initializer makes this a definition for v
int w; // global variable declarations not preceded by extern are also definitions
```

> 正如 `int w;` 这样没有 extern 修饰的声明也被视为定义，其会分配空间。而如果有 extern 修饰，则允许其不分配空间仅作为声明使用。

作为扩展，**如果一个类模板或者函数模板有包含在`{}`中的主体的话，那么声明也会变成定义。**

声明：

```cpp
template<typename T>
void func (T);
```

定义：

```cpp
template<typename T>
class S {}
```

#### 完整类型和非完整类型（complete versus incomplete types）

非完整类型是以下情况之一：

- 一个被声明但是还没有被定义的 class 类型。
- 一个没有指定边界的数组。
- 一个存储非完整类型的数组。
- Void 类型。
- 一个底层类型未定义或者枚举值未定义的枚举类型。
- 任何一个被 const 或者 volatile 修饰的以上某种类型。

比如：

```cpp
class C; // C is an incomplete type
extern int arr[]; // arr has an incomplete type...c
extern C elems[10]; // elems has an incomplete type,因为C没有定义，整体的空间分配还不能确定
C const* cp; // cp is a pointer to an incomplete type
class C { }; // C now is a complete type (and therefore elems no longer refer to an incomplete type)
int arr[10]; // arr now has a complete type
C elems[10]; // 注意：如果要正确使用elems，需要在此处真正定义，也就是分配空间
```

其它所有类型都是完整类型。

### 替换，实例化，和特例化

在处理模板相关的代码时，C++编译器会尝试去用模板实参**替换**模板参数。

用实际参数替换模板参数，以从一个模板创建一个常规类、类型别名、函数、成员函数或者变量的过程，被称为模板的**实例化**。实例化可以由编译器自动完成，也可以由程序员显式完成。

隐式实例化（编译器自动完成）：

```cpp
template <typename T>
class MyClass {
public:
    void display(T a);
};

template <typename T>
void MyClass<T>::display(T a){
    return;
}

// template class MyClass<int>; // 无需显式进行模板实例化
MyClass<int> obj; // 在首次使用该模板时编译器会自动进行模板实例化

int main(){obj.display(3);}
```

显式实例化（当类模板声明和定义放在不同位置时，需要程序员显式完成实例化）：

```cpp
// MyClass.h
#pragma once
template <typename T>
class MyClass {
public:
    void display(T a);
};

// MyClass.cpp
#include "MyClass.h"
#include <iostream>
template <typename T> void MyClass<T>::display(T a){
    std::cout<<a<<std::endl;
    return;
}

template class MyClass<int>; // 此句不能省略，因为MyClass.cpp和main.cpp并没有关联关系，省略后此处不知道如何对display进行实例化。

// main.cpp
#include "MyClass.h"
MyClass<int> obj;
int main(){
  obj.display(3);
}
```

上面说的都是生成完整的定义的情况，如果生成的是一个声明而不是定义，那么我们可以称其为模板的**不完全实例化**（incomplete instantiation）

#### 特例化

通过实例化或者**不完全实例化**产生的实体，或是由程序员显式进行特殊替换完后的实体通常被称为**特例化**（specialization）

- 显式特例化（程序员显式进行特殊替换，使用`templete<>`方式）

  ```cpp
  template<typename T1, typename T2> // 主模板
  class MyClass {
  };
  template<> // 没有未特例化部分
  class MyClass<std::string,float> {
  };
  ```

- 部分特例化

  ```cpp
  template<typename T1, typename T2> // 主模板
  class MyClass {
  };
  template<typename T> // 部分特例化1
  class MyClass<T,T> {
  };
  template<typename T> // 部分特例化2
  class MyClass<bool,T> {
  };
  ```

  该情况下，匹配将会按照"最特殊化匹配"，也就是匹配最接近的、特例化程度最高的模板：

  ```cpp
  MyClass<int> obj; // 匹配部分特例化1
  MyClass<bool> obj2; // 匹配部分特例化2？
  ```

特例化之前的模板称为**主模板**

### 唯一定义法则

C++语言中对实体的重复定义做了限制。这一限制就是“唯一定义法则（one-definition rule, ODR）”。

- 常规（比如非模板）非 inline 函数和成员函数，以及非 inline 的全局变量和静态数据成员，在整个程序中只能被定义一次（和 C 语言相同）。
- Class 类型（包含 struct 和 union），模板（包含部分特例化，但不能是全特例化），以及 inline 函数和变量，在**一个编译单元中**只能被定义一次，而且不同编译单元间的定义应该相同(重复定义)。

## 元组

它采用了类似于 class 和 struct 的方式来组织数据。比如，一个包含 int，double 和 std::string 的 tuple，和一个包含 int，double 以及 std::string 类型的成员的 struct 类似，只不过 tuple 中的元素是用**位置信息**（比如 0，1，2）索引的，而不是通过名字。元组的位置接口，以及能够容易地从 typelist 构建 tuple 的特性，使得其相比于 struct 更适用于模板元编程技术。

元组的一种用途是可以作为返回值从而实现类似 python 中的多返回值（使用此方法无需定义一个结构体，比较简单）：

```cpp
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

## 编译期编程

### SFINAE

SFINAE(Substitution Failure Is Not An Error, 替换失败不是错误)是使用模板编程时经常需要利用到的一个重要特性。

在引入了模板后，我们可以将编译过程分为三步：

- 检查模板合法性和匹配度

  将模板实参带入模板中检查有效性和匹配度，如果发现该模板无效，可能是这个模板并不是为了这个用途，也可能是这个模板就是写错了，此时由于 SFINAE 特性，该模板被忽略，不会报错。

  ```cpp
  // number of elements in a raw array:
  template<typename T, unsigned N>
  std::size_t len (T(&)[N])
  {
    return N;
  }
  // number of elements for a type having size_type:
  template<typename T>
  typename T::size_type len (T const& t)
  {
    return t.size();
  }

  int main()
  {
    int a[10]; // a是个裸数组
    /*
     * 当使用len模板函数时，发现有两个模板函数都叫len,符合要求。
     * 然后代入模板实参类型，发现使用第二个模板时T没有size_type内置类型，
     * 所以第二个模板不合法，该模板被忽略。此时最匹配的模板就是第一个了
     */
    std::cout << len(a); // OK: 匹配第一个模板
    std::cout << len("tmp"); //OK: 匹配第一个模板

    int* p;
    // 如过参数是裸指针，不符合第一个模板函数的参数类型，而且该类型也没有size_type内置类型，
    // 所以两个都不匹配。
    std::cout << len(p); // ERROR: no matching len() function found
  }
  ```

- 找到合法且最匹配的模板后，进行实例化，也就是生成相应代码。如果上一步没有找到匹配的模板，则不会实例化任何的模板。
- 进行编译。如果第一步没有找到合适的模板，第二步也不会生成任何代码，则会在此时报错：无法找到相应的 len 函数。

SFINAE 的初衷应该是一个模板可能会用于特定的用途，如果编译器尝试使用该模板时发现不合法，可能仅仅是因为用途不匹配，而不是该模板有错误，所以不应该报错。

后来人们开始利用这个特性来实现一些其他功能，比如故意添加限制条件来让一个模板在某一个用途下产生错误，而无法生成，在该情况下编译器只能使用其他的重载。

显然这并不是 SFINAE 的初衷，所以 C++ 提出了`std:enable_if<>`的概念，专门用于所谓的`条件实例化`：

```cpp
namespace std {
  class thread {
  public:
    template<typename F, typename... Args>
    explicit thread(F&& f, Args&&... args);
  };
}
```

在上面例子中，我们希望当 F 的类型为 `std::thread`(也就是自身)时 SFINAE 掉这个构造函数，强制其使用 copy 或 move 构造函数。此时如果利用 SFINAE，我们会想到在 thread 的实现中故意让 F 为 `std::thread` 时产生错误，让该模板在阶段一就无效。

如果使用 `std:enable_if<>`，就会简单得多：

```cpp
namespace std {
  class thread {
  public:
    template<typename F, typename... Args,
             typename =
             std::enable_if_t<!std::is_same_v<std::decay_t<F>,thread>>>
    explicit thread(F&& f, Args&&... args);
  };
}
```

上面例子中使用了一个`typename = std::enable_if_t<!std::is_same_v<std::decay_t<F>,thread>>`的模板参数，当 is_same_v 为正确时，通过取反的操作，enable_if_t 内的判断条件为错误，此时该模板就无效。虽然其本质也是利用了 SFINAE，但就不需要用户专门想办法让 F 为 thread 时怎么让该模板无效了。

### 编译期 if

另一种实现选择性的实例化的方式就是使用 `constexpr if`，只有符合条件的分支才会被实例化：

```cpp
template <typename Iterator, typename Distance>
void advanceIter(Iterator &x, Distance n) {
  if constexpr (IsRandomAccessIterator<Iterator>) {
    // implementation for random access iterators:
    x += n; // constant time
  } else if constexpr (IsBidirectionalIterator<Iterator>) {
    // implementation for bidirectional iterators:
    if (n > 0) {
      for (; n > 0; ++x, --n) { // linear time for positive n
      }
    } else {
      for (; n < 0; --x, ++n) { // linear time for negative n
      }
    }
  } else {
    // implementation for all other iterators that are at least input iterators:
    if (n < 0) {
      throw "advanceIter(): invalid iterator category for negative n";
    }
    while (n > 0) { // linear time for positive n only
      ++x;
      --n;
    }
  }
}
```

### 扩展：模板类成员函数的不完全实例化

如果一个类模板的成员函数从未被使用过，那么它甚至不会被实例化--编译器根本不会查看它，也许只是进行**语法检查(syntax checking)**而已。

```cpp
#include <iostream>

class Array {
public:
  int at(int index) { return 1; }
};

class Structure {
public:
};

template <typename T>
class Entity {
private:
  T type;

public:
  Entity(T &type) : type(type) {}
  int element(int index) { return type.at(index); }
};

class EntityStructure {
private:
  Structure type;

public:
  EntityStructure(Structure &type) : type(type) {}
  // int element(int index) { return type.at(index); } // error
};

int main() {
  Array arr;
  Entity<Array> entity_array(arr);
  std::cout << entity_array.element(1) << std::endl;

  Structure stru;
  Entity<Structure> entity_struct(stru);
  //   std::cout << entity_struct.element(1) << std::endl; // error
}
```

在上面的代码中，有个类模板 `Entity`，当其模板参数为 Structure 时，因为 Structure 并没有 at()函数，所以 element 函数在实例化的语义检查时就会出现错误：找不到 type 的 at()函数。就如同 `EntityStructure` 的情况。

但是由于不完全实例化这个特性，在进行语义检查前，因为 `element()` 函数没有被使用，编译器就会直接跳过该函数的语义检查，也不会去实例化它。最终生成的类模板实例不会有这个函数。

当然语法检查可能会发生，如果 element() 内出现语法错误，还是有可能会报错的。

> 可见《Morden C++ Design》 1.8 Optional Functionality Through Incomplete Instantiation
>
> It gets even better. C++ contributes to the power of policies by providing an interesting feature. If a member function of a class template is never used, it is not even instantiated—the compiler does not look at it at all, except perhaps for syntax checking.
>
> According to the C++ standard, the degree of syntax checking for unused template functions is up to the implementation. The compiler does not do any semantic checking—for example, symbols are not looked up.

## 引用

- [雾里看花：真正意义上的理解 C++ 模板(Template) - 知乎](https://zhuanlan.zhihu.com/p/655902377)
- [CPP-Templates-2nd--](https://github.com/Walton1128/CPP-Templates-2nd--)
- [C++可变参数模板的展开方式](https://blog.csdn.net/albertsh/article/details/123978539)
