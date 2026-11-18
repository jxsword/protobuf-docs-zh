+++
title = "样式指南"
weight = 50
description = "为如何以最佳方式组织你的 proto 定义提供指导。"
type = "docs"
source_url = "https://protobuf.dev/programming-guides/style/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

本文为 `.proto` 文件提供一份样式指南（style guide）。遵循这些约定，可以让你的 Protobuf 消息（message）定义及其对应的类保持一致、易于阅读。

以下样式规则的强制执行由 [enforce_naming_style](/editions/features#enforce-naming) 控制。

## 标准文件格式 {#standard-file-formatting}

*   每行长度保持在 80 个字符以内。
*   使用 2 个空格的缩进。
*   字符串优先使用双引号。

## 文件结构 {#file-structure}

文件应命名为 `lower_snake_case.proto`。

所有文件都应按以下顺序组织：

1.  许可声明头（如适用）
1.  文件概览
1.  语法（syntax）或版次（edition）声明
1.  package 声明
1.  已排序的导入（import）
1.  文件选项
1.  其余所有内容

## 标识符命名风格 {#identifier}

Protobuf 标识符（identifier）使用以下命名风格之一：

1.  TitleCase
    *   包含大写字母、小写字母和数字
    *   首字符为大写字母
    *   每个单词的首字母大写
1.  lower_snake_case
    *   包含小写字母、下划线（underscore）和数字
    *   单词之间以单个下划线分隔
1.  UPPER_SNAKE_CASE
    *   包含大写字母、下划线和数字
    *   单词之间以单个下划线分隔
1.  camelCase
    *   包含大写字母、小写字母和数字
    *   首字符为小写字母
    *   后续每个单词的首字母大写
    *   **注意：** 下文的样式指南不会在 .proto 文件中对任何标识符使用 camelCase；此处澄清该术语，只是因为某些语言的生成代码（generated code）可能会将标识符转换成这种风格。

在所有情况下，都应把缩写词当作单个单词对待：使用 `GetDnsRequest` 而不是 `GetDNSRequest`，使用 `dns_request` 而不是 `d_n_s_request`。

#### 标识符中的下划线 {#underscores}

不要用下划线作为名称的首字符或末字符。任何下划线之后都应紧跟字母（而不是数字或另一个下划线）。

这条规则的动机在于：每种 Protobuf 语言的实现都可能把标识符转换为该语言的本地风格——.proto 文件中名为 `song_id` 的字段（field），其访问器（accessor）在不同语言中可能分别呈现为 `SongId`、`songId` 或 `song_id`。

只在字母之前使用下划线，就能避免以下情形：两个名称在一种风格下彼此不同，但转换为其他某种风格后却发生冲突。

例如，`DNS2` 和 `DNS_2` 都会被转换成 TitleCase 形式的 `Dns2`。如果允许这两种命名，当某个消息起初只在生成代码保留原始 UPPER_SNAKE_CASE 风格的部分语言中使用、并因此被广泛确立，之后才在另一种会把名称转换为 TitleCase 的语言中使用时，两者就会发生冲突，带来棘手的局面。

这条样式规则落实到实际，意味着应使用 `XYZ2` 或 `XYZ_V2`，而不是 `XYZ_2` 或 `XYZ_2V`。

## 包（package） {#packages}

package 名称应是由点号分隔的 lower_snake_case 名称序列，不应包含大写字母。

由多个单词组成的 package 名称可以使用 lower_snake_case，也可以使用 dot.delimited 形式（点号分隔的 package 名称在大多数语言中会生成嵌套的包/命名空间）。

package 名称应力求基于项目名取一个简短且唯一的名字。package 不应与目录路径耦合，尤其是当文件位于嵌套很深的路径中时。

即使文件位于 Java 或 Kotlin 目录中，package 名称也不应采用 Java 风格的命名。不要使用以下任何一种风格：

*   `com.company.x.y`
*   `com_company_x_y`
*   `java_com_company_x_y`

作为替代，应使用 `x.y` 作为 `package` 名称，并设置 `java_package = "com.company.x.y"`。

## 消息名称 {#message-names}

消息名称使用 TitleCase。

```proto
message SongRequest {
}
```

## 字段名称 {#field-names}

字段名称使用 snake_case，扩展（extension）名称也包括在内。

repeated 字段应使用复数形式的名称。

```proto
string song_name = 1;
repeated Song songs = 2;
```

## oneof 名称 {#oneof-names}

oneof 名称使用 lower_snake_case。

```proto
oneof song_id {
  string song_human_readable_id = 1;
  int64 song_machine_id = 2;
}
```

## 枚举 {#enums}

枚举（enum）类型名称使用 TitleCase。

枚举值名称使用 UPPER_SNAKE_CASE。

```proto
enum FooBar {
  FOO_BAR_UNSPECIFIED = 0;
  FOO_BAR_FIRST_VALUE = 1;
  FOO_BAR_SECOND_VALUE = 2;
}
```

列表中的第一个值应当是零值枚举，并带有 `_UNSPECIFIED` 或 `_UNKNOWN` 后缀。该值可以用作未知值/默认值（default value），并且应当与你预期会被显式设置的任何语义值都不相同。关于未指定枚举值的更多信息，请参阅 [Proto 最佳实践页面](/best-practices/dos-donts#unspecified-enum)。

为各个值分配的编号应紧凑且依次递增。只有当先前使用的枚举值被移除时，编号中才应出现空档。避免使用负值。

#### 枚举值前缀 {#enum-value-prefixing}

从语义上看，枚举值不被认为受其所属枚举名称的作用域约束，因此两个同级枚举中不允许出现相同的名称。例如，下面的代码会被 protoc 拒绝，因为这两个枚举中定义的 `SET` 值被视为处于同一作用域：

```proto {.bad}
enum CollectionType {
  COLLECTION_TYPE_UNSPECIFIED = 0;
  SET = 1;
  MAP = 2;
  ARRAY = 3;
}

// 无法编译——`SET` 这个枚举值名称会与
// `CollectionType` 枚举中定义的那个同名值冲突。
enum TennisVictoryType {
  TENNIS_VICTORY_TYPE_UNSPECIFIED = 0;
  GAME = 1;
  SET = 2;
  MATCH = 3;
}
```

当枚举定义在文件的顶层（而非嵌套在消息定义内部）时，命名冲突的风险很高；此时“同级”还包括在其他文件中声明了相同 package 的枚举，而 protoc 在代码生成时可能无法检测到已经发生的冲突。

未来的版次将增加对带作用域枚举的支持，届时将无需再为每个枚举值手动添加前缀，并且可以直接简写为 `TIER1 = 1`。

在此之前，为了避免这些风险，强烈建议遵循以下各节介绍的某一种做法。

##### 为每个值添加枚举名称前缀（转换为 UPPER_SNAKE_CASE） {#prefix-value}

在为枚举值添加前缀时，去掉前缀后剩下的名称部分仍应是一个合法且符合样式的枚举值名称。例如，应避免以下写法：

```
enum DeviceTier {
  DEVICE_TIER_UNKNOWN = 0;
  DEVICE_TIER_1 = 1;
  DEVICE_TIER_2 = 2;
}
```

应改用 `DEVICE_TIER_TIER1` 这样的值名称，其中 `DEVICE_TIER_` 部分被视为枚举值的作用域限定，而不是单个枚举值名称的一部分。一些 Protobuf 实现会在确保安全的前提下自动剥离与所属枚举名称匹配的前缀，但在本例中却无法这样做，因为单独的 `1` 不是合法的枚举值名称。

##### 将枚举嵌套在专用的容器消息中 {#nest-enum}

比起仅仅为了缓解冲突风险而专门创建一个 `message`，更应优先选择带前缀值的顶层枚举。由于有些语言不支持在“结构体（struct）”类型中定义枚举，优先使用带前缀的值可以确保各绑定语言之间做法一致。

当把枚举嵌套进容器消息是作为解决 C++ 全局命名空间污染的变通手段时（即 C++ 命名空间例外），“将枚举嵌套在容器消息中”特指为每个枚举定义一个仅充当命名空间包装的 `local` 空消息。这个容器包装消息必须包含 `reserved 1 to max;`，以防止今后有任何字段被加入其中。

在 2024 版次及更高版次中，使用 `features.default_symbol_visibility = STRICT` 时，嵌套符号默认为 `local`。在包含 `reserved 1 to max;` 的 `local message` 内定义的 `export enum`，是 `STRICT` 模式下唯一允许的例外情况，此时支持导出嵌套枚举。（参见[符号可见性](/programming-guides/symbol_visibility.md)）

2024 版次中规范的命名空间包装消息示例：

```proto
edition = "2024";

option features.default_symbol_visibility = STRICT;

local message MyEnumNamespace {
  export enum Enum {
    ENUM_UNSPECIFIED = 0;
    ENUM_FIRST_VALUE = 1;
  }

  // 确保不会向容器消息添加任何字段。
  reserved 1 to max;
}
```

## 服务 {#services}

服务（service）名称和方法名称都使用 TitleCase。

```proto
service FooService {
  rpc GetSomething(GetSomethingRequest) returns (GetSomethingResponse);
  rpc ListSomething(ListSomethingRequest) returns (ListSomethingResponse);
}
```

## 应避免的事项 {#avoid}

### 避免在字段类型上使用令人困惑的相对 package {#confusing-relative-packages}

.proto 语法允许以相对方式引用定义在另一个 package 中的类型。名称解析时会向上逐级搜索父级 package 来解析相对名称。例如：

```
// 文件：a.proto
package a.b;
message C {}
```

```
// 文件：x.proto
package a.x;
message SomeMsg {
  // 由于我们位于 a.x.SomeMsg 中，该名称会按以下顺序查找：
  //  .a.x.SomeMsg.b.C
  //  .a.x.b.C
  //  .a.b.C
  //  .b.C
  b.C field3 = 1;
}
```

在引用定义于另一个 package 中的类型时，依赖“相对于父级 package”的功能是受支持的，但可能造成困惑：在本例中应使用 `a.b.C` 这种写法。

引用当前 package 中的其他类型（例如同级消息）时不写出 package 名称，是符合惯例的做法。

你可以使用前导点号书写全限定名，以避免任何歧义；但在大多数情况下，即使 package 名称已完整写出，这个前导点号通常也会省略。

### required 字段 {#required}

required 字段是一种强制机制：解析线路字节时，给定字段必须已被设置，否则将拒绝解析该消息。对于在内存中构造的消息，required 这一不变式通常不会被强制执行。proto3 移除了 required 字段。已迁移到 2023 版次的 proto2 `required` 字段，可以使用 `field_presence`（字段存在性）特性并将其设置为 `LEGACY_REQUIRED` 来实现兼容。

虽然在模式（schema）层面强制要求必填在直觉上很可取，但 Protobuf 的主要设计目标之一是支持长期的模式演进。无论某个字段在今天看来多么明显是必需的，都存在一种合理的未来情形：届时该字段不应再被设置（例如，`int64 user_id` 将来可能需要迁移为 `UserId user_id`）。

尤其是对于那些可能转发自己并不真正需要处理的消息的中间件服务器来说，`required` 的语义已被证明对这些长期演进目标危害太大，因此现在强烈不建议使用。

参见[required 已被强烈弃用](/programming-guides/proto2#required-deprecated)。

### 组 {#groups}

组（group）是嵌套消息的另一种语法和线路格式（wire format）。组在 proto2 中被视为已弃用，在 proto3 中已被移除，并在 2023 版次中被转换为 delimited（分隔）表示形式。你可以使用嵌套消息定义和该类型的字段来代替组语法，并使用 [`message_encoding`](/editions/features#message_encoding) 特性来保持线路兼容。

参见[组](/programming-guides/proto2#groups)。

### 避免使用可能引起冲突的字段名和 oneof 名称 {#collisions}

某些名称组合使用会在生成代码中引起冲突，可能导致代码无法编译。为了降低特定语言出现故障的风险，应避免使用某些前缀、后缀和名称。

#### 前缀： {#avoid-prefixes}

*   has_
*   get_
*   set_
*   clear_

#### 后缀： {#avoid-suffixes}

*   _value

#### 名称： {#avoid-names}

*   `descriptor`（描述符）
*   其他语言的关键字和保留字也应避免使用；参见[避免使用语言关键字](/best-practices/dos-donts#avoid-keywords)和 [Python 关键字冲突](/reference/python/python-generated#keyword-conflicts)。
