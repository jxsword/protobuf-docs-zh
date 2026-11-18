+++
title = "概览"
weight = 10
description = "Protobuf 是一种语言无关、平台无关的可扩展机制，用于序列化结构化数据。"
type = "docs"
source_url = "https://protobuf.dev/overview/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

它类似于 JSON，但更小、更快，并且会生成原生语言绑定（native language bindings）。你只需一次性定义好数据的结构方式，之后便可以使用特殊生成的源代码，轻松地以多种语言、通过各种数据流写入和读取你的结构化数据。

Protobuf 由以下几部分组合而成：定义语言（在 `.proto` 文件中编写）、proto 编译器生成的用于与数据交互的代码、各语言专用的运行时（runtime）库、用于写入文件（或通过网络连接发送）的数据的序列化（serialization）格式，以及序列化后的数据。

## Protobuf 解决了哪些问题？ {#solve}

Protobuf 为大小在几 MB 以内的类型化、结构化数据包提供了一种序列化格式。该格式既适用于临时性的网络流量，也适用于长期的数据存储。Protobuf 可以在不使现有数据失效、也不要求更新代码的前提下，通过新增信息进行扩展。

Protobuf 是 Google 使用最广泛的数据格式。它被广泛用于服务器之间的通信，以及磁盘上数据的归档存储。Protobuf 的*消息*（message）与*服务*（service）由工程师编写的 `.proto` 文件描述。下面展示了一个 `message` 示例：

```proto
edition = "2023";

message Person {
  string name = 1;
  int32 id = 2;
  string email = 3;
}
```

proto 编译器会在构建时对 `.proto` 文件进行调用，以生成多种编程语言的代码（本主题后面的[跨语言兼容性](#cross-lang)一节将介绍），用于操作相应的 Protobuf 消息。每个生成的类都为每个字段提供了简单的访问器（accessor），以及把整个结构序列化为原始字节、或从原始字节解析回来的方法。下面展示了一个使用这些生成方法的示例：

```java
Person john = Person.newBuilder()
    .setId(1234)
    .setName("John Doe")
    .setEmail("jdoe@example.com")
    .build();
output = new FileOutputStream(args[0]);
john.writeTo(output);
```

由于 Protobuf 在 Google 的各类服务中都得到广泛使用，而且消息中的数据可能会留存一段时间，因此保持向后兼容（backward compatibility）至关重要。Protobuf 支持对任何 Protobuf 消息进行无缝变更——包括新增字段和删除现有字段——而不会破坏现有服务。有关这一主题的更多信息，请参阅本主题后面的[无需更新代码即可更新 proto 定义](#updating-defs)。

## 使用 Protobuf 有哪些好处？ {#benefits}

凡是你需要以语言无关（language-neutral）、平台无关（platform-neutral）、可扩展（extensible）的方式序列化结构化的、类似记录的类型化数据的场合，Protobuf 都是理想之选。它最常与 gRPC 搭配用于定义通信协议，以及用于数据存储。

使用 Protobuf 的一些优势包括：

*   紧凑的数据存储
*   快速解析
*   支持多种编程语言
*   通过自动生成的类获得优化后的功能

### 跨语言兼容性 {#cross-lang}

用任何受支持的编程语言编写的代码都可以读取相同的消息。你可以让一个平台上的 Java 程序从某个软件系统采集数据，依据 `.proto` 定义将其序列化，然后在运行于另一个平台的独立 Python 应用中，从这份数据的序列化结果里提取特定的值。

以下语言受到 Protobuf 编译器 protoc 的直接支持：

*   [C++](/reference/cpp/cpp-generated#invocation)
*   [C#](/reference/csharp/csharp-generated#invocation)
*   [Java](/reference/java/java-generated#invocation)
*   [Kotlin](/reference/kotlin/kotlin-generated#invocation)
*   [Objective-C](/reference/objective-c/objective-c-generated#invocation)
*   [PHP](/reference/php/php-generated#invocation)
*   [Python](/reference/python/python-generated#invocation)
*   [Ruby](/reference/ruby/ruby-generated#invocation)

以下语言由 Google 提供支持，但这些项目的源代码位于 GitHub 仓库中。protoc 编译器通过插件（plugin）来支持这些语言：

*   [Dart](https://github.com/google/protobuf.dart)
*   [Go](https://github.com/protocolbuffers/protobuf-go)

还有一些语言并非由 Google 直接支持，而是由 GitHub 上的其他项目提供支持。这些语言收录于 [Protobuf 的第三方附加组件](https://github.com/protocolbuffers/protobuf/blob/master/docs/third_party.md)。

### 跨项目支持 {#cross-proj}

你可以在位于特定项目代码库之外的 `.proto` 文件中定义 `message` 类型，从而跨项目使用 Protobuf。如果你定义的 `message` 类型或枚举（enum）预计会在你所在团队之外被广泛使用，可以将它们放入一个没有依赖关系的独立文件中。

在 Google 内部广泛使用的 proto 定义示例包括 [`timestamp.proto`](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) 和 [`status.proto`](https://github.com/googleapis/googleapis/blob/master/google/rpc/status.proto)。

### 无需更新代码即可更新 proto 定义 {#updating-defs}

软件产品做到向后兼容是常态，但做到向前兼容（forward compatibility）则较为少见。只要在更新 `.proto` 定义时遵循一些[简单实践](/programming-guides/proto3#updating)，旧代码就能毫无问题地读取新消息，并忽略所有新增的字段。对旧代码而言，被删除的字段将取其默认值（default value），被删除的 repeated 字段则为空。有关 “repeated” 字段是什么的说明，请参阅本主题后面的 [Protobuf 定义语法](#syntax)。

新代码同样可以透明地读取旧消息。旧消息中不会存在新字段；在这种情况下，Protobuf 会提供一个合理的默认值。

### Protobuf 在哪些情况下不适用？ {#not-good-fit}

Protobuf 并不适用于所有数据。具体来说：

*   Protobuf 倾向于假设整条消息可以一次性载入内存，且大小不超过一个对象图。对于超过几 MB 的数据，请考虑其他方案；处理更大的数据时，由于存在序列化副本，你实际上可能最终持有数据的多个副本，这可能导致内存使用量出现惊人的峰值。
*   Protobuf 消息被序列化后，同一份数据可能存在多种不同的二进制序列化形式。如果不将两条消息完整解析，就无法比较它们是否相等。
*   消息本身不会被压缩。虽然消息可以像其他任何文件一样进行 zip 或 gzip 压缩，但对于合适类型的数据，JPEG 和 PNG 所采用的那类专用压缩算法能生成小得多的文件。
*   对于许多涉及大型多维浮点数数组的科学和工程应用而言，Protobuf 消息在大小和速度上都达不到最优效率。对于这类应用，[FITS](https://en.wikipedia.org/wiki/FITS) 及类似格式的开销更小。
*   在科学计算领域流行的非面向对象语言（如 Fortran 和 IDL）中，Protobuf 得到的支持并不理想。
*   Protobuf 消息本身并不天然地自描述其数据，但它们拥有完全支持反射（reflection）的模式（schema），你可以借助它来实现自描述。也就是说，如果无法访问相应的 `.proto` 文件，你就无法完整解读一条消息。
*   Protobuf 不是任何组织的正式标准。这使得它不适合用于在法律或其他方面要求必须基于标准进行构建的环境。

## 谁在使用 Protobuf？ {#who-uses}

许多项目都在使用 Protobuf，其中包括：

+   [gRPC](https://grpc.io)
+   [Google Cloud](https://cloud.google.com)
+   [Envoy Proxy](https://www.envoyproxy.io)

## Protobuf 是如何工作的？ {#work}

下图展示了你如何使用 Protobuf 处理自己的数据。

![展示 proto 文件的创建、生成代码与编译后类的编译工作流](/images/protocol-buffers-concepts.png) \
**图 1. Protobuf 工作流**

Protobuf 生成的代码提供了一些实用方法，可用于从文件和流中获取数据、从数据中提取单个值、检查数据是否存在、把数据序列化回文件或流，以及其他有用的功能。

下面的代码示例以 Java 为例展示了这一流程。如前文所示，这是一个 `.proto` 定义：

```proto
message Person {
  string name = 1;
  int32 id = 2;
  string email = 3;
}
```

编译这个 `.proto` 文件会生成一个 `Builder`（构建器）类，你可以用它来创建新实例，如下面的 Java 代码所示：

```java
Person john = Person.newBuilder()
    .setId(1234)
    .setName("John Doe")
    .setEmail("jdoe@example.com")
    .build();
output = new FileOutputStream(args[0]);
john.writeTo(output);
```

然后，你可以使用 Protobuf 为其他语言生成的方法来反序列化数据，例如 C++：

```cpp
Person john;
fstream input(argv[1], ios::in | ios::binary);
john.ParseFromIstream(&input);
int id = john.id();
std::string name = john.name();
std::string email = john.email();
```

## Protobuf 定义语法 {#syntax}

定义 `.proto` 文件时，你可以指定字段的基数（cardinality），即单数还是可重复。在 proto2 和 proto3 中，你还可以将字段指定为 optional。在 proto3 中，把字段设置为 optional 会[将其从隐式存在性（implicit presence）变为显式存在性（explicit presence）](/programming-guides/field_presence)。

设置好字段的基数之后，你需要指定数据类型。Protobuf 支持常见的原始数据类型，例如整数、布尔值和浮点数。完整列表请参阅[标量值类型](/programming-guides/proto3#scalar)。

字段还可以是以下类型：

*   `message` 类型，让你可以嵌套定义的各个部分，例如用于重复出现的数据集合。
*   `enum`（枚举）类型，让你可以指定一组可供选择的值。
*   `oneof` 类型，当一条消息有许多 optional 字段、而同一时间最多只会设置其中一个字段时可以使用。
*   `map` 类型，用于在你的定义中添加键值对。

消息可以允许**扩展（extension）**在消息本身之外定义字段。例如，Protobuf 库的内部消息模式允许通过扩展来添加自定义的、面向特定用途的选项。

有关可用选项的更多信息，请参阅 [proto2](/programming-guides/proto2)、[proto3](/programming-guides/proto3) 或 [版次 2023](/programming-guides/editions) 的语言指南（language guide）。

设置好基数和数据类型之后，你需要为字段选择一个名称。设置字段名（field name）时需要注意以下几点：

*   字段名在生产环境中投入使用后，有时会难以更改，甚至无法更改。
*   字段名不能包含连字符。有关字段名语法的更多信息，请参阅[消息与字段名](/programming-guides/style#message-field-names)。
*   repeated 字段应使用复数形式的名称。

为字段指定名称之后，你还要为它分配一个字段编号（field number）。字段编号不能被改作他用，也不能重复使用。如果你删除了某个字段，应当保留它的字段编号，以防有人无意间复用该编号。

## 其他数据类型支持 {#data-types}

Protobuf 支持许多标量（scalar）值类型，包括采用可变长度编码（variable-length encoding）和固定大小的整数。你还可以通过定义消息来创建自己的复合数据类型——这些消息本身就是可以赋给字段的数据类型。除了简单值类型和复合值类型之外，还有一些[常用类型](/best-practices/dos-donts#well-known-common)已经发布。

## 历史 {#history}

要了解 Protobuf 项目的历史，请参阅 [Protobuf 的历史](/history)。

## Protobuf 开源理念 {#philosophy}

Protobuf 于 2008 年开源，目的是让 Google 之外的开发者也能获得我们在内部从中获得的同样收益。当我们为满足内部需求而对语言做出相应变更时，也会通过定期更新语言来支持开源社区。虽然我们接受外部开发者的部分拉取请求（pull request），但无法始终优先处理那些不符合 Google 具体需求的特性请求和缺陷修复。

## 开发者社区 {#community}

若想及时了解 Protobuf 即将发生的变更，并与 Protobuf 的开发者和用户建立联系，请[加入 Google 网上论坛](https://groups.google.com/g/protobuf)。

## 其他资源 {#additional-resources}

*   [Protobuf GitHub](https://github.com/protocolbuffers/protobuf/)
    * [教程](https://protobuf.dev/getting-started/)
