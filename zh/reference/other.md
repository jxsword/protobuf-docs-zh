+++
title = "其他语言"
weight = 840
description = "protoc，即 Protobuf 编译器，可通过插件扩展以支持新语言。"
type = "docs"
source_url = "https://protobuf.dev/reference/other/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

尽管当前发布版本已包含 C++、Java、Go、Ruby、C\# 和 Python 的编译器与 API，但编译器代码在设计上使得添加对其他语言的支持变得容易。目前有多个进行中的项目正在为 Protobuf 添加新语言实现，包括 C、Haskell、Perl、Rust 等。

如需查看我们所了解项目的链接列表，请参见[第三方附加组件（add-on）wiki 页面](https://github.com/protocolbuffers/protobuf/blob/main/docs/third_party.md)。

## 编译器插件 {#plugins}

`protoc`，即 Protobuf 编译器，可通过插件（plugin）扩展以支持新语言。插件只是一个程序，它从标准输入读取一个 `CodeGeneratorRequest` Protobuf 消息（message），然后将一个 `CodeGeneratorResponse` Protobuf 消息写入标准输出。这些消息类型定义在 [`plugin.proto`](/reference/cpp/api-docs/google.protobuf.compiler.plugin.pb) 中。我们建议所有第三方代码生成器都以插件形式编写，这样所有生成器便能提供一致的接口，并共享同一个解析器实现。

插件可以用任何编程语言编写，但 Google 自有的插件是用 C++ 编写的。如果你要编写自己的插件，或许会发现用 C++ 编写最容易上手，这样插件就能参照这些示例并复用其中的实用工具。

此外，插件还能够向其他代码生成器生成的文件中插入代码。更多细节请参见 `plugin.proto` 中关于“插入点（insertion points）”的注释。例如，可以借此编写一个插件，为特定远程过程调用（RPC）系统生成量身定制的 RPC 服务代码。各语言的生成代码文档中说明了它们所提供的插入点。
