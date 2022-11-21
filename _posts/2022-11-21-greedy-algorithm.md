---
title: "贪心算法详解"
author: Jinkai
date: 2022-11-21 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [算法]
---

## 定义

贪心算法，又名贪婪法，是`寻找最优解问题`的常用方法（其实得到的往往是近似最优解），这种方法模式一般将求解过程分成若干个步骤，但每个步骤都应用贪心原则，选取`当前状态下最好`/最优的选择（`局部最有利`的选择），并以此希望最后堆叠出的结果也是最好/最优的解。

## 基本步骤

- 步骤 1：从某个初始解出发；
- 步骤 2：采用迭代的过程，当可以向目标前进一步时，就根据`局部最优策略`，得到一部分解，`缩小问题规模`；
- 步骤 3：将所有解综合起来。

## 实例：找零钱问题

假设你开了间小店，不能电子支付，钱柜里的货币只有 25 分、10 分、5 分和 1 分四种硬币，如果你是售货员且要找给客户 41 分钱的硬币，如何安排才能找给客人的钱既正确且硬币的`个数又最少`？

### 分析步骤

问题的解的限制条件为`个数最少`，符合`寻找最优解问题`的特征

分解问题：取一个硬币，使用贪心策略，为了使总硬币个数最少，硬币取尽可能最大面额的，然后计算剩余找零额

对上述子问题迭代，得到最优解

### 代码实现

```cpp
#include<iostream>
using namespace std;

#define ONEFEN    1
#define FIVEFEN    5
#define TENFEN    10
#define TWENTYFINEFEN 25

int main()
{
  int sum_money=41;
  int num_25=0,num_10=0,num_5=0,num_1=0;

  //不断尝试每一种硬币
  while(money>=TWENTYFINEFEN) { num_25++; sum_money -=TWENTYFINEFEN; }
  while(money>=TENFEN) { num_10++; sum_money -=TENFEN; }
  while(money>=FIVEFEN)  { num_5++;  sum_money -=FIVEFEN; }
  while(money>=ONEFEN)  { num_1++;  sum_money -=ONEFEN; }

  //输出结果
  cout<< "25分硬币数："<<num_25<<endl;
  cout<< "10分硬币数："<<num_10<<endl;
  cout<< "5分硬币数："<<num_5<<endl;
  cout<< "1分硬币数："<<num_1<<endl;

  return 0;
}
```

### 扩展：最优解

将问题中的硬币种类改为 25 分、`20 分`、10 分、5 分和 1 分五种硬币，找零额依然为 41 分

此时使用贪心算法得到结果与原问题相同：25 分 1 枚，10 分 1 枚，5 分 1 枚，1 分 1 枚，`共 4 枚`

但该解`并非最优解`，最优解为：20 分 2 枚，1 分 1 枚，`共 3 枚`

可以看出贪心算法的局限性是不能得到确定的全局最优解，但优点就是速度快且占用资源少

## 实例：01 背包问题

有一个背包，最多能承载重量为 C=150 的物品，现在有 7 个物品（物品`不能分割`成任意大小），编号为 1~7，`重量`分别是 wi=[35,30,60,50,40,10,25]，`价值`分别是 pi=[10,40,30,50,35,40,30]，现在从这 7 个物品中选择一个或多个装入背包，要求在物品总重量不超过 C 的前提下，所装入的物品`总价值最高`。

### 分析

问题解的限制条件为`总价值最高`，符合`寻找最优解问题`的特征

分解问题：根据策略选择 1 个物品放入，计算剩余重量

由于需要总价值最高，有如下几种选择策略：

- 价值最高商品
- 重量最低商品
- 价重比最高商品

这里选择价重比最高商品为例，迭代以上子问题，找到最终解

### 代码实现

```cpp
// 价重比最高策略
int Choosefunc3(std::vector<OBJECT> &objs, int c)
{
  int index = -1;
  double max_s = 0.0;
  for (int i = 0; i < static_cast<int>(objs.size()); i++)
  {
    if (objs[i].status == 0)
    {
      double si = objs[i].price;
      si = si / objs[i].weight;
      if (si > max_s)
      {
        max_s = si;
        index = i;
      }
    }
  }

  return index;
}

void GreedyAlgo(KNAPSACK_PROBLEM *problem, SELECT_POLICY spFunc)
{
  int idx;
  int sum_weight_current = 0;
  // 先选
  while ((idx = spFunc(problem->objs, problem->totalC - sum_weight_current)) != -1)
  { // 再检查，是否能装进去
    if ((sum_weight_current + problem->objs[idx].weight) <= problem->totalC)
    {
      // 如果背包没有装满，还可以再装,标记下装进去的物品状态为1
      problem->objs[idx].status = 1;
      // 把这个idx的物体的重量装进去，计算当前的重量
      sum_weight_current += problem->objs[idx].weight;
    }
    else
    {
      // 不能选这个物品了，做个标记2后重新选剩下的
      problem->objs[idx].status = 2;
    }
  }
  PrintResult(problem->objs); // 输出函数的定义，查看源代码
}
```

## 扩展：A\*算法

- [Introduction to the A\* Algorithm](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
- [路径规划之 A\* 算法](https://zhuanlan.zhihu.com/p/54510444)
- [A Star Algorithm 总结与实现](https://scm_mos.gitlab.io/motion-planner/a-star/)

### 启发函数

评估当前点与终点的距离代价。结合贪心策略，每次都往`距离代价最小`的点移动

### Dijkstra 算法

广度优先扩散式遍历所有点，直到遍历到终点开始寻找最近的路线返回，一定能找到最短路径

### A\*算法

结合广度优先遍历的 Dijkstra 算法和启发函数

f(n) = g(n) + h(n)

`f(n)`表示在当前情况下从**起点到终点的总代价（预估）**，`g(n)`表示**起点到 n 的代价**，`h(n)`表示启发函数算得的**预估 n 到终点的代价**

使用贪心策略，总是往`f(n)`更小的点移动

## 参考

- [小白带你学---贪心算法（Greedy Algorithm)](https://zhuanlan.zhihu.com/p/53334049)
