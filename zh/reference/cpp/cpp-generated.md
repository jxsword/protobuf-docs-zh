+++
title = "C++ 生成代码指南"
weight = 510
linkTitle = "生成代码指南"
description = "详细描述 Protobuf 编译器针对任意给定协议定义所生成的 C++ 代码。 "
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/cpp-generated/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

proto2、proto3 与版次（edition）生成代码之间的任何差异都会重点标出。请注意，这些差异存在于本文档所描述的生成代码（generated code）中，而非基础消息（message）类/接口——后者在所有版本（version）中都是相同的。阅读本文档之前，请先阅读 [proto2 语言指南](/programming-guides/proto2)、[proto3 语言指南](/programming-guides/proto3)或 [2023 版次语言指南](/programming-guides/editions)。

## 编译器调用 {#invocation}

使用 `--cpp_out=` 命令行标志调用时，Protobuf 编译器会生成 C++ 输出。`--cpp_out=` 选项的参数是你希望编译器写入 C++ 输出的目录。编译器会为每个输入的 `.proto` 文件创建一个头文件和一个实现文件。输出文件名的计算方式是：取 `.proto` 文件的名称并做两处修改：

-   扩展名（`.proto`）分别被替换为 `.pb.h` 或 `.pb.cc`，前者用于头文件，后者用于实现文件。
-   proto 路径（通过 `--proto_path=` 或 `-I` 命令行标志指定）被替换为输出路径（通过 `--cpp_out=` 标志指定）。

例如，假设你按如下方式调用编译器：

```shell
protoc --proto_path=src --cpp_out=build/gen src/foo.proto src/bar/baz.proto
```

编译器将读取 `src/foo.proto` 和 `src/bar/baz.proto`，并生成四个输出文件：`build/gen/foo.pb.h`、`build/gen/foo.pb.cc`、`build/gen/bar/baz.pb.h`、`build/gen/bar/baz.pb.cc`。如有必要，编译器会自动创建目录 `build/gen/bar`，但*不会*创建 `build` 或 `build/gen`；这两个目录必须已经存在。

## 包 {#package}

如果 `.proto` 文件包含 `package` 声明，文件的全部内容都会被置于相应的 C++ 命名空间（namespace）中。例如，给定如下 `package` 声明：

```proto
package foo.bar;
```

文件中的所有声明都将位于 `foo::bar` 命名空间中。

## 消息 {#message}

给定一个简单的消息声明：

```proto
message Foo {}
```

Protobuf 编译器会生成一个名为 `Foo` 的类，它公开继承自 [`google::protobuf::Message`](/reference/cpp/api-docs/google.protobuf.message)。该类是一个具体类；没有留待实现的纯虚方法。那些在 `Message` 中为虚方法但非纯虚的方法，`Foo` 可能会重写也可能不会，具体取决于优化模式。默认情况下，`Foo` 会为实现最高速度而提供所有方法的专门实现。但是，如果 `.proto` 文件包含以下行：

```proto
option optimize_for = CODE_SIZE;
```

那么 `Foo` 将只重写正常运作所必需的最少方法集，其余方法则依赖基于反射（reflection）的实现。这会显著减小生成代码的体积，但也会降低性能。另外，如果 `.proto` 文件包含：

```proto
option optimize_for = LITE_RUNTIME;
```

那么 `Foo` 将包含所有方法的快速实现，但实现的是 [`google::protobuf::MessageLite`](/reference/cpp/api-docs/google.protobuf.message_lite) 接口，该接口只包含 `Message` 方法的一个子集。特别是，它不支持描述符（descriptor）或反射。不过，在这种模式下，生成代码只需链接 `libprotobuf-lite.so`（Windows 上为 `libprotobuf-lite.lib`），而无需链接 `libprotobuf.so`（`libprotobuf.lib`）。这个 "lite" 库比完整库小得多，更适合手机等资源受限的系统。

你*不应*创建自己的 `Foo` 子类。如果你继承该类并重写某个虚方法，该重写可能会被忽略，因为许多生成的方法调用已被去虚拟化（de-virtualized）以提升性能。

`Message` 接口定义了一些方法，让你能够检查、操作、读取或写入整个消息，包括从二进制字符串解析（parse）消息，以及把消息序列化（serialization）为二进制字符串。

-   `bool ParseFromString(::absl::string_view data)`：从给定的已序列化二进制字符串解析消息，这种格式也称为线路格式（wire format）。
-   `bool SerializeToString(string* output) const`：把给定消息序列化为二进制字符串。
-   `string DebugString()`：返回一个字符串，给出该 proto 的 `text_format` 表示形式（只应用于调试）。

如果解析失败（方法返回 `false`），消息将处于任意但有效的状态。类似于 C++ 中被移动之后的对象，此时销毁消息或对其调用 `Clear()` 是安全的，但其内容应视为未指定。

除这些方法之外，`Foo` 类还定义了以下方法：

-   `Foo()`：默认构造函数。
-   `~Foo()`：默认析构函数。
-   `Foo(const Foo& other)`：拷贝构造函数。
-   `Foo(Foo&& other)`：移动构造函数。
-   `Foo& operator=(const Foo& other)`：赋值运算符。
-   `Foo& operator=(Foo&& other)`：移动赋值运算符。
-   `void Swap(Foo* other)`：与另一个消息交换内容。
-   `const UnknownFieldSet& unknown_fields() const`：返回解析此消息时遇到的未知字段（unknown fields）集合。如果 `.proto` 文件中指定了 `option optimize_for = LITE_RUNTIME`，则返回类型变为 `std::string&`。
-   `UnknownFieldSet* mutable_unknown_fields()`：返回指向解析此消息时遇到的未知字段的可变集合的指针。如果 `.proto` 文件中指定了 `option optimize_for = LITE_RUNTIME`，则返回类型变为 `std::string*`。

**注意：** 拷贝构造函数和赋值运算符会对消息数据执行深拷贝。这确保每个消息对象拥有并管理自己的数据副本，从而避免双重释放（double free）或释放后使用（use-after-free）等问题。此行为与 C++ 中拥有自身数据的对象（如 `std::vector`）的标准实践一致。对于来自具有不同拷贝语义的语言（如 JavaScript 或 TypeScript，浅拷贝在这些语言中更常见）的开发者来说，需要注意的是：对拷贝出的消息所做的修改不会影响原消息，反之亦然。

该类还定义了以下静态方法：

-   `static const Descriptor* descriptor()`：返回该类型的描述符。它包含该类型的信息，包括它有哪些字段（field）以及这些字段各自的类型。它可以与[反射](/reference/cpp/api-docs/google.protobuf.message#Reflection)配合使用，以编程方式检查字段。
-   `static const Foo& default_instance()`：返回 `Foo` 的 const 单例实例，它与新建构造的 `Foo` 实例完全相同，即所有单数（singular）字段均未设置，且所有 repeated 字段均为空。注意，可以通过调用其 `New()` 方法，把消息的默认实例用作工厂。

### Abseil flag 支持 {#absl-flags-messages}

`Message` 对象原生支持 Abseil 的 flag 解析/反解析逻辑。它们可以用作 `ABSL_FLAG` 声明的类型。flag 语法为 `:format,options...:value`，其中：

-   `format` 是 `text`、`serialized` 二者之一。
-   `options` 是一个可能为空的选项（option）列表。每种格式都有各自支持的选项。
-   `value` 是指定格式的载荷（payload）。

有效选项如下：

*   对于 `text`：
    -   `base64`：表示 `value` 以 base64 编码。
    -   `ignore_unknown`：指定后，未知字段/扩展会被丢弃；否则它们会导致解析失败。
*   对于 `serialized`：
    -   `base64`：表示 `value` 以 base64 编码。建议将 `serialized` 与 `base64` 搭配使用，因为在 shell 中传递二进制数据既困难又容易出错。

注意，`LITE_RUNTIME` 配置不提供消息类型的 flag 支持。

示例：

```cpp
ABSL_FLAG(MyProtoType, my_proto_config, {},
          "This is a proto config description.");
```

### 嵌套类型 {#nested-types}

消息可以声明在另一个消息内部。例如：

```proto
message Foo {
  message Bar {}
}
```

在这种情况下，编译器会生成两个类：`Foo` 和 `Foo_Bar`。此外，编译器还会在 `Foo` 内部生成如下 typedef：

```cpp
typedef Foo_Bar Bar;
```

这意味着你可以像使用嵌套类 `Foo::Bar` 一样使用该嵌套类型（nested type）的类。但请注意，C++ 不允许对嵌套类型进行前向声明。如果你想在另一个文件中前向声明 `Bar` 并使用该声明，必须把它标识为 `Foo_Bar`。

## 字段 {#fields}

除上一节描述的方法之外，Protobuf 编译器还会为 `.proto` 文件中消息内定义的每个字段生成一组访问器（accessor）方法。这些方法采用小写/蛇形命名（snake-case），例如 `has_foo()` 和 `clear_foo()`。

除访问器方法之外，编译器还会为每个字段生成一个整型常量，其中包含该字段的字段编号（field number）。该常量的名称以字母 `k` 开头，随后是转换为驼峰命名（camel-case）的字段名（field name），最后以 `FieldNumber` 结尾。例如，给定字段 `optional int32 foo_bar = 5;`，编译器将生成常量 `static const int kFooBarFieldNumber = 5;`。

对于返回 `const` 引用的字段访问器，当下一次对消息进行修改性访问时，该引用可能会失效。这包括调用任何字段的任何非 `const` 访问器、调用继承自 `Message` 的任何非 `const` 方法，或通过其他方式修改消息（例如，把消息作为 `Swap()` 的参数传入）。相应地，只有在期间没有对消息进行修改性访问的前提下，才能保证返回的引用在不同访问器调用之间地址相同。

对于返回指针的字段访问器，当下一次对消息进行修改性或非修改性访问时，该指针都可能失效。无论 const 与否，这包括调用任何字段的任何访问器、调用继承自 `Message` 的任何方法，或通过其他方式访问消息（例如，使用拷贝构造函数复制消息）。相应地，返回的指针值在任何两次访问器调用之间都绝不保证相同。

<a id="generated-filenames"><!-- old anchor name, retained to avoid broken links --></a>

### 生成的字段名 {#generated-fieldnames}

[保留关键字](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/compiler/cpp/helpers.cc#L4)在生成输出中会附加一个下划线。

例如，以下 proto3 定义语法：

```proto
message MyMessage {
  string false = 1;
  string myFalse = 2;
}
```

会生成以下部分输出：

```cpp
  void clear_false_() ;
  const std::string& false_() const;
  void set_false_(Arg_&& arg, Args_... args);
  std::string* mutable_false_();
  PROTOBUF_NODISCARD std::string* release_false_();
  void set_allocated_false_(std::string* ptr);

  void clear_myfalse() ;
  const std::string& myfalse() const;
  void set_myfalse(Arg_&& arg, Args_... args);
  std::string* mutable_myfalse();
  PROTOBUF_NODISCARD std::string* release_myfalse();
  void set_allocated_myfalse(std::string* ptr);
```

### 显式存在性数值字段 {#numeric}

对于具有[显式存在性（explicit presence）](/programming-guides/field_presence#presence-in-proto2-apis)的数值字段定义：

```proto
int32 foo = 1;
```

编译器将生成以下访问器方法：

-   `bool has_foo() const`：如果字段已设置，返回 `true`。
-   `int32_t foo() const`：返回字段的当前值。如果字段未设置，返回默认值（default value）。
-   `void set_foo(::int32_t value)`：设置字段的值。调用此方法后，`has_foo()` 将返回 `true`，`foo()` 将返回 `value`。
-   `void clear_foo()`：清除字段的值。调用此方法后，`has_foo()` 将返回 `false`，`foo()` 将返回默认值。

对于其他数值字段类型（包括 `bool`），`int32_t` 会根据[标量（scalar）值类型表](/programming-guides/editions#scalar)替换为对应的 C++ 类型。

### 隐式存在性数值字段 {#implicit-numeric}

对于具有[隐式存在性（implicit presence）](/programming-guides/field_presence#presence-in-proto2-apis)的数值字段定义：

```proto
int32 foo = 1;
```

编译器将生成以下访问器方法：

-   `::int32_t foo() const`：返回字段的当前值。如果字段未设置，返回 0。
-   `void set_foo(::int32_t value)`：设置字段的值。调用此方法后，`foo()` 将返回 `value`。
-   `void clear_foo()`：清除字段的值。调用此方法后，`foo()` 将返回 0。

对于其他数值字段类型（包括 `bool`），`int32_t` 会根据[标量值类型表](/programming-guides/editions#scalar)替换为对应的 C++ 类型。

### 显式存在性字符串/字节字段 {#string}

**注意：** 自 2023 版次起，如果 [`features.(pb.cpp).string_type`](/editions/features#string_type) 被设置为 `VIEW`，将改为生成 [string_view](/reference/cpp/string-view#singular-view) API。

对于这些具有[显式存在性](/programming-guides/field_presence#presence-in-proto2-apis)的字段定义：

```proto
string foo = 1;
bytes foo = 2;
```

编译器将生成以下访问器方法：

-   `bool has_foo() const`：如果字段已设置，返回 `true`。
-   `const string& foo() const`：返回字段的当前值。如果字段未设置，返回默认值。
-   `void set_foo(...)`：设置字段的值。调用此方法后，`has_foo()` 将返回 `true`，`foo()` 将返回 `value` 的副本。
-   `string* mutable_foo()`：返回指向存储字段值的可变 `string` 对象的指针。如果调用前字段未设置，则返回的字符串将为空（*不是*默认值）。调用此方法后，`has_foo()` 将返回 `true`，`foo()` 将返回写入给定字符串中的任何值。

    **注意：** 此方法将在新的 `string_view` API 中被移除。

-   `void clear_foo()`：清除字段的值。调用此方法后，`has_foo()` 将返回 `false`，`foo()` 将返回默认值。

-   `void set_allocated_foo(string* value)`：
    把 `string` 对象设置给该字段，并释放先前的字段值（如果存在）。如果 `string` 指针不是 `NULL`，消息将取得所分配 `string` 对象的所有权，且 `has_foo()` 将返回 `true`。消息可以随时删除所分配的 `string` 对象，因此指向该对象的引用可能会失效。否则，如果 `value` 为 `NULL`，其行为与调用 `clear_foo()` 相同。

-   `string* release_foo()`：
    释放字段的所有权并返回 `string` 对象的指针。调用此方法后，调用者取得所分配 `string` 对象的所有权，`has_foo()` 将返回 `false`，`foo()` 将返回默认值。

<a id="proto3_string"></a>

### 隐式存在性字符串/字节字段 {#implicit-string}

**注意：** 自 2023 版次起，如果 [`features.(pb.cpp).string_type`](/editions/features#string_type) 被设置为 `VIEW`，将改为生成 [string_view](/reference/cpp/string-view#singular-view) API。

对于这些具有[隐式存在性](/programming-guides/field_presence#presence-in-proto2-apis)的字段定义：

```proto
string foo = 1 [features.field_presence = IMPLICIT];
bytes foo = 1 [features.field_presence = IMPLICIT];
```

编译器将生成以下访问器方法：

-   `const string& foo() const`：返回字段的当前值。如果字段未设置，返回空字符串/空字节序列。
-   `void set_foo(Arg_&& arg, Args_... args)`：设置字段的值。调用此方法后，`foo()` 将返回 `value` 的副本。
-   `string* mutable_foo()`：返回指向存储字段值的可变 `string` 对象的指针。如果调用前字段未设置，则返回的字符串将为空。调用此方法后，`foo()` 将返回写入给定字符串中的任何值。
-   `void clear_foo()`：清除字段的值。调用此方法后，`foo()` 将返回空字符串/空字节序列。
-   `void set_allocated_foo(string* value)`：
    把 `string` 对象设置给该字段，并释放先前的字段值（如果存在）。如果 `string` 指针不是 `NULL`，消息将取得所分配 `string` 对象的所有权。消息可以随时删除所分配的 `string` 对象，因此指向该对象的引用可能会失效。否则，如果 `value` 为 `NULL`，其行为与调用 `clear_foo()` 相同。
-   `string* release_foo()`：
    释放字段的所有权并返回 `string` 对象的指针。调用此方法后，调用者取得所分配 `string` 对象的所有权，且 `foo()` 将返回空字符串/空字节序列。

### 带 Cord 支持的单数字节字段 {#cord}

v23.0 为单数 `bytes` 字段（包括 [`oneof` 字段](#oneof-numeric)）添加了对 [`absl::Cord`](https://github.com/abseil/abseil-cpp/blob/master/absl/strings/cord.h) 的支持。单数 `string`、repeated `string` 和 repeated `bytes` 字段不支持使用 `Cord`。

要把单数 `bytes` 字段设置为使用 `absl::Cord` 存储数据，请使用以下语法：

```proto
// 版次（默认设置）
bytes foo = 25 [ctype=CORD];
bytes foo = 26 [ctype=CORD, features.field_presence = IMPLICIT];
```

`repeated bytes` 字段不能使用 `cord`。protoc 会忽略这些字段上的 `[ctype=CORD]` 设置。

编译器将生成以下访问器方法：

-   `const ::absl::Cord& foo() const`：返回字段的当前值。如果字段未设置，返回空的 `Cord`（proto3）或默认值（proto2 与版次）。
-   `void set_foo(const ::absl::Cord& value)`：设置字段的值。调用此方法后，`foo()` 将返回 `value`。
-   `void set_foo(::absl::string_view value)`：设置字段的值。调用此方法后，`foo()` 将以 `absl::Cord` 的形式返回 `value`。
-   `void clear_foo()`：清除字段的值。调用此方法后，`foo()` 将返回空的 `Cord`（proto3）或默认值（proto2 与版次）。
-   `bool has_foo()`：如果字段已设置，返回 `true`。仅适用于 proto3 中的 `optional` 字段和版次中的显式存在性字段。

### 显式存在性枚举字段 {#enum_field}

给定枚举类型：

```proto
enum Bar {
  BAR_UNSPECIFIED = 0;
  BAR_VALUE = 1;
  BAR_OTHER_VALUE = 2;
}
```

对于这个具有[显式存在性](/programming-guides/field_presence#presence-in-proto2-apis)的字段定义：

```proto
Bar bar = 1;
```

编译器将生成以下访问器方法：

-   `bool has_bar() const`：如果字段已设置，返回 `true`。
-   `Bar bar() const`：返回字段的当前值。如果字段未设置，返回默认值。
-   `void set_bar(Bar value)`：设置字段的值。调用此方法后，`has_bar()` 将返回 `true`，`bar()` 将返回 `value`。在调试模式下（即未定义 NDEBUG），如果 `value` 与为 `Bar` 定义的任何值都不匹配，此方法将终止进程。
-   `void clear_bar()`：清除字段的值。调用此方法后，`has_bar()` 将返回 `false`，`bar()` 将返回默认值。

### 隐式存在性枚举字段 {#implicit-enum}

给定枚举类型：

```proto
enum Bar {
  BAR_UNSPECIFIED = 0;
  BAR_VALUE = 1;
  BAR_OTHER_VALUE = 2;
}
```

对于这个具有[隐式存在性](/programming-guides/field_presence#presence-in-proto2-apis)的字段定义：

```proto
Bar bar = 1;
```

编译器将生成以下访问器方法：

-   `Bar bar() const`：返回字段的当前值。如果字段未设置，返回默认值（0）。
-   `void set_bar(Bar value)`：设置字段的值。调用此方法后，`bar()` 将返回 `value`。
-   `void clear_bar()`：清除字段的值。调用此方法后，`bar()` 将返回默认值。

### 显式存在性嵌入消息字段 {#embeddedmessage}

给定消息类型：

```proto
message Bar {}
```

对于这个具有[显式存在性](/programming-guides/field_presence#presence-in-proto2-apis)的字段定义：

```proto
Bar bar = 1;
```

编译器将生成以下访问器方法：

-   `bool has_bar() const`：如果字段已设置，返回 `true`。
-   `const Bar& bar() const`：返回字段的当前值。如果字段未设置，返回一个没有任何字段被设置的 `Bar`（可能是 `Bar::default_instance()`）。
-   `Bar* mutable_bar()`：返回指向存储字段值的可变 `Bar` 对象的指针。如果调用前字段未设置，则返回的 `Bar` 将没有任何字段被设置（即它与新建分配的 `Bar` 完全相同）。调用此方法后，`has_bar()` 将返回 `true`，`bar()` 将返回同一个 `Bar` 实例的引用。
-   `void clear_bar()`：清除字段的值。调用此方法后，`has_bar()` 将返回 `false`，`bar()` 将返回默认值。
-   `void set_allocated_bar(Bar* value)`：把 `Bar` 对象设置给该字段，并释放先前的字段值（如果存在）。如果 `Bar` 指针不是 `NULL`，消息将取得所分配 `Bar` 对象的所有权，且 `has_bar()` 将返回 `true`。否则，如果 `Bar` 为 `NULL`，其行为与调用 `clear_bar()` 相同。
-   `Bar* release_bar()`：释放字段的所有权并返回 `Bar` 对象的指针。调用此方法后，调用者取得所分配 `Bar` 对象的所有权，`has_bar()` 将返回 `false`，`bar()` 将返回默认值。

### repeated 数值字段 {#repeatednumeric}

对于以下字段定义：

```proto
repeated int32 foo = 1;
```

编译器将生成以下访问器方法：

-   `int foo_size() const`：返回字段中当前的元素数量。要检查集合是否为空，建议改用底层 `RepeatedField` 中的 [`empty()`](/reference/cpp/api-docs/google.protobuf.repeated_field#RepeatedPtrField) 方法，而不是此方法。
-   `int32_t foo(int index) const`：返回给定从零开始的索引处的元素。使用 [0, foo_size()) 范围之外的索引调用此方法会产生未定义行为。
-   `void set_foo(int index, int32_t value)`：设置给定从零开始的索引处元素的值。
-   `void add_foo(int32_t value)`：把具有给定值的新元素追加到字段末尾。
-   `void clear_foo()`：移除字段中的所有元素。调用此方法后，`foo_size()` 将返回零。
-   `const RepeatedField<int32_t>& foo() const`：返回存储字段元素的底层 [`RepeatedField`](/reference/cpp/api-docs/google.protobuf.repeated_field#RepeatedField)。该容器类提供类似 STL 的迭代器和其他方法。
-   `RepeatedField<int32_t>* mutable_foo()`：返回指向存储字段元素的底层可变 `RepeatedField` 的指针。该容器类提供类似 STL 的迭代器和其他方法。

对于其他数值字段类型（包括 `bool`），`int32_t` 会根据[标量值类型表](/programming-guides/editions#scalar)替换为对应的 C++ 类型。

### repeated 字符串字段 {#repeatedstring}

**注意：** 自 2023 版次起，如果 [`features.(pb.cpp).string_type`](/editions/features#string_type) 被设置为 `VIEW`，将改为生成 [string_view](/reference/cpp/string-view#singular-view) API。

对于以下任一字段定义：

```proto
repeated string foo = 1;
repeated bytes foo = 1;
```

编译器将生成以下访问器方法：

-   `int foo_size() const`：返回字段中当前的元素数量。要检查集合是否为空，建议改用底层 `RepeatedField` 中的 [`empty()`](/reference/cpp/api-docs/google.protobuf.repeated_field#RepeatedPtrField) 方法，而不是此方法。
-   `const string& foo(int index) const`：返回给定从零开始的索引处的元素。使用 [0, foo_size()-1] 范围之外的索引调用此方法会产生未定义行为。
-   `void set_foo(int index, ::absl::string_view value)`：设置给定从零开始的索引处元素的值。
-   `void set_foo(int index, const string& value)`：设置给定从零开始的索引处元素的值。
-   `void set_foo(int index, string&& value)`：设置给定从零开始的索引处元素的值，从传入的字符串移动。
-   `void set_foo(int index, const char* value)`：使用 C 风格的以空字符结尾的字符串，设置给定从零开始的索引处元素的值。
-   `void set_foo(int index, const char* value, int size)`：使用显式指定大小的 C 风格字符串（而不是通过查找空终止字节来确定大小），设置给定从零开始的索引处元素的值。
-   `string* mutable_foo(int index)`：返回指向存储给定从零开始的索引处元素值的可变 `string` 对象的指针。使用 [0, foo_size()) 范围之外的索引调用此方法会产生未定义行为。
-   `void add_foo(::absl::string_view value)`：把具有给定值的新元素追加到字段末尾。
-   `void add_foo(const string& value)`：把具有给定值的新元素追加到字段末尾。
-   `void add_foo(string&& value)`：把新元素追加到字段末尾，从传入的字符串移动。
-   `void add_foo(const char* value)`：使用 C 风格的以空字符结尾的字符串，把新元素追加到字段末尾。
-   `void add_foo(const char* value, int size)`：使用显式指定大小的字符串（而不是通过查找空终止字节来确定大小），把新元素追加到字段末尾。
-   `string* add_foo()`：在字段末尾添加一个新的空字符串元素，并返回指向它的指针。
-   `void clear_foo()`：移除字段中的所有元素。调用此方法后，`foo_size()` 将返回零。
-   `const RepeatedPtrField<string>& foo() const`：返回存储字段元素的底层 [`RepeatedPtrField`](/reference/cpp/api-docs/google.protobuf.repeated_field#RepeatedPtrField)。该容器类提供类似 STL 的迭代器和其他方法。
-   `RepeatedPtrField<string>* mutable_foo()`：返回指向存储字段元素的底层可变 `RepeatedPtrField` 的指针。该容器类提供类似 STL 的迭代器和其他方法。

### repeated 枚举字段 {#repeated_enum}

给定枚举类型：

```proto
enum Bar {
  BAR_UNSPECIFIED = 0;
  BAR_VALUE = 1;
  BAR_OTHER_VALUE = 2;
}
```

对于以下字段定义：

```proto
repeated Bar bar = 1;
```

编译器将生成以下访问器方法：

-   `int bar_size() const`：返回字段中当前的元素数量。要检查集合是否为空，建议改用底层 `RepeatedField` 中的 [`empty()`](/reference/cpp/api-docs/google.protobuf.repeated_field#RepeatedPtrField) 方法，而不是此方法。
-   `Bar bar(int index) const`：返回给定从零开始的索引处的元素。使用 [0, bar_size()) 范围之外的索引调用此方法会产生未定义行为。
-   `void set_bar(int index, Bar value)`：设置给定从零开始的索引处元素的值。在调试模式下（即未定义 NDEBUG），如果 `value` 与为 `Bar` 定义的任何值都不匹配且它是封闭式枚举（closed enum），此方法将终止进程。
-   `void add_bar(Bar value)`：把具有给定值的新元素追加到字段末尾。在调试模式下（即未定义 NDEBUG），如果 `value` 与为 `Bar` 定义的任何值都不匹配，此方法将终止进程。
-   `void clear_bar()`：移除字段中的所有元素。调用此方法后，`bar_size()` 将返回零。
-   `const RepeatedField<int>& bar() const`：返回存储字段元素的底层 [`RepeatedField`](/reference/cpp/api-docs/google.protobuf.repeated_field#RepeatedField)。该容器类提供类似 STL 的迭代器和其他方法。
-   `RepeatedField<int>* mutable_bar()`：返回指向存储字段元素的底层可变 `RepeatedField` 的指针。该容器类提供类似 STL 的迭代器和其他方法。

### repeated 嵌入消息字段 {#repeatedmessage}

给定消息类型：

```proto
message Bar {}
```

对于以下字段定义：

```proto
repeated Bar bar = 1;
```

编译器将生成以下访问器方法：

-   `int bar_size() const`：返回字段中当前的元素数量。要检查集合是否为空，建议改用底层 `RepeatedField` 中的 [`empty()`](/reference/cpp/api-docs/google.protobuf.repeated_field#RepeatedPtrField) 方法，而不是此方法。
-   `const Bar& bar(int index) const`：返回给定从零开始的索引处的元素。使用 [0, bar_size()) 范围之外的索引调用此方法会产生未定义行为。
-   `Bar* mutable_bar(int index)`：返回指向存储给定从零开始的索引处元素值的可变 `Bar` 对象的指针。使用 [0, bar_size()) 范围之外的索引调用此方法会产生未定义行为。
-   `Bar* add_bar()`：在字段末尾添加一个新元素，并返回指向它的指针。返回的 `Bar` 是可变的，且没有任何字段被设置（即它与新建分配的 `Bar` 完全相同）。
-   `void clear_bar()`：移除字段中的所有元素。调用此方法后，`bar_size()` 将返回零。
-   `const RepeatedPtrField<Bar>& bar() const`：返回存储字段元素的底层 [`RepeatedPtrField`](/reference/cpp/api-docs/google.protobuf.repeated_field#RepeatedPtrField)。该容器类提供类似 STL 的迭代器和其他方法。
-   `RepeatedPtrField<Bar>* mutable_bar()`：返回指向存储字段元素的底层可变 `RepeatedPtrField` 的指针。该容器类提供类似 STL 的迭代器和其他方法。

### oneof 数值字段 {#oneof-numeric}

对于以下 [oneof](#oneof) 字段定义：

```proto
oneof example_name {
    int32 foo = 1;
    ...
}
```

编译器将生成以下访问器方法：

-   `bool has_foo() const`：如果 oneof 分支（case）为 `kFoo`，返回 `true`。
-   `int32 foo() const`：如果 oneof 分支为 `kFoo`，返回字段的当前值；否则返回默认值。
-   `void set_foo(int32 value)`：
    -   如果同一 oneof 中的任何其他 oneof 字段已设置，则调用 `clear_example_name()`。
    -   设置此字段的值，并把 oneof 分支设置为 `kFoo`。
    -   `has_foo()` 将返回 true，`foo()` 将返回 `value`，`example_name_case()` 将返回 `kFoo`。
-   `void clear_foo()`：
    -   如果 oneof 分支不是 `kFoo`，则不会有任何改变。
    -   如果 oneof 分支是 `kFoo`，则清除字段的值和 oneof 分支。`has_foo()` 将返回 `false`，`foo()` 将返回默认值，`example_name_case()` 将返回 `EXAMPLE_NAME_NOT_SET`。

对于其他数值字段类型（包括 `bool`），`int32_t` 会根据[标量值类型表](/programming-guides/editions#scalar)替换为对应的 C++ 类型。

### oneof 字符串字段 {#oneof-string}

**注意：** 自 2023 版次起，可能会改为生成 [string_view](/reference/cpp/string-view#oneof-view) API。

对于以下任何 [oneof](#oneof) 字段定义：

```proto
oneof example_name {
    string foo = 1;
    ...
}
oneof example_name {
    bytes foo = 1;
    ...
}
```

编译器将生成以下访问器方法：

-   `bool has_foo() const`：如果 oneof 分支为 `kFoo`，返回 `true`。
-   `const string& foo() const`：如果 oneof 分支为 `kFoo`，返回字段的当前值；否则返回默认值。
-   `void set_foo(::absl::string_view value)`：
    -   如果同一 oneof 中的任何其他 oneof 字段已设置，则调用 `clear_example_name()`。
    -   设置此字段的值，并把 oneof 分支设置为 `kFoo`。
    -   `has_foo()` 将返回 `true`，`foo()` 将返回 `value` 的副本，`example_name_case()` 将返回 `kFoo`。
-   `void set_foo(const string& value)`：与第一个 `set_foo()` 类似，但从 const 字符串引用拷贝。
-   `void set_foo(string&& value)`：与第一个 `set_foo()` 类似，但从传入的字符串移动。
-   `void set_foo(const char* value)`：与第一个 `set_foo()` 类似，但从 C 风格的以空字符结尾的字符串拷贝。
-   `void set_foo(const char* value, int size)`：与第一个 `set_foo()` 类似，但从显式指定大小的字符串拷贝（而不是通过查找空终止字节来确定大小）。
-   `string* mutable_foo()`：
    -   如果同一 oneof 中的任何其他 oneof 字段已设置，则调用 `clear_example_name()`。
    -   把 oneof 分支设置为 `kFoo`，并返回指向存储字段值的可变字符串对象的指针。如果调用前 oneof 分支不是 `kFoo`，则返回的字符串将为空（不是默认值）。
    -   `has_foo()` 将返回 `true`，`foo()` 将返回写入给定字符串中的任何值，`example_name_case()` 将返回 `kFoo`。
-   `void clear_foo()`：
    -   如果 oneof 分支不是 `kFoo`，则不会有任何改变。
    -   如果 oneof 分支是 `kFoo`，则释放字段并清除 oneof 分支。`has_foo()` 将返回 `false`，`foo()` 将返回默认值，`example_name_case()` 将返回 `EXAMPLE_NAME_NOT_SET`。
-   `void set_allocated_foo(string* value)`：
    -   调用 `clear_example_name()`。
    -   如果字符串指针不是 `NULL`：把字符串对象设置给该字段，并把 oneof 分支设置为 `kFoo`。消息取得所分配字符串对象的所有权，`has_foo()` 将返回 `true`，`example_name_case()` 将返回 `kFoo`。
    -   如果字符串指针为 `NULL`，`has_foo()` 将返回 `false`，`example_name_case()` 将返回 `EXAMPLE_NAME_NOT_SET`。
-   `string* release_foo()`：
    -   如果 oneof 分支不是 `kFoo`，返回 `NULL`。
    -   清除 oneof 分支，释放字段的所有权，并返回字符串对象的指针。调用此方法后，调用者取得所分配字符串对象的所有权，`has_foo()` 将返回 false，`foo()` 将返回默认值，`example_name_case()` 将返回 `EXAMPLE_NAME_NOT_SET`。

### oneof 枚举字段 {#oneof-enum}

给定枚举类型：

```proto
enum Bar {
  BAR_UNSPECIFIED = 0;
  BAR_VALUE = 1;
  BAR_OTHER_VALUE = 2;
}
```

对于以下 [oneof](#oneof) 字段定义：

```proto
oneof example_name {
    Bar bar = 1;
    ...
}
```

编译器将生成以下访问器方法：

-   `bool has_bar() const`：如果 oneof 分支为 `kBar`，返回 `true`。
-   `Bar bar() const`：如果 oneof 分支为 `kBar`，返回字段的当前值；否则返回默认值。
-   `void set_bar(Bar value)`：
    -   如果同一 oneof 中的任何其他 oneof 字段已设置，则调用 `clear_example_name()`。
    -   设置此字段的值，并把 oneof 分支设置为 `kBar`。
    -   `has_bar()` 将返回 `true`，`bar()` 将返回 `value`，`example_name_case()` 将返回 `kBar`。
    -   在调试模式下（即未定义 NDEBUG），如果 `value` 与为 `Bar` 定义的任何值都不匹配且它是封闭式枚举，此方法将终止进程。
-   `void clear_bar()`：
    -   如果 oneof 分支不是 `kBar`，则不会有任何改变。
    -   如果 oneof 分支是 `kBar`，则清除字段的值和 oneof 分支。`has_bar()` 将返回 `false`，`bar()` 将返回默认值，`example_name_case()` 将返回 `EXAMPLE_NAME_NOT_SET`。

### oneof 嵌入消息字段 {#oneof-embedded}

给定消息类型：

```proto
message Bar {}
```

对于以下 [oneof](#oneof) 字段定义：

```proto
oneof example_name {
    Bar bar = 1;
    ...
}
```

编译器将生成以下访问器方法：

-   `bool has_bar() const`：如果 oneof 分支为 `kBar`，返回 true。
-   `const Bar& bar() const`：如果 oneof 分支为 `kBar`，返回字段的当前值；否则返回一个没有任何字段被设置的 Bar（可能是 `Bar::default_instance()`）。
-   `Bar* mutable_bar()`：
    -   如果同一 oneof 中的任何其他 oneof 字段已设置，则调用 `clear_example_name()`。
    -   把 oneof 分支设置为 `kBar`，并返回指向存储字段值的可变 Bar 对象的指针。如果调用前 oneof 分支不是 `kBar`，则返回的 Bar 将没有任何字段被设置（即它与新建分配的 Bar 完全相同）。
    -   调用此方法后，`has_bar()` 将返回 `true`，`bar()` 将返回同一个 `Bar` 实例的引用，`example_name_case()` 将返回 `kBar`。
-   `void clear_bar()`：
    -   如果 oneof 分支不是 `kBar`，则不会有任何改变。
    -   如果 oneof 分支等于 `kBar`，则释放字段并清除 oneof 分支。`has_bar()` 将返回 `false`，`bar()` 将返回默认值，`example_name_case()` 将返回 `EXAMPLE_NAME_NOT_SET`。
-   `void set_allocated_bar(Bar* bar)`：
    -   调用 `clear_example_name()`。
    -   如果 `Bar` 指针不是 `NULL`：把 `Bar` 对象设置给该字段，并把 oneof 分支设置为 `kBar`。消息取得所分配 `Bar` 对象的所有权，has_bar() 将返回 true，`example_name_case()` 将返回 `kBar`。
    -   如果指针为 `NULL`，`has_bar()` 将返回 `false`，`example_name_case()` 将返回 `EXAMPLE_NAME_NOT_SET`。（其行为类似于调用 `clear_example_name()`）
-   `Bar* release_bar()`：
    -   如果 oneof 分支不是 `kBar`，返回 `NULL`。
    -   如果 oneof 分支是 `kBar`，则清除 oneof 分支，释放字段的所有权，并返回 `Bar` 对象的指针。调用此方法后，调用者取得所分配 `Bar` 对象的所有权，`has_bar()` 将返回 `false`，`bar()` 将返回默认值，`example_name_case()` 将返回 `EXAMPLE_NAME_NOT_SET`。

### map 字段 {#map}

对于以下 map 字段定义：

```proto
map<int32, int32> weight = 1;
```

编译器将生成以下访问器方法：

-   `const google::protobuf::Map<int32, int32>& weight();`：返回一个不可变的 `Map`。
-   `google::protobuf::Map<int32, int32>* mutable_weight();`：返回一个可变的 `Map`。

[`google::protobuf::Map`](/reference/cpp/api-docs/google.protobuf.map) 是 Protobuf 中用来存储 map 字段的一种特殊容器类型。从下面的接口可以看出，它使用了 `std::map` 和 `std::unordered_map` 方法的一个常用子集。

{{% alert title="Note" color="note" %}} 这些映射是无序的。{{% /alert %}}

```cpp
template<typename Key, typename T> {
class Map {
  // 成员类型
  typedef Key key_type;
  typedef T mapped_type;
  typedef MapPair< Key, T > value_type;

  // 迭代器
  iterator begin();
  const_iterator begin() const;
  const_iterator cbegin() const;
  iterator end();
  const_iterator end() const;
  const_iterator cend() const;
  // 容量
  int size() const;
  bool empty() const;

  // 元素访问
  T& operator[](const Key& key);
  const T& at(const Key& key) const;
  T& at(const Key& key);

  // 查找
  bool contains(const Key& key) const;
  int count(const Key& key) const;
  const_iterator find(const Key& key) const;
  iterator find(const Key& key);

  // 修改器
  pair<iterator, bool> insert(const value_type& value);
  template<class InputIt>
  void insert(InputIt first, InputIt last);
  size_type erase(const Key& Key);
  iterator erase(const_iterator pos);
  iterator erase(const_iterator first, const_iterator last);
  void clear();

  // 拷贝
  Map(const Map& other);
  Map& operator=(const Map& other);
}
```

添加数据最简单的方式是使用普通的 map 语法，例如：

```cpp
std::unique_ptr<ProtoName> my_enclosing_proto(new ProtoName);
(*my_enclosing_proto->mutable_weight())[my_key] = my_value;
```

`pair<iterator, bool> insert(const value_type& value)` 会隐式导致对 `value_type` 实例的深拷贝。向 `google::protobuf::Map` 插入新值最高效的方式如下：

```cpp
T& operator[](const Key& key): map[new_key] = new_mapped;
```

#### 将 `google::protobuf::Map` 与标准 map 配合使用 {#protobuf-map}

`google::protobuf::Map` 支持与 `std::map` 和 `std::unordered_map` 相同的迭代器 API。如果不想直接使用 `google::protobuf::Map`，可以按如下方式把 `google::protobuf::Map` 转换为标准 map：

```cpp
std::map<int32, int32> standard_map(message.weight().begin(),
                                    message.weight().end());
```

注意，这会对整个 map 执行深拷贝。

也可以按如下方式从标准 map 构造一个 `google::protobuf::Map`：

```cpp
google::protobuf::Map<int32, int32> weight(standard_map.begin(), standard_map.end());
```

#### 解析未知值 {#parsing-unknown}

在线路格式中，.proto map 等价于：每个键（key）/值（value）对对应一个映射条目（map entry）消息，而 map 本身则是 map entry 的 repeated 字段。与普通消息类型一样，解析出的 map entry 消息也可能含有未知字段：例如，在定义为 `map<int32, string>` 的 map 中出现 `int64` 类型的字段。

如果 map entry 消息的线路格式中存在未知字段，它们将被丢弃。

如果 map entry 消息的线路格式中存在未知枚举值，proto2、proto3 和版次的处理方式各不相同。在 proto2 中，整个 map entry 消息会被放入包含它的消息的未知字段集合中。在 proto3 中，它会作为一个已知枚举值放入 map 字段。对于版次，默认行为与 proto3 一致；如果 `features.enum_type` 被设置为 `CLOSED`，则行为与 proto2 一致。

## Any {#any}

给定如下 [`Any`](/programming-guides/proto3#any) 字段：

```proto
import "google/protobuf/any.proto";

message ErrorStatus {
  string message = 1;
  google.protobuf.Any details = 2;
}
```

在我们的生成代码中，`details` 字段的 getter 返回一个 `google::protobuf::Any` 实例。它提供以下特殊方法来打包（pack）和解包（unpack）`Any` 的值：

```cpp
class Any {
 public:
  // 使用默认类型 URL 前缀“type.googleapis.com”把给定消息打包进此 Any。如果消息序列化失败则返回 false。
  bool PackFrom(const google::protobuf::Message& message);

  // 使用给定的类型 URL 前缀把给定消息打包进此 Any。如果消息序列化失败则返回 false。
  bool PackFrom(const google::protobuf::Message& message,
                ::absl::string_view type_url_prefix);

  // 把此 Any 解包为 Message。如果此 Any 表示的是其他 protobuf 类型或解析失败，则返回 false。
  bool UnpackTo(google::protobuf::Message* message) const;

  // 如果此 Any 表示给定的 protobuf 类型，则返回 true。
  template<typename T> bool Is() const;
}
```

## oneof {#oneof}

给定如下 oneof 定义：

```proto
oneof example_name {
    int32 foo_int = 4;
    string foo_string = 9;
    ...
}
```

编译器将生成以下 C++ 枚举类型：

```cpp
enum ExampleNameCase {
  kFooInt = 4,
  kFooString = 9,
  EXAMPLE_NAME_NOT_SET = 0
}
```

此外，它还会生成以下方法：

-   `ExampleNameCase example_name_case() const`：返回指示哪个字段被设置的枚举。如果它们都没有被设置，则返回 `EXAMPLE_NAME_NOT_SET`。
-   `void clear_example_name()`：如果已设置的 oneof 字段使用指针（Message 或 String），则释放该对象，并把 oneof 分支设置为 `EXAMPLE_NAME_NOT_SET`。

## 枚举 {#enum}

**注意：** 自 2024 版次起，在某些特性（feature）设置下可能会生成 `string_view` API。有关此主题的更多信息，请参见[枚举名称辅助函数](/reference/cpp/string-view#enum-name)。

给定如下枚举定义：

```proto
enum Foo {
  VALUE_A = 0;
  VALUE_B = 5;
  VALUE_C = 1234;
}
```

Protobuf 编译器将生成一个名为 `Foo` 的 C++ 枚举类型，其值集合与原定义相同。此外，编译器还会生成以下函数：

-   `const EnumDescriptor* Foo_descriptor()`：返回该类型的描述符，其中包含此枚举类型定义了哪些值的信息。
-   `bool Foo_IsValid(int value)`：如果给定的数值与 `Foo` 定义的某个值匹配，返回 `true`。在上面的示例中，如果输入是 0、5 或 1234，它将返回 `true`。
-   `const string& Foo_Name(int value)`：返回给定数值对应的名称。如果不存在这样的值，则返回空字符串。如果多个值具有此数值，则返回最先定义的那个。在上面的示例中，`Foo_Name(5)` 将返回 `"VALUE_B"`。
-   `bool Foo_Parse(::absl::string_view name, Foo* value)`：如果 `name` 是此枚举的有效值名称，则把该值赋给 `value` 并返回 true；否则返回 false。在上面的示例中，`Foo_Parse("VALUE_C", &some_foo)` 将返回 true 并把 `some_foo` 设置为 1234。
-   `const Foo Foo_MIN`：枚举的最小有效值（示例中为 VALUE_A）。
-   `const Foo Foo_MAX`：枚举的最大有效值（示例中为 VALUE_C）。
-   `const int Foo_ARRAYSIZE`：始终定义为 `Foo_MAX + 1`。

**把整数强制转换为 proto2 枚举时要当心。** 如果把整数强制转换为 proto2 枚举值，该整数*必须*是该枚举的有效值之一，否则结果可能是未定义的。如果拿不准，请使用生成的 `Foo_IsValid()` 函数来测试该转换是否有效。把 proto2 消息的枚举类型字段设置为无效值可能导致断言失败。如果在解析 proto2 消息时读取到无效的枚举值，它将被视为[未知字段](/reference/cpp/api-docs/google.protobuf.unknown_field_set)。这些语义在 proto3 中已经改变：只要整数能放入 int32，把任何整数强制转换为 proto3 枚举值都是安全的。解析 proto3 消息时，无效的枚举值也会被保留，并由枚举字段访问器返回。

**在 switch 语句中使用 proto3 和版次枚举时要当心。** proto3 和版次枚举是开放式枚举（open enum）类型，可能存在超出已指定符号范围的值。（版次枚举可以使用 [`enum_type`](/editions/features#enum_type) 特性设置为封闭式枚举。）对于开放式枚举类型，无法识别的枚举值会在解析消息时被保留，并由枚举字段访问器返回。对开放式枚举使用没有 default 分支的 switch 语句将无法覆盖所有情况，即使列出了所有已知字段。这可能导致意外行为，包括数据损坏和运行时崩溃。**务必添加 default 分支，或者在 switch 之外显式调用 `Foo_IsValid(int)` 来处理未知枚举值。**

可以在消息类型内部定义枚举。在这种情况下，Protobuf 编译器生成的代码会让枚举类型看起来像是声明为嵌套在消息的类中。`Foo_descriptor()` 和 `Foo_IsValid()` 函数会被声明为静态方法。实际上，枚举类型本身及其值是以经名字修饰（mangled）的名称在全局作用域中声明的，然后通过一个 `typedef` 和一系列常量定义导入到类的作用域中。这样做只是为了绕开声明顺序的问题。不要依赖这些经名字修饰的顶层名称；请当作枚举真的嵌套在消息类中来使用。

### Abseil flag 支持 {#absl-flags-enums}

生成的枚举值原生支持 Abseil 的 flag 解析/反解析逻辑。它们可以用作 `ABSL_FLAG` 声明的类型。

flag 解析器同时支持名称和数字。名称在没有歧义时可以使用小写。无效的名称/数字会导致解析失败。

## 扩展（仅限 proto2 与版次） {#extension}

给定一个带有扩展区间（extension range）的消息：

```proto
message Foo {
  extensions 100 to 199;
}
```

Protobuf 编译器会为 `Foo` 生成一些额外的方法：`HasExtension()`、`ExtensionSize()`、`ClearExtension()`、`GetExtension()`、`SetExtension()`、`MutableExtension()`、`AddExtension()`、`SetAllocatedExtension()` 和 `ReleaseExtension()`。这些方法中的每一个都把一个扩展标识符（extension identifier，本节后文描述）作为其第一个参数，用于标识一个扩展字段。其余参数和返回值，与为类型与该扩展标识符相同的普通（非扩展）字段所生成的对应访问器方法的参数和返回值完全相同。（`GetExtension()` 对应没有特殊前缀的那些访问器。）

给定如下扩展定义：

```proto
extend Foo {
  optional int32 bar = 123;
  repeated int32 repeated_bar = 124;
  optional Bar message_bar = 125;
}
```

对于单数扩展字段 `bar`，Protobuf 编译器会生成一个名为 `bar` 的“扩展标识符”，你可以将它与 `Foo` 的扩展访问器搭配使用来访问该扩展，如下所示：

```cpp
Foo foo;
assert(!foo.HasExtension(bar));
foo.SetExtension(bar, 1);
assert(foo.HasExtension(bar));
assert(foo.GetExtension(bar) == 1);
foo.ClearExtension(bar);
assert(!foo.HasExtension(bar));
```

对于消息扩展字段 `message_bar`，如果字段未设置，`foo.GetExtension(message_bar)` 会返回一个没有任何字段被设置的 `Bar`（可能是 `Bar::default_instance()`）。

类似地，对于 repeated 扩展字段 `repeated_bar`，编译器会生成一个名为 `repeated_bar` 的扩展标识符，你也可以将它与 `Foo` 的扩展访问器搭配使用：

```cpp
Foo foo;
for (int i = 0; i < kSize; ++i) {
  foo.AddExtension(repeated_bar, i)
}
assert(foo.ExtensionSize(repeated_bar) == kSize)
for (int i = 0; i < kSize; ++i) {
  assert(foo.GetExtension(repeated_bar, i) == i)
}
```

（扩展标识符的具体实现相当复杂，涉及对模板的巧妙运用——不过，无需了解扩展标识符的工作原理，你也可以使用它们。）

扩展可以声明为嵌套在另一个类型内部。例如，一种常见模式是像这样：

```proto
message Baz {
  extend Foo {
    optional Baz foo_ext = 124;
  }
}
```

在这种情况下，扩展标识符 `foo_ext` 被声明为嵌套在 `Baz` 内部。它可以按如下方式使用：

```cpp
Foo foo;
Baz* baz = foo.MutableExtension(Baz::foo_ext);
FillInMyBaz(baz);
```

## Arena 分配 {#arena}

Arena 分配是一项仅限 C++ 的特性，帮助你在使用 Protobuf 时优化内存使用并提升性能。在 `.proto` 中启用 arena 分配，会给你的 C++ 生成代码添加用于处理 arena 的额外代码。你可以在 [Arena 分配指南](/reference/cpp/arenas)中了解有关 arena 分配 API 的更多信息。

## 服务 {#service}

如果 `.proto` 文件包含以下行：

```proto
option cc_generic_services = true;
```

那么 Protobuf 编译器将按照本节的描述，基于文件中的服务（service）定义生成代码。但是，生成的代码可能并不理想，因为它不与任何特定的远程过程调用（RPC）系统绑定，因此相比针对单一系统定制的代码需要更多的间接层。如果你*不*希望生成这些代码，请在文件中添加以下行：

```proto
option cc_generic_services = false;
```

如果上述两行都未给出，该选项默认为 `false`，因为通用服务已弃用（deprecated）。（注意，在 2.4.0 之前，该选项默认为 `true`。）弃用背后的原因请参见[通用服务的设计决策](/design-decisions/insertion-points-and-generic-services#generic-services)。

基于 `.proto` 语言服务定义的 RPC 系统应当提供[插件（plugin）](/reference/cpp/api-docs/google.protobuf.compiler.plugin.pb)来生成适合该系统的代码。这些插件很可能要求禁用抽象服务，以便它们能够生成自己的同名类。

本节余下部分描述在启用抽象服务时 Protobuf 编译器生成的内容。

### 接口

给定如下服务定义：

```proto
service Foo {
  rpc Bar(FooRequest) returns(FooResponse);
}
```

Protobuf 编译器将生成一个类 `Foo` 来表示此服务。`Foo` 会为服务定义中定义的每个方法提供一个虚方法。在本例中，方法 `Bar` 的定义如下：

```cpp
virtual void Bar(RpcController* controller, const FooRequest* request,
                 FooResponse* response, Closure* done);
```

这些参数与 `Service::CallMethod()` 的参数等价，只是 `method` 参数是隐含的，而 `request` 和 `response` 指定了它们的确切类型。

这些生成的方法是虚方法，但不是纯虚方法。默认实现只是调用 `controller->SetFailed()` 并附带一条指示该方法未实现的错误消息，然后调用 `done` 回调。在实现你自己的服务时，你必须继承这个生成的服务类，并按需实现其方法。

`Foo` 继承自 `Service` 接口。Protobuf 编译器会按如下方式自动生成 `Service` 各方法的实现：

-   `GetDescriptor`：返回该服务的 [`ServiceDescriptor`](/reference/cpp/api-docs/google.protobuf.descriptor#ServiceDescriptor)。
-   `CallMethod`：根据提供的方法描述符确定正在调用的是哪个方法并直接调用它，把请求和响应消息对象向下转型（down-cast）为正确的类型。
-   `GetRequestPrototype` 和 `GetResponsePrototype`：返回给定方法所对应的正确类型的请求或响应的默认实例。

还会生成以下静态方法：

-   `static ServiceDescriptor descriptor()`：返回该类型的描述符，其中包含此服务有哪些方法以及它们的输入和输出类型的信息。

### 存根 {#stub}

Protobuf 编译器还会为每个服务接口生成一个“存根”（stub）实现，供希望向实现该服务的服务器发送请求的客户端使用。对于 `Foo` 服务（前文已描述），将会定义存根实现 `Foo_Stub`。与嵌套消息类型一样，这里使用了 `typedef`，因此 `Foo_Stub` 也可以被称为 `Foo::Stub`。

`Foo_Stub` 是 `Foo` 的子类，它还实现了以下方法：

-   `Foo_Stub(RpcChannel* channel)`：构造一个新的存根，在给定的通道（channel）上发送请求。
-   `Foo_Stub(RpcChannel* channel, ChannelOwnership ownership)`：构造一个新的存根，在给定的通道上发送请求，并可能拥有该通道。如果 `ownership` 为 `Service::STUB_OWNS_CHANNEL`，那么当存根对象被删除时，它也会删除该通道。
-   `RpcChannel* channel()`：返回此存根的通道，即传递给构造函数的那个通道。

此外，该存根把服务的每个方法都实现为围绕通道的包装器。调用其中一个方法只是简单地调用 `channel->CallMethod()`。

Protobuf 库本身不包含 RPC 实现。不过，它包含了把生成的服务类接入你所选的任意 RPC 实现所需的全部工具。你只需提供 [`RpcChannel`](/reference/cpp/api-docs/google.protobuf.service#RpcChannel) 和 [`RpcController`](/reference/cpp/api-docs/google.protobuf.service#RpcController) 的实现。更多信息请参见 [`service.h`](/reference/cpp/api-docs/google.protobuf.service) 的文档。

## 插件插入点 {#plugins}

希望扩展 C++ 代码生成器（code generator）输出的[代码生成器插件](/reference/cpp/api-docs/google.protobuf.compiler.plugin.pb)，可以使用给定的插入点名称插入以下类型的代码。除非另有说明，每个插入点都会同时出现在 `.pb.cc` 文件和 `.pb.h` 文件中。

-   `includes`：包含指令（include directives）。
-   `namespace_scope`：属于文件的包/命名空间但不属于任何特定类的声明。出现在所有其他命名空间作用域代码之后。
-   `global_scope`：属于顶层、位于文件命名空间之外的声明。出现在文件的最末尾。
-   `class_scope:TYPENAME`：属于某个消息类的成员声明。`TYPENAME` 是完整的 proto 名称，例如 `package.MessageType`。出现在类中所有其他公开声明之后。此插入点仅出现在 `.pb.h` 文件中。

不要生成依赖标准代码生成器所声明的私有类成员的代码，因为这些实现细节在 Protobuf 的未来版本中可能会改变。
