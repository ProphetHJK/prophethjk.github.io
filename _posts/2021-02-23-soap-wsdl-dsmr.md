---
title: SOAP,WSDL,DSMR详解
author: Jinkai
date: 2021-02-23 10:00:00 +0800
published: true
categories: [技术]
tags: [SOAP, WSDL, DSMR]
---
>参考：
>
>- [SOAP与WSDL详解](<https://juejin.cn/post/6844903537629986824>)
>- [WS-Addressing - 维基百科](<https://zh.wikipedia.org/wiki/WS-Addressing>)

前置阅读：
- [XML命名空间](<https://hjk.life/posts/xml-namespace/>)
- [Schema 教程](<https://www.w3school.com.cn/schema/index.asp>)

## 前言

--------

SOAP是我们Web Service中很常见的一个协议，SOAP确定了一种通过XML实现跨语言、跨机器传输调用的协议，WSDL更像是所提供服务的一个规范、一个文档，本篇文章介绍梳理一下他们的规则与逻辑，更好的认识一下SOAP协议及WSDL描述文件。

## SOAP简单对象访问协议

--------

**`SOAP`(Simple Object Access Protocol)简单对象访问协议**是交换数据的一种规范，在Web Service中，交换带结构信息。可基于HTTP等协议，使用XML格式传输，抽象于语言实现、平台和硬件。即多语言包括PHP、Java、.Net均可支持。

优点是跨语言，非常适合异步通信和针对松耦合的C/S，缺点是必须做很多运行时检查。

### 相关概念

- `SOAP封装(envelop)`,定义了一个框架，描述消息中的内容是什么，是谁发送的，谁应当接受并处理。
- `SOAP编码规则(encoding rules)`,定义了一种序列化的机制，表示应用程序需要使用的数据类型的实例。
- `SOAP RPC表示(RPC representation)`，定义了一个协定，用于表示远程过程调用和应答。
- `SOAP绑定(binding)`，定义了SOAP使用哪种协议交换信息。使用HTTP/TCP/UDP协议都可以。

### 基本结构

示例：

```xml
<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2001/12/soap-envelope" soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">
 
    <soap:Header>
      ...
      ...
    </soap:Header>
 
    <soap:Body>
          ...
          ...
          <soap:Fault>
            ...
            ...
          </soap:Fault>
    </soap:Body>
</soap:Envelope>
```

一条SOAP消息就是一个普通的XML文档，`Envelope`元素与`Body`元素（包含调用和响应信息）**必须存在**，`Header`元素（包含头部信息）和`Fault`元素（提供有关在处理此消息所发生的错误的信息）可以作为**可选存在**

### SOAP封装(envelop)

SOAP消息的`根元素`，可把XML文档定义为SOAP消息

### 命名空间

xmlns：SOAP命名空间,固定不变。

>在WSDL中，SOAP命名空间为<http://www.w3.org/2003/05/soap-envelope>

SOAP在默认命名空间中定义了3个属性：`actor`，`mustUnderstand`，`encodingStyle`。这些被定义在SOAP头部的属性**可定义容器如何对SOAP消息进行处理**。

>在WSDL中主要用到了mustUnderstand属性

- `mustUnderstand`属性——用于标识标题项对其进行处理的接受者来说是强制的还是可选的。（0可选1强制）`soap:mustUnderstand="0/1"`
- `actor`属性可用于将Header元素寻址到一个特定的端点 `soap:actor="URI"`
- `encodingStyle`属性用于定义在文档中使用的数据类型。此属性可出现在任何SOAP元素中，并会被应用到元素的内容及元素的所有子元素上。SOAP消息没有默认的编码方式。`soap:encodingstyle="URI"`

### SOAP Header元素

可选的SOAP Header元素可包含有关SOAP消息的应用程序专用信息。如果Header元素被提供，则它必须是Envelope元素的**第一个子元素**

```xml
<soap:Header>
   <m:Trans xmlns:m="http://www.w3schools.com/transaction/" soap:mustUnderstand="1">
    <!-- mustUnderstand表示处理此头部的接受者必须认可此元素，假如此元素接受者无法认可此元素，则在处理此头部时必须失效 -->
    234
   </m:Trans> 
</soap:Heaser>
```

### SOAP Body元素

必须的SOAP Body元素可包含打算传送到消息最终端点的实际SOAP消息。SOAP Body元素的直接子元素可以使合格的命名空间

### SOAP Fault元素

用于存留SOAP消息的错误和状态消息，可选的SOAP Fault元素用于指示错误消息。如果已提供了Fault元素，则它必须是**Body元素的子元素**，在一条SOAP消息中，Fault元素只能出现一次。

SOAP Fault子元素：

- 供识别障碍的代码
- 可供人阅读的有关障碍的说明
- 有关是谁引发故障的信息
- 存留涉及Body元素的应用程序的专用错误信息

`faultcode`值描述：

- versionMismatch SOAP Envelope的无效命名空间被发现
- mustUnderstand Header元素的一个直接子元素(mustUnderstand=”1′)无法被理解
- Client 消息被不正确的构成，或包含不正确的信息
- Server 服务器有问题，因此无法处理进行下去

### 与Restful协议对比

TODO

## WSDL网络服务描述语言

--------

**`WSDL`(Web Services Description Language)网络服务描述语言**，WSDL 是一种使用 XML 编写的文档。这种文档可描述某个 Web Service。文档的后缀名为一般为wsdl

- 官网：<http://schemas.xmlsoap.org/wsdl/>
- WS-RT的WSDL描述：<http://schemas.xmlsoap.org/ws/2006/08/resourceTransfer/wsrt.wsdl>

### 基本结构

```xml
<definitions>
    <types>
       definition of types........
    </types>
    <message>
       definition of a message....
    </message>
    <portType>
       definition of a port.......
    </portType>
    <binding>
       definition of a binding....
    </binding>
    <service>
       definition of a service....
    </service>
</definitions>
```

一个WSDL文档通常包含7个重要的元素，即types、import、message、portType、operation、binding、service元素。这些元素嵌套在definitions元素中，definitions是WSDL文档的根元素。

### 实例

以盛付通的一个接口为例，介绍一下整个wsdl描述文件，网址如下<http://cardpay.shengpay.com/api-acquire-channel/services/receiveOrderService?wsdl>

### Definitions

WSDL文档中对于`definitions`的描述：

```xml
<xs:element name="definitions" type="wsdl:tDefinitions" >
    <xs:key name="message" >
        <xs:selector xpath="wsdl:message" />
        <xs:field xpath="@name" />
    </xs:key>
    <xs:key name="portType" >
        <xs:selector xpath="wsdl:portType" />
        <xs:field xpath="@name" />
    </xs:key>
    <xs:key name="binding" >
        <xs:selector xpath="wsdl:binding" />
        <xs:field xpath="@name" />
    </xs:key>
    <xs:key name="service" >
        <xs:selector xpath="wsdl:service" />
        <xs:field xpath="@name" />
    </xs:key>
    <xs:key name="import" >
        <xs:selector xpath="wsdl:import" />
        <xs:field xpath="@namespace" />
    </xs:key>
</xs:element>
```

### Types

数据类型定义的容器，它使用某种类型系统(一般地使用XML Schema中的类型系统)。

```xml
<xs:element name="receB2COrderRequest" type="tns:ReceB2COrderRequest"/>  
<xs:element name="receB2COrderResponse" type="tns:ReceB2COrderResponse"/>
 
<xs:complexType name="ReceB2COrderRequest"> 
    <xs:sequence> 
      <xs:element minOccurs="0" name="buyerContact" type="xs:string"/>  
      .......
    </xs:sequence> 
</xs:complexType>  
 
<xs:complexType name="receiveB2COrder"> 
        <xs:sequence> 
          <xs:element minOccurs="0" name="arg0" type="tns:ReceB2COrderRequest"/> 
        </xs:sequence> 
</xs:complexType>  
```

### Message

通信消息的数据结构的抽象类型化定义。使用Types所定义的类型来定义整个消息的数据结构。

```xml
<wsdl:message name="receiveB2COrder"> 
    <wsdl:part element="tns:receiveB2COrder" name="parameters"/> 
</wsdl:message> 
```

### Operation & PortType

`Operation` 对服务中所支持的操作的抽象描述，一般单个`Operation`描述了一个访问入口的`请求/响应消息对`。 `PortType` 对于某个访问入口点类型所支持的操作的`抽象集合`，这些操作可以由一个或多个服务访问点来支持。

```xml
<wsdl:portType name="ReceiveOrderAPI"> 
    <wsdl:operation name="receiveB2COrder"> 
      <wsdl:input message="tns:receiveB2COrder" name="receiveB2COrder"/>  
      <wsdl:output message="tns:receiveB2COrderResponse" name="receiveB2COrderResponse"/>  
      <wsdl:fault message="tns:MasAPIException" name="MasAPIException"/> 
    </wsdl:operation> 
</wsdl:portType>  
```

### Binding

特定端口类型的具体协议和数据格式规范的绑定。

```xml
<wsdl:binding name="ReceiveOrderAPIExplorterServiceSoapBinding" type="tns:ReceiveOrderAPI"> 
    <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>  
    <wsdl:operation name="receiveB2COrder"> 
      <soap:operation soapAction="" style="document"/>  
      <wsdl:input name="receiveB2COrder"> 
        <soap:body use="literal"/> 
      </wsdl:input>  
      <wsdl:output name="receiveB2COrderResponse"> 
        <soap:body use="literal"/> 
      </wsdl:output>  
      <wsdl:fault name="MasAPIException"> 
        <soap:fault name="MasAPIException" use="literal"/> 
      </wsdl:fault> 
    </wsdl:operation> 
</wsdl:binding>  
```

### Port&Service

Port 定义为协议/数据格式绑定与具体Web访问地址组合的单个服务访问点。 Service 相关服务访问点的集合。

```xml
<wsdl:service name="ReceiveOrderAPIExplorterService"> 
    <wsdl:port binding="tns:ReceiveOrderAPIExplorterServiceSoapBinding" name="ReceiveOrderAPIExplorterPort"> 
      <soap:address location="http://cardpay.shengpay.com/api-acquire-channel/services/receiveOrderService"/> 
    </wsdl:port> 
</wsdl:service>
```

## WS-Addressing

--------

Web服务寻址（`WS-Addressing`）是一个W3C推荐标准，为Web服务提供一种与传输层无关的，传送寻址信息的机制。规范主要由两部分组成：传送Web服务端点的引用的数据结构，以及一套能够在特定的消息上关联寻址信息的消息寻址属性。

WS-Addressing是将消息路由数据包含在SOAP头中的一种标准方法。**利用WS-Addressing的消息可以在标准化的SOAP头中包含自己的包含发送元数据，而不是依赖于网络层传输来传送路由信息**。网络级传输只负责将消息发送到能够读取WS-Addressing元数据的分配器那里。一旦消息抵达了URI所制定的分配器，网络层传输的工作就完成了。

通过在标准的SOAP头中(wsa:ReplyTo)指定应答消息应该发送到哪里的端点引用，WS-Addressing可以支持异步交互方式。 服务提供者使用另一个连接，将应答消息发送给wsa:ReplyTo所指定的端点。这就将SOAP请求/应答消息的交互与HTTP请求/应答协议分离，这样，跨越任意时间的长时间运行的交互成为可能。

### 端点引用

端点引用（Endpoint Reference，速写EPR）是一个XML结构，封装了对访问Web服务的消息寻址有用的信息。这包括了消息的目的地地址，任何其他路由消息到目的地所需的参数（称作引用参数），以及有关服务的任选的元数据（例如WSDL或WS-Policy）。

### 消息寻址属性

消息寻址属性表明与将消息传送到Web服务有关的寻址信息，包括：

- 目的地(To) -- 该消息的目的地的URI。
- 源端点(From) -- 发出该消息的服务端点（EPR）
- 应答端点(ReplyTo) -- 应答消息接收者的端点（EPR）
- 故障端点(FaultTo) -- 故障消息接收者的端点（EPR）
- 动作(Action) -- 指示该消息的语义（可能有助于该消息的寻址）的URI
- 消息ID(MessageID) -- 唯一消息标识符URI
- 关系(RelatesTo) -- 与之前消息的关系(一对URI)

### DSMR示例

Example “Delete” operation:

```xml
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
    xmlns:wsa="http://www.w3.org/2005/08/addressing"
    xmlns:p32="http://www.energiened.nl/Content/Publications/dsmr/P32">
    <s:Header>
        <wsa:To> http://10.0.1.2/services/Resources
        </wsa:To>
        <wsa:Action s:mustUnderstand="true"> http://schemas.xmlsoap.org/ws/2004/09/transfer/Delete
        </wsa:Action>
        <wsa:MessageID> uuid:ddacc64d-c64d-1dac-acbc-017f00000001
        </wsa:MessageID>
        <p32:ResourceURI wsa:IsReferenceParameter="true"> http://www.energiened.nl/Content/Publications/dsmr/P32/meterAccess
        </p32:ResourceURI>
        <p32:SelectorSet>
            <p32:Selector Name="ResourceID">MeterAccess-1</p32:Selector>
        </p32:SelectorSet>
    </s:Header>
    <s:Body>
        <DeleteRequest xmlns="http://schemas.xmlsoap.org/ws/2004/09/transfer"/>
    </s:Body>
</s:Envelope>
```

Example “Delete” response:

```xml
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
    xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <s:Header>
        <wsa:ReplyTo>
            <wsa:Address> http://www.w3.org/2005/08/addressing/anonymous
            </wsa:Address>
        </wsa:ReplyTo>
        <wsa:From>
            <wsa:Address> http://10.0.1.2/services/Resources
            </wsa:Address>
            <wsa:ReferenceParameters/>
        </wsa:From>
        <wsa:MessageID> uuid:C986EEAA-484B-4b94-AB46-743EE560B5F9
        </wsa:MessageID>
        <wsa:Action> http://schemas.xmlsoap.org/ws/2004/09/transfer/DeleteResponse
        </wsa:Action>
        <wsa:RelatesTo wsa:RelationshipType="wsa:Reply"> uuid:ddacc64d-c64d-1dac-acbc-017f00000001
        </wsa:RelatesTo>
    </s:Header>
    <s:Body>
        <DeleteResponse xmlns="http://schemas.xmlsoap.org/ws/2004/09/transfer"/>
    </s:Body>
</s:Envelope>
```

## WS-RT (Web Services Resource Transfer)

--------

This specification defines `extensions` to `WS-Transfer` primarily to provide `fragment-based` access to resources.

WS-RT是WS-Transfer的扩展，主要用于基于片段的资源的访问

- 官网：<https://www.w3.org/TR/2010/NOTE-ws-resource-transfer-20100713/>
- 协议：<http://schemas.xmlsoap.org/ws/2006/08/resourceTransfer/>

### 介绍

This specification is intended to form an essential core component of a unified resource access protocol for the Web services space.

The operations described in this specification constitute an extension to the WS-Transfer specification, which defines standard messages for controlling resources using the familiar paradigms of "`get`", "`put`", "`create`", and "`delete`". The extensions deal primarily with fragment-based access to resources.

This document constitutes WS-ResourceTransfer, hereafter referred to as WS-RT.

主要用于资源传输，定义了"`get`", "`put`", "`create`", "`delete`"四个方法，类似于HTTP请求，包含了WSDL的说明

更多内容详见[官网](<https://www.w3.org/TR/2010/NOTE-ws-resource-transfer-20100713/>)

## WS-Transfer (Web Services Transfer)

--------

- 官网：<https://www.w3.org/Submission/WS-Transfer/>
- 协议：<http://schemas.xmlsoap.org/ws/2004/09/transfer/>

### 介绍

与WS-RT类似，不再过多介绍

## DSMR

--------

DSMR协议是由荷兰Energie-Nederland协会编写的能源管理与通信标准，以下是Energie-Nederland协会的简介：

```text
Energie-Nederland is de branchevereniging voor alle partijen die stroom, gas en warmte produceren, leveren en verhandelen. Samen vertegenwoordigen wij circa 80% van de markt. Onze ruim 60 leden zijn actief in zowel ‘groene’ als ‘grijze’ energie en allerlei soorten dienstverlening. Onder hen zijn ook veel nieuwkomers op de markt, innovatieve spelers en duurzame initiatieven. Energie-Nederland gaat voor een duurzame, betrouwbare en betaalbare energievoorziening; wij zijn een van de trekkers van het Klimaatakkoord.
```

简介是荷兰语的，我也看不懂，只能找Google机翻一下：

```text
Energie-Nederland是所有生产，供应和贸易电，气和热的各方的贸易协会。 我们共同代表了约80％的市场。 我们的60多个成员活跃于“绿色”和“灰色”能源以及各种服务中。 他们还包括许多新进入市场的人，创新参与者和可持续发展倡议。 Energie-Nederland致力于可持续，可靠和负担得起的能源供应； 我们是《气候协定》的发起人之一。
```

### Scope

This part provides a companion standard for an Automatic Meter Reading (AMR) system for electricity thermal, (heat & cold), gas and water meters.

The scope of this standard is on:

- Residential electricity meters
- Residential thermal (heat & cold) meters
- Residential gas meters and gas valve
- Residential water meters

This companion standard focuses on the P3 interface for Electricity meters.

![Meter interfaces overview](/assets/img/2021-02-23-soap-wsdl-dsmr/Meter-interfaces-overview.png)

本文主要介绍其中P3.2部分，也就是采集网关和主站之间的通信协议

## 附录：盛付通接口实例

--------

```xml
<wsdl:definitions xmlns:ns1="http://schemas.xmlsoap.org/soap/http"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:tns="http://www.sdo.com/mas/api/receive/"
    xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema" name="ReceiveOrderAPIExplorterService" targetNamespace="http://www.sdo.com/mas/api/receive/">
    <wsdl:types>
        <xs:schema xmlns:tns="http://www.sdo.com/mas/api/receive/"
            xmlns:xs="http://www.w3.org/2001/XMLSchema" attributeFormDefault="unqualified" elementFormDefault="unqualified" targetNamespace="http://www.sdo.com/mas/api/receive/">
            <xs:element name="receB2COrderRequest" type="tns:ReceB2COrderRequest"/>
            <xs:element name="receB2COrderResponse" type="tns:ReceB2COrderResponse"/>
            <xs:complexType name="ReceB2COrderRequest">
                <xs:sequence>
                    <xs:element minOccurs="0" name="buyerContact" type="xs:string"/>
                    <xs:element minOccurs="0" name="buyerId" type="xs:string"/>
                    <xs:element minOccurs="0" name="buyerIp" type="xs:string"/>
                    <xs:element minOccurs="0" name="buyerName" type="xs:string"/>
                    <xs:element minOccurs="0" name="cardPayInfo" type="xs:string"/>
                    <xs:element minOccurs="0" name="cardValue" type="xs:string"/>
                    <xs:element minOccurs="0" name="currency" type="xs:string"/>
                    <xs:element minOccurs="0" name="depositId" type="xs:string"/>
                    <xs:element minOccurs="0" name="depositIdType" type="xs:string"/>
                    <xs:element minOccurs="0" name="expireTime" type="xs:string"/>
                    <xs:element minOccurs="0" name="extension" type="tns:extension"/>
                    <xs:element minOccurs="0" name="header" type="tns:header"/>
                    <xs:element minOccurs="0" name="instCode" type="xs:string"/>
                    <xs:element minOccurs="0" name="language" type="xs:string"/>
                    <xs:element minOccurs="0" name="notifyUrl" type="xs:string"/>
                    <xs:element minOccurs="0" name="orderAmount" type="xs:string"/>
                    <xs:element minOccurs="0" name="orderNo" type="xs:string"/>
                    <xs:element minOccurs="0" name="orderTime" type="xs:string"/>
                    <xs:element minOccurs="0" name="pageUrl" type="xs:string"/>
                    <xs:element minOccurs="0" name="payChannel" type="xs:string"/>
                    <xs:element minOccurs="0" name="payType" type="xs:string"/>
                    <xs:element minOccurs="0" name="payeeId" type="xs:string"/>
                    <xs:element minOccurs="0" name="payerAuthTicket" type="xs:string"/>
                    <xs:element minOccurs="0" name="payerId" type="xs:string"/>
                    <xs:element minOccurs="0" name="payerMobileNo" type="xs:string"/>
                    <xs:element minOccurs="0" name="productDesc" type="xs:string"/>
                    <xs:element minOccurs="0" name="productId" type="xs:string"/>
                    <xs:element minOccurs="0" name="productName" type="xs:string"/>
                    <xs:element minOccurs="0" name="productNum" type="xs:string"/>
                    <xs:element minOccurs="0" name="productUrl" type="xs:string"/>
                    <xs:element minOccurs="0" name="sellerId" type="xs:string"/>
                    <xs:element minOccurs="0" name="signature" type="tns:signature"/>
                    <xs:element minOccurs="0" name="terminalType" type="xs:string"/>
                    <xs:element minOccurs="0" name="unitPrice" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>
            <xs:complexType name="extension">
                <xs:sequence>
                    <xs:element minOccurs="0" name="ext1" type="xs:string"/>
                    <xs:element minOccurs="0" name="ext2" type="xs:string"/>
                    <xs:element minOccurs="0" name="ext3" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>
            <xs:complexType name="header">
                <xs:sequence>
                    <xs:element minOccurs="0" name="charset" type="xs:string"/>
                    <xs:element minOccurs="0" name="sendTime" type="xs:string"/>
                    <xs:element minOccurs="0" name="sender" type="tns:sender"/>
                    <xs:element minOccurs="0" name="service" type="tns:service"/>
                    <xs:element minOccurs="0" name="traceNo" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>
            <xs:complexType name="sender">
                <xs:sequence>
                    <xs:element minOccurs="0" name="senderId" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>
            <xs:complexType name="service">
                <xs:sequence>
                    <xs:element minOccurs="0" name="serviceCode" type="xs:string"/>
                    <xs:element minOccurs="0" name="version" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>
            <xs:complexType name="signature">
                <xs:sequence>
                    <xs:element minOccurs="0" name="signMsg" type="xs:string"/>
                    <xs:element minOccurs="0" name="signType" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>
            <xs:complexType name="ReceB2COrderResponse">
                <xs:sequence>
                    <xs:element minOccurs="0" name="customerLogoUrl" type="xs:string"/>
                    <xs:element minOccurs="0" name="customerName" type="xs:string"/>
                    <xs:element minOccurs="0" name="customerNo" type="xs:string"/>
                    <xs:element minOccurs="0" name="extension" type="tns:extension"/>
                    <xs:element minOccurs="0" name="header" type="tns:header"/>
                    <xs:element minOccurs="0" name="orderAmount" type="xs:string"/>
                    <xs:element minOccurs="0" name="orderNo" type="xs:string"/>
                    <xs:element minOccurs="0" name="orderType" type="xs:string"/>
                    <xs:element minOccurs="0" name="returnInfo" type="tns:returnInfo"/>
                    <xs:element minOccurs="0" name="sessionId" type="xs:string"/>
                    <xs:element minOccurs="0" name="signature" type="tns:signature"/>
                    <xs:element minOccurs="0" name="tokenId" type="xs:string"/>
                    <xs:element minOccurs="0" name="transNo" type="xs:string"/>
                    <xs:element minOccurs="0" name="transStatus" type="xs:string"/>
                    <xs:element minOccurs="0" name="transTime" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>
            <xs:complexType name="returnInfo">
                <xs:sequence>
                    <xs:element minOccurs="0" name="errorCode" type="xs:string"/>
                    <xs:element minOccurs="0" name="errorMsg" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>
            <xs:element name="MasAPIException" type="tns:MasAPIException"/>
            <xs:complexType name="MasAPIException">
                <xs:sequence/>
            </xs:complexType>
            <xs:element name="receiveB2COrder" type="tns:receiveB2COrder"/>
            <xs:complexType name="receiveB2COrder">
                <xs:sequence>
                    <xs:element minOccurs="0" name="arg0" type="tns:ReceB2COrderRequest"/>
                </xs:sequence>
            </xs:complexType>
            <xs:element name="receiveB2COrderResponse" type="tns:receiveB2COrderResponse"/>
            <xs:complexType name="receiveB2COrderResponse">
                <xs:sequence>
                    <xs:element minOccurs="0" name="return" type="tns:ReceB2COrderResponse"/>
                </xs:sequence>
            </xs:complexType>
        </xs:schema>
    </wsdl:types>
    <wsdl:message name="receiveB2COrder">
        <wsdl:part element="tns:receiveB2COrder" name="parameters"></wsdl:part>
    </wsdl:message>
    <wsdl:message name="receiveB2COrderResponse">
        <wsdl:part element="tns:receiveB2COrderResponse" name="parameters"></wsdl:part>
    </wsdl:message>
    <wsdl:message name="MasAPIException">
        <wsdl:part element="tns:MasAPIException" name="MasAPIException"></wsdl:part>
    </wsdl:message>
    <wsdl:portType name="ReceiveOrderAPI">
        <wsdl:operation name="receiveB2COrder">
            <wsdl:input message="tns:receiveB2COrder" name="receiveB2COrder"></wsdl:input>
            <wsdl:output message="tns:receiveB2COrderResponse" name="receiveB2COrderResponse"></wsdl:output>
            <wsdl:fault message="tns:MasAPIException" name="MasAPIException"></wsdl:fault>
        </wsdl:operation>
    </wsdl:portType>
    <wsdl:binding name="ReceiveOrderAPIExplorterServiceSoapBinding" type="tns:ReceiveOrderAPI">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <wsdl:operation name="receiveB2COrder">
            <soap:operation soapAction="" style="document"/>
            <wsdl:input name="receiveB2COrder">
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output name="receiveB2COrderResponse">
                <soap:body use="literal"/>
            </wsdl:output>
            <wsdl:fault name="MasAPIException">
                <soap:fault name="MasAPIException" use="literal"/>
            </wsdl:fault>
        </wsdl:operation>
    </wsdl:binding>
    <wsdl:service name="ReceiveOrderAPIExplorterService">
        <wsdl:port binding="tns:ReceiveOrderAPIExplorterServiceSoapBinding" name="ReceiveOrderAPIExplorterPort">
            <soap:address location="http://cardpay.shengpay.com/api-acquire-channel/services/receiveOrderService"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>
```
