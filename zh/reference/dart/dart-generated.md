+++
title = "Dart 生成代码"
weight = 580
linkTitle = "生成代码"
description = "描述 Protobuf 编译器针对任意给定协议定义所生成的 Dart 代码。"
type = "docs"
source_url = "https://protobuf.dev/reference/dart/dart-generated/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

proto2、proto3 与版次（editions）生成代码之间的任何差异都会重点标出。请注意，这些差异存在于本文档所描述的生成代码（generated code）中，而非基础 API——基础 API 在所有版本中都是相同的。阅读本文档之前，请先阅读 [proto2 语言指南](/programming-guides/proto2)、[proto3 语言指南](/programming-guides/proto3)或[版次语言指南](/programming-guides/editions)。

## 编译器调用 {#invocation}

Protobuf 编译器需要一个[用于生成 Dart 代码的插件（plugin）](https://github.com/dart-lang/dart-protoc-plugin)。按照[说明](https://github.com/dart-lang/dart-protoc-plugin#how-to-build-and-use)安装后，会得到一个 `protoc-gen-dart` 二进制文件，`protoc` 在带有 `--dart_out` 命令行标志调用时会使用它。`--dart_out` 标志告诉编译器把 Dart 源文件写到哪里。对于一个 `.proto` 文件输入，编译器除其他文件外还会产出一个 `.pb.dart` 文件。

`.pb.dart` 文件名的确定方式是：取 `.proto` 文件的名称并做两处修改：

-   扩展名（`.proto`）被替换为 `.pb.dart`。例如，名为 `foo.proto` 的文件会生成名为 `foo.pb.dart` 的输出文件。
-   proto 路径（通过 `--proto_path` 或 `-I` 命令行标志指定）被替换为输出路径（通过 `--dart_out` 标志指定）。

例如，当你按如下方式调用编译器时：

```shell
protoc --proto_path=src --dart_out=build/gen src/foo.proto src/bar/baz.proto
```

编译器将读取 `src/foo.proto` 和 `src/bar/baz.proto` 这两个文件，并生成 `build/gen/foo.pb.dart` 和 `build/gen/bar/baz.pb.dart`。如有必要，编译器会自动创建 `build/gen/bar` 目录，但*不会*创建 `build` 或 `build/gen`；这两个目录必须已经存在。

## 消息 {#message}

给定一个简单的消息（message）声明：

```proto
message Foo {}
```

Protobuf 编译器会生成一个名为 `Foo` 的类，它继承自 `GeneratedMessage` 类。

`GeneratedMessage` 类定义了一些方法，让你能够检查、操作、读取或写入整个消息。除这些方法之外，`Foo` 类还定义了以下方法和构造函数：

-   `Foo()`：默认构造函数。创建一个所有单数字段（singular field）均未设置、repeated 字段均为空的实例。
-   `Foo.fromBuffer(...)`：从表示该消息的已序列化 Protobuf 数据创建一个 `Foo`。
-   `Foo.fromJson(...)`：从对该消息进行 JSON 编码的字符串创建一个 `Foo`。
-   `Foo clone()`：创建消息中各字段的深拷贝。
-   `Foo copyWith(void Function(Foo) updates)`：为本消息创建一个可写副本，把 `updates` 应用到该副本上，并在返回前将副本标记为只读。
-   `static Foo create()`：用于创建单个 `Foo` 的工厂函数。
-   `static PbList<Foo> createRepeated()`：用于创建一个 List 的工厂函数，该 List 实现了由 `Foo` 元素组成的可变 repeated 字段。
-   `static Foo getDefault()`：返回 `Foo` 的单例实例，它与新建构造的 Foo 实例完全相同（因此所有单数字段均未设置，且所有 repeated 字段均为空）。

### 嵌套类型

消息可以声明在另一个消息内部。例如：

```proto
message Foo {
  message Bar {
  }
}
```

在这种情况下，编译器会生成两个类：`Foo` 和 `Foo_Bar`。

## 字段

除上一节描述的方法之外，Protobuf 编译器还会为 `.proto` 文件中消息内定义的每个字段（field）生成访问器（accessor）方法。

请注意，生成的名称一律采用驼峰命名法（camel-case），即使 `.proto` 文件中的字段名（field name）使用的是小写加下划线的形式（[理应如此](/programming-guides/style)）。大小写转换规则如下：

1.  名称中的每个下划线都会被移除，其后的字母转为大写。
2.  如果该名称会附加前缀（例如 \"has\"），则首字母转为大写；否则转为小写。

因此，对于字段 `foo_bar_baz`，getter 会变成 `get fooBarBaz`，而以 `has` 为前缀的方法则是 `hasFooBarBaz`。

### 单数原始类型字段

在 Dart 实现中，所有字段都具有[显式存在性（explicit presence）](/programming-guides/field_presence#presence-proto2)。

对于以下字段定义：

```proto
int32 foo = 1;
```

编译器将在消息类中生成以下访问器方法：

-   `int get foo`：返回字段的当前值。如果字段未设置，则返回默认值（default value）。
-   `bool hasFoo()`：如果字段已设置，则返回 `true`。
-   `set foo(int value)`：设置字段的值。调用之后，`hasFoo()` 将返回 `true`，`get foo` 将返回 `value`。
-   `void clearFoo()`：清除字段的值。调用之后，`hasFoo()` 将返回 `false`，`get foo` 将返回默认值。

    {{% alert title="Note" color="note" %}} 由于 Dart proto3 实现的一个特殊之处，即使配置了隐式存在性（implicit presence），以下方法也会被生成。{{% /alert %}}

-   `bool hasFoo()`：如果字段已设置，则返回 `true`。

    {{% alert title="Note" color="note" %}} 如果该 proto 是由另一种支持隐式存在性的语言（例如 Java）序列化的，那么这个值实际上并不可信。尽管 Dart 会追踪存在性，但其他语言不会；对一个值为零的隐式存在性字段进行往返（round-trip）处理后，从 Dart 的视角看它会“消失”。
    {{% /alert %}}

-   `void clearFoo()`：清除字段的值。调用之后，`hasFoo()` 将返回 `false`，`get foo` 将返回默认值。

对于其他简单字段类型，会根据[标量（scalar）值类型表](/programming-guides/editions#scalar)选择相应的 Dart 类型。对于消息和枚举类型，值类型会被替换为相应的消息类或枚举类。

### 单数消息字段 {#singular-message}

给定消息类型：

```proto
message Bar {}
```

对于包含 `Bar` 字段的消息：

```proto
// proto2
message Baz {
  optional Bar bar = 1;
  // 如果使用 required 而不是 optional，生成的代码结果相同。
}

// proto3 与版次
message Baz {
  Bar bar = 1;
}
```

编译器将在消息类中生成以下访问器方法：

-   `Bar get bar`：返回字段的当前值。如果字段未设置，则返回默认值。
-   `set bar(Bar value)`：设置字段的值。调用之后，`hasBar()` 将返回 `true`，`get bar` 将返回 `value`。
-   `bool hasBar()`：如果字段已设置，则返回 `true`。
-   `void clearBar()`：清除字段的值。调用之后，`hasBar()` 将返回 `false`，`get bar` 将返回默认值。
-   `Bar ensureBar()`：如果 `hasBar()` 返回 `false`，就把 `bar` 设置为空实例，然后返回 `bar` 的值。调用之后，`hasBar()` 将返回 `true`。

### repeated 字段

对于以下字段定义：

```proto
repeated int32 foo = 1;
```

编译器将生成：

-   `List<int> get foo`：返回该字段底层的列表。如果字段未设置，则返回一个空列表。对列表的修改会反映在该字段上。

### Int64 字段

对于以下字段定义：

```proto
int64 bar = 1;
```

编译器将生成：

-   `Int64 get bar`：返回一个包含字段值的 `Int64` 对象。

请注意，`Int64` 并不是 Dart 核心库的内置类型。要使用这些对象，你可能需要导入 Dart 的 `fixnum` 库：

```dart
import 'package:fixnum/fixnum.dart';
```

### map 字段

给定如下 [`map`](/programming-guides/editions#maps) 字段定义：

```proto
map<int32, int32> map_field = 1;
```

编译器将生成以下 getter：

-   `Map<int, int> get mapField`：返回该字段底层的 Dart map。如果字段未设置，则返回一个空 map。对 map 的修改会反映在该字段上。

### Any

给定如下 [`Any`](/programming-guides/editions#any) 字段：

```proto
import "google/protobuf/any.proto";

message ErrorStatus {
  string message = 1;
  google.protobuf.Any details = 2;
}
```

在我们的生成代码中，`details` 字段的 getter 会返回一个 `com.google.protobuf.Any` 实例。该实例提供以下特殊方法，用于打包（pack）和解包（unpack）`Any` 的值：

```dart
    /// 把 [value] 中的消息解包到 [instance] 中。
    ///
    /// 如果 [typeUrl] 与 [instance] 的类型不对应，则抛出 [InvalidProtocolBufferException]。
    ///
    /// 典型用法是 `any.unpackInto(new Message())`。
    ///
    /// 返回 [instance]。
    T unpackInto<T extends GeneratedMessage>(T instance,
        {ExtensionRegistry extensionRegistry = ExtensionRegistry.EMPTY});

    /// 如果已编码的消息与 [instance] 的类型匹配，则返回 `true`。
    ///
    /// 可与默认实例一起使用：
    /// `any.canUnpackInto(Message.getDefault())`
    bool canUnpackInto(GeneratedMessage instance);

    /// 创建一个编码了 [message] 的新 [Any]。
    ///
    /// [typeUrl] 将为 [typeUrlPrefix]/`fullName`，其中 `fullName` 是
    /// [message] 类型的全限定名。
    static Any pack(GeneratedMessage message,
        {String typeUrlPrefix = 'type.googleapis.com'});
```

### Oneof

给定如下 [`oneof`](/programming-guides/editions#oneof) 定义：

```proto
message Foo {
  oneof test {
    string name = 1;
    SubMessage sub_message = 2;
  }
}
```

编译器会生成以下 Dart 枚举类型：

```dart
 enum Foo_Test { name, subMessage, notSet }
```

此外，它还会生成以下方法：

-   `Foo_Test whichTest()`：返回指示已设置哪个字段的枚举值；如果没有任何字段被设置，则返回 `Foo_Test.notSet`。
-   `void clearTest()`：清除当前已设置的 oneof 字段的值（如果有的话），并把 oneof 分支（case）设置为 `Foo_Test.notSet`。

对于 oneof 定义内的每个字段，都会生成常规的字段访问器方法。以 `name` 为例：

-   `String get name`：如果 oneof 分支为 `Foo_Test.name`，则返回字段的当前值；否则返回默认值。
-   `set name(String value)`：设置字段的值，并把 oneof 分支设置为 `Foo_Test.name`。调用之后，`get name` 将返回 `value`，`whichTest()` 将返回 `Foo_Test.name`。
-   `void clearName()`：如果 oneof 分支不是 `Foo_Test.name`，则不会有任何改变；否则清除字段的值。调用之后，`get name` 将返回默认值，`whichTest()` 将返回 `Foo_Test.notSet`。

### 枚举 {#enum}

给定如下枚举定义：

```proto
enum Color {
  COLOR_UNSPECIFIED = 0;
  COLOR_RED = 1;
  COLOR_GREEN = 2;
  COLOR_BLUE = 3;
}
```

Protobuf 编译器会生成一个名为 `Color` 的类，它继承自 `ProtobufEnum` 类。该类会为这四个枚举值各包含一个 `static const Color`，还会包含一个含有这些值的 `static const List<Color>`。

```dart
static const List<Color> values = <Color> [
  COLOR_UNSPECIFIED,
  COLOR_RED,
  COLOR_GREEN,
  COLOR_BLUE,
];
```

该类还会包含以下方法：

-   `static Color? valueOf(int value)`：返回与给定数值对应的 `Color`。

每个枚举值都具有以下属性：

-   `name`：枚举的名称，如 .proto 文件中所指定。
-   `value`：枚举的整数值，如 .proto 文件中所指定。

请注意，`.proto` 语言允许多个枚举符号拥有相同的数值。具有相同数值的符号互为同义词。例如：

```proto
enum Foo {
  BAR = 0;
  BAZ = 0;
}
```

在这种情况下，`BAZ` 是 `BAR` 的同义词，将按如下方式定义：

```dart
static const Foo BAZ = BAR;
```

枚举也可以嵌套定义在消息类型内部。例如，给定如下枚举定义：

```proto
message Bar {
  enum Color {
    COLOR_UNSPECIFIED = 0;
    COLOR_RED = 1;
    COLOR_GREEN = 2;
    COLOR_BLUE = 3;
  }
}
```

Protobuf 编译器会生成一个继承自 `GeneratedMessage` 的 `Bar` 类，以及一个继承自 `ProtobufEnum` 的 `Bar_Color` 类。

## 扩展（proto3 中不可用） {#extension}

给定一个 `foo_test.proto` 文件，其中包含一个带有[扩展区间（extension range）](/programming-guides/editions#extensions)的消息和一个顶层扩展（extension）定义：

```proto
message Foo {
  extensions 100 to 199;
}

extend Foo {
  optional int32 bar = 101;
}
```

除 `Foo` 类之外，Protobuf 编译器还会生成一个 `Foo_test` 类；该类会为文件中的每个扩展字段包含一个 `static Extension`，还会包含一个把所有扩展注册到 `ExtensionRegistry` 的方法：

-   `static final Extension bar`
-   `static void registerAllExtensions(ExtensionRegistry registry)`：在给定的注册表中注册所有已定义的扩展。

`Foo` 的扩展访问器可按如下方式使用：

```dart
Foo foo = Foo();
foo.setExtension(Foo_test.bar, 1);
assert(foo.hasExtension(Foo_test.bar));
assert(foo.getExtension(Foo_test.bar)) == 1);
```

扩展也可以嵌套声明在另一个消息内部：

```proto
message Baz {
  extend Foo {
    int32 bar = 124;
  }
}
```

在这种情况下，扩展 `bar` 会改为声明为 `Baz` 类的静态成员。

解析可能带有扩展的消息时，你必须提供一个 `ExtensionRegistry`，并在其中注册你希望能够解析的所有扩展。否则，这些扩展只会被当作未知字段（unknown fields）处理。例如：

```dart
ExtensionRegistry registry = ExtensionRegistry();
registry.add(Baz.bar);
Foo foo = Foo.fromBuffer(input, registry);
```

如果你已经有一个带有未知字段的已解析消息，可以在 `ExtensionRegistry` 上使用 `reparseMessage` 来重新解析该消息。如果未知字段集合中包含注册表中已存在的扩展，这些扩展会被解析出来，并从未知字段集合中移除。消息中已经存在的扩展则会被保留。

```dart
Foo foo = Foo.fromBuffer(input);
ExtensionRegistry registry = ExtensionRegistry();
registry.add(Baz.bar);
Foo reparsed = registry.reparseMessage(foo);
```

请注意，这种获取扩展的方式总体开销更大。因此，在执行 `GeneratedMessage.fromBuffer` 时，我们建议尽可能使用带有全部所需扩展的 `ExtensionRegistry`。

## 服务 {#service}

给定一个服务（service）定义：

```proto
service Foo {
  rpc Bar(FooRequest) returns(FooResponse);
}
```

可以使用 \`grpc\` 选项（例如 `--dart_out=grpc:output_folder`）来调用 Protobuf 编译器，此时它会生成支持 [gRPC](//www.grpc.io/) 的代码。详情请参阅 [gRPC Dart 快速开始指南](https://grpc.io/docs/quickstart/dart.html)。
