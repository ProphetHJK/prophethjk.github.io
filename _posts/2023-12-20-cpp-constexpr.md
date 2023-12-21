---
title: "使用 constexpr 将 C++ 常量对象放到 rodata 段中"
author: Jinkai
date: 2023-12-20 08:00:00 +0800
published: true
categories: [教程]
tags: [constexpr, cpp]
---

## 问题

在内存受限条件下，我们希望将一些常量对象放在 text 或 rodata 这种只读段中，而不是 data 或 bss 段，再搭配 XIP 技术来节省内存空间。见[一文看懂内存分段](/posts/segment-ram/)。

在 C 语言中实现该效果非常容易，只需将在声明全局变量时加上 `const` 修饰符，常见的编译器一般会将该变量放置在只读段中。

在 C++ 语言中，GCC 编译器的行为不同，对于声明为 const 的全局非基本类型对象，默认不会将其放在只读段中，这时可以考虑使用 C++ 11 引入的 `constexpr` 修饰符，实测在新版本的 GCC 中可以实现将常量全局对象放置到只读段中。

## constexpr 介绍

constexpr 修饰符是在 C++ 11 标准中引入的，官方规定的含义为 specifies that the value of a variable or function can appear in constant expressions(指定变量或函数的值可以出现在**常量表达式**中)，用于在**编译时**计算表达式的值，并在某些情况下将函数标记为在编译时可执行的常量表达式。

将部分无需在运行时执行的运算放到编译时可以在一定程度上提高运行时性能(可能会以编译时间增加作为代价)，所以在性能敏感系统中应尽可能考虑使用 constexpr。

其与 C 语言中的宏的区别在于其可以理解部分高级语法，比如从 C++14 开始其可以在编译时完成对 if 等条件语句的判断并返回对应分支的结果。可以将 constexpr 理解为加强版的宏，在 C++ 编程中应该尽可能多的使用 constexpr 而不是宏。

```cpp
#define MAX_HEIGHT 720 // 宏变量无法指定类型，默认为 int 类型
constexpr unsigned int max_height = 720;
```

```cpp
constexpr int square(int x) {
    return x * x;
}
constexpr int factorial(int n) {
    // int a = 10; // ERROR in C++11，NO ERROR in C++14
    return (n <= 1) ? 1 : n * factorial(n - 1); // C++ 11 标准规定三元条件运算符可以在编译时展开
}
int main() {
    const int square_result = square(5); // 在编译时计算
    const int factorial_result = factorial(5); // 编译时全部展开并计算
}
```

## 使用条件

**constexpr 函数**必须保证在编译时能够完成计算，因此其定义和使用都有一些限制。例如，递归调用必须在编译时展开，循环次数必须在编译时确定等。不过不同的 C++ 标准对于该限制有所不同，比如从 C++14 开始，可以在编译时确定 if 等条件语句甚至可以在函数中包含局部变量和 for 控制流，而在 C++11 中不行。

**constexpr 变量**必须满足以下要求：

- 其类型必须是 _LiteralType_
- 必须**立即初始化**（定义即赋值）
- 其初始化的完整表达式（包括所有隐式转换、**构造函数调用**等），必须是**常量表达式**（比如构造函数也需要使用 constexpr 修饰，不允许在构造函数调用时使用非常量参数）

同时要保证 GCC 版本 >= 4.7

## 实例代码

```cpp
#include <iostream>
using namespace std;

class Person
{
protected:
    int m_height;

public:
    constexpr Person(int height) : m_height(height) {}
    constexpr Person() : Person(170) {}
    int getHeight() const
    {
        return m_height;
    }
    virtual void action1() const = 0;
    virtual void action2() const
    {
        cout << "Person action2" << endl;
    }
};

class Student : public Person
{
public:
    constexpr Student();
    constexpr Student(char *name, int age, float score);

public:
    void show();
    void setscore(float score);
    char *getname() const;
    int getage() const;
    float getscore() const;
    void action1() const {
        cout<< "Student action1" << endl;
    }

public:
    char *m_name;
    int m_age;
    float m_score;
};

class SpecStudent : public Student
{
public:
    constexpr SpecStudent();
};

constexpr Student::Student(char *name, int age, float score) : m_name(name), m_age(age), m_score(score), Person(171)
{
}
constexpr Student::Student() : Student("name", 10, 12.0)
{
}

constexpr SpecStudent::SpecStudent() : Student("name2", 15, 14.0)
{
}
void Student::show()
{
    cout << m_name << "的年龄是" << m_age << "，成绩是" << m_score << endl;
}
char *Student::getname() const
{
    return m_name;
}
int Student::getage() const
{
    return m_age;
}
void Student::setscore(float score)
{
    m_score = score;
}
float Student::getscore() const
{
    return m_score;
}

constexpr Student stuList[10];
constexpr SpecStudent stu2List[10];

int main()
{
    cout << "ptr:" << stuList << endl;
    cout << "ptr:" << &stuList[9] << endl;
    cout << "ptr:" << stu2List << endl;
    cout << "ptr:" << &stu2List[9] << endl;
    stuList[0].getname();
    int age = 12;
    const Student stu("小明", age, 90.6);
    // constexpr Student stu("小明", age, 90.6); // error
    // stu.show();  //error
    cout << stu.getname() << "的年龄是" << stu.getage() << "，成绩是" << stu.getscore() << endl;

    const Student *pstu = new Student("李磊", 16, 80.5);
    // pstu -> show();  //error
    cout << pstu->getname() << "的年龄是" << pstu->getage() << "，成绩是" << pstu->getscore() << endl;

    return 0;
}
```

输出：

```console
ptr:0x402260
ptr:0x402380
ptr:0x402120
ptr:0x402240
小明的年龄是12，成绩是90.6
李磊的年龄是16，成绩是80.5
```

map 文件：

```console
.rodata         0x0000000000402000      0x3b0
 *(.rodata .rodata.* .gnu.linkonce.r.*)
 .rodata.cst4   0x0000000000402000        0x4 /usr/lib/gcc/x86_64-linux-gnu/8/../../../x86_64-linux-gnu/crt1.o
                0x0000000000402000                _IO_stdin_used
 .rodata._ZNK6Person7action2Ev.str1.1
                0x0000000000402004        0xf /tmp/ccZwN7EM.o
 .rodata._ZNK7Student7action1Ev.str1.1
                0x0000000000402013       0x10 /tmp/ccZwN7EM.o
 .rodata.str1.1
                0x0000000000402023       0x38 /tmp/ccZwN7EM.o
 *fill*         0x000000000040205b        0x5
 .rodata._ZTS6Person
                0x0000000000402060        0x8 /tmp/ccZwN7EM.o
                0x0000000000402060                typeinfo name for Person
 .rodata._ZTI6Person
                0x0000000000402068       0x10 /tmp/ccZwN7EM.o
                0x0000000000402068                typeinfo for Person
 .rodata._ZTS7Student
                0x0000000000402078        0x9 /tmp/ccZwN7EM.o
                0x0000000000402078                typeinfo name for Student
 *fill*         0x0000000000402081        0x7
 .rodata._ZTI7Student
                0x0000000000402088       0x18 /tmp/ccZwN7EM.o
                0x0000000000402088                typeinfo for Student
 .rodata._ZTS11SpecStudent
                0x00000000004020a0        0xe /tmp/ccZwN7EM.o
                0x00000000004020a0                typeinfo name for SpecStudent
 *fill*         0x00000000004020ae        0x2
 .rodata._ZTI11SpecStudent
                0x00000000004020b0       0x18 /tmp/ccZwN7EM.o
                0x00000000004020b0                typeinfo for SpecStudent
 .rodata._ZTV7Student
                0x00000000004020c8       0x20 /tmp/ccZwN7EM.o
                0x00000000004020c8                vtable for Student
 .rodata._ZTV11SpecStudent
                0x00000000004020e8       0x20 /tmp/ccZwN7EM.o
                0x00000000004020e8                vtable for SpecStudent
 *fill*         0x0000000000402108       0x18
 .rodata        0x0000000000402120      0x280 /tmp/ccZwN7EM.o
 .rodata.cst8   0x00000000004023a0       0x10 /tmp/ccZwN7EM.o
```

可以看到打印出的 stuList 的首地址为 0x402040，处于 rodata 段中。

## 引用

- [4131 – The C++ compiler doesn't place a const class object to ".rodata" section with non trivial constructor](https://gcc.gnu.org/bugzilla/show_bug.cgi?id=4131)
- [constexpr specifier (since C++11) - cppreference.com](https://en.cppreference.com/w/cpp/language/constexpr)
