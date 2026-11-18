+++
title = "Go Opaque API 常见问题"
weight = 670
linkTitle = "Opaque API 常见问题"
description = "关于 Opaque API 的常见问题列表。"
type = "docs"
source_url = "https://protobuf.dev/reference/go/opaque-faq/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

<style>
.good pre {
  border-left: 2px solid;
  border-left-color: #0b8043;
  background-color: #e2f3eb !important;
}
.bad pre {
  border-left: 2px solid;
  border-left-color: #c53929;
  background-color: #fbe9e7 !important;
}
</style>

Opaque API 是面向 Go 编程语言的 Protobuf 实现的最新版本。旧版本现在称为 Open Struct API。简介请参阅博文 [Go Protobuf: The new Opaque API](https://go.dev/blog/protobuf-opaque)。

本 FAQ 回答关于新 API 以及迁移过程的常见问题。

## 创建新 .proto 文件时应选用哪个 API？ {#which}

我们建议你在新开发中选用 Opaque API。

Protobuf 版次（edition）2024（参见 [Protobuf 版次概览](/editions/overview/)）将 Opaque API 设为默认。

## 如何为我的消息启用新的 Opaque API？ {#enable}

从 Protobuf 版次 2023 开始，你可以在 `.proto` 文件中把 `api_level` 这个版次特性（feature）设置为 `API_OPAQUE`，从而选择 Opaque API。它既可以按文件设置，也可以按消息（message）设置：

```proto
edition = "2023";

package log;

import "google/protobuf/go_features.proto";
option features.(pb.go).api_level = API_OPAQUE;

message LogEntry { … }
```

Protobuf 版次 2024 默认采用 Opaque API，也就是说你不再需要额外的导入或选项：

```proto
edition = "2024";

package log;

message LogEntry { … }
```

为方便起见，你也可以用 `protoc` 命令行标志来覆盖默认的 API 级别：

```
protoc […] --go_opt=default_api_level=API_HYBRID
```

要针对某个特定文件（而非所有文件）覆盖默认的 API 级别，请使用 `apilevelM` 映射标志（类似于[用于导入路径的 `M` 标志](/reference/go/go-generated/#package)）：

```
protoc […] --go_opt=apilevelMhello.proto=API_HYBRID
```

这些命令行标志对仍在使用 proto2 或 proto3 语法的 `.proto` 文件同样有效；但如果你想从 `.proto` 文件内部选择 API 级别，则需要先把该文件迁移到版次。

## 如何启用惰性解码（lazy decoding）？ {#lazydecoding}

1.  将你的代码迁移为使用 Opaque 实现。
1.  在需要进行惰性解码的 proto 子消息（submessage）字段（field）上设置 `[lazy = true]` 选项。
1.  运行你的单元测试和集成测试，然后部署到预发布（staging）环境。

## 惰性解码是否会忽略错误？ {#lazydecodingerrors}

不会。
[`proto.Marshal`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#Marshal)
始终会校验线路格式（wire format）数据，即使解码被推迟到首次访问时才执行。

## 在哪里可以提问或报告问题？ {#questions}

如果你发现 `open2opaque` 迁移工具存在问题（例如重写出的代码不正确），请在 [open2opaque 问题跟踪器（issue tracker）](https://github.com/golang/open2opaque/issues)中报告。

如果你发现 Go Protobuf 本身的问题，请在 [Go Protobuf 问题跟踪器](https://github.com/golang/protobuf/issues/)中报告。

## Opaque API 有哪些好处？ {#benefits}

Opaque API 带来诸多好处：

*   它采用更高效的内存表示，从而降低内存和垃圾回收（Garbage Collection）开销。
*   它使惰性解码成为可能，可以显著提升性能。
*   它修复了若干容易踩坑的细节（sharp edges）。指针地址比较、意外的数据共享或对 Go 反射（reflection）的非预期使用所导致的缺陷，在使用 Opaque API 时都会被杜绝。
*   它通过启用基于性能剖析（profile-driven）的优化，让理想的内存布局（memory layout）成为可能。

更多细节请参阅博文 [Go Protobuf: The new Opaque API](https://go.dev/blog/protobuf-opaque)。

## 构建器（builder）与 setter 哪个更快？ {#builders-faster}

一般来说，使用构建器的代码：

```go
_ = pb.M_builder{
  F: &val,
}.Build()
```

比下面这段等价代码更慢：

```go
m := &pb.M{}
m.SetF(val)
```

原因如下：

1.  `Build()` 调用会遍历消息中的所有字段（包括未显式设置的字段），并把它们的值（如果有）复制到最终消息中。对于字段众多的消息，这种线性性能开销影响很大。
1.  可能产生一次额外的堆分配（`&val`）。
1.  在存在 oneof 字段时，构建器可能明显更大、占用更多内存。构建器为 oneof 联合中的每个成员都保留一个字段，而消息可以把 oneof 本身作为单个字段存储。

除了运行时（runtime）性能之外，如果你在意二进制体积，避免使用构建器还能带来更少的代码。

## 如何使用构建器？ {#builders-how}

构建器被设计成以*值*的方式使用，并紧跟一次 `Build()` 调用。避免使用指向构建器的指针，也避免把构建器存入变量。

```go {.good}
m := pb.M_builder{
    // ...
}.Build()
```

```go {.bad}
// 不佳：避免使用指针
m := (&pb.M_builder{
    // ...
}).Build()
```

```go {.bad highlight="content:b.:= "}
// 不佳：避免存入变量
b := pb.M_builder{
    // ...
}
m := b.Build()
```

在某些其他语言中，proto 消息是不可变的，因此用户在构造 proto 消息时倾向于把构建器类型传入函数调用。而 Go 的 proto 消息是可变的，因此无需把构建器传入函数调用——直接传递 proto 消息即可。

```go {.bad}
// 不佳：避免在函数间传递构建器
func populate(mb *pb.M_builder) {
  mb.Field1 = proto.Int32(4711)
  //...
}
// ...
mb := pb.M_builder{}
populate(&mb)
m := mb.Build()
```

```go {.good}
func populate(mb *pb.M) {
  mb.SetField1(4711)
  //...
}
// ...
m := &pb.M{}
populate(m)
```

构建器的设计初衷是模仿 Open Struct API 的复合字面量（composite literal）构造方式，而不是作为 proto 消息的另一种表示形式。

推荐的模式性能也更好。在构建器结构体字面量上直接调用 `Build()` 这一预期用法可以得到充分优化。而单独调用一次 `Build()` 则很难优化，因为编译器可能不容易识别哪些字段被赋了值。如果构建器存活得更久，标量（scalar）这类小对象很有可能必须在堆上分配，之后还需要由垃圾回收器释放。

## 应该使用构建器还是 setter？ {#builders-vs-setters}

构造空的 Protobuf 消息时，你应该使用 `new` 或空的复合字面量。在 Go 中，这两种写法构造零初始化值都同样地道，而且比空构建器性能更好。

```go {.good}
m1 := new(pb.M)
m2 := &pb.M{}
```

```go {.bad}
// 不佳：避免：不必要地复杂
m1 := pb.M_builder{}.Build()
```

当需要构造非空的 Protobuf 消息时，你可以选择使用 setter 或构建器。两者皆可，但大多数人会觉得构建器可读性更好。如果你编写的代码需要追求性能，[setter 通常比构建器性能略好](#builders-faster)。

```go {.good}
// 推荐：使用构建器
m1 := pb.M1_builder{
    Submessage: pb.M2_builder{
        Submessage: pb.M3_builder{
            String: proto.String("hello world"),
            Int:    proto.Int32(42),
        }.Build(),
        Bytes: []byte("hello"),
    }.Build(),
}.Build()
```

```go
// 也可以：使用 setter
m3 := &pb.M3{}
m3.SetString("hello world")
m3.SetInt(42)
m2 := &pb.M2{}
m2.SetSubmessage(m3)
m2.SetBytes([]byte("hello"))
m1 := &pb.M1{}
m1.SetSubmessage(m2)
```

如果某些字段在设置前需要条件逻辑，你可以将构建器与 setter 结合使用。

```go {.good}
m1 := pb.M1_builder{
    Field1: value1,
}.Build()
if someCondition() {
    m1.SetField2(value2)
    m1.SetField3(value3)
}
```

## 如何影响 open2opaque 的构建器行为？ {#builders-flags}

`open2opaque` 工具的 `--use_builders` 标志可以取以下值：

*   `--use_builders=everywhere`：总是使用构建器，无一例外。
*   `--use_builders=tests`：仅在测试中使用构建器，其余情况使用 setter。
*   `--use_builders=nowhere`：从不使用构建器。

## 可以期望多大的性能收益？ {#performance-benefit}

这在很大程度上取决于你的工作负载（workload）。以下几个问题可以引导你进行性能探索：

*   Go Protobuf 占你 CPU 使用率的比例有多大？某些工作负载——例如基于 Protobuf 输入记录计算统计信息的日志分析流水线——可能有约 50% 的 CPU 使用率消耗在 Go Protobuf 上。这类工作负载的性能提升很可能清晰可见。而处于另一个极端，在 Go Protobuf 仅占 CPU 使用率 3-5% 的程序中，相比其他优化机会，性能提升往往微不足道。
*   你的程序在多大程度上适合惰性解码？如果输入消息的很大一部分从未被访问，惰性解码就能省去大量工作。这种模式通常出现在代理服务器（将输入原样透传）或高选择性的日志分析流水线（基于上层谓词丢弃大量记录）这类作业中。
*   你的消息定义是否包含许多具有显式存在性（explicit presence）的基本类型字段（elementary field）？Opaque API 对整数、布尔值、枚举（enum）和浮点数这类基本类型字段使用更高效的内存表示，但字符串、repeated 字段和子消息则不然。

## proto2、proto3 和版次与 Opaque API 是什么关系？ {#proto23editions}

proto2 和 proto3 这两个术语指 `.proto` 文件中不同的语法版本。[Protobuf 版次](/editions/overview)是 proto2 和 proto3 二者的后继者。

Opaque API 只影响 `.pb.go` 文件中的生成代码（generated code），而不影响你在 `.proto` 文件中编写的内容。

无论 `.proto` 文件使用哪种语法或版次，Opaque API 的行为都完全相同。不过，如果你想按文件选择 Opaque API（而不是在运行 `protoc` 时使用命令行标志），就必须先把该文件迁移到版次。详情请参见[如何为我的消息启用新的 Opaque API？](#enable)。

## 为什么只改变基本类型字段的内存布局？ {#memorylayout}

[发布博文（announcement blog post）中“Opaque 结构体占用更少内存”一节](https://go.dev/blog/protobuf-opaque#lessmemory)解释道：

> 这项性能提升[更高效地为字段存在性（field presence）建模]在很大程度上取决于你的 Protobuf 消息形态：这一变更只影响整数、布尔值、枚举和浮点数等基本类型字段，而不影响字符串、repeated 字段或子消息。

一个自然的后续问题是：为什么在 Opaque API 中字符串、repeated 字段和子消息仍是指针。答案有两个方面。

### 考量 1：内存占用

如果将子消息表示为值而非指针，内存占用会增加：每种 Protobuf 消息类型都带有内部状态，即使子消息实际上未被设置，这些状态也会消耗内存。

对于字符串和 repeated 字段，情况更为微妙。我们来比较一下使用字符串值与字符串指针各自的内存占用：

Go 变量类型 | 是否已设置？ | 机器字（[word]）数       | 字节数
---------------- | ---- | ------------------------ | ------
`string`         | 是   | 2 (data, len)            | 16
`string`         | 否   | 2 (data, len)            | 16
`*string`        | 是   | 1 (data) + 2 (data, len) | 24
`*string`        | 否   | 1 (data)                 | 8

[word]: https://en.wikipedia.org/wiki/Word_(computer_architecture)

（切片的情况类似，但切片头需要 3 个机器字：data、len、cap。）

如果你的字符串字段绝大多数都未被设置，使用指针可以节省 RAM。当然，这种节省的代价是给程序引入更多的分配和指针，从而加重垃圾回收器的负载。

Opaque API 的优势在于，我们无需对用户代码做任何改动就能改变其表示方式。当前的内存布局在引入时对我们而言是最优的，但如果放到今天或 5 年后再来衡量，我们或许会选择另一种布局。

正如[发布博文中“让理想的内存布局成为可能”一节](https://go.dev/blog/protobuf-opaque#idealmemory)所述，我们希望在未来按工作负载逐案做出这些优化决策。

### 考量 2：惰性解码

除内存占用方面的考量外，还有另一项限制：启用了[惰性解码](#lazydecoding)的字段必须以指针表示。

Protobuf 消息可以安全地并发访问（但不能并发修改），因此如果两个不同的 goroutine 触发了惰性解码，它们需要以某种方式进行协调。这种协调通过 [`sync/atomic` 包](https://pkg.go.dev/sync/atomic)实现：该包可以原子地更新指针，却无法原子地更新切片头（切片头的大小超过一个 [word]）。

虽然 `protoc` 目前只允许对（非 repeated 的）子消息启用惰性解码，但这一论证适用于所有字段类型。
