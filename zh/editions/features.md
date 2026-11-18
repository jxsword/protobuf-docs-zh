+++
title = "版次特性设置"
weight = 43
description = "Protobuf 版次（Editions）的特性及其对 Protobuf 行为的影响。"
type = "docs"
source_url = "https://protobuf.dev/editions/features/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-18"
status = "translated"
translator = "agent"
+++

本主题概览已发布版次（edition）中包含的特性（feature）。后续版次的特性将陆续补充至本主题。我们会在[新闻栏目（News）](/news)中公布新版次。

在新的模式（schema）定义内容中配置特性设置之前，请确保你理解自己为什么要使用它们。请避免对特性[照搬教条（cargo-culting）](/best-practices/no-cargo-cults)。

## Prototiller {#prototiller}

Prototiller 是一个命令行工具，用于在语法版本与版次之间更新 proto 模式配置文件。该工具尚未发布，但在本主题中会被多处引用。

## 特性 {#features}

以下各节涵盖了版次中所有可通过特性进行配置的行为。[在版次 2023 中保留 proto2 或 proto3 行为](#preserving)展示了如何覆盖默认行为，使你的 proto 定义文件表现得如同 proto2 或 proto3 文件。有关版次与特性如何协同设定行为的更多信息，请参阅 [Protobuf 版次概览](/editions/overview)。

<span id="cascading"> 特性设置应用于不同的层级：</span>

**文件级：**这些设置应用于所有没有覆盖设置的元素（消息（message）、字段（field）、枚举（enum）等）。

**非嵌套：**消息、枚举和服务（service）可以覆盖文件级设置。它们适用于其内部所有未被覆盖的内容（消息字段、枚举值），但不适用于与之平行的其他消息和枚举。

**嵌套：**oneof、消息和枚举可以覆盖它们所嵌套于其中的消息的设置。

**最低层级：**字段、扩展（extension）、枚举值、扩展范围和方法是可以覆盖设置的最低层级。

以下每一节都有一个注释，说明该特性可以应用于哪个作用域（scope）。下面的示例展示了一个应用于各个作用域的模拟特性：

```proto
edition = "2024";

// File-level scope definition
option features.bar = BAZ;

enum Foo {
  // Enum (non-nested scope) definition
  option features.bar = QUX;

  A = 1;
  B = 2;
}

message Corge {
  // Message (non-nested scope) definition
  option features.bar = QUUX;

  message Garply {
    // Message (nested scope) definition
    option features.bar = WALDO;
    string id = 1;
  }

  // Field (lowest-level scope) definition
  Foo A = 1 [features.bar = GRAULT];
}
```

在此示例中，最低层级作用域的特性定义中的设置“`GRAULT`”覆盖了非嵌套作用域的“`QUUX`”设置。而在 Garply 消息内部，“`WALDO`”覆盖了“`QUUX`”。

### `features.default_symbol_visibility` {#symbol-vis}

该特性用于设置消息和枚举的默认可见性（visibility），决定它们在被其他 proto 导入时是否可用。使用该特性可以减少无效符号（dead symbol），从而生成更小的二进制文件。

> **作用域说明：**符号可见性**仅**控制 Protobuf 编译器（protoc）在解析 `.proto` 文件之间的引用时的导入行为，对特定语言的生成代码（generated code）或 proto 描述符（descriptor）的使用者**没有任何影响**。

除了为整个文件设置默认值之外，你还可以使用 `local` 和 `export` 关键字来设置字段级行为。详情请参阅 [`export` / `local` 关键字](/editions/overview#export-local)。

**可用值：**

*   `EXPORT_ALL`：这是版次 2024 之前的默认值。所有消息和枚举默认导出。在版次 2024 及之后请勿设置该值；它的存在只是为了与先前的 proto 版次保持兼容。
*   `EXPORT_TOP_LEVEL`：所有顶层符号默认导出；嵌套符号默认为本地。
*   `LOCAL_ALL`：所有符号默认为本地。
*   `STRICT`：所有符号默认为本地。嵌套类型（nested type）无法导出，唯一例外是 `message { enum {} reserved 1 to max; }` 这一特殊情况。

**适用作用域：**文件

**引入于：**版次 2024

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | ------------------
2026           | `STRICT`
2024           | `EXPORT_TOP_LEVEL`
2023           | `EXPORT_ALL`
proto3         | `EXPORT_ALL`
proto2         | `EXPORT_ALL`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

以下示例展示了如何将该特性应用于 proto 模式定义文件中的元素：

```proto
// foo.proto
edition = "2024";

// Symbol visibility defaults to EXPORT_TOP_LEVEL in Edition 2024. Setting
// default_symbol_visibility overrides this default.
option features.default_symbol_visibility = LOCAL_ALL;

// Setting default_symbol_visibility to LOCAL_ALL makes all symbols local by
// default. Applying the export keyword explicitly overrides this.
export message ExportedMessage {
  int32 baz = 1;
  // Nested symbols also default to local under LOCAL_ALL (and under Edition
  // 2024 defaults). Without an explicit export keyword, this enum remains local.
  enum LocalNestedEnum {
    UNKNOWN_LOCAL_NESTED_ENUM_VALUE = 0;
  }
}

// bar.proto
edition = "2024";

import "foo.proto";

message ImportedMessage {
  // The following is valid because ExportedMessage explicitly overrides
  // the LOCAL_ALL visibility setting in foo.proto.
  ExportedMessage bar = 1;

  // The following is not valid because LocalNestedEnum is local by default,
  // even though its parent message is exported.
  // ExportedMessage.LocalNestedEnum qux = 2;
}
```

### `features.enforce_naming_style` {#enforce_naming}

该特性于版次 2024 中引入，用于按照[样式指南](/programming-guides/style)中的定义强制执行严格的命名风格，以确保 proto 在默认情况下可往返（round-trippable）；同时提供一个可用于选择退出（opt-out）、改用旧式命名风格的特性值。

**可用值：**

*   `STYLE2026`：强制严格遵循 2026 样式指南的命名规则，以减少常见的字段命名冲突。
*   `STYLE2024`：强制严格遵循样式指南的命名规则。
*   `STYLE_LEGACY`：采用版次 2024 之前的样式指南强制级别。

**适用作用域：**文件、扩展范围、消息、字段、oneof、枚举、枚举值、服务、方法

**引入于：**版次 2024

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | --------------
2026           | `STYLE2026`
2024           | `STYLE2024`
2023           | `STYLE_LEGACY`
proto3         | `STYLE_LEGACY`
proto2         | `STYLE_LEGACY`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

以下代码示例展示了一个版次 2023 文件：

版次 2023 默认为 `STYLE_LEGACY`，因此不符合规范的字段名没有问题：

```proto
edition = "2023";

message Foo {
  // A non-conforming field name is not a problem
  int64 bar_1 = 1;
}
```

版次 2024 默认为 `STYLE2024`，因此需要覆盖设置才能保留不符合规范的字段名：

```proto
edition = "2024";

// To keep the non-conformant field name, override the STYLE2024 setting
option features.enforce_naming_style = STYLE_LEGACY;

message Foo {
  int64 bar_1 = 1;
}
```

以下代码示例展示了一个版次 2024 文件：

版次 2024 默认为 `STYLE2024`，因此不强制避免命名冲突：

```proto
edition = "2024";

// Field name collision avoidance is not enforced
message Bar {
  int64 x = 1;
  int64 has_x = 2;
}
```

版次 2026 默认为 `STYLE2026`，因此需要覆盖设置才能保留这些冲突的字段名：

```proto
edition = "2026";

option features.enforce_naming_style = STYLE2024;

// To keep the colliding field names, override the STYLE2026 setting
message Bar {
  int64 x = 1;
  int64 has_x = 2;
}
```

### `features.enforce_proto_limits` {#enforce_proto_limits}

该特性于版次 2026 中引入，用于在 Protobuf 编译器解析 `.proto` 文件时强制执行结构大小限制，以防止定义过大的消息和枚举。

**可用值：**

*   `PROTO_LIMITS2026`：强制执行最大上限检查：
    *   每个消息最多 1500 个字段
    *   每个消息最多 1000 个 oneof
    *   每个 oneof 最多 1200 个字段
    *   每个枚举最多 1700 个值
*   `LEGACY_NO_EXPLICIT_LIMITS`：选择退出上限检查。

**适用作用域：**消息、oneof、枚举

**引入于：**版次 2026

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | ---------------------------
2026           | `PROTO_LIMITS2026`
2024           | `LEGACY_NO_EXPLICIT_LIMITS`
2023           | `LEGACY_NO_EXPLICIT_LIMITS`
proto3         | `LEGACY_NO_EXPLICIT_LIMITS`
proto2         | `LEGACY_NO_EXPLICIT_LIMITS`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

以下代码示例展示了一个版次 2024 文件：

版次 2024 默认为 `LEGACY_NO_EXPLICIT_LIMITS`，因此包含 1501 个字段的消息没有问题：

```proto
edition = "2024";

message Foo {
  // A message with more than 1500 fields
  int64 one = 1;
  int64 two = 2;
  int64 three = 3;
  # ...
  int64 one_thousand_five_hundred = 1500;
  int64 one_thousand_five_hundred_and_one = 1501;
}
```

版次 2026 默认为 `PROTO_LIMITS2026`，因此需要覆盖设置才能保留超大消息：

```proto
edition = "2026";

message Foo {
  // Must be set at the level of the oversized message, enum, or oneof as this
  // feature is not allowed at the file level.
  option features.enforce_proto_limits = PROTO_LIMITS2026;

  int64 one = 1;
  int64 two = 2;
  int64 three = 3;
  # ...
  int64 one_thousand_five_hundred = 1500;
  int64 one_thousand_five_hundred_and_one = 1501;
}
```

### `features.enum_type` {#enum_type}

该特性设定如何处理不在已定义集合之内的枚举值。有关开放枚举与封闭枚举的更多信息，请参阅[枚举行为](/programming-guides/enum)。

该特性不影响 proto3 文件，因此本节没有 proto3 文件的前后对比。

**可用值：**

*   `CLOSED:` 封闭枚举将超出范围的枚举值存储到未知字段（unknown field）集中。
*   `OPEN:` 开放枚举将超出范围的值直接解析到其字段中。

**适用作用域：**文件、枚举

**引入于：**版次 2023

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | --------
2026           | `OPEN`
2024           | `OPEN`
2023           | `OPEN`
proto3         | `OPEN`
proto2         | `CLOSED`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

以下代码示例展示了一个 proto2 文件：

```proto
syntax = "proto2";

enum Foo {
  A = 2;
  B = 4;
  C = 6;
}
```

运行 [Prototiller](#prototiller) 之后，等价的代码可能如下所示：

```proto
edition = "2024";

enum Foo {
  // Setting the enum_type feature overrides the default OPEN enum
  option features.enum_type = CLOSED;
  A = 2;
  B = 4;
  C = 6;
}
```

### `features.field_presence` {#field_presence}

该特性设定追踪字段存在性（field presence）的行为，即 Protobuf 字段是否有值这一概念。

**可用值：**

*   `LEGACY_REQUIRED`：字段在解析和序列化（serialization）时是必需的。任何显式设置的值都会被序列化到线路上（即使它与默认值相同）。
*   `EXPLICIT`：字段具有显式存在性（explicit presence）追踪。任何显式设置的值都会被序列化到线路上（即使它与默认值相同）。对于单数原始类型字段，设置为 `EXPLICIT` 的字段会生成 `has_*` 函数。
*   `IMPLICIT`：字段没有存在性追踪。默认值不会被序列化到线路上（即使它是显式设置的）。设置为 `IMPLICIT` 的字段不会生成 `has_*` 函数。

**适用作用域：**文件、字段

**引入于：**版次 2023

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | -----------
2026           | `EXPLICIT`
2024           | `EXPLICIT`
2023           | `EXPLICIT`
proto3         | `IMPLICIT`*
proto2         | `EXPLICIT`

\* proto3 为 `IMPLICIT`，除非字段带有 `optional` 标签（label），此时其行为如同 `EXPLICIT`。更多信息请参阅 [proto3 API 中的存在性](/programming-guides/field_presence#presence-proto3)。

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

以下代码示例展示了一个 proto2 文件：

```proto
syntax = "proto2";

message Foo {
  required int32 x = 1;
  optional int32 y = 2;
  repeated int32 z = 3;
}
```

运行 Prototiller 之后，等价的代码可能如下所示：

```proto
edition = "2024";

message Foo {
  // Setting the field_presence feature retains the proto2 required behavior
  int32 x = 1 [features.field_presence = LEGACY_REQUIRED];
  int32 y = 2;
  repeated int32 z = 3;
}
```

以下展示了一个 proto3 文件：

```proto
syntax = "proto3";

message Bar {
  int32 x = 1;
  optional int32 y = 2;
  repeated int32 z = 3;
}
```

运行 Prototiller 之后，等价的代码可能如下所示：

```proto
edition = "2024";
// Setting the file-level field_presence feature matches the proto3 implicit default
option features.field_presence = IMPLICIT;

message Bar {
  int32 x = 1;
  // Setting the field_presence here retains the explicit state that the proto3
  // field has because of the optional syntax
  int32 y = 2 [features.field_presence = EXPLICIT];
  repeated int32 z = 3;
}
```

请注意，`required` 和 `optional` 标签在版次中已不复存在，因为对应的行为已改为通过 `field_presence` 特性显式设置。

### `features.json_format` {#json_format}

该特性设定 JSON 解析与序列化的行为。

该特性不影响 proto3 文件，因此本节没有 proto3 文件的前后对比。版次的行为与 proto3 的行为一致。

**可用值：**

*   `ALLOW`：运行时（runtime）必须允许 JSON 解析与序列化。系统会在 proto 层面进行检查，确保存在定义完善的 JSON 映射（JSON mapping）。
*   `LEGACY_BEST_EFFORT`：运行时尽力解析和序列化 JSON。允许某些可能导致运行时行为未定义的 proto 存在（例如多对一或一对多映射）。

**适用作用域：**文件、消息、枚举

**引入于：**版次 2023

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | --------------------
2026           | `ALLOW`
2024           | `ALLOW`
2023           | `ALLOW`
proto3         | `ALLOW`
proto2         | `LEGACY_BEST_EFFORT`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

以下代码示例展示了一个 proto2 文件：

```proto
syntax = "proto2";

message Foo {
  // Warning only
  string bar = 1;
  string bar_ = 2;
}
```

运行 Prototiller 之后，等价的代码可能如下所示：

```proto
edition = "2024";
option features.json_format = LEGACY_BEST_EFFORT;

message Foo {
  string bar = 1;
  string bar_ = 2;
}
```

### `features.message_encoding` {#message_encoding}

该特性设定序列化时字段的编码行为。

该特性不影响 proto3 文件，因此本节没有 proto3 文件的前后对比。

取决于具体语言，"类组"字段在生成代码和文本格式（text format）中可能出现一些意想不到的大小写形式，这是为了与 proto2 保持向后兼容（backward compatibility）。当消息字段满足以下全部条件时，即为"类组"字段：

*   指定了 `DELIMITED` 消息编码
*   消息类型定义在与字段相同的作用域中
*   字段名恰好是类型名的小写形式

**可用值：**

*   `LENGTH_PREFIXED`：字段使用[消息结构](/programming-guides/encoding#structure)中描述的 LEN 线路类型进行编码。
*   `DELIMITED`：消息类型的字段按[组（group）](/programming-guides/proto2#groups)的方式编码。

**适用作用域：**文件、字段

**引入于：**版次 2023

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | -----------------
2026           | `LENGTH_PREFIXED`
2024           | `LENGTH_PREFIXED`
2023           | `LENGTH_PREFIXED`
proto3         | `LENGTH_PREFIXED`
proto2         | `LENGTH_PREFIXED`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

以下代码示例展示了一个 proto2 文件：

```proto
syntax = "proto2";

message Foo {
  group Bar = 1 {
    optional int32 x = 1;
    repeated int32 y = 2;
  }
}
```

运行 Prototiller 之后，等价的代码可能如下所示：

```proto
edition = "2024";

message Foo {
  message Bar {
    int32 x = 1;
    repeated int32 y = 2;
  }
  Bar bar = 1 [features.message_encoding = DELIMITED];
}
```

### `features.repeated_field_encoding` {#repeated_field_encoding}

proto2/proto3 中用于 `repeated` 字段的 [`packed` 选项](/programming-guides/encoding#packed)在版次中已迁移为该特性。

**可用值：**

*   `PACKED`：原始类型的 `Repeated` 字段编码为单条 LEN 记录，其中所有元素串联在一起。
*   `EXPANDED`：`Repeated` 字段中的每个值都使用字段编号（field number）单独编码。

**适用作用域：**文件、字段

**引入于：**版次 2023

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | ----------
2026           | `PACKED`
2024           | `PACKED`
2023           | `PACKED`
proto3         | `PACKED`
proto2         | `EXPANDED`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

以下代码示例展示了一个 proto2 文件：

```proto
syntax = "proto2";

message Foo {
  repeated int32 bar = 6 [packed=true];
  repeated int32 baz = 7;
}
```

运行 Prototiller 之后，等价的代码可能如下所示：

```proto
edition = "2024";
option features.repeated_field_encoding = EXPANDED;

message Foo {
  repeated int32 bar = 6 [features.repeated_field_encoding=PACKED];
  repeated int32 baz = 7;
}
```

以下展示了一个 proto3 文件：

```proto
syntax = "proto3";

message Foo {
  repeated int32 bar = 6;
  repeated int32 baz = 7 [packed=false];
}
```

运行 Prototiller 之后，等价的代码可能如下所示：

```proto
edition = "2024";

message Foo {
  repeated int32 bar = 6;
  repeated int32 baz = 7 [features.repeated_field_encoding=EXPANDED];
}
```

### `features.utf8_validation` {#utf8_validation}

该特性设定字符串的校验方式。它适用于所有语言，除非存在覆盖它的语言专属 `utf8_validation` 特性。Java 语言专属特性请参阅 [`features.(pb.java).utf8_validation`](#java-utf8_validation)。

**重要提示：**在 Java 中，`map<string, ...>` 字段始终会进行 UTF-8 校验，即使配置了 `utf8_validation = NONE`。由于 Java 的键将表示为 `java.lang.String` 对象，禁用校验将迫使运行时使用替换字符对无效字节序列进行*有损*转换。这种有损转换可能导致意外行为，例如键冲突。作为一种保持线路兼容的变通方案，请考虑改用带自定义"映射条目"消息的 `repeated` 字段。

该特性不影响 proto3 文件，因此本节没有 proto3 文件的前后对比。

**可用值：**

*   `VERIFY`：运行时应校验 UTF-8。这是 proto3 的默认行为。
*   `NONE`：该字段在线路上表现为未经校验的 `bytes` 字段。解析器可能以不可预测的方式处理这类字段，例如替换无效字符。这是 proto2 的默认行为。

**适用作用域：**文件、字段

**引入于：**版次 2023

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | --------
2026           | `VERIFY`
2024           | `VERIFY`
2023           | `VERIFY`
proto3         | `VERIFY`
proto2         | `NONE`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

以下代码示例展示了一个 proto2 文件：

```proto
syntax = "proto2";

message MyMessage {
  string foo = 1;
}
```

运行 Prototiller 之后，等价的代码可能如下所示：

```proto
edition = "2024";

message MyMessage {
  string foo = 1 [features.utf8_validation = NONE];
}
```

## 语言专属特性 {#lang-specific}

有些特性仅适用于特定语言，而不适用于其他语言中的相同 proto。使用这些特性需要从相应语言的运行时导入对应的 *_features.proto 文件。以下各节中的示例展示了这些导入。

### `features.(pb.go).api_level` {#go-api_level}

**适用语言：**Go

`api_level` 特性让你可以选择 Go Protobuf 插件（plugin）应为哪个 API 版本生成代码。Opaque API 是 Go 编程语言的 Protobuf 实现的最新版本；先前的版本现在称为 Open Struct API。简介请参阅博文 [Go Protobuf: Releasing the Opaque API](https://go.dev/blog/protobuf-opaque)。

**可用值：**

*   `API_OPEN`：Open Struct API 生成允许直接访问的 struct 类型。
*   `API_HYBRID`：Hybrid 是介于 Open 与 Opaque 之间的一档：Hybrid API 同样包含访问器（accessor）方法（因此你可以更新自己的代码），但仍像以前一样导出 struct 字段。两者没有性能差异；这一 API 级别仅用于辅助迁移。
*   `API_OPAQUE`：在 Opaque API 下，struct 字段被隐藏，无法再直接访问，取而代之的是通过新的访问器方法来读取、设置或清除字段。

**适用作用域：**消息、文件

**引入于：**版次 2023

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | ------------
2026           | `API_OPAQUE`
2024           | `API_OPAQUE`
2023           | `API_OPEN`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

从版次 2023 开始即可设置 `api_level` 特性：

```proto
edition = "2023";

import option "google/protobuf/go_features.proto";

// Remove this line after migrating the code to the Opaque API.
option features.(pb.go).api_level = API_HYBRID;
```

注意：`import option` 特性的加入是为了尽量减少这些新增导入对运行时反射（reflection）行为或其他描述符处理的影响。如果你导入另一个 `.proto` 文件只是为了在选项中使用它，请始终使用 `import option`。

另请参阅：
[Opaque API：迁移](/reference/go/opaque-migration)

### `features.(pb.cpp).enum_name_uses_string_view` {#enum-name-string-view}

**适用语言：**C++

在版次 2024 之前，所有生成的枚举类型都提供以下函数，用于从枚举值获取其名称，而在运行时构造 `std::string` 实例会带来一定开销：

```cpp
const std::string& Foo_Name(int);
```

版次 2024 中的默认特性值将此签名改为返回 `absl::string_view`，以实现更好的存储解耦，并可能节省内存/CPU 开销。如果你尚未准备好迁移，可以覆盖该设置，将其恢复为先前的行为。有关此主题的更多信息，请参阅迁移指南中的 [string_view 返回类型](/support/migration#string_view-return-type)。

**可用值：**

*   `true`：枚举对其值使用 `string_view`。
*   `false`：枚举对其值使用 `std::string`。

**适用作用域：**文件、枚举

**引入于：**版次 2024

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | -------
2026           | `true`
2024           | `true`
2023           | `false`
proto3         | `false`
proto2         | `false`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

### `features.(pb.cpp).repeated_type` {#cpp-repeated_type}

**适用语言：**C++

设置为 `PROXY` 时，repeated 字段访问器返回代理类型（`RepeatedFieldProxy`），而不是指向 `RepeatedField` 或 `RepeatedPtrField` 的指针或引用。代理能够以更高效的内存表示形式存放消息中的 repeated 字段。

导入该特性需要 `import option "google/protobuf/cpp_features.proto";`

**可用值：**

*   `PROXY`：访问器返回代理类型。
*   `LEGACY`：访问器返回传统的 `RepeatedField` 或 `RepeatedPtrField` 指针/引用。

**适用作用域：**文件、字段

**引入于：**版次 2026

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | --------
2026           | `LEGACY`
2024           | `LEGACY`
2023           | `LEGACY`
proto3         | `LEGACY`
proto2         | `LEGACY`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

### `features.(pb.java).large_enum` {#java-large_enum}

**适用语言：**Java

启用后，Java 代码生成器（code generator）会生成一个不继承 `java.lang.Enum` 的"类枚举"类，这样包含大量值的枚举就不会触及 Java 编译器和类文件（classfile）的限制。

生成的类会实现 `ProtocolMessageEnum`（对于 lite 运行时则实现 `Internal.EnumLite`）。请注意，该特性复刻了类枚举行为，但存在一些显著差异：不支持对枚举类型使用 Java `switch` 语句，也不支持 `EnumSet`/`EnumMap`，并且该枚举必须是[开放枚举](#enum_type)（不允许设置 `features.enum_type = CLOSED`）。

**可用值：**

*   `true`：生成"类枚举"式的 final 类，而不是 `java.lang.Enum`。
*   `false`：生成标准的 Java `enum`。

**适用作用域：**文件、枚举

**引入于：**版次 2024

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | -------
2026           | `false`
2024           | `false`
2023           | `false`
proto3         | `false`
proto2         | `false`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

要在枚举定义上启用 `large_enum`：

```proto
edition = "2024";

import option "google/protobuf/java_features.proto";

enum MyLargeEnum {
  option features.(pb.java).large_enum = true;

  MY_LARGE_ENUM_UNSPECIFIED = 0;
  // ...
}
```

在版次 2026 及之后的版次中，值超过 1,700 的枚举还必须在该枚举上设置 `option features.enforce_proto_limits = LEGACY_NO_EXPLICIT_LIMITS;`（参见 [`features.enforce_proto_limits`](#enforce_proto_limits)）。过大的枚举在其他编程语言中也可能引发问题，但 Java 的底层语言限制最低，这正是 `enforce_proto_limits` 将枚举限制为 1,700 个值的原因。

### `features.(pb.cpp/pb.java).legacy_closed_enum` {#legacy_closed_enum}

**适用语言：**C++、Java

该特性决定带有开放枚举类型的字段是否应表现得如同封闭枚举。这使版次能够复现 proto2 和 proto3 在 Java 和 C++ 中的[不符合规范的行为](/programming-guides/enum)。

该特性不影响 proto3 文件，因此本节没有 proto3 文件的前后对比。

**可用值：**

*   `true`：无论 [`enum_type`](#enum_type) 如何设置，都将枚举视为封闭枚举。
*   `false`：遵循 `enum_type` 中设置的值。

**适用作用域：**文件、字段

**引入于：**版次 2023

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | -------
2026           | `false`
2024           | `false`
2023           | `false`
proto3         | `false`
proto2         | `true`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

以下代码示例展示了一个 proto2 文件：

```proto
syntax = "proto2";

import "myproject/proto3file.proto";

message Msg {
  myproject.proto3file.Proto3Enum name = 1;
}
```

运行 Prototiller 之后，等价的代码可能如下所示：

```proto
edition = "2024";

import "myproject/proto3file.proto";

import option "google/protobuf/cpp_features.proto";
import option "google/protobuf/java_features.proto";

message Msg {
  myproject.proto3file.Proto3Enum name = 1 [
    features.(pb.cpp).legacy_closed_enum = true,
    features.(pb.java).legacy_closed_enum = true
  ];
}
```

### `features.(pb.java).nest_in_file_class` {#java-nest_in_file}

**适用语言：**Java

该特性控制 Java 生成器是否将生成的类嵌套在 Java 生成文件类中。将该选项设置为 `NO` 等价于在 proto2/proto3/版次 2023 中设置 `java_multiple_files = true`。

默认的外层类名也会更新为默认始终采用 .proto 文件名的驼峰形式并加 Proto 后缀（例如，`foo/bar_baz.proto` 变为 `BarBazProto`）。你仍然可以使用 `java_outer_classname` 文件选项覆盖它，以取代版次 2024 之前视冲突情况而定的默认值 `BarBaz` 或 `BarBazOuterClass`。

**可用值：**

*   `NO`：不将生成的类嵌套在文件类中。
*   `YES`：将生成的类嵌套在文件类中。
*   Legacy：嵌套行为由 `java_multiple_files` 选项控制（参见 go/java-proto-names#immutable-api-message-names）。

**适用作用域：**消息、枚举、服务

**引入于：**版次 2024

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | -------
2026           | `NO`
2024           | `NO`
2023           | Legacy
proto3         | Legacy
proto2         | Legacy

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

### `features.(pb.cpp).string_type` {#string_type}

**适用语言：**C++

该特性决定生成代码应如何处理字符串字段。它取代了 proto2 和 proto3 中的 `ctype` 选项，并提供新的 `string_type` 特性。在版次 2023 中，你可以在字段上指定 `ctype` 或 `string_type` 之一，但不能同时指定两者。在版次 2024 中，`ctype` 选项已被移除。

**可用值：**

*   `VIEW`：为该字段生成 `string_view` 访问器。
*   `CORD`：为该字段生成 `Cord` 访问器。扩展字段不支持。
*   `STRING`：为该字段生成 `string` 访问器。

**适用作用域：**文件、字段

**引入于：**版次 2023

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | --------
2026           | `VIEW`
2024           | `VIEW`
2023           | `STRING`
proto3         | `STRING`
proto2         | `STRING`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

以下代码示例展示了一个 proto2 文件：

```proto
syntax = "proto2";

message Foo {
  optional string bar = 6;
  optional string baz = 7 [ctype = CORD];
}
```

运行 Prototiller 之后，等价的代码可能如下所示：

```proto
edition = "2024";

import option "google/protobuf/cpp_features.proto";

message Foo {
  string bar = 6 [features.(pb.cpp).string_type = STRING];
  string baz = 7 [features.(pb.cpp).string_type = CORD];
}
```

以下展示了一个 proto3 文件：

```proto
syntax = "proto3"

message Foo {
  string bar = 6;
  string baz = 7 [ctype = CORD];
}
```

运行 Prototiller 之后，等价的代码可能如下所示：

```proto
edition = "2024";

import option "google/protobuf/cpp_features.proto";

message Foo {
  string bar = 6 [features.(pb.cpp).string_type = STRING];
  string baz = 7 [features.(pb.cpp).string_type = CORD];
}
```

### `features.(pb.java).utf8_validation` {#java-utf8_validation}

**适用语言：**Java

该语言专属特性让你可以仅在 Java 中于字段层级覆盖文件级设置。

该特性不影响 proto3 文件，因此本节没有 proto3 文件的前后对比。

**可用值：**

*   `DEFAULT`：行为与 [`features.utf8_validation`](#utf8_validation) 所设定的行为一致。
*   `VERIFY`：覆盖文件级 `features.utf8_validation` 设置，仅在 Java 中强制为 `VERIFY`。

**适用作用域：**文件、字段

**引入于：**版次 2023

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | ---------
2026           | `DEFAULT`
2024           | `DEFAULT`
2023           | `DEFAULT`
proto3         | `DEFAULT`
proto2         | `DEFAULT`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

以下代码示例展示了一个 proto2 文件：

```proto
syntax = "proto2";

option java_string_check_utf8=true;

message MyMessage {
  string foo = 1;
  string bar = 2;
}
```

运行 Prototiller 之后，等价的代码可能如下所示：

```proto
edition = "2024";

import "google/protobuf/java_features.proto";

option features.utf8_validation = NONE;
option features.(pb.java).utf8_validation = VERIFY;
message MyMessage {
  string foo = 1;
  string bar = 2;
}
```

### `features.(pb.go).strip_enum_prefix` {#go-strip_enum_prefix}

**适用语言：**Go

枚举值不受其所属枚举名的作用域限定，因此[建议为每个值加上枚举名前缀](/programming-guides/style#enums)：

```proto
edition = "2024";

enum Strip {
  STRIP_ZERO = 0;
  STRIP_ONE = 1;
}
```

然而，生成的 Go 代码此时会包含两个前缀！

```go
type Strip int32

const (
    Strip_STRIP_ZERO Strip = 0
    Strip_STRIP_ONE  Strip = 1
)
```

语言专属的 `strip_enum_prefix` 特性决定 Go 代码生成器是否去除重复的前缀。

**可用值：**

*   `STRIP_ENUM_PREFIX_KEEP`：保留名称原样，即使重复。
*   `STRIP_ENUM_PREFIX_GENERATE_BOTH`：两种都生成，即完整名称和去除前缀后的名称（帮助迁移你的 Go 代码）。
*   `STRIP_ENUM_PREFIX_STRIP`：从枚举值名中去除枚举名前缀。

**适用作用域：**文件、枚举、枚举值

**引入于：**版次 2024

**各语法/版次的默认行为：**

语法/版次 | 默认值
-------------- | ------------------------
2026           | `STRIP_ENUM_PREFIX_KEEP`
2024           | `STRIP_ENUM_PREFIX_KEEP`

**注意：**对不同模式元素设置的特性[具有不同的作用域](#cascading)。

你可以在版次 2024（或更新）的 .proto 文件中设置 `strip_enum_prefix` 特性：

```proto
edition = "2024";

import option "google/protobuf/go_features.proto";

option features.(pb.go).strip_enum_prefix = STRIP_ENUM_PREFIX_STRIP;

enum Strip {
  STRIP_ZERO = 0;
  STRIP_ONE = 1;
}
```

生成的 Go 代码此时会去除 `STRIP` 前缀：

```go
type Strip int32

const (
    Strip_ZERO Strip = 0
    Strip_ONE  Strip = 1
)
```

## 在版次 2023 中保留 proto2 或 proto3 行为 {#preserving}

你可能希望迁移到版次格式，但暂时不想处理生成代码行为方式的更新。本节展示 Prototiller 工具为你的 .proto 文件所做的更改，使基于版次 2023 的 proto 表现得如同 proto2 或 proto3 文件。

在文件级完成这些更改后，你将获得 proto2 或 proto3 的默认值。你可以在更低层级（消息级、字段级）进行覆盖，以顾及额外的行为差异（例如 [required 与 proto3 optional](#caveats)），或者当你只希望定义*大体*像 proto2 或 proto3 时也是如此。

除非你有特定的理由不使用，否则我们建议使用 Prototiller。如果不使用 Prototiller 而是手动应用所有这些设置，请将以下各节的内容添加到你的 .proto 文件顶部。

### proto2 行为 {#proto2-behavior}

以下展示用版次 2023 复刻 proto2 行为所需的设置。

```proto
edition = "2023";

import "google/protobuf/cpp_features.proto";
import "google/protobuf/java_features.proto";

option features.field_presence = EXPLICIT;
option features.enum_type = CLOSED;
option features.repeated_field_encoding = EXPANDED;
option features.json_format = LEGACY_BEST_EFFORT;
option features.utf8_validation = NONE;
option features.(pb.cpp).legacy_closed_enum = true;
option features.(pb.java).legacy_closed_enum = true;
```

### proto3 行为 {#proto3-behavior}

以下展示用版次 2023 复刻 proto3 行为所需的设置。

```proto
edition = "2023";

import "google/protobuf/cpp_features.proto";
import "google/protobuf/java_features.proto";

option features.field_presence = IMPLICIT;
option features.enum_type = OPEN;
// `packed=false` needs to be transformed to field-level repeated_field_encoding
// features in Editions syntax
option features.json_format = ALLOW;
option features.utf8_validation = VERIFY;
option features.(pb.cpp).legacy_closed_enum = false;
option features.(pb.java).legacy_closed_enum = false;
```

### 从版次 2023 到 2024 {#2023-2024}

以下展示用版次 2024 复刻版次 2023 行为所需的设置。

```proto
// foo/bar_baz.proto
edition = "2024";

import option "google/protobuf/cpp_features.proto";
import option "google/protobuf/java_features.proto";
import option "google/protobuf/go_features.proto";

// If previously relying on edition 2023 default java_outer_classname.
option java_outer_classname = "BarBaz" // or BarBazOuterClass

option features.(pb.cpp).string_type = STRING;
option features.enforce_naming_style = STYLE_LEGACY;
option features.default_symbol_visibility = EXPORT_ALL;
option features.(pb.cpp).enum_name_uses_string_view = false;
option features.(pb.go).api_level = API_OPEN;

message MyMessage {
  option features.(pb.java).nest_in_file_class = YES;
}
```

### 从版次 2024 到 2026 {#2024-2026}

以下展示用版次 2026 复刻版次 2024 行为所需的设置。

```proto
edition = "2026";

option features.enforce_naming_style = STYLE2024;
option features.default_symbol_visibility = EXPORT_TOP_LEVEL;
```

### 注意事项与例外情况 {#caveats}

本节展示如果你选择不使用 Prototiller，则需要手动进行的更改。

在大多数情况下，设置上一节所示的文件级默认值即可设定默认行为，但仍有一些例外。

**版次 2023 及之后的版次**

*   `optional`：移除所有 `optional` 标签实例；如果文件默认值为 `IMPLICIT`，则将 [`features.field_presence`](#field_presence) 改为 `EXPLICIT`。
*   `required`：移除所有 `required` 标签实例，并在字段级添加 [`features.field_presence=LEGACY_REQUIRED`](#field_presence) 选项。
*   `groups`：将 `groups` 展开为单独的消息，并在字段级添加 `features.message_encoding = DELIMITED` 选项。更多信息请参阅 [`features.message_encoding`](#message_encoding)。
*   `java_string_check_utf8`：移除该文件选项，改用 [`features.(pb.java).utf8_validation`](#java-utf8_validation)。你需要导入 Java 特性，如[语言专属特性](#lang-specific)一节所述。
*   `packed`：对于转换为版次格式的 proto2 文件，当你不想要[proto2 行为](#proto2-behavior)中设置的 `EXPANDED` 行为时，移除 `packed` 字段选项并在字段级添加 `[features.repeated_field_encoding=PACKED]`。对于转换为版次格式的 proto3 文件，当你不想要默认的 proto3 行为时，在字段级添加 `[features.repeated_field_encoding=EXPANDED]`。

**版次 2024 及之后的版次**

*   （C++）`ctype`：移除所有 `ctype` 选项实例，并设置 [`features.(pb.cpp).string_type`](#string_type) 的值。
*   （C++ 和 Go）`weak`：移除弱导入（weak import），改用 [`import option`](/editions/overview#import-option)。
*   （Java）`java_multiple_files`：移除 `java_multiple_files`，改用 [`features.(pb.java).nest_in_file_class`](#java-nest_in_file)。

**版次 2026 及之后的版次**

*   （C++）移除语言专属选项（`cc_api_version`、`cc_utf8_verification`、`cc_enable_arenas`）。
*   将 `features.enforce_proto_limits` 设置为 `LEGACY_NO_EXPLICIT_LIMITS`，适用于以下情况：
    1.  拥有超过 1500 个字段或超过 1000 个 oneof 的消息
    1.  拥有超过 1200 个字段的 oneof
    1.  拥有超过 1700 个值的枚举
