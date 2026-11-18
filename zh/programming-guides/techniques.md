+++
title = "技巧"
weight = 70
description = "介绍处理 Protobuf 时常用的一些设计模式。"
type = "docs"
source_url = "https://protobuf.dev/programming-guides/techniques/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

你也可以把设计与使用方面的问题发送到
[Protobuf 讨论组](http://groups.google.com/group/protobuf)。

## 常见文件名后缀 {#suffixes}

把消息（message）写入多种不同格式的文件是相当常见的做法。我们建议对这些文件使用以下文件扩展名。

内容 | 扩展名
--- | ---
[文本格式](/reference/protobuf/textformat-spec) | `.txtpb`
[线路格式](/programming-guides/encoding) | `.binpb`
[JSON 格式](/programming-guides/proto3#json) | `.json`

具体到文本格式，`.textproto` 也相当常见，但出于简洁考虑，我们推荐使用 `.txtpb`。

## 流式写入多条消息 {#streaming}

如果你想将多条消息写入单个文件或流，就需要由你自己来记录一条消息在哪里结束、下一条消息从哪里开始。Protobuf 的线路格式（wire format）不具备自定界能力，因此 Protobuf 解析器无法自行确定一条消息在哪里结束。解决这一问题最简单的办法，是在写入每条消息本身之前，先写入该消息的大小。读回消息时，先读取这个大小，再把相应的字节读入一个单独的缓冲区，然后从该缓冲区进行解析。（如果想避免把字节复制到单独的缓冲区，可以了解一下 `CodedInputStream` 类（C++ 和 Java 中均有提供），它可以被设置为将读取限制在指定数量的字节之内。）

## 大型数据集 {#large-data}

Protobuf 的设计初衷并不是处理大型消息。根据一般经验，如果你要处理的消息每条都超过 1 MB，那么也许是时候考虑换一种策略了。

话虽如此，对于大型数据集*内部*的单条消息，Protobuf 处理起来得心应手。通常，大型数据集是许多小片段的集合，其中每个小片段都是结构化数据（structured data）。尽管 Protobuf 无法一次性处理整个数据集，但用 Protobuf 对每个片段进行编码会大大简化你的问题：此时你只需要处理一组字节串，而不必处理一组结构。

Protobuf 没有为大型数据集提供任何内建支持，因为不同的场景需要不同的解决方案。有时一个简单的记录列表就够用了，而有时你需要的则更像一个数据库。每种解决方案都应当作为独立的库来开发，这样只有真正需要它的人才需要付出相应的代价。

## 自描述消息 {#self-description}

Protobuf 消息并不包含对自身类型的描述。因此，如果只有一个原始消息，而没有定义其类型的对应 `.proto` 文件，就很难从中提取出任何有用的数据。

不过，.proto 文件的内容本身也可以用 Protobuf 来表示。源代码包中的 `src/google/protobuf/descriptor.proto` 文件定义了其中涉及的消息类型。`protoc` 可以使用 `--descriptor_set_out` 选项输出一个 `FileDescriptorSet`——它表示一组 .proto 文件。借助这一点，你可以像下面这样定义一个自描述的协议消息：

```proto
syntax = "proto3";

import "google/protobuf/any.proto";
import "google/protobuf/descriptor.proto";

message SelfDescribingMessage {
  // 描述该类型及其依赖项的 FileDescriptorProto 集合。
  google.protobuf.FileDescriptorSet descriptor_set = 1;

  // 以 Any 消息编码的消息及其类型。
  google.protobuf.Any message = 2;
}
```

借助 `DynamicMessage`（C++ 和 Java 中均有提供）这样的类，你就可以编写能够操作 `SelfDescribingMessage` 的工具。

尽管如此，Protobuf 库之所以没有包含这项功能，是因为我们在 Google 内部从未用到过它。

这种技巧的前提是环境支持基于描述符（descriptor）的动态消息。在使用自描述消息之前，请确认你的平台支持这一特性。
