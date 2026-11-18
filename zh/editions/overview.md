+++
title = "Protobuf 版次概览"
linkTitle = "概览"
weight = 42
description = "Protobuf 版次（Editions）功能概览。"
type = "docs"
source_url = "https://protobuf.dev/editions/overview/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-18"
status = "translated"
translator = "agent"
+++

Protobuf 版次（Editions）取代了我们此前在 Protobuf 中使用的 proto2 和 proto3 称谓。你无需再在 proto 定义文件顶部添加 `syntax = "proto2"` 或 `syntax = "proto3"`，而是使用版次（edition）编号，例如 `edition = "2024"`，来指定你的文件将具有的默认行为。版次让这门语言能够随时间推移增量演进。

版次代表的不是旧版本那种硬编码的行为，而是一组[特性（feature）](/editions/features)的集合，每个特性都带有一个默认值（即行为）。特性是文件、消息（message）、字段（field）、枚举（enum）等之上的选项（option），用于指定 protoc、代码生成器（code generator）和 Protobuf 运行时（runtime）的行为。当你的需求与你所选版次的默认行为不匹配时，你可以在这些不同层级（文件、消息、字段……）上显式覆盖某个行为。你也可以再覆盖自己的覆盖设置。本主题稍后的[词法作用域（lexical scoping）一节](#scoping)对此有更详细的介绍。

**注意：**最新发布的版次是 2024。

## 特性的生命周期 {#lifecycles}

版次为特性的生命周期提供了基本的增量。特性有一个预期的生命周期：引入特性、更改其默认行为、弃用（deprecate）特性，然后再移除特性。例如：

1.  版次 2031 创建了 `feature.amazing_new_feature`，默认值为 `false`。该值保持与所有更早版次相同的行为。也就是说，它默认不产生任何影响。并非所有新特性都会默认采用无操作（no-op）选项，但就本例而言，`amazing_new_feature` 正是如此。

2.  开发者将他们的 .proto 文件更新为 `edition = "2031"`。

3.  之后的版次（例如版次 2033）将 `feature.amazing_new_feature` 的默认值从 `false` 切换为 `true`。这是所有 proto 都期望的行为，也正是 Protobuf 团队创建该特性的原因。

    使用 Prototiller 工具把更早版本的 proto 文件迁移到版次 2033 时，会根据需要添加显式的 `feature.amazing_new_feature = false` 条目，以继续保留先前的行为。当开发者希望新行为应用于自己的 .proto 文件时，即可移除这些新添加的设置。

<!-- mdformat off (preserve single lines/no wrapping) -->

4.  在某个时间点，`feature.amazing_new_feature` 会在某个版次中被标记为弃用，并在之后的版次中被移除。

    当特性被移除时，实现该行为的代码生成器和支持它的运行时库也可能随之移除。不过时间安排会相当宽裕。按照前面生命周期步骤中的示例，弃用可能发生在版次 2034，但直到大约两年后的版次 2036 才会真正移除。移除特性总是会触发主版本号提升。

<!-- mdformat on -->

你将拥有 Google 迁移的完整时间窗口，再加上弃用窗口，来升级你的代码。

前面的生命周期示例中的特性使用的是布尔值，但特性也可以使用枚举。例如，`features.field_presence` 的取值有 `LEGACY_REQUIRED`、`EXPLICIT` 和 `IMPLICIT.`

## 迁移到 Protobuf 版次 {#migrating}

版次不会破坏现有的二进制文件，也不会改变消息的二进制、文本或 JSON 序列化（serialization）格式。版次 2023 尽可能将干扰降到最低。它确立了基线，并将 proto2 和 proto3 定义合并为一种全新的单一定义格式。

随着更多版次发布，特性的默认行为可能会发生变化。你可以让 Prototiller 对你的 .proto 文件执行无操作转换，也可以选择接受部分或全部新行为。版次计划大约每年发布一次。

### 从 proto2 迁移到版次 {#proto2-migration}

本节展示一个 proto2 文件，以及运行 Prototiller 工具将定义文件改为使用 Protobuf 版次语法之后它可能的样子。

<section class="tabs">

#### proto2 语法 {.new-tab}

```proto
// proto2 file
syntax = "proto2";

package com.example;

message Player {
  // in proto2, optional fields have explicit presence
  optional string name = 1 [default = "N/A"];
  // proto2 still supports the problematic "required" field rule
  required int32 id = 2;
  // in proto2 this is not packed by default
  repeated int32 scores = 3;

  enum Handed {
    HANDED_UNSPECIFIED = 0;
    HANDED_LEFT = 1;
    HANDED_RIGHT = 2;
    HANDED_AMBIDEXTROUS = 3;
  }

  // in proto2 enums are closed
  optional Handed handed = 4;

  reserved "gender";
}
```

#### 版次语法 {.new-tab}

```proto
// Edition version of proto2 file
edition = "2024";

package com.example;

option features.utf8_validation = NONE;
option features.enforce_naming_style = STYLE_LEGACY;
// NOTE: You should generally avoid setting EXPORT_ALL; it is used here only to
// illustrate how options can be used to match previous proto2 defaults.
option features.default_symbol_visibility = EXPORT_ALL;

// Sets the default behavior for C++ strings
option features.(pb.cpp).string_type = STRING;

message Player {
  // fields have explicit presence, so no explicit setting needed
  string name = 1 [default = "N/A"];
  // to match the proto2 behavior, LEGACY_REQUIRED is set at the field level
  int32 id = 2 [features.field_presence = LEGACY_REQUIRED];
  // to match the proto2 behavior, EXPANDED is set at the field level
  repeated int32 scores = 3 [features.repeated_field_encoding = EXPANDED];

  export enum Handed {
    // this overrides the default editions behavior, which is OPEN
    option features.enum_type = CLOSED;
    HANDED_UNSPECIFIED = 0;
    HANDED_LEFT = 1;
    HANDED_RIGHT = 2;
    HANDED_AMBIDEXTROUS = 3;
  }

  Handed handed = 4;

  reserved gender;
}
```

</section>

### 从 proto3 迁移到版次 {#proto3-migration}

本节展示一个 proto3 文件，以及运行 Prototiller 工具将定义文件改为使用 Protobuf 版次语法之后它可能的样子。

<section class="tabs">

#### proto3 语法 {.new-tab}

```proto
// proto3 file
syntax = "proto3";

package com.example;

message Player {
  // in proto3, optional fields have explicit presence
  optional string name = 1;
  // in proto3 no specified field rule defaults to implicit presence
  int32 id = 2;
  // in proto3 this is packed by default
  repeated int32 scores = 3;

  enum Handed {
    HANDED_UNSPECIFIED = 0;
    HANDED_LEFT = 1;
    HANDED_RIGHT = 2;
    HANDED_AMBIDEXTROUS = 3;
  }

  // in proto3 enums are open
  optional Handed handed = 4;

  reserved "gender";
}
```

#### 版次语法 {.new-tab}

```proto
// Editions version of proto3 file
edition = "2024";

package com.example;

option features.utf8_validation = NONE;
option features.enforce_naming_style = STYLE_LEGACY;
// NOTE: Avoid setting EXPORT_ALL; it is used here only to
// illustrate how options can be used to match previous proto3 defaults.
option features.default_symbol_visibility = EXPORT_ALL;

// Sets the default behavior for C++ strings
option features.(pb.cpp).string_type = STRING;

message Player {
  // fields have explicit presence, so no explicit setting needed
  string name = 1 [default = "N/A"];
  // to match the proto3 behavior, IMPLICIT is set at the field level
  int32 id = 2 [features.field_presence = IMPLICIT];
  // PACKED is the default state, and is provided just for illustration
  repeated int32 scores = 3 [features.repeated_field_encoding = PACKED];

  export enum Handed {
    HANDED_UNSPECIFIED = 0;
    HANDED_LEFT = 1;
    HANDED_RIGHT = 2;
    HANDED_AMBIDEXTROUS = 3;
  }

  Handed handed = 4;

  reserved gender;
}
```

</section>

<a name="inheritance"></a>

### 词法作用域 {#scoping}

版次语法支持词法作用域，每个特性都有各自允许的目标层级列表。例如，在版次 2023 中，特性只能在文件层级或最细粒度层级上指定。词法作用域的实现让你可以为某个特性在整个文件范围内设置默认行为，然后再在消息、字段、枚举、枚举值、oneof、服务（service）或方法层级上覆盖该行为。较高层级（文件、消息）上所做的设置，会在同一作用域内没有其他设置（字段、枚举值）时生效。任何未显式设置的特性都将遵循该 .proto 文件所用版次中定义的行为。

下面的代码示例展示了在文件、字段和枚举层级上设置的部分特性。

```proto {highlight="lines:3,7,16"}
edition = "2024";

option features.enum_type = CLOSED;

message Person {
  string name = 1;
  int32 id = 2 [features.field_presence = IMPLICIT];

  enum Pay_Type {
    PAY_TYPE_UNSPECIFIED = 1;
    PAY_TYPE_SALARY = 2;
    PAY_TYPE_HOURLY = 3;
  }

  enum Employment {
    option features.enum_type = OPEN;
    EMPLOYMENT_UNSPECIFIED = 0;
    EMPLOYMENT_FULLTIME = 1;
    EMPLOYMENT_PARTTIME = 2;
  }
  Employment employment = 4;
}
```

在上面的示例中，存在性（presence）特性被设置为 `IMPLICIT`；如果不设置，它将默认为 `EXPLICIT`。`Pay_Type` 这个 `enum` 将是 `CLOSED`，因为它应用的是文件层级的设置。而 `Employment` 这个 `enum` 则是 `OPEN`，因为它是在枚举内部设置的。

### Prototiller {#prototiller}

在 Prototiller 工具发布时，我们将同时提供迁移指南和迁移工具，以简化向版次的迁移以及版次之间的迁移。该工具将让你能够：

*   大规模地将 proto2 和 proto3 定义文件转换为新的版次语法
*   将文件从一个版次迁移到另一个版次
*   以其他方式操作 proto 文件

### 向后兼容 {#compatibility}

我们构建 Protobuf 版次的目标是尽可能不造成干扰。例如，你可以将 proto2 和 proto3 定义导入（import）到基于版次的定义文件中，反之亦然：

```proto
// file myproject/foo.proto
syntax = "proto2";

enum Employment {
  EMPLOYMENT_UNSPECIFIED = 0;
  EMPLOYMENT_FULLTIME = 1;
  EMPLOYMENT_PARTTIME = 2;
}
```

```proto
// file myproject/edition.proto
edition = "2024";

import "myproject/foo.proto";
```

当你从 proto2 或 proto3 迁移到版次时，生成代码（generated code）会发生变化，但线路格式（wire format）不会。你仍然可以使用版次语法的 proto 定义来访问 proto2 和 proto3 数据文件或文件流。

### 语法变更 {#syntax}

与 proto2 和 proto3 相比，版次存在一些语法变更。

#### 语法描述 {#syntax-descrip}

你不再使用 `syntax` 元素，而是使用 `edition` 元素：

```proto
syntax = "proto2";
syntax = "proto3";
edition = "2028";
```

#### 保留名称 {#reserved-names}

保留（reserved）字段名和枚举值名时，不再需要用引号将它们括起来：

```proto
reserved foo, bar;
```

#### 组语法 {#group-syntax}

proto2 中可用的组（group）语法在版次中已被移除。组所使用的特殊线路格式仍可通过 `DELIMITED` 消息编码来使用。

#### required 标签 {#required-label}

仅在 proto2 中可用的 `required` 标签在版次中不再可用。其底层功能仍可通过使用 `features.field_presence=LEGACY_REQUIRED` 来实现。

#### `import option` {#import-option}

版次 2024 新增了对选项导入（option import）的支持，所用语法为 `import option`。

选项导入必须位于所有其他 `import` 语句之后。

与普通的 `import` 语句不同，`import option` 只导入 `.proto` 文件中定义的自定义选项，不导入其他符号。

这意味着消息和枚举会被排除在选项导入之外。在下面的示例中，`Bar` 消息不能在 `foo.proto` 中用作字段类型，但类型为 `Bar` 的选项仍可设置。

```proto
// bar.proto
edition = "2024";

import "google/protobuf/descriptor.proto";

message Bar {
  bool bar = 1;
}

extend proto2.FileOptions {
  bool file_opt1 = 5000;
  Bar file_opt2 = 5001;
}

// foo.proto:
edition = "2024";

import option "bar.proto";

option (file_opt1) = true;
option (file_opt2) = {bar: true};

message Foo {
  // Bar bar = 1; // This is not allowed
}
```

选项导入不需要为其符号生成代码，因此应当在 `proto_library` 中以 `option_deps`（而不是 `deps`）的形式提供。这样可以避免生成不可达的代码。

```proto
proto_library(
  name = "foo",
  srcs = ["foo.proto"],
  option_deps = [":custom_option_proto"]
)
```

在导入 Protobuf 语言特性和其他自定义选项时，强烈建议使用选项导入和 `option_deps`，以避免生成不必要的代码。

它取代了已在版次 2024 中被移除的 `import weak`。

#### `export` / `local` 关键字 {#export-local}

版次 2024 新增了 `export` 和 `local` 关键字，作为可导入符号的符号可见性修饰符，用于在 [`features.default_symbol_visibility`](/editions/features#symbol-vis) 所指定默认行为的基础上进行调整。

它控制哪些符号可以被其他 proto 文件导入，但不影响代码生成。

在版次 2024 中，这些关键字默认可设置在所有 `message` 和 `enum` 符号上。不过，`default_symbol_visibility` 特性的某些取值会进一步限制哪些符号可以导出。

示例：

```proto
// Top-level symbols are exported by default in Edition 2024
message LocalMessage {
  int32 baz = 1;
  // Nested symbols are local by default in Edition 2024; applying the `export`
  // keyword overrides this
  export enum ExportedNestedEnum {
    UNKNOWN_EXPORTED_NESTED_ENUM_VALUE = 0;
  }
}

// The `local` keyword overrides the default behavior of exporting messages
local message AnotherMessage {
  int32 foo = 1;
}
```

#### `import weak` 与弱字段选项 {#import-weak}

从版次 2024 开始，不再允许弱导入（weak import）。

如果你此前依赖 `import weak` 来声明"弱依赖"（weak dependency）&mdash;即在没有生成代码的情况下为 C++ 和 Go 导入自定义选项&mdash;那么你应改为迁移到 `import option`。

更多详情请参阅 [`import option`](/editions/overview#import-option)。

#### `ctype` 字段选项 {#ctype}

从版次 2024 开始，`ctype` 字段选项不再被允许。请改用 `string_type` 特性。

更多详情请参阅 [`features.(pb.cpp).string_type`](/editions/features#string_type)。

#### `java_multiple_files` 文件选项 {#java-mult-files}

从版次 2024 开始，`java_multiple_files` 文件选项不再可用。请改用 Java 特性 [`features.(pb.java).nest_in_file_class`](/editions/features#java-nest_in_file)。
