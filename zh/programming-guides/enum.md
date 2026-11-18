+++
title = "枚举行为"
weight = 55
description = "讲解 Protobuf 中枚举（enum）目前的工作方式与应有的工作方式。"
type = "docs"
source_url = "https://protobuf.dev/programming-guides/enum/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

枚举（enum）在不同语言的库中行为各不相同。本主题涵盖这些不同的行为，以及让 Protobuf 最终实现枚举在所有语言间保持一致的相关计划。如果你想了解枚举的一般用法，请参阅 [proto2](/programming-guides/proto2#enum)、[proto3](/programming-guides/proto3#enum) 与[版次（editions）2023](/programming-guides/editions#enum) 语言指南主题中的相应章节。

## 定义 {#definitions}

枚举有两种截然不同的形式：*开放式*（open）与*封闭式*（closed）。除了对未知值的处理方式之外，二者的行为完全相同。实际使用中，这意味着简单场景下二者表现一致，但某些边缘情况会产生有趣的影响。

为便于说明，假设我们有下面这个 `.proto` 文件（这里刻意不指明它是 `syntax = "proto2"`、`syntax = "proto3"` 还是 `edition = "2023"` 文件）：

```
enum Enum {
  A = 0;
  B = 1;
}

message Msg {
  optional Enum enum = 1;
}
```

*开放式*与*封闭式*的区别可以归结为一个问题：

> 当程序解析包含字段 1 且其值为 `2` 的二进制数据时，会发生什么？

*   **开放式**枚举会解析值 `2` 并将其直接存储在字段中。访问器（accessor）会将该字段报告为*已设置*，并返回某个表示 `2` 的值。
*   **封闭式**枚举会解析值 `2` 并将其存储到消息（message）的未知字段集（unknown field set）中。访问器会将该字段报告为*未设置*，并返回该枚举的默认值（default value）。

## *封闭式*枚举的影响

*封闭式*枚举的行为在解析可重复字段（repeated field）时会产生意想不到的后果。解析 `repeated Enum` 字段时，所有未知值都会被放入[未知字段](/programming-guides/proto3/#unknowns)集。当消息被再次序列化时，这些未知值会被重新写入，*但不会写回它们在列表中原有的位置*。例如，给定以下 `.proto` 文件：

```
enum Enum {
  A = 0;
  B = 1;
}

message Msg {
  repeated Enum r = 1;
}
```

当线路格式（wire format）中字段 1 的值为 `[0, 2, 1, 2]` 时，解析后可重复字段将包含 `[0, 1]`，而值 `[2, 2]` 最终会作为未知字段存储。重新序列化该消息后，线路格式将对应 `[0, 1, 2, 2]`。

同样，对于值类型为*封闭式*枚举的 map，只要值未知，整个条目（键和值）都会被放入未知字段中。

## 历史 {#history}

在 `syntax = "proto3"` 出现之前，所有枚举都是*封闭式*的。Proto3 与版次（editions）之所以使用*开放式*枚举，正是因为*封闭式*枚举会引发上述意外行为。如有需要，你可以使用 [`features.enum_type`](/editions/features#enum_type) 将版次枚举显式设置为封闭式。

## 规范 {#spec}

以下内容规定了符合规范的 Protobuf 实现所应具备的行为。由于其中细节颇为微妙，许多实现并不符合规范。各实现的具体行为差异详见[已知问题](#known-issues)。

*   当 `proto2` 文件导入 `proto2` 文件中定义的枚举时，该枚举应被视为**封闭式**。
*   当 `proto3` 文件导入 `proto3` 文件中定义的枚举时，该枚举应被视为**开放式**。
*   当 `proto3` 文件导入 `proto2` 文件中定义的枚举时，`protoc` 编译器会产生错误。
*   当 `proto2` 文件导入 `proto3` 文件中定义的枚举时，该枚举应被视为**开放式**。

版次会沿用枚举在被导入文件中原有的行为：Proto2 枚举始终按封闭式处理，proto3 枚举始终按开放式处理，而从另一个版次文件导入时，则使用特性（feature）设置。

## 已知问题 {#known-issues}

### C++ {#cpp}

所有已知的 C++ 发布版本均不符合规范。当 `proto2` 文件导入 `proto3` 文件中定义的枚举时，C++ 会将该字段视为**封闭式**枚举。在版次下，这一行为由已弃用的字段特性 [`features.(pb.cpp).legacy_closed_enum`](/editions/features#legacy_closed_enum) 表示。有两种方式可以转为符合规范的行为：

*   移除该字段特性。这是推荐的做法，但可能导致运行时（runtime）行为变化。移除该特性后，无法识别的整数将被强制转换为枚举类型并存入该字段，而不会放入未知字段集。
*   将枚举改为封闭式。不建议这样做：如果有*其他人*正在使用该枚举，可能导致运行时行为变化。无法识别的整数将进入未知字段集，而不是存入这些字段。

### C&#35; {#csharp}

所有已知的 C# 发布版本均不符合规范。C# 将所有枚举视为**开放式**。

### Java {#java}

所有已知的 Java 发布版本均不符合规范。当 `proto2` 文件导入 `proto3` 文件中定义的枚举时，Java 会将该字段视为**封闭式**枚举。

在版次下，这一行为由已弃用的字段特性 [`features.(pb.java).legacy_closed_enum`](/editions/features#legacy_closed_enum)) 表示。有两种方式可以转为符合规范的行为：

*   移除该字段特性。这可能导致运行时行为变化。移除该特性后，无法识别的整数将存入该字段，枚举 getter 将返回 `UNRECOGNIZED` 值。在此之前，这些值会被放入未知字段集。
*   将枚举改为封闭式。如果有*其他人*正在使用它，他们可能会遇到运行时行为变化。无法识别的整数将进入未知字段集，而不是存入这些字段。

> **注意：** Java 对**开放式**枚举的处理存在一些令人意外的边缘情况。给定以下定义：
>
> ```
> syntax = "proto3";
>
> enum Enum {
>   A = 0;
>   B = 1;
> }
>
> message Msg {
>   repeated Enum name = 1;
> }
> ```
>
> Java 会生成 `Enum getName()` 与 `int getNameValue()` 方法。对于已知集合之外的值（例如 `2`），`getName` 方法将返回 `Enum.UNRECOGNIZED`，而 `getNameValue` 将返回 `2`。
>
> 同样，Java 会生成 `Builder setName(Enum value)` 与 `Builder setNameValue(int value)` 方法。传入 `Enum.UNRECOGNIZED` 时，`setName` 方法会抛出异常，而 `setNameValue` 则会接受 `2`。

### Kotlin {#kotlin}

所有已知的 Kotlin 发布版本均不符合规范。当 `proto2` 文件导入 `proto3` 文件中定义的枚举时，Kotlin 会将该字段视为**封闭式**枚举。

Kotlin 基于 Java 构建，因此继承了 Java 的所有怪异行为。

### Go {#go}

所有已知的 Go 发布版本均不符合规范。Go 将所有枚举视为**开放式**。

### JSPB {#jspb}

所有已知的 JSPB 发布版本均不符合规范。JSPB 将所有枚举视为**开放式**。

### PHP {#php}

PHP 符合规范。

### Python {#python}

Python 在 4.22.0 以上的版本（发布于 2023 年第一季度）中符合规范。

不再受支持的旧版本不符合规范。当 `proto2` 文件导入 `proto3` 文件中定义的枚举时，不符合规范的 Python 版本会将该字段视为**封闭式**枚举。

### Ruby {#ruby}

所有已知的 Ruby 发布版本均不符合规范。Ruby 将所有枚举视为**开放式**。

### Objective-C {#obj-c}

Objective-C 在 3.22.0 以上的版本（发布于 2023 年第一季度）中符合规范。

不再受支持的旧版本不符合规范。当 `proto2` 文件导入 `proto3` 文件中定义的枚举时，不符合规范的 ObjC 版本会将该字段视为**封闭式**枚举。

### Swift {#swift}

Swift 符合规范。

### Dart {#dart}

Dart 将所有枚举视为**封闭式**。
