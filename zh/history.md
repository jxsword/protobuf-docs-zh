+++
title = "历史"
weight = 1020
description = "Protobuf 诞生背后的简要历史。"
type = "docs"
source_url = "https://protobuf.dev/history/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-20"
status = "translated"
translator = "agent"
+++

了解 Protobuf 为何被创造出来，以及哪些决策随时间推移改变了它，有助于你
更好地使用这款工具的各项特性（feature）。

## 你们为什么要发布 Protobuf？{#why}

我们发布 Protobuf 有几个原因。

Google 内部有许多项目在使用 Protobuf。我们还有一些使用 Protobuf 的其他
项目想要以开源形式发布，要做到这一点，就必须先发布 Protobuf。事实上，
这项技术的部分成果早已流入外界：如果你深挖 Google AppEngine 的代码，
或许就能找到一些。

我们希望提供既能接受 Protobuf 也能接受 XML 的公共 API，一来这样效率
更高，二来反正我们在自己这一端也会把这些 XML 转换成 Protobuf。

我们认为 Google 之外的人可能也会觉得 Protobuf 有用。把 Protobuf 打理成
我们愿意发布的形式，本身就是个有趣的业余项目。

## 首个发布版本为何是 2？版本 1 去哪了？{#version-1}

Protobuf 的最初版本（"Proto1"）从 2001 年初开始开发，并在多年间不断
演进：只要有人需要新特性并愿意动手实现，它就会长出新特性。像任何以
这种方式造就的东西一样，它有点杂乱。我们最终得出的结论是：按原样发布
这些代码并不可行。

版本 2（"Proto2"）是一次彻底重写，不过它保留了大部分设计，并沿用了
Proto1 的许多实现思路。有些特性被加入，有些被移除。但最重要的是，代码
得到了清理，不再依赖任何尚未开源的 Google 库。

## 为何取名 "Protocol Buffers"？{#name}

这个名字源于这种格式的早期，当时还没有 Protobuf 编译器来为我们生成类。
那时有一个名为 `ProtocolBuffer` 的类，它实际上充当单个方法的缓冲区。
用户通过调用类似 `AddValue(tag, value)` 的方法，把标签（tag）/值（value）
对逐个加入该缓冲区。原始字节存储在缓冲区中，待消息（message）构建完成
后即可写出。

从那时起，名字中的 "buffers" 部分已失去其本意，但它仍是我们沿用至今的
名字。如今，人们通常用 "protocol message" 一词指抽象意义上的消息，用
"protocol buffer" 指消息经序列化后的副本，用 "protocol message object"
指表示已解析消息的内存中对象。

## Proto3 和版次（Editions）呢？{#proto3}

2023 年，我们推出了 Protobuf 版次（Editions），以便对特性进行更细粒度的
控制，并摆脱 `proto2` 和 `proto3` "全有或全无"的做法。借助版次，你现在
可以在 `.proto` 文件中显式指定想要使用的特性。

例如，要使用 2023 版次，你需要在 `.proto` 文件中添加如下内容：

```proto
edition = "2023";
```

将有一段过渡期，在此期间 `proto2`、`proto3` 与版次并存。有关版次的更多
信息，请参阅 [Protobuf 版次概览](/editions/overview)。

## Google 是否拥有 Protobuf 的专利？{#patents}

Google 目前没有与 Protobuf 相关的已授权专利，我们也乐意回应大家对
Protobuf 与专利可能存在的任何疑虑。

## Protobuf 与 ASN.1、COM、CORBA 和 Thrift 有何不同？{#differ}

我们认为这些系统各有优劣。Google 在内部依赖 Protobuf，它是我们取得成功
的重要组成部分，但这并不意味着它能理想地解决每一个问题。你应当结合自己
项目的实际情况来评估每一种替代方案。

不过值得注意的是，这些技术中有几种同时定义了交换格式和远程过程调用
（RPC）协议。Protobuf 只是一种交换格式。它很容易就能用于
RPC&mdash;而且事实上，它确实对定义 RPC 服务提供了有限的支持&mdash;但
它并不绑定于任何一种特定的 RPC 实现或协议。
