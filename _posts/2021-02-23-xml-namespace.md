---
title: XML命名空间
author: Jinkai
date: 2021-02-23 09:00:00 +0800
published: true
categories: [技术]
tags: [xml, namespace, 命名空间]
---

## xmlns 属性

--------

当在 XML 中使用前缀时，一个所谓的用于前缀的命名空间必须被定义。

命名空间是在元素的开始标签的 `xmlns` 属性中定义的。

命名空间声明的语法如下。`xmlns:前缀="URI"`。

- 示例：

```xml
<root>

<h:table xmlns:h="http://www.w3.org/TR/html4/">
<h:tr>
<h:td>Apples</h:td>
<h:td>Bananas</h:td>
</h:tr>
</h:table>

<f:table xmlns:f="http://www.w3cschool.cc/furniture">
<f:name>African Coffee Table</f:name>
<f:width>80</f:width>
<f:length>120</f:length>
</f:table>

</root>
```

在上面的实例中，`<table>` 标签的 `xmlns` 属性定义了 `h:` 和 `f:` 前缀的合格命名空间。

当命名空间被定义在元素的开始标签中时，所有带有相同前缀的子元素都会与同一个命名空间相关联。

命名空间，可以在他们被使用的元素中或者在 XML 根元素中声明：

```xml
<root xmlns:h="http://www.w3.org/TR/html4/"
xmlns:f="http://www.w3cschool.cc/furniture">

<h:table>
<h:tr>
<h:td>Apples</h:td>
<h:td>Bananas</h:td>
</h:tr>
</h:table>

<f:table>
<f:name>African Coffee Table</f:name>
<f:width>80</f:width>
<f:length>120</f:length>
</f:table>

</root>
```

>注释：*命名空间 URI 不会被解析器用于查找信息。其目的是赋予命名空间一个惟一的名称。不过，很多公司常常会作为指针来使用命名空间指向实际存在的网页，这个网页包含关于命名空间的信息。请访问 <http://www.w3.org/TR/html4/>。*

## 统一资源标识符

--------

`统一资源标识符`（`URI`，全称 Uniform Resource Identifier），是一串可以标识因特网资源的字符。

最常用的 `URI` 是用来标识因特网域名地址的`统一资源定位器`（`URL`）。另一个不那么常用的 `URI` 是`统一资源命名`（`URN`）。

在我们的实例中，我们仅使用 `URL`。

>注意`URI`和`URL`是不同的概念，`URI`是用于标识的，`URL`是一串链接，只不过`URI`常用`URL`作为表示显示

## 默认的命名空间

--------

为元素定义默认的命名空间可以让我们省去在所有的子元素中使用前缀的工作。它的语法如下：

```xml
xmlns="namespaceURI"
```

>*使用默认命名空间时，xmlns就无需指定命名空间名称，也不用在对应的标签前添加命名空间名称*

这个 XML 携带 HTML 表格的信息：

```xml
<table xmlns="http://www.w3.org/TR/html4/">
<tr>
<td>Apples</td>
<td>Bananas</td>
</tr>
</table>
```

这个XML携带有关一件家具的信息：

```xml
<table xmlns="http://www.w3schools.com/furniture">
<name>African Coffee Table</name>
<width>80</width>
<length>120</length>
</table>
```

## 参考

- [XML 命名空间（XML Namespaces）](<https://www.w3school.com.cn/xml/xml_namespaces.asp>)
