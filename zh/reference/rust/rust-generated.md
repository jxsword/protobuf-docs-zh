+++
title = "Rust 生成代码指南"
weight = 782
linkTitle = "生成代码指南"
description = "描述 Protobuf 编译器针对任意给定协议定义所生成的消息对象 API。"
type = "docs"
source_url = "https://protobuf.dev/reference/rust/rust-generated/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

本页确切描述 Protobuf 编译器针对任意给定协议定义会生成哪些 Rust 代码。

本文档介绍 Protobuf 编译器如何针对 proto2、proto3 和 Protobuf 版次（edition）生成 Rust 代码。proto2、proto3 与版次的生成代码（generated code）之间的任何差异都会重点标出。阅读本文档之前，请先阅读 [proto2 语言指南](/programming-guides/proto2)、[proto3 语言指南](/programming-guides/proto3)或[版次指南](/programming-guides/editions)。

## Protobuf Rust {#rust}

Protobuf Rust 是 Protobuf 的一个实现，其设计目标是能够构建在其他现有 Protobuf 实现之上，我们将这些底层实现称为“内核（kernel）”。

支持多种非 Rust 内核的决定显著影响了我们的公开 API，包括选择使用 `ProtoStr` 这类自定义类型而非 `str` 这类 Rust 标准库类型。有关此主题的更多信息，请参见 [Rust Proto 设计决策](/reference/rust/rust-design-decisions)。

## 包 {#packages}

与大多数其他语言不同，`.proto` 文件中的 `package` 声明在 Rust 代码生成中不会被使用。

使用 `rust_proto_library` 时，该库会对应一个 crate。目标（target）的名称会被用作 crate 名称，请相应地选择你的库名称。

使用 Cargo 时，我们建议你把 `generated.rs` 入口文件 `include!` 到一个名称合适的 mod 中，如我们的[示例 crate（Example Crate）](https://docs.rs/crate/protobuf-example)所示。

## 消息 {#messages}

给定如下消息（message）声明：

```proto
message Foo {}
```

编译器会生成一个名为 `Foo` 的结构体。`Foo` 结构体定义了以下关联函数和方法：

### 关联函数

*   `fn new() -> Self`：创建 `Foo` 的新实例。

### trait

出于多方面原因——包括生成代码体积、命名冲突问题以及生成代码的稳定性——消息上的大多数常用功能都是通过 trait 实现的，而不是以固有实现（inherent implementation）的形式提供。

大多数用户应当导入我们的 prelude，其中只包含若干 trait 和我们的 `proto!` 宏，不含其他类型（`use protobuf::prelude::*`）。如果你不想使用 prelude，也可以始终按需导入具体的 trait（如果你想直接导入，可参阅
<!-- TODO: replace `4.32.0-prerelease` with `latest` once we do a stable release -->
[此处文档](https://docs.rs/protobuf/4.33.5-release/protobuf/trait.Message.html)了解各 trait 的名称与定义）。

*   `fn parse(data: &[u8]) -> Result<Self, ParseError>`：解析出一个新的消息实例。
*   `fn parse_dont_enforce_required(data: &[u8]) -> Result<Self, ParseError>`：与 `parse` 相同，但不会因缺失 proto2 `required` 字段（field）而失败。
*   `fn clear(&mut self)`：清空消息。
*   `fn clear_and_parse(&mut self, data: &[u8]) -> Result<(), ParseError>`：清空并解析到已有实例中。
*   `fn clear_and_parse_dont_enforce_required(&mut self, data: &[u8]) -> Result<(), ParseError>`：与 `parse` 相同，但不会因缺失 proto2 `required` 字段而失败。
*   `fn serialize(&self) -> Result<Vec<u8>, SerializeError>`：将消息序列化为 Protobuf 线路格式（wire format）。序列化可能会失败，但很少真的失败。失败原因包括：表示形式超出最大编码消息大小（必须小于 2 GiB），以及存在未设置的 `required` 字段（proto2）。
*   `fn serialized_len(&self) -> usize`：返回序列化后消息的大小（以字节为单位）。
*   `fn take_from(&mut self, other)`：将 `other` 移动到 `self` 中，丢弃 `self` 原有的任何状态。
*   `fn copy_from(&mut self, other)`：将 `other` 复制到 `self` 中，丢弃 `self` 原有的任何状态。`other` 不会被修改。
*   `fn merge_from(&mut self, other)`：将 `other` 合并到 `self` 中。
*   `fn as_view(&self) -> FooView<'_>`：返回指向 `Foo` 的不可变句柄（view）。代理类型一节会进一步介绍。
*   `fn as_mut(&mut self) -> FooMut<'_>`：返回指向 `Foo` 的可变句柄（mut）。代理类型一节会进一步介绍。
*   `fn into_view(self) -> FooView<'_>`：消费 `self` 并返回一个生命周期更短的、指向 `Foo` 的不可变句柄（view）。
*   `fn into_mut(self) -> FooMut<'_>`：消费 `self` 并返回一个生命周期更短的、指向 `Foo` 的可变句柄（mut）。

此外，`Foo` 还实现了以下标准库 trait：

*   `std::fmt::Debug`
*   `std::default::Default`
*   `std::clone::Clone`
*   `std::marker::Send`
*   `std::marker::Sync`

### 流畅地创建新实例 {#proto-macro}

setter 的 API 设计遵循我们既有的 Protobuf 惯例，但在某些其他语言中，构造新实例时的冗长是一个轻度痛点。为缓解这一问题，我们提供了 `proto!` 宏，可用于更简洁、更流畅地创建新实例。

例如，与其这样写：

```
let mut msg = SomeMsg::new();
msg.set_x(1);
msg.set_y("hello");
msg.some_submessage_mut().set_z(42);
```

可以使用该宏写成如下形式：

```
let msg = proto!(SomeMsg {
  x: 1,
  y: "hello",
  some_submsg: SomeSubmsg {
    z: 42
  }
});
```

### 消息代理类型 {#message-proxy-types}

出于若干技术原因，我们选择在某些场景下避免使用 Rust 原生引用（`&T` 和 `&mut T`），而是使用类型来表达这些概念——即 `View` 和 `Mut`。这些场景包括对以下内容的共享引用和可变引用：

*   消息
*   repeated 字段
*   map 字段

例如，编译器会在生成 `Foo` 的同时生成结构体 `FooView<'a>` 和 `FooMut<'msg>`。这些类型用于替代 `&Foo` 和 `&mut Foo`，并且在借用检查器（borrow checker）行为方面与原生 Rust 引用完全一致。与原生借用一样，View 是 `Copy` 的，借用检查器会强制保证：在任一时刻，你要么可以拥有任意数量的 View，要么最多只能拥有一个 Mut。

在本文档中，我们重点描述为消息的所有权类型（owned type，即 `Foo`）生成的全部方法。其中带 `&self` 接收者的函数子集也会出现在 `FooView<'msg>` 上；带 `&self` 或 `&mut self` 接收者的函数子集也会出现在 `FooMut<'msg>` 上。

要从 View / Mut 类型创建所有权消息类型，可调用 `to_owned()`，它会创建一份深拷贝（deep copy）。

关于为何做出这一选择的更多讨论，请参见我们的[设计决策](/reference/rust/rust-design-decisions#view-mut-proxy-types)文档中的相应章节。

## 嵌套类型 {#nested-types}

给定如下消息声明：

```proto
message Foo {
  message Bar {
      enum Baz { ... }
  }
}
```

除了名为 `Foo` 的结构体外，编译器还会创建一个名为 `foo` 的模块来容纳 `Bar` 对应的结构体；类似地，还会创建一个嵌套模块 `bar` 来容纳深层嵌套的枚举 `Baz`：

```rs
pub struct Foo {}

pub mod foo {
   pub struct Bar {}
   pub mod bar {
      pub struct Baz { ... }
   }
}
```

## 字段 {#fields}

除了上一节描述的方法之外，Protobuf 编译器还会为消息在 `.proto` 文件中定义的每个字段生成一组访问器（accessor）方法。

遵循 Rust 风格，这些方法采用小写/蛇形命名（snake-case），例如 `has_foo()` 和 `clear_foo()`。请注意，访问器中字段名部分的大小写沿用了原始 .proto 文件中的风格，而按照 [.proto 文件样式指南](/programming-guides/style)的要求，后者本身应当是小写/蛇形命名。

### 具有显式存在性的字段 {#explicit-presence}

显式存在性（explicit presence）是指字段能够区分默认值（default value）与未设置值这两种状态。在 proto2 中，`optional` 字段具有显式存在性。在 proto3 中，只有消息字段以及 `oneof` 或 `optional` 字段具有显式存在性。在版次中，存在性通过 [`features.field_presence`](/editions/features#field_presence) 选项设置。

**注意：** 虽然具有显式存在性的字段提供了返回 `Option` 的 `foo_opt()` getter，但我们不会生成与之对应的 `set_foo_opt()` setter。“设置或可能清空某个字段”这种操作被认为是少见的用法，最好让调用方“可见地”表达它正在执行两种可能变更之一（`set_foo` 或 `clear_foo`）。此外，生成代码的原始代码体积也是我们关注的问题，因此为少见的操作增加更多情形被认为不值得带来体积增长。不过，我们清楚这种带有 `opt` getter 的 API 不对称性有些别扭，如果未来证明这种操作合理且并不少见，我们可能会重新审视。[不支持可空的 setter/getter](/design-decisions/nullable-getters-setters)与此相关。

#### 数值字段 {#numeric-fields}

对于如下字段定义：

```proto
int32 foo = 1;
```

编译器会生成以下访问器方法：

*   `fn has_foo(&self) -> bool`：如果字段已设置，则返回 `true`。
*   `fn foo(&self) -> i32`：返回字段的当前值。如果字段未设置，则返回默认值。
*   `fn foo_opt(&self) -> std::option::Option<i32>`：如果字段已设置，返回 `Some(value)`；如果未设置，返回 `None`。
*   `fn set_foo(&mut self, val: i32)`：设置字段的值。调用该方法后，`has_foo()` 将返回 `true`，`foo()` 将返回 `value`。
*   `fn clear_foo(&mut self)`：清空字段的值。调用该方法后，`has_foo()` 将返回 `false`，`foo()` 将返回默认值。

对于其他数值字段类型（包括 `bool`），`int32` 会按照[标量（scalar）值类型表](/programming-guides/proto3#scalar)替换为对应的 Rust 类型。

#### string 与 bytes 字段 {#string-byte-fields}

对于如下字段定义：

```proto
string foo = 1;
bytes foo = 1;
```

编译器会生成以下访问器方法：

*   `fn has_foo(&self) -> bool`：如果字段已设置，则返回 `true`。
*   `fn foo(&self) -> &protobuf::ProtoStr`：返回字段的当前值。如果字段未设置，则返回默认值。参见 [`ProtoStr` 的 rustdoc](https://docs.rs/protobuf/4.33.5-release/protobuf/struct.ProtoStr.html)。
*   `fn foo_opt(&self) -> std::option::Option<&ProtoStr>`：如果字段已设置，返回 `Some(value)`；如果未设置，返回 `None`。
*   `fn set_foo(&mut self, val: impl IntoProxied<ProtoString>)`：设置字段的值。`&str`、`String`、`&ProtoStr` 和 `ProtoString` 都实现了 `IntoProxied`，都可以传入该方法。
*   `fn clear_foo(&mut self)`：清空字段的值。调用该方法后，`has_foo()` 将返回 `false`，`foo()` 将返回默认值。

对于 `bytes` 类型的字段，编译器会改为生成 `ProtoBytes` 类型。

#### 枚举字段 {#enum-fields}

给定任意 proto 语法版本中的如下枚举（enum）定义：

```proto
enum Bar {
  BAR_UNSPECIFIED = 0;
  BAR_VALUE = 1;
  BAR_OTHER_VALUE = 2;
}
```

编译器会生成一个结构体，其中每个枚举项（enumerator）都是一个关联常量：

```rust
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
#[repr(transparent)]
pub struct Bar(i32);

impl Bar {
  pub const Unspecified: Bar = Bar(0);
  pub const Value: Bar = Bar(1);
  pub const OtherValue: Bar = Bar(2);
}
```

对于如下字段定义：

```proto
Bar foo = 1;
```

编译器会生成以下访问器方法：

*   `fn has_foo(&self) -> bool`：如果字段已设置，则返回 `true`。
*   `fn foo(&self) -> Bar`：返回字段的当前值。如果字段未设置，则返回默认值。
*   `fn foo_opt(&self) -> std::option::Option<Bar>`：如果字段已设置，返回 `Some(value)`；如果未设置，返回 `None`。
*   `fn set_foo(&mut self, val: Bar)`：设置字段的值。调用该方法后，`has_foo()` 将返回 `true`，`foo()` 将返回 `value`。
*   `fn clear_foo(&mut self)`：清空字段的值。调用该方法后，`has_foo()` 将返回 `false`，`foo()` 将返回默认值。

#### 嵌入消息字段 {#embedded-message-fields}

给定任意 proto 语法版本中的消息类型 `Bar`：

```proto
message Bar {}
```

对于如下任意一种字段定义：

```proto

message MyMessage {
  Bar foo = 1;
}
```

编译器会生成以下访问器方法：

*   `fn foo(&self) -> BarView<'_>`：返回字段当前值的视图。如果字段未设置，则返回一个空消息。
*   `fn foo_mut(&mut self) -> BarMut<'_>`：返回指向字段当前值的可变句柄。如果字段未设置，会先设置该字段。调用该方法后，`has_foo()` 返回 true。
*   `fn foo_opt(&self) -> std::option::Option<BarView<'_>>`：如果字段已设置，返回包含其视图的 `Some`；否则返回 `None`。
*   `fn set_foo(&mut self, value: impl protobuf::IntoProxied<Bar>)`：将该字段设置为 `value`。调用该方法后，`has_foo()` 返回 `true`。
*   `fn has_foo(&self) -> bool`：如果字段已设置，则返回 `true`。
*   `fn clear_foo(&mut self)`：清空该字段。调用该方法后，`has_foo()` 返回 `false`。

### 具有隐式存在性的字段（proto3 与版次） {#implicit-presence}

隐式存在性（implicit presence）是指字段不区分默认值与未设置值。在 proto3 中，字段默认具有隐式存在性。在版次中，你可以通过将 `field_presence` 特性设置为 `IMPLICIT` 来声明一个具有隐式存在性的字段。

#### 数值字段 {#implicit-numeric-fields}

对于如下字段定义：

```proto
// proto3
int32 foo = 1;

// 版次
message MyMessage {
  int32 foo = 1 [features.field_presence = IMPLICIT];
}
```

编译器会生成以下访问器方法：

*   `fn foo(&self) -> i32`：返回字段的当前值。如果字段未设置，则返回 `0`。
*   `fn set_foo(&mut self, val: i32)`：设置字段的值。

对于其他数值字段类型（包括 `bool`），`int32` 会按照[标量值类型表](/programming-guides/proto3#scalar)替换为对应的 Rust 类型。

#### string 与 bytes 字段 {#implicit-string-byte-fields}

对于如下字段定义：

```proto
// proto3
string foo = 1;
bytes foo = 1;

// 版次
string foo = 1 [features.field_presence = IMPLICIT];
bytes bar = 2 [features.field_presence = IMPLICIT];
```

编译器会生成以下访问器方法：

*   `fn foo(&self) -> &ProtoStr`：返回字段的当前值。如果字段未设置，返回空字符串/空字节串。参见 [`ProtoStr` 的 rustdoc](https://docs.rs/protobuf/4.33.5-release/protobuf/struct.ProtoStr.html)。
*   `fn set_foo(&mut self, value: IntoProxied<ProtoString>)`：将该字段设置为 `value`。

对于 `bytes` 类型的字段，编译器会改为生成 `ProtoBytes` 类型。

### 支持 Cord 的单数 string 与 bytes 字段 {#singular-string-bytes}

`[ctype = CORD]` 使 bytes 和 string 可以在 C++ Protobuf 中存储为 [absl::Cord](https://github.com/abseil/abseil-cpp/blob/master/absl/strings/cord.h)。Protobuf Rust 不会将这些字段暴露为 Rust 的 Cord 类型。在使用 C++ 内核时，Protobuf Rust 用一个枚举来表示 cord 字段：

```rust
enum ProtoStringCow<'a> {
  Owned(ProtoString),
  Borrowed(&'a ProtoStr)
}
```

在常见情形下，对于较小的字符串，`absl::Cord` 会将其数据存储为连续字符串。此时 cord 访问器返回 `ProtoStringCow::Borrowed`。如果底层 `absl::Cord` 不是连续的，访问器会把数据从 cord 复制到一个持有所有权的 `ProtoString` 中，并返回 `ProtoStringCow::Owned`。`ProtoStringCow` 实现了 `Deref<Target=ProtoStr>`。

对于如下任意一种字段定义：

```proto
optional string foo = 1 [ctype = CORD];
string foo = 1 [ctype = CORD];
optional bytes foo = 1 [ctype = CORD];
bytes foo = 1 [ctype = CORD];
```

编译器会生成以下访问器方法：

*   `fn foo(&self) -> ProtoStringCow<'_>`：返回字段的当前值。如果字段未设置，返回空字符串/空字节串。
*   `fn set_foo(&mut self, value: impl IntoProxied<ProtoString>)`：将该字段设置为 `value`。调用该函数后，`foo()` 返回 `value`，`has_foo()` 返回 `true`。
*   `fn has_foo(&self) -> bool`：如果字段已设置，则返回 `true`。
*   `fn clear_foo(&mut self)`：清空字段的值。调用该方法后，`has_foo()` 返回 `false`，`foo()` 返回默认值。

对于 `bytes` 类型的字段，编译器会改为生成 `ProtoBytesCow` 类型。

在使用 upb 内核时，`[ctype = CORD]` 不起作用，编译器会为该字段生成与没有该设置时相同的访问器方法。例如：

*   `fn foo(&self) -> &ProtoStr`：返回字段的当前值。如果字段未设置，返回空字符串/空字节串。
*   `fn set_foo(&mut self, value: impl IntoProxied<ProtoString>)`：将该字段设置为 `value`。

#### 枚举字段 {#implicit-presence-enum}

给定如下枚举类型：

```proto
enum Bar {
  BAR_UNSPECIFIED = 0;
  BAR_VALUE = 1;
  BAR_OTHER_VALUE = 2;
}
```

编译器会生成一个结构体，其中每个枚举项都是一个关联常量：

```rust
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
#[repr(transparent)]
pub struct Bar(i32);

impl Bar {
  pub const Unspecified: Bar = Bar(0);
  pub const Value: Bar = Bar(1);
  pub const OtherValue: Bar = Bar(2);
}
```

对于如下字段定义：

```proto
// proto3
Bar foo = 1;

// 版次
message MyMessage {
 Bar foo = 1 [features.field_presence = IMPLICIT];
}
```

编译器会生成以下访问器方法：

*   `fn foo(&self) -> Bar`：返回字段的当前值。如果字段未设置，则返回默认值。
*   `fn set_foo(&mut self, value: Bar)`：设置字段的值。调用该方法后，`has_foo()` 将返回 `true`，`foo()` 将返回 `value`。

### repeated 字段 {#repeated-fields}

对于任意 repeated 字段定义，编译器都会生成相同的三个访问器方法，仅字段类型有所不同。

在版次中，你可以使用 [`repeated_field_encoding`](/editions/features#repeated_field_encoding) 特性来控制 repeated 基本类型字段的线路格式编码。

```proto
// proto2
repeated int32 foo = 1; // 默认为 EXPANDED

// proto3
repeated int32 foo = 1; // 默认为 PACKED

// 版次
repeated int32 foo = 1 [features.repeated_field_encoding = PACKED];
repeated int32 bar = 2 [features.repeated_field_encoding = EXPANDED];
```

对于上述任意一种字段定义，编译器都会生成以下访问器方法：

*   `fn foo(&self) -> RepeatedView<'_, i32>`：返回底层 repeated 字段的视图。参见 [`RepeatedView` 的 rustdoc](https://docs.rs/protobuf/4.33.5-release/protobuf/struct.RepeatedView.html)。
*   `fn foo_mut(&mut self) -> RepeatedMut<'_, i32>`：返回底层 repeated 字段的可变句柄。参见 [`RepeatedMut` 的 rustdoc](https://docs.rs/protobuf/4.33.5-release/protobuf/struct.RepeatedMut.html)。
*   `fn set_foo(&mut self, src: impl IntoProxied<Repeated<i32>>)`：将底层 repeated 字段设置为 `src` 提供的新 repeated 字段。接受 `RepeatedView`、`RepeatedMut` 或 `Repeated`。参见 [`Repeated` 的 rustdoc](https://docs.rs/protobuf/4.33.5-release/protobuf/struct.Repeated.html)。

对于不同的字段类型，只有 `RepeatedView`、`RepeatedMut` 和 `Repeated` 类型各自对应的泛型参数会变化。例如，对于 `string` 类型的字段，`foo()` 访问器将返回 `RepeatedView<'_, ProtoString>`。

### map 字段 {#map}

对于如下 map 字段定义：

```proto
map<int32, int32> weight = 1;
```

编译器会生成以下 3 个访问器方法：

*   `fn weight(&self) -> protobuf::MapView<'_, i32, i32>`：返回底层 map 的不可变视图。参见 [`MapView` 的 rustdoc](https://docs.rs/protobuf/4.33.5-release/protobuf/struct.MapView.html)。
*   `fn weight_mut(&mut self) -> protobuf::MapMut<'_, i32, i32>`：返回底层 map 的可变句柄。参见 [`MapMut` 的 rustdoc](https://docs.rs/protobuf/4.33.5-release/protobuf/struct.MapMut.html)。
*   `fn set_weight(&mut self, src: protobuf::IntoProxied<Map<i32, i32>>)`：将底层 map 设置为 `src`。接受 `MapView`、`MapMut` 或 `Map`。参见 [`Map` 的 rustdoc](https://docs.rs/protobuf/4.33.5-release/protobuf/struct.Map.html)。

对于不同的字段类型，只有 `MapView`、`MapMut` 和 `Map` 类型各自对应的泛型参数会变化。例如，对于 `string` 类型的字段，`foo()` 访问器将返回 `MapView<'_, int32, ProtoString>`。

## Any {#any}

目前 Rust Protobuf 尚未对 Any 做特殊处理；它会表现得如同一个具有如下定义的普通消息：

```proto
message Any {
  string type_url = 1;
  bytes value = 2;
}
```

## Oneof {#oneof}

给定如下 oneof 定义：

```proto
oneof example_name {
    int32 foo_int = 4;
    string foo_string = 9;
    ...
}
```

编译器会为每个字段生成访问器（getter、setter、hazzer），就像该字段是在 oneof 之外声明为 `optional` 字段一样。因此你可以像操作普通字段那样操作 oneof 字段，但设置其中一个字段会清空 oneof 块中的其他字段。此外，编译器还会为 `oneof` 块生成以下类型：

```rust
  #[non_exhaustive]
  #[derive(Debug, Clone, Copy)]

  pub enum ExampleNameOneof<'msg> {
    FooInt(i32) = 4,
    FooString(&'msg protobuf::ProtoStr) = 9,
    not_set(std::marker::PhantomData<&'msg ()>) = 0
  }
```

```rust
  #[derive(Debug, Copy, Clone, PartialEq, Eq)]

  pub enum ExampleNameCase {
    FooInt = 4,
    FooString = 9,
    not_set = 0
  }
```

此外，它还会生成以下两个访问器：

*   `fn example_name(&self) -> ExampleNameOneof<_>`：返回指示哪个字段已设置及其值的枚举变体。如果没有字段被设置，则返回 `not_set`。
*   `fn example_name_case(&self) -> ExampleNameCase`：返回指示哪个字段已设置的枚举变体。如果没有字段被设置，则返回 `not_set`。

## 枚举 {#enumerations}

给定如下枚举定义：

```proto
enum FooBar {
  FOO_BAR_UNKNOWN = 0;
  FOO_BAR_A = 1;
  FOO_B = 5;
  VALUE_C = 1234;
}
```

编译器会生成：

```rust
  #[derive(Clone, Copy, PartialEq, Eq, Hash)]
  #[repr(transparent)]
  pub struct FooBar(i32);

  impl FooBar {
    pub const Unknown: FooBar = FooBar(0);
    pub const A: FooBar = FooBar(1);
    pub const FooB: FooBar = FooBar(5);
    pub const ValueC: FooBar = FooBar(1234);
  }
```

请注意，对于带有与枚举名相匹配前缀的取值，该前缀会被去除；这样做是为了提升使用体验。枚举取值通常会加上枚举名作为前缀，以避免同级枚举之间的命名冲突（这遵循 C++ 枚举的语义，即取值不会被其所在枚举限定作用域）。由于生成的 Rust 常量已被限定在 `impl` 作用域内，在 .proto 文件中值得添加的这个额外前缀在 Rust 中就成了冗余。

## 扩展 {#extensions}

Protobuf Rust 支持 proto2 消息的扩展（extension）。扩展通过生成的 `ExtensionId` 常量来访问。

给定一个定义了扩展的消息：

```proto
package xyz;
message Foo {
  extensions 100 to 199;
}

extend Foo {
  optional int32 i32_ext = 100;
  repeated int32 repeated_i32_ext = 101;
}
```

编译器会生成类型为 `protobuf::ExtensionId`、名为 `I32_EXT` 和 `REPEATED_I32_EXT` 的常量，你可以用它们在 `Foo` 类型上读写扩展。

### 访问扩展 {#accessing-exts}

`ExtensionId<Extendee, T>` 类型提供了与消息上的扩展交互的方法，其中 `Extendee` 是被扩展的消息类型（即前文的 `Foo`），`T` 是扩展的类型（对于 repeated 扩展为 `Repeated<E>`）。这些方法适用于消息的所有权类型、视图和 Mut。

*   `fn has(&self, msg: impl AsView<Proxied = Extendee>) -> bool`：如果消息上已设置该扩展，则返回 `true`。（出于设计考虑，不适用于 repeated 扩展。）
*   `fn get<'msg>(&self, msg: impl IntoView<'msg, Proxied = Extendee>) -> View<'msg, T>`：返回扩展的值。如果未设置，返回默认值。对于 repeated 字段，返回 `RepeatedView`。
*   `fn set(&self, msg: impl AsMut<MutProxied = Extendee>, value: impl IntoProxied<T>)`：设置扩展的值。
*   `fn clear(&self, msg: impl AsMut<MutProxied = Extendee>)`：从消息中清空该扩展。
*   `fn get_mut<'msg>(&self, msg: impl IntoMut<'msg, MutProxied = Extendee>) -> Mut<'msg, T>`：返回扩展的可变句柄。仅适用于消息扩展和 repeated 扩展；如果字段不存在，会创建该字段。

### 用法示例 {#ext-example}

```rust
use protobuf::prelude::*;

let mut foo = xyz::Foo::new();

// 检查并设置标量扩展
assert!(!xyz::I32_EXT.has(&foo));
xyz::I32_EXT.set(&mut foo, 42);
assert!(xyz::I32_EXT.has(&foo));
assert_eq!(xyz::I32_EXT.get(&foo), 42);

// 清空标量扩展
xyz::I32_EXT.clear(&mut foo);
assert!(!xyz::I32_EXT.has(&foo));

// 操作 repeated 扩展
{
    let mut rep_mut = xyz::REPEATED_I32_EXT.get_mut(&mut foo);
    rep_mut.push(1);
    rep_mut.push(2);
}
assert_eq!(xyz::REPEATED_I32_EXT.get(&foo).len(), 2);
assert_eq!(xyz::REPEATED_I32_EXT.get(&foo).get(0), Some(1));
```

## Arena 分配 {#arena}

针对 arena 分配消息的 Rust API 尚未实现。

在内部，upb 内核上的 Protobuf Rust 使用 arena，而 C++ 内核则不使用。不过，在 C++ 中以 arena 分配的消息，其引用（包括 const 引用和可变引用）都可以安全地传递给 Rust 进行访问或修改。

## 服务 {#services}

针对服务的 Rust API 尚未实现。
