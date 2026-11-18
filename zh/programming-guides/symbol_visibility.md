+++
title = "符号可见性"
weight = 85
linkTitle = "符号可见性"
description = "解释版次 2024 中引入的可见性机制的术语与功能。"
type = "docs"
source_url = "https://protobuf.dev/programming-guides/symbol-visibility/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

本文介绍 proto `edition = "2024"` 中引入的符号可见性（symbol visibility）系统的术语与功能。

## TL;DR {#tldr}

> **范围说明：** 符号可见性**仅**控制 Protobuf 编译器（`protoc`）在解析 `.proto` 文件之间的引用时的导入行为。它对特定语言的生成代码（generated code）以及 proto 描述符（descriptor）的使用方**没有任何影响**。

在版次 2024 及更高版次中，请在 `message` 和 `enum` 上使用显式的 `export` 关键字，使其可在文件之外使用。大多数文件应使用 `features.default_symbol_visibility = STRICT`；为支持既有的嵌套导出（nested export），可以例外地使用 `LOCAL_ALL`。

在版次 2024 及更高版次中，应避免使用 `default_symbol_visibility = EXPORT_ALL`；它只是为了兼容之前的 proto 版次而存在。

正确用法示例：

```proto
edition = "2024";

option features.default_symbol_visibility = STRICT;

export message PublicMessage {
  // 在 STRICT 模式下，嵌套符号不能使用 `export`，并且会被强制为 `local`。
  enum NestedEnum {
    UNKNOWN_VALUE = 0;
  }

  NestedEnum type = 1;
}

export enum ExportedEnum {
  EXP_VALUE = 0;
}

// 在 STRICT 模式下默认为 `local`
message InternalHelperMessage {
  string name = 1;
}
```

## 术语表 {#glossary}

*   **符号（Symbol）**：`message`、`enum`、`service` 或 `extend <type>` 中的任意一种，即 `.proto` 文件中允许出现的**顶层**类型。
*   **顶层（Top-Level）**：定义在 `.proto` 文件根部的**符号**。包括所有 `service` 定义，以及任何未嵌套在 `message` 中的 `message`、`enum` 或 `extend` 块。
*   **可见性（Visibility）**：**符号**的一种属性，控制该符号能否被导入另一个 `.proto` 文件。既可显式设置，也可由文件默认值推导得出。
*   **入口点（Entry-Point）**：`.proto` 文件中的一个**符号**，充当该文件中**符号**局部子图（sub-graph）的根；生成代码或其他 `.proto` 文件正是经由它“进入”该文件。
*   **符号浪费（Symbol Waste）**：对于给定的**符号** 'X'，造成浪费的**符号**集合是指：从 'X' 不可达、但定义在那些文件中的**符号**——这些文件是为了满足对 'X' 所在文件的处理而被传递导入的。

## 简介 {#introduction}

版次 2024 及更高版次中的可见性为作者提供了一种手段，可以在 `message` 和 `enum` 声明上使用访问修饰符（access modifier）。符号的可见性控制着能否通过 `import` 从另一个 `.proto` 文件引用该符号。当某个符号在其所在文件之外不可见时，从另一个 `.proto` 文件对它的引用将会失败并产生编译器错误。

这一特性允许作者控制外部使用者对其符号的访问，并鼓励使用更小的文件——当只需要用到所定义符号的一部分时，这可能减小代码占用规模。

可见性适用于通过以下方式引用的任何 `message` 或 `enum`：

*   `message` 和 `extend` 字段定义。
*   `extend <symbol>`
*   `service` 方法的请求与响应类型。

符号可见性**仅**作用于 proto 语言，控制 proto 编译器能否通过 `import` 从另一个 proto 文件引用该符号。可见性对特定语言的生成代码**没有影响**，对 proto 描述符的使用方以及运行时反射（reflection）也**没有影响**。

## 详细用法 {#syntax}

可见性引入了一组新的文件级选项，以及两个新的 Protobuf 关键字——`local` 和 `export`，它们可以作为前缀加在 `message` 和 `enum` 类型上。

```proto
local message MyLocal {...}

export enum MyExported {...}
```

每个 `.proto` 文件还有一个默认可见性，由该版次的默认值或文件级的 `option features.default_symbol_visibility` 控制。这一可见性会影响文件中的所有 `message` 和 `enum` 定义。

**可用取值：**

*   `EXPORT_ALL`：这是版次 2024 之前的默认值。所有消息和枚举默认导出。在版次 2024 及更高版次中不应使用该取值，它只是为了兼容之前的 proto 版次而存在。

*   `EXPORT_TOP_LEVEL`：这是版次 2024 的默认值。所有顶层符号默认为 `export`；嵌套符号默认为 `local`。
*   `LOCAL_ALL`：所有符号默认为 `local`。
*   `STRICT`：这是版次 2026 及更高版次的默认值。所有符号默认为 `local`，可见性关键字仅在顶层 `message` 和 `enum` 类型上有效。嵌套类型（nested type）不能再使用这些关键字，并且总是被视为 `local`，[但 C++ 中的某些情形除外](#strict)。

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | ------------------
2026           | `STRICT`
2024           | `EXPORT_TOP_LEVEL`
2023           | `EXPORT_ALL`
proto3         | `EXPORT_ALL`
proto2         | `EXPORT_ALL`

任何顶层 `message` 和 `enum` 定义都可以标注显式的 `local` 或 `export` 关键字，以表明其预期用途。嵌套在 `message` 中的符号也可能允许使用这些关键字。

示例：

```proto
// foo.proto
edition = "2024";

// 在版次 2024 中，符号可见性默认为 EXPORT_TOP_LEVEL。设置
// default_symbol_visibility 将覆盖这一默认值。
option features.default_symbol_visibility = LOCAL_ALL;

// 将 default_symbol_visibility 设置为 LOCAL_ALL 会让所有符号默认为
// local。显式应用 export 关键字则会覆盖这一设置。
export message ExportedMessage {
  int32 baz = 1;
  // 在 LOCAL_ALL（以及版次 2024 的默认设置）下，嵌套符号同样默认为
  // local。如果没有显式的 export 关键字，此枚举将保持为 local。
  enum LocalNestedEnum {
    UNKNOWN_LOCAL_NESTED_ENUM_VALUE = 0;
  }
}

// bar.proto
edition = "2024";

import "foo.proto";

message ImportedMessage {
  // 下面这行是合法的，因为 ExportedMessage 显式覆盖了
  // foo.proto 中的 LOCAL_ALL 可见性设置。
  ExportedMessage bar = 1;

  // 下面这行不合法，因为 LocalNestedEnum 默认为 local，
  // 即使其父消息已被导出。
  // ExportedMessage.LocalNestedEnum qux = 2;
}
```

### STRICT default_symbol_visibility {#strict}

当 `default_symbol_visibility` 被设置为 `STRICT` 时（或在使用 Protobuf 版次 2026 及更高版次时，此时 `STRICT` 是默认值），文件将采用更严格的可见性规则。这种模式旨在成为一种更优但更具侵入性的可见性类型：嵌套类型不得在其自身文件之外使用。在 `STRICT` 模式下：

1.  所有符号默认为 `local`。
2.  `local` 和 `export` 只能用于顶层 `message` 和 `enum` 声明。
3.  在嵌套符号上使用 `local` 和 `export` 关键字将导致语法错误。

针对嵌套可见性关键字，仅存在一处单独的例外：为解决 C++ 命名空间（namespace）污染问题而使用的特定包装（wrapper）`message` 类型。在这种情况下，当且仅当满足以下条件时，才支持 `export enum`：

1.  顶层 `message` 为 `local`
2.  所有字段均为 `reserved`，并通过 `reserved 1 to max;` 来阻止任何字段定义

示例：

```proto
local message MyNamespaceMessage {
  export enum Enum {
    MY_VAL = 1;
  }

  // 确保不会向该消息添加任何字段。
  reserved 1 to max;
}
```

## 可见性的目的 {#purpose}

可见性特性有两个目的。第一个目的是引入访问修饰符——这是许多流行编程语言共有的特性，用于传达并强制执行作者关于某个 API 用法的意图。可见性让 proto 拥有一组有限的、proto 特有的访问控制，使 proto 作者能够对其 API 中可复用的部分施加一些额外控制，并定义 API 的入口点。

第二个目的是鼓励把 `.proto` 文件的范围限定在一小组定义上，以减少处理不必要定义的需要。Protobuf 语言定义要求 `Descriptor` 类型数据捆绑在 `FileDescriptorSet` 和 `FileDescriptor` 层级。这意味着，每当处理某个 `.proto` 文件时，该文件中的所有定义，以及它通过导入形成的传递依赖（transitive dependencies），都会被无条件处理。对于庞大的定义集合而言，这可能成为大块无用定义的重要来源——这些定义既拖慢处理速度，又会生成大量无用的生成代码。对抗这类反模式（anti-pattern）的最佳方式，是让 `.proto` 文件保持狭窄的作用域，只包含同一文件中某个给定子图所需的符号。通过为 `message` 和 `enum` 类型添加可见性，我们可以枚举给定文件中的入口点集合，并确定可以在哪里把不相关的定义拆分到不同的文件中，从而提供细粒度的依赖。

## 入口点 {#entry-point}

`.proto` 文件的入口点，是指在为处理给定文件而处理的全部 proto 符号的完整传递闭包（transitive closure）中，充当某个子图起始点的任何符号。该子图表示定义该入口点符号所需的各类型的完整传递闭包，它是处理该入口点所在文件所需符号的一个子集。

入口点通常有 3 种类型。

### 简单类型入口点 {#simple-entry-point}

具有 `export` 可见性的 `message` 和 `enum` 类型都可以充当符号图（symbol graph）中的入口点。就 `enum` 而言，该子图是空集，这意味着相对于导入该枚举所需的符号图来说，与该 `export enum Type {}` 位于同一文件中的任何其他类型定义都可以被视为“浪费”。

对于 `message` 类型，该消息充当一个入口点：它涵盖该消息字段定义所需的各类型的完整传递闭包，以及该入口点所引用的任何子消息的字段定义的递归集合。

值得注意的是，对 `enum` 和 `message` 两者而言，同一文件中的任何 `service` 或 `extend` 定义都无法被引用，对于这些 `message` 和 `enum` 定义的使用者来说，它们可以被视为“浪费”。

当一个 `.proto` 文件包含多个没有共享依赖的 `local` 消息时，在被生成代码使用时它们都可能充当独立的入口点。Protobuf 编译器和静态分析系统无法确定这类文件的最优入口点布局。由于缺乏这一上下文，我们假定同一文件中的 `local` 消息对于预期的生成代码用例而言是最优的。

### 服务入口点 {#service-entry-point}

`service` 定义充当一个入口点，涵盖从该 `service` 传递引用的所有符号，其中包括所有 `rpc` 方法定义所涉及的 `message` 和 `enum` 类型的完整传递闭包。

服务定义无法从另一个 proto 以任何有意义的方式被引用。这意味着，当一个被导入的 `.proto` 文件包含 `service` 定义时，该定义及其方法类型的传递闭包都可以被视为浪费。即使所有 `method` 输入和输出类型都从导入方文件中被引用，情况也是如此。

### 扩展入口点 {#extend-entry-point}

`extend <symbol>` 是一种扩展（Extend）类型的入口点。与 `service` 类似，无法从 `message` 或 `enum` 中引用扩展（extension）字段。一个扩展需要同时 `import` 两类内容：`extend ExtendeeType` 中的被扩展方（Extendee）类型，以及 `ExtenderType my_ext = ...` 中的扩展方（Extender）类型；这要求同时依赖 `ExtendeeType` 和 `ExtenderType` 各自所需符号的完整传递闭包。对于与该 `extend` 位于同一文件中的其他入口点而言，`ExtendeeType` 的符号可以被视为浪费。

扩展的存在是为了把扩展方类型与被扩展方类型解耦；然而，当扩展与其他入口点定义在同一文件中时，这会造成依赖倒置（dependency inversion），迫使同一文件中的其他入口点依赖于被扩展方类型。

当被扩展方类型非常简单（不含导入或非基本类型）时，这种依赖倒置可能无害；但如果被扩展方拥有庞大的传递依赖集合，它也可能成为巨大浪费的来源。

在某些生成代码中，把扩展嵌套在 `message` 内部可以提供一个有用的命名空间。这可以借助可见性关键字、以下面两种方式之一安全地实现。示例：

```proto
import "expensive/extendee_type.proto";

// 你可以为你的扩展定义一个 local 消息。
local message ExtenderType {
  extend expensive.ExtendeeType {
    ExtenderType ext = 12345;
  }

  string one = 1;
  int two = 2;
}
```

另一种做法：如果你有一个符号，既想把它用作扩展字段，又想让同一类型在另一个消息中作为普通字段使用，那么该消息应当定义在它自己的文件中，而 `extend` 则应定义在它自己独立的文件中。你仍然可以为该扩展提供一个友好的命名空间——使用一个没有任何字段的 `local` 包装消息，这对 C++ 之类的语言尤其有用：

```proto
package my.pkg;

import "expensive/extendee_type.proto";
import "other/foo_type.proto";

// 专门用于把 other.FooType 绑定为 expensive.ExtendeeType 的扩展，
// 从而为 `ext` 提供一个有用的带命名空间的名称：
// `my.pkg.WrapperForFooMsg.ext`
local message WrapperForFooMsg {
  extend expensive.ExtendeeType {
    other.FooMsg ext = 45678;
  }

  // 保留（reserve）所有字段，以确保除了包装该扩展之外，
  // 不会有任何东西使用此消息。
  reserved 1 to max;
}

```

### 最佳实践：每个文件维护 1 个入口点

一般来说，为了避免 proto 符号浪费，应力求让 `.proto` 文件与入口点保持 1:1 的比例，这样可以确保不会为任何给定符号执行多余的 proto 编译器处理或代码生成。这一做法还可以进一步延伸到构建系统：确保每个构建步骤一次只处理一个 `.proto` 文件。在 Bazel 中，这对应于每条 `proto_library` 规则只包含一个 `.proto` 文件。
