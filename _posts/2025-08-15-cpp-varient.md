---
title: "C++ 中的 variant 解析"
date: 2025-08-15 08:00:00 +0800
published: true
categories: [技术]
tags: [C++]
---

_自己写了一个能自动构造的 union，结果发现和标准库的 variant 重复了，正好研究下_

## 示例

```cpp
template <typename... Types>
class StaticUnion {
private:
    // 定义一个union用于分配空间
    template <typename T, typename... Rest>
    union StorageUnion {
        T first;
        StorageUnion<Rest...> rest;

        StorageUnion() {}
    };

    template <typename T>
    union StorageUnion<T> {
        T first;

        StorageUnion() {}
    };

    // 从 union 中找到对应的类型的成员，其实union中的成员的地址是一样的。
    // 用途就是可以不用 reinterpret_cast 将union指针强制转为成员指针
    template <class T, class U, class... Rest>
    constexpr T *find_(StorageUnion<U, Rest...> &u)
    {
        if constexpr (std::is_same_v<T, U>) {
            return &u.first;
        }
        else {
            return find_<T>(u.rest);
        }
    }

    template <class T>
    constexpr T *find_(StorageUnion<T> &u)
    {
        return &u.first;
    }

    // 编译期获取类型在模板参数中的索引
    template <typename T, u8 Index = 0>
    static consteval u8 typeIndex_()
    {
        static_assert(Index != sizeof...(Types), "Type not in type list");
        if constexpr (std::is_same_v<T, std::tuple_element_t<Index, std::tuple<Types...>>>) {
            return Index;
        }
        else {
            return typeIndex_<T, Index + 1>();
        }
    }

    // 对指针的封装，可以避免对指针的复制操作，
    // 可以管控指针的生命周期，比较像智能指针
    template <typename T>
    class SlotPtr {
        T *ptr;

    public:
        explicit SlotPtr(T *p) :
            ptr(p)
        {}

        ~SlotPtr()                          = default;
        SlotPtr(const SlotPtr &)            = delete; // 禁止拷贝
        SlotPtr &operator=(const SlotPtr &) = delete;
        SlotPtr(SlotPtr &&other)            = delete;
        SlotPtr &operator=(SlotPtr &&other) = delete;

        T *operator->() const { return ptr; }
    };

    // 用union分配空间，保证空间够用
    StorageUnion<Types...> buffer_;
    // 运行时的union中的当前激活的成员索引
    u8 currentIndex_; // 255 表示空

public:
    StaticUnion() :
        currentIndex_(255)
    {}

    // 获取成员
    template <typename T>
        requires(std::is_same_v<T, Types> || ...)
    SlotPtr<T> get()
    {
        // Types 内不要有重复的(有的话也没什么太大问题)
        static_assert(
            ((0 + ... + (std::is_same_v<T, Types> ? 1 : 0)) == 1),
            "T appears zero or multiple times"
        );
        constexpr u8 targetIndex = typeIndex_<T>();

        // 如果当前的激活成员就是想要的，直接返回指针，不用重新构造
        if (currentIndex_ == targetIndex) {
            return SlotPtr<T>(find_<T>(buffer_));
        }
        else { // 否则重新构造
            // 用到了placement new
            T *obj        = std::launder(::new (find_<T>(buffer_)) T());
            currentIndex_ = targetIndex;
            return SlotPtr<T>(obj);
        }
    }
};
```
