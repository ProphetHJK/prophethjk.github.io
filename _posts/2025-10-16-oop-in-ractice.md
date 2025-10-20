---
title: "面向对象编程(OOP)实战论"
date: 2025-10-16 08:00:00 +0800
published: true
categories: [教程]
tags: [C, oop]
---

## 前言

本文将通过一个实际的案例，通过需求分析、代码编写、OOP 优化的方式来阐述 OOP 在软件开发中的实际用处

本文案例将使用 C 语言进行编写，以此表明 OOP 是一种泛用的编程思想，并不是只能应用在 C++/python 之类的面向对象语言上。Linux 内核就用到了大量的面向对象的思想，但它是完全使用 C 语言编写的

本文编写时尽可能考虑到了无面向对象基础的读者，但推荐无基础读者在观看本文之前先看 [面向对象编程(OOP)的 C 语言实现](/posts/c-oop/)

## 需求分析

### 自动轮显模式需求

自动轮显：电能表上电默认显示方式为自动循环显示模式，表计在运行超过**轮显周期**后自动切换到**下一屏**的显示，如当前只设置了**一个轮显项，则不切换**。

```c
// 无封装实现
uint8_t autoScrollMode_scrollIntervals; // 轮显周期(秒)
uint8_t autoScrollMode_page; // 当前屏号
uint8_t autoScrollMode_maxPage; // 最大屏数
void autoScrollMode_nextPage()
{
    autoScrollMode_page++;
    if(autoScrollMode_page >= autoScrollMode_maxPage)
    {
        autoScrollMode_page = 0;
    }
    return;
}
```

至此，我们完成了该需求的一种实现方式

#### 使用封装优化

但是可以发现这些变量名称比较长，不直观，易出错，我们可以考虑将它们封装一下：

```c
typedef struct {
    uint8_t scrollIntervals; // 轮显周期(秒)
    uint8_t page; // 当前屏号
    uint8_t maxPage;
} AutoScrollMode;

// 每次加 1，溢出时归 0，0 表示第一屏
void AutoScrollMode_nextPage(AutoScrollMode* this)
{
    this->page++;
    if(this->page >= this->maxPage)
    {
        this->page = 0;
    }
    return;
}

// 使用时
AutoScrollMode autoScrollModeObject;
AutoScrollMode_nextPage(&autoScrollModeObject);
```

通过该例，可以引申出 2 个基本概念：

- 类(Class)：定义了一件事物的抽象特点。类的定义包含了数据的形式以及对数据的操作
- 对象(Object)：是类的实例（Instance）

现在介绍面向对象的第一个关键概念：

- 封装：将彼此之间有联系的变量和函数放在一起

> 比如你去餐馆吃饭，老板给你介绍他们家的招牌菜，用的是什么食材、工艺、调料等等细节，描绘的栩栩如生。但是光听描述可填不饱肚子，就让老板赶紧把菜做出来。老板对菜的介绍就是类，是一种抽象的概念，用来描述一个事物(对应了程序中不占用内存的概念)，根据描述做出来的菜，就是对象，可以真正用来吃的。而且菜可以做多份，服务给各个不同的客人，对应了对象可以有多个，每个可以用于不同目的。

使用 C++ 实现的封装：

```cpp
struct AutoScrollMode {
    uint8_t scrollIntervals; // 轮显周期(秒)
    uint8_t page; // 当前屏号
    uint8_t maxPage;
    void nextPage();
};

AutoScrollMode::nextPage()
{
    page++;
    if(page >= maxPage)
    {
        page = 0;
    }
    return;
}
```

C 语言可以实现类似的语法，但要增加一个函数指针，导致每个对象的空间都要变大，一般不采取这种方式：

```c
typedef struct {
    uint8_t scrollIntervals; // 轮显周期(秒)
    uint8_t page; // 当前屏号
    uint8_t maxPage;

    void (*nextPage)(AutoScrollMode*);
} AutoScrollMode;

AutoScrollMode autoScrollMode{.nextPage = AutoScrollMode_nextPage};
```

> C++ 中的类的成员函数默认包含一个 `this 指针`，函数实现中的类成员变量也默认有 `this->` 的引用。C 语言完全可以实现面向对象，只是有些不太方便的地方，C++ 就是为了解决这个问题的。

#### 构造函数

对 C 语言来说，我们一般使用值初始化或默认初始化来初始化一个对象实例：

```c
typedef struct {
    uint8_t scrollIntervals;
    uint8_t page;
    uint8_t maxPage;
} AutoScrollMode;

AutoScrollMode autoScrollMode_default; // 默认初始化
AutoScrollMode autoScrollMode{0,0,5};  // 值初始化
```

但值初始化的表达能力不够，只能赋值，不能在初始化的时候执行一些动作(比如动态计算某些初始化值,判断合法性等)，所以我们引入构造函数代替值初始化：

```cpp
void AutoScrollMode_ctor(AutoScrollMode* this, uint8_t maxPage)
{
    this->scrollIntervals = 0;
    this->page = 0;
    if(maxPage > 10)
    {
        assert(0);
    }
    else
    {
        this->maxPage = maxPage;
    }
}
```

其中，`scrollIntervals` 和 `page` 使用默认的初始化值，而 `maxPage` 使用用户提供的值，同时增加了范围的限定。

引入构造函数后，我们将不再使用值初始化的方式：

```c
AutoScrollMode autoScrollMode;  // 值初始化
AutoScrollMode_ctor(&autoScrollMode, 5);
```

### 按键轮显模式需求

键显模式: 从第一个键显项开始显示。键显模式下**不自动切换**显示项，此时按显示按键，在键显项中**按顺序切换**显示项。**超过键显时间**（可通信配置，单位为秒）未按键，电能表切换到自动轮显模式，并从第一个轮显项开始显示。

```c
typedef struct{
    uint8_t timeout; // 超时时间(秒)
    uint8_t page; // 当前屏号
    uint8_t maxPage;
} KeyScrollMode;
// 每次加 1，溢出时归 0，0 表示第一屏
void KeyScrollMode_nextPage(KeyScrollMode* this)
{
    this->page++;
    if(this->page >= this->maxPage)
    {
        this->page = 0;
    }
    return;
}
```

对对象进行操作，完成需求：

```c
AutoScrollMode autoScrollMode;
KeyScrollMode keyScrollMode;

int main()
{
    void* currMode = &autoScrollMode; // 当前模式

    // 系统参数
    uint32_t now;
    bool keyPressed;
    uint8_t idleTime;
    while(true)
    {
        if(currMode == &autoScrollMode) // 如果当前是AutoScrollMode
        {
            if(now % autoScrollMode.scrollIntervals == 0)
            {
                // 翻页间隔时间到达
                AutoScrollMode_nextPage(&autoScrollMode);
            }
        }
        else if(currMode == &keyScrollMode) // 如果当前是KeyScrollMode
        {
            if(keyPressed == true)  // 按键被按下
            {
                KeyScrollMode_nextPage(&keyScrollMode);
                keyPressed = false;
                idleTime = 0;
            }
            else
            {
                idleTime++;
                // 超时时间到达，返回autoScrollMode
                if(idleTime > keyScrollMode.timeout)
                {
                    currMode = &autoScrollMode;
                }
            }
        }
    }
}
```

可以发现代码中有很多的重复：page、maxPage 两个成员变量是重复的，nextPage 函数的实现也是重复的。

## 使用继承优化

为了解决代码重复问题，我们对相同点做抽象：

```c
typedef struct {
    uint8_t page;
    uint8_t maxPage;
} ScrollMode;
void ScrollMode_nextPage(ScrollMode* this)
{
    this->page++;
    if(this->page >= this->maxPage)
    {
        this->page = 0;
    }
    return;
}

typedef struct {
    ScrollMode super;
    uint8_t scrollIntervals;
} AutoScrollMode;

typedef struct {
    ScrollMode super;
    uint8_t timeout;
} KeyScrollMode;
```

构造函数也使用继承的结构：

```c
void ScrollMode_ctor(ScrollMode* this, uint8_t maxPage)
{
    this->page = 0;
    this->maxPage = maxPage;
}

void AutoScrollMode_ctor(AutoScrollMode* this, uint8_t maxPage,
                    uint8_t scrollIntervals)
{
    ScrollMode_ctor(&this->super, maxPage);
    this->scrollIntervals = scrollIntervals;
}

void KeyScrollMode_ctor(KeyScrollMode* this, uint8_t maxPage,
                    uint8_t timeout)
{
    ScrollMode_ctor(&this->super, maxPage);
    this->timeout = timeout;
}
```

main 函数也做相应修改：

```diff
- AutoScrollMode_nextPage(&autoScrollMode);
+ ScrollMode_nextPage(&autoScrollMode.super);

- KeyScrollMode_nextPage(&keyScrollMode);
+ ScrollMode_nextPage(&keyScrollMode.super);
```

> 从该实例中也能发现封装是继承的基础。

### 需求扩展

新增一个类型“低功耗按键显示模式”，要求每隔一定时间自动翻页，且超过一定时间后能自动退出该模式：

```c
typedef struct {
    ScrollMode super;
    uint8_t timeout; // 超时时间(秒)
    uint8_t scrollIntervals; // 轮显周期(秒)
} LowPowerAutoScrollMode;
```

```c
LowPowerAutoScrollMode lowPowerAutoScrollMode;

else if(currMode == &lowPowerAutoScrollMode) // 如果当前是KeyScrollMode
{
    if(now % lowPowerAutoScrollMode.scrollIntervals == 0)
    {
        // 翻页间隔时间到达
        ScrollMode_nextPage((ScrollMode*)currMode);
    }
    idleTime++;
    // 超时时间到达，返回autoScrollMode
    if(idleTime > lowPowerAutoScrollMode.timeout)
    {
        currMode = &autoScrollMode;
    }
}
```

> 关于 super 成员的位置：在 C 语言的 struct 中，第一个成员的内存地址和 struct 本身是一样的，所以 `&autoScrollMode` 和 `&autoScrollMode.super` 的值是一样的，所以 `ScrollMode_nextPage((ScrollMode*)currMode);` 和 `ScrollMode_nextPage(&currMode->super);` 可以互相替代。但是如果采用后一种写法，对 super 的位置并没有要求，可以把它放在最后一个成员的位置上。但为了实现多态，这里将其放在了第一位。

## 多态的应用

现在我们添加显示页面的逻辑，每个模式要显示的内容不同，键显模式需要显示当前页号，单独写出它们的实现：

```c
// 自动滚动显示模式获取显示项
void AutoScrollMode_displayPage(AutoScrollMode* this)
{
    static const char* displayList[] = {
        "autoScrollModePage1",
        "autoScrollModePage2",
        "autoScrollModePage3",
        // ...
    };

    printf("%s\n", displayList[this->super.page]);
    return;
}

// 按键滚动显示模式获取显示项
void KeyScrollMode_displayPage(KeyScrollMode* this)
{
    static const char* displayList[] = {
        "keyScrollModePage1",
        "keyScrollModePage2",
        "keyScrollModePage3",
        "keyScrollModePage4",
        // ...
    };

    printf("%d:%s\n", this->super.page, displayList[this->super.page]);
    return;
}
```

使用时：

```c
void display(void* currMode)
{
    if(currMode == &autoScrollMode)
    {
        AutoScrollMode_displayPage((AutoScrollMode*)currMode);
    }
    else if(currMode == &keyScrollMode)
    {
        KeyScrollMode_displayPage((KeyScrollMode*)currMode);
    }
}

int main(
    while(true)
    {
        // ...
        // 屏幕每两秒刷新一次
        if(now % 2 == 0)
        {
            display(currMode);
        }
    }
)
```

还能不能使用继承呢？不行，它们相似之处比较少，难以进行抽象。所以我们使用面向对象中最重要的概念：多态。首先在父类中创建一个虚函数：

```c
struct ScrollMode {
    uint8_t page;
    uint8_t maxPage;

    void (*displayPage)(ScrollMode*); // 虚函数(virtual function)
};

void ScrollMode_ctor(ScrollMode* this, uint8_t maxPage, void (*displayPage)(ScrollMode*))
{
    this->page = 0;
    this->maxPage = maxPage;
    this->displayPage = displayPage;
}

void AutoScrollMode_ctor(AutoScrollMode* this, uint8_t maxPage,
                    uint8_t scrollIntervals)
{
    // 绑定虚函数
    ScrollMode_ctor(&this->super, maxPage, AutoScrollMode_displayPage);
    this->scrollIntervals = scrollIntervals;
}

// 无论传进来的currMode是哪个对象，都会调用其对应的displayPage的实现
void display(void* currMode)
{
    ((ScrollMode*)currMode)->displayPage((ScrollMode*)currMode);
    return;
}

int main()
{
    AutoScrollMode autoScrollMode;
    AutoScrollMode_ctor(&autoScrollMode, 5, 10);
    // ...
}
```

这样做的好处是，display 函数更加简洁，且后续新增显示模式时，display 函数都无需改动。

C 语言对多态的实现比较繁琐，每次定义一个对象都要重新绑定其虚函数

```cpp
struct ScrollMode {
    uint8_t page;
    uint8_t maxPage;

    virtual void displayPage(); // virtual关键字修饰虚函数
};

struct AutoScrollMode: public ScrollMode{
    // ...
    virtual void displayPage(){
        // ...
        return;
    }
};
struct KeyScrollMode: public ScrollMode{
    // ...
    virtual void displayPage(){
        // ...
        return;
    }
};

AutoScrollMode autoScrollMode;
KeyScrollMode keyScrollMode;

int main()
{
    // 无需手动绑定
    // autoScrollMode.super.getAttribute = AutoScrollMode_getAttribute;
    // keyScrollMode.super.getAttribute = KeyScrollMode_getAttribute;
}

void display(void* currMode)
{
    ((ScrollMode*)currMode)->displayPage();
    return;
}
```

### 继续扩展需求

继续完成“低功耗按键显示模式”需求，所要做的很简单，只是添加其对应的 `displayPage()` 虚函数的实现即可：

```c
// 按键滚动显示模式获取显示项
void LowPowerAutoScrollMode_displayPage(LowPowerAutoScrollMode* this)
{
    static const char* displayList[] = {
        "lowPowerAutoScrollModePage1",
        "lowPowerAutoScrollModePage2",
        // ...
    };

    printf("%d:%s\n",this->super.page, displayList[this->super.page]);
    return;
}

int main()
{
    // ...
    lowPowerAutoScrollMode.super.displayPage = LowPowerAutoScrollMode_displayPage;
    // ...
}
```

至此，我们使用面向对象的**封装**、**继承**、**多态**完成了滚动显示的需求的实现。

## 总结

面向对象是一种编程思想，用来解决代码重复和类型扩展难的问题。想要理解面向对象需要较多的实践，本教程旨在帮助大家初步理解面向对象的思路。当在开发中遇到重复代码或结构复杂的情况时，希望大家能想到：是否可以通过封装、继承、多态来让代码更清晰、更可维护？
