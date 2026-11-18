+++
title = "Go Opaque API 迁移"
weight = 650
linkTitle = "Opaque API 迁移"
description = "描述向 Opaque API 的自动化迁移。"
type = "docs"
source_url = "https://protobuf.dev/reference/go/opaque-migration/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

Opaque API 是面向 Go 编程语言的 Protobuf 实现的最新版本。旧版本现在称为 Open Struct API。简介请参阅博文 [Go Protobuf: The new Opaque API](https://go.dev/blog/protobuf-opaque)。

向 Opaque API 的迁移以增量方式进行，以单个 proto 消息（message）或单个 `.proto` 文件为单位，方法是将其 `api_level` 特性（feature）设置为以下可能的取值之一：

*   `API_OPEN` 选择 Open Struct API。该取值已向后移植进版次 2023，因此较旧版本的 Go 插件（plugin）可能不会遵守它。
*   `API_HYBRID` 是介于 Open 与 Opaque 之间的一步：Hybrid API 也提供访问器（accessor）方法（因此你可以更新代码），但仍像以前一样导出结构体（struct）字段。二者在性能上没有差异；这一 API 级别只是为迁移提供便利。
*   `API_OPAQUE` 选择 Opaque API；这是版次 2024 及更高版次的默认值。

要为特定的 `.proto` 文件覆盖默认值，请设置 `api_level` 特性：

```proto
edition = "2024";

package log;

import "google/protobuf/go_features.proto";
option features.(pb.go).api_level = API_OPEN;

message LogEntry { … }
```

在将现有文件的 `api_level` 更改为 `API_OPAQUE` 之前，需要先更新生成代码（generated code）的所有现有用法。`open2opaque` 工具可以协助完成这项工作。

为方便起见，你也可以用 `protoc` 命令行标志覆盖默认 API 级别：

```
protoc […] --go_opt=default_api_level=API_OPEN
```

要为特定文件（而非所有文件）覆盖默认 API 级别，请使用 `apilevelM` 映射标志（类似于[用于导入路径的 `M` 标志](/reference/go/go-generated/#package)）：

```
protoc […] --go_opt=apilevelMhello.proto=API_OPEN
```

## 自动化迁移 {#automated}

我们尽力让现有项目向 Opaque API 的迁移对你来说尽可能简单：我们的 open2opaque 工具会完成大部分工作！

要安装迁移工具，请执行：

```
go install google.golang.org/open2opaque@latest
go install golang.org/x/tools/cmd/goimports@latest
```

{{% alert title="Note" color="info" %}}如果你在使用自动化迁移方式时遇到任何问题，请参阅 [Opaque API：手动迁移](/reference/go/opaque-migration-manual) 指南。 {{% /alert %}}

### 项目准备 {#projectprep}

确保你的构建环境和项目所使用的 Protobuf 与 Go Protobuf 版本足够新：

1.  从 [Protobuf 发布页面](https://github.com/protocolbuffers/protobuf/releases/latest) 将 Protobuf 编译器（protoc）更新到 29.0 或更新版本。

1.  将 Protobuf 编译器 Go 插件（protoc-gen-go）更新到 1.36.0 或更新版本：

    ```
    go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
    ```

1.  在每个项目中，更新 `go.mod` 文件，使其使用 1.36.0 或更新版本的 Protobuf 模块：

    ```
    go get google.golang.org/protobuf@latest
    ```

    {{% alert title="Note" color="note" %}}如果你尚未导入 `google.golang.org/protobuf`，你可能仍在使用较旧的模块。请参阅 [`google.golang.org/protobuf` 公告（2020 年）](https://go.dev/blog/protobuf-apiv2)，先迁移你的代码，然后再回到本页。 {{% /alert %}}

### 步骤 1：切换到 Hybrid API {#setup}

使用 `open2opaque` 工具将你的 `.proto` 文件切换到 Hybrid API：

```
open2opaque setapi -api HYBRID $(find . -name "*.proto")
```

然后，[重新编译](/getting-started/gotutorial#compiling-protocol-buffers)你的 `.proto` 文件。

你现有的代码将继续正常编译。Hybrid API 是介于 Open 与 Opaque API 之间的一个过渡步骤，它添加了新的访问器方法，但保持结构体字段可见。

### 步骤 2：`open2opaque rewrite` {#rewrite}

要改写你的 Go 代码以改用 Opaque API，请运行 `open2opaque rewrite` 命令：

```
open2opaque rewrite -levels=red github.com/robustirc/robustirc/...
```

你可以指定一个或多个[包（package）或模式（pattern）](https://pkg.go.dev/cmd/go#hdr-Package_lists_and_patterns)。

举例来说，如果你原来有这样一段代码：

```go
logEntry := &logpb.LogEntry{}
if req.IPAddress != nil {
    logEntry.IPAddress = redactIP(req.IPAddress)
}
logEntry.BackendServer = proto.String(host)
```

该工具会将其改写为使用访问器：

```go
logEntry := &logpb.LogEntry{}
if req.HasIPAddress() {
    logEntry.SetIPAddress(redactIP(req.GetIPAddress()))
}
logEntry.SetBackendServer(host)
```

另一个常见示例是用结构体字面量初始化 Protobuf 消息：

```go
return &logpb.LogEntry{
    BackendServer: proto.String(host),
}
```

在 Opaque API 中，等价写法是使用构建器（Builder）：

```go
return logpb.LogEntry_builder{
    BackendServer: proto.String(host),
}.Build()
```

该工具会将其可用的改写划分为不同级别。`-levels=red` 参数会启用全部改写，包括那些需要人工审查的改写。可用级别如下：

*   <span style="background-color: lightgreen">green:</span> 安全的改写（置信度高）。包括该工具所做的大部分变更。这些变更无需仔细检查，甚至可以由自动化提交，无需任何人工监督。
*   <span style="background-color: yellow">yellow:</span>（置信度尚可）这些改写需要人工审查。它们应该是正确的，但仍请加以审查。
*   <span style="background-color: salmon">red:</span> 有潜在危险的改写，会改动罕见且复杂的模式。这类改写需要仔细的人工审查。例如，当某个现有函数接受 `*string` 参数时，如果该函数本意是通过写入指针（`*foo = "value"`）来修改字段值，那么使用 `proto.String(msg.GetFoo())` 这一典型修复方式就不会生效。

许多程序只需 green 级别的变更即可完成完整迁移。在将某个 proto 消息或文件迁移到 Opaque API 之前，你需要完成所有级别的全部改写，届时你的代码中就不会再残留任何直接的结构体访问。

### 步骤 3：迁移并验证 {#migrate-and-verify}

要完成迁移，请使用 `open2opaque` 工具将你的 `.proto` 文件切换到 Opaque API：

```
open2opaque setapi -api OPAQUE $(find . -name "*.proto")
```

此时，任何尚未改写为 Opaque API 的剩余代码都将无法再通过编译。

运行你的单元测试、集成测试以及其他验证步骤（如有）。

## 有疑问？遇到问题？

首先，请查阅 [Opaque API 常见问题（FAQ）](/reference/go/opaque-faq)。如果它没有解答你的疑问或解决你的问题，请参阅[在哪里可以提问或报告问题？](/reference/go/opaque-faq#questions)
