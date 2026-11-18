+++
title = "Protobuf"
weight = 5
toc_hide = "true"
description = "Protobuf 是一种语言无关、平台无关的可扩展结构化数据序列化机制。"
type = "docs"
no_list = "true"
source_url = "https://protobuf.dev/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-18"
status = "translated"
translator = "agent"
+++

## 什么是 Protobuf？

Protobuf（“Protocol Buffers”）是 Google 的语言无关（language-neutral）、平台无关（platform-neutral）、可扩展（extensible）的结构化数据（structured data）序列化（serialization）机制——可以把它想成 XML，但更小、更快、也更简单。你只需定义一次自己的数据结构，之后就可以使用特殊的生成代码（generated code），在多种语言中轻松地将结构化数据写入和读出各种数据流。

## 选择你喜欢的语言

Protobuf 支持为 C++、C#、Dart、Go、Java、Kotlin、Objective-C、Python、Rust 和 Ruby 生成代码。使用 proto3 时，你还可以使用 PHP。

## 示例实现

```proto
edition = "2024";

message Person {
  string name = 1;
  int32 id = 2;
  string email = 3;
}
```

**图 1.** 一条 proto 定义。

```java
// Java 代码
Person john = Person.newBuilder()
    .setId(1234)
    .setName("John Doe")
    .setEmail("jdoe@example.com")
    .build();
output = new FileOutputStream(args[0]);
john.writeTo(output);
```

**图 2.** 使用生成的类持久化数据。

```cpp
// C++ 代码
Person john;
fstream input(argv[1],
    ios::in | ios::binary);
john.ParseFromIstream(&input);
id = john.id();
name = john.name();
email = john.email();
```

**图 3.** 使用生成的类解析已持久化的数据。

## 如何开始？

<ol>

  <li>
    <a href="https://github.com/protocolbuffers/protobuf#protobuf-compiler-installation">下载并安装</a> Protobuf 编译器。
  </li>

  <li>
    阅读<a href="/overview">概览</a>。
  </li>
  <li>
    试一试适合你所选语言的<a href="/getting-started">教程</a>。
  </li>
</ol>
