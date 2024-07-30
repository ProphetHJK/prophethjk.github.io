---
title: "C++ STL function解析"
date: 2024-07-23 08:00:00 +0800
published: False
categories: [技术]
tags: [c++,stl]
---

## 定义

```cpp
template< class >
class function; /* undefined */

template< class R, class... Args >
class function<R(Args...)>;
```

首先需要前向声明一个主模板，该主模板不能直接使用。然后使用模板特例化(specialization)
