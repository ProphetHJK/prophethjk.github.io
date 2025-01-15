---
title: "聊聊设计模式"
date: 2024-09-05 08:00:00 +0800
published: false
mermaid: true
categories: [技术]
tags: [design patterns, c++]
---

## 创建型模式

### 简单工厂模式

假设我们有一家工厂(Factory)生产**苹果**手机产品(Product)，现在我们要让这家工厂也生产**小米**手机

![alt text](/assets/img/2024-09-05-design-patterns/simplefactory.webp)

- Factory：即工厂类（手机工厂）， 简单工厂模式的核心部分，负责实现创建所有产品的内部逻辑；工厂类可以被外界直接调用，创建所需对象
- Product：抽象类产品（手机产品），它是工厂类所创建的所有对象的父类，封装了各种产品对象的公有方法（比如所有手机共有的 display() 方法），它的引入将提高系统的灵活性，使得在工厂类中只需定义一个通用的工厂方法，因为所有创建的具体产品对象都是其子类对象
- ConcreteProduct：具体产品，它是简单工厂模式的创建目标，所有被创建的对象都充当这个角色的某个具体类的实例。它要实现抽象产品中声明的抽象方法

> 重点：通过工厂创建的产品必须拥有统一的接口（基于同一个父类，如上图的IProduct）

```cpp
// Product
class PhoneProduct{
public:
  void display(){}
};

// ConcreteProduct
class XiaomiPhoneProduct:public PhoneProduct{};
class ApplePhoneProduct:public PhoneProduct{};

// Factory
class PhoneFactory {
public:
  static PhoneProduct* producePhone(string branding){
    PhoneProduct* product = null;
    switch (branding)
    {
      case "Xiaomi":
        product =  new XiaomiPhoneProduct();
        break;
      case "Apple":
        product = new ApplePhoneProduct();
        break;
      default:
        assert(0);
    }
    return prodect;
  }
};

// client
int main(){
  PhoneProduct* phoneProduct1 = PhoneFactory::producePhone("Xiaomi");
  // 用来取代 PhoneProduct phoneProduct1 = new XiaomiPhoneProduct();好处是使用者无需看到具体产品类，只需知道产品的id(本例中为品牌名称字符串)，所有产品创建统一由工厂类提供。
  PhoneProduct* phoneProduct2 = PhoneFactory::producePhone("Apple");

  // 增加一个具体产品类需要改动上述代码(PhoneFactory类)，不符合开闭原则

  phoneProduct1->display();
}
```

#### 简单工厂的缺点

每次增加一款产品，都需要在 Factory 类的switch中多加一个 case，不满足开闭原则。

### 工厂方法模式

为了解决简单工厂的问题，我们对工厂再进行抽象。也就是不在一家工厂生产两个产品，而是开两家工厂各自生产产品。

![alt text](/assets/img/2024-09-05-design-patterns/factorymethod.webp)

- Product：抽象产品，定义工厂方法所创建的对象的接口，也就是实际需要使用的对象的接口
- ConcreteProduct：具体产品，具体的 Product 接口的实现对象
- Factory：工厂接口，也可以叫 Creator(创建器)，申明工厂方法，通常返回一个 Product 类型的实例对象
- ConcreteFactory：工厂实现，或者叫 ConcreteCreator(创建器对象)，覆盖 Factory 定义的工厂方法，返回具体的 Product 实例

> 重点：所有工厂创建的产品必须拥有统一接口（基于同一个父类，如上图IProduct）

```cpp
// Factory
class PhoneFactory {
public:
  virtual PhoneProduct* producePhone() = 0;
}

// ConcreteFactory
class XiaomiPhoneFactory:public PhoneFactory{
public:
  virtual PhoneProduct* producePhone(){
    PhoneProduct* product = null;
    product =  new XiaomiPhoneProduct();
    return prodect;
  }
};
class ApplePhoneFactory:public PhoneFactory{
public:
  virtual PhoneProduct* producePhone(){
    PhoneProduct* product = null;
    product =  new XiaomiPhoneProduct();
    return prodect;
  }
};

// client
int main(){
  // 客户端需要知道具体产品对应的工厂类，只不过不需要知道具体产品类而已
  PhoneFactory* phoneFactory1 = XiaomiPhoneFactory();
  PhoneProduct* phoneProduct1 = phoneFactory1->producePhone();

  PhoneFactory* phoneFactory2 = ApplePhoneFactory();
  PhoneProduct* phoneProduct2 = phoneFactory2->producePhone();

  // 新增一个具体产品类和具体工厂类不影响上面的代码，符合开闭原则

  phoneProduct1.display();
}
```

可以看出工厂方法比简单工厂更复杂，所以它“不简单”。优势主要是满足开闭原则。

#### 工厂方法模式的缺点

一个具体工厂只能生产一个具体产品，每新增一个具体产品都必须创建一个具体工厂。有些时候我们希望一个具体工厂能生产一系列（同一个品牌）的产品，新建同一个系列的不同具体产品时可以共用一个具体工厂。

### 抽象工厂模式

现在我们想要生产苹果耳机和小米耳机，我们需要创建一个新的抽象产品类（EarphoneProduct）和两个具体产品类，然后如果安装工厂方法模式，我们还需要新建一个工厂接口（EarphoneFactory），然后新建两个具体工厂（AppleEarphoneFactory,XiaomiEarphoneFactory）。现在如果我们把这两个产品加入原来的工厂生产，就无需新建工厂接口和具体工厂。

> 重点：不要求所有产品必须拥有相同的接口，但不同工厂的同类产品(手机类或耳机类)必须拥有统一接口。

```cpp
// Product
class PhoneProduct{
public:
  void display(){}
};

// ConcreteProduct
class XiaomiPhoneProduct:public PhoneProduct{};
class ApplePhoneProduct:public PhoneProduct{};

// Product
class EarphoneProduct{
public:
  void playMusic(){}
};

// ConcreteProduct
class XiaomiEarphoneProduct:public EarphoneProduct{};
class AppleEarphoneProduct:public EarphoneProduct{};

// AbstractFactory
class Factory {
public:
  virtual PhoneProduct* producePhone() = 0;
  virtual EarphoneProduct* produceEarphone() = 0;
}

// ConcreteFactory
class XiaomiFactory:public Factory{
public:
  virtual PhoneProduct* producePhone(){
    PhoneProduct* product = null;
    product =  new XiaomiPhoneProduct();
    return prodect;
  }
  virtual EarphoneProduct* produceEarphone(){
    EarphoneProduct* product = null;
    product =  new XiaomiEarphoneProduct();
    return prodect;
  }
};

// ConcreteFactory
class AppleFactory:public PhoneFactory{
public:
  virtual PhoneProduct* producePhone(){
    PhoneProduct* product = null;
    product =  new XiaomiPhoneProduct();
    return prodect;
  }
  virtual EarphoneProduct* produceEarphone(){
    EarphoneProduct* product = null;
    product =  new AppleEarphoneProduct();
    return prodect;
  }
};

// client1
int main(){
  // 客户端需要知道具体产品对应的工厂类，只不过不需要知道具体产品类而已
  Factory* factory1 = XiaomiFactory();
  PhoneProduct* phoneProduct1 = factory1->producePhone();
  EarphoneProduct* earphoneProduct1 = factory1->produceEarphone();

  phoneProduct1.display();
  earphoneProduct1.playMusic();
}

// client2
int main(){
  // 仅就修改一行代码即可切换产品品牌，生产过程和使用过程都相同。按照工厂方法模式这4种产品需要4个工厂生产，替换系列需要将小米两个工厂替换为苹果的两个工厂，抽象了工厂后一个工厂能生产两种产品，所以能实现仅替换一次。
  Factory* factory1 = AppleFactory();
  PhoneProduct* phoneProduct1 = factory1->producePhone();
  EarphoneProduct* earphoneProduct1 = factory1->produceEarphone();

  phoneProduct1.display();
  earphoneProduct1.playMusic();
}
```

将同一系列的产品加入同一工厂生产的另一个好处是只需替换具体工厂，就能实现整个系列产品的切换（小米产线切换成苹果产线）。

### 生成器

在对象构造时我们有时会传入大量的(初始化)参数用于配置该类中每个功能模块，特别是功能很庞大的一个类：

```cpp
class Car{
public:
  // 大量的参数
  Car(int seatSum, Engine& engine, TripComputer& computer, bool& gps, int& wheelSize){}
};

int main(){
  // 而且有些可能是NULL值
  Car* car = new Car(4, engine ,NULL, false, 16);
  Car* car = new Car(6, engine ,NULL, true, 18);
}
```

每次构造一个对象都要填大量参数，而且不同对象间很多参数是**重复**的(比如都使用同一种引擎)。

我们可以对所有对象进行分类，将参数相同的对象整合起来，比如 SUV、轿车、越野车，统一品类的车除了最终的涂装不同外其他都相同，涂装可以最后修改所以不在 Car 对象构建过程中。



