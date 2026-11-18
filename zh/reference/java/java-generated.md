+++
title = "Java 生成代码指南"
weight = 650
linkTitle = "生成代码指南"
description = "详细描述 Protobuf 编译器针对任意给定协议定义所生成的 Java 代码。"
type = "docs"
source_url = "https://protobuf.dev/reference/java/java-generated/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

proto2、proto3 与版次（edition）生成代码之间的任何差异都会重点标出——请注意，这些差异存在于本文档所描述的生成代码（generated code）中，而非基础消息（message）类/接口——后者在所有版本（version）中都是相同的。阅读本文档之前，请先阅读 [proto2 语言指南](/programming-guides/proto2)、[proto3 语言指南](/programming-guides/proto3)和/或 [版次语言指南](/programming-guides/editions)。

请注意，除非另有说明，否则任何 Java Protobuf 方法都不接受也不返回 null。

## 编译器调用 {#invocation}

使用 `--java_out=` 命令行标志调用时，Protobuf 编译器会生成 Java 输出。`--java_out=` 选项的参数是你希望编译器写入 Java 输出的目录。编译器会为每个输入的 `.proto` 文件创建一个包装用的 `.java` 文件，其中包含一个表示该 `.proto` 文件本身的 Java 类。

如果 `.proto` 文件包含如下一行：

```proto
option java_multiple_files = true;
```

那么，对于它将为 `.proto` 文件中声明的每个顶层消息、枚举（enum）和服务（service）生成的各个类/枚举，编译器还会分别创建单独的 `.java` 文件。

否则（当 `java_multiple_files` 选项被禁用时——这也是默认情况），上述包装类（wrapper class）还将被用作外部类（outer class），而为 `.proto` 文件中声明的每个顶层消息、枚举和服务生成的各个类/枚举都将嵌套在这个外层包装类之中。这样，编译器只会为整个 `.proto` 文件生成单个 `.java` 文件，并且它在包中会多出一层。

包装类名的选定规则如下：如果 `.proto` 文件包含如下一行：

```proto
option java_outer_classname = "Foo";
```

那么包装类名将为 `Foo`。否则，包装类名通过把 `.proto` 文件的基本名转换为驼峰命名（camel case）来确定。例如，`foo_bar.proto` 会生成类名 `FooBar`。如果文件中存在同名的服务、枚举或消息（包括嵌套类型（nested type）），则会在包装类名后追加“OuterClass”。例如：

-   如果 `foo_bar.proto` 包含一个名为 `FooBar` 的消息，则包装类将生成类名 `FooBarOuterClass`。
-   如果 `foo_bar.proto` 包含一个名为 `FooService` 的服务，并且 `java_outer_classname` 也被设置为字符串 `FooService`，则包装类将生成类名 `FooServiceOuterClass`。

{{% alert title="Note" color="note" %}}如果你使用的是已弃用（deprecated）的 Protobuf API v1，那么无论是否与消息名冲突，都会添加 `OuterClass`。
{{% /alert %}}

除各类嵌套类之外，包装类本身还将具有以下 API（假设包装类名为 `Foo`，由 `foo.proto` 生成）：

```java
public final class Foo {
  private Foo() {}  // 不可实例化。

  /** 返回一个描述 {@code foo.proto} 内容的 FileDescriptor 消息。 */
  public static com.google.protobuf.Descriptors.FileDescriptor getDescriptor();
  /** 把 {@code foo.proto} 中定义的所有扩展添加到给定的注册表。 */
  public static void registerAllExtensions(com.google.protobuf.ExtensionRegistry registry);
  public static void registerAllExtensions(com.google.protobuf.ExtensionRegistryLite registry);

  // （嵌套类从略）
}
```

Java 包名的选定方式如下文 [包](#package) 一节所述。

输出文件的路径由 `--java_out=` 的参数、包名（把其中的 `.` 替换为 `/`）和 `.java` 文件名拼接而成。

举例来说，假设你按如下方式调用编译器：

```shell
protoc --proto_path=src --java_out=build/gen src/foo.proto
```

如果 `foo.proto` 的 Java 包是 `com.example`，它没有启用 `java_multiple_files`，并且其外部类名是 `FooProtos`，那么 Protobuf 编译器将生成文件 `build/gen/com/example/FooProtos.java`。必要时，Protobuf 编译器会自动创建 `build/gen/com` 和 `build/gen/com/example` 目录；但它不会创建 `build/gen` 或 `build`，这两个目录必须已经存在。你可以在一次调用中指定多个 `.proto` 文件；所有输出文件会一次性全部生成。

输出 Java 代码时，Protobuf 编译器直接输出到 JAR 归档文件的功能尤其方便，因为许多 Java 工具都能直接从 JAR 文件读取源代码。要输出到 JAR 文件，只需提供一个以 `.jar` 结尾的输出位置即可。注意，归档中只会放入 Java 源代码；你仍需单独编译它以生成 Java 类文件。

## 包 {#package}

生成的类会被放入一个基于 `java_package` 选项确定的 Java 包中。如果省略该选项，则改用 `package` 声明。

例如，如果 `.proto` 文件包含：

```proto
package foo.bar;
```

那么生成的 Java 类将被放入 Java 包 `foo.bar`。但如果 `.proto` 文件还包含如下 `java_package` 选项：

```proto
package foo.bar;
option java_package = "com.example.foo.bar";
```

那么该类将被放入 `com.example.foo.bar` 包。之所以提供 `java_package` 选项，是因为通常 `.proto` 的 `package` 声明并不会以反向域名开头。

## 消息 {#message}

如果你正在设计新的 Protobuf 模式（schema），请参阅 [Java proto 命名建议](/reference/java/java-proto-names)。

给定如下简单消息声明：

```proto
message Foo {}
```

Protobuf 编译器会生成一个名为 `Foo` 的类，该类实现了 `Message` 接口。该类被声明为 `final`；不允许进一步子类化。`Foo` 继承自 `GeneratedMessage`，但这应被视为实现细节。默认情况下，`Foo` 会用专门化的实现覆写 `GeneratedMessage` 的许多方法，以求最快速度。不过，如果 `.proto` 文件包含如下一行：

```proto
option optimize_for = CODE_SIZE;
```

那么 `Foo` 将只覆写正常运行所必需的最少方法集，其余方法则依赖 `GeneratedMessage` 基于反射（reflection）的实现。这会显著缩小生成代码的体积，但也会降低性能。或者，如果 `.proto` 文件包含：

```proto
option optimize_for = LITE_RUNTIME;
```

那么 `Foo` 将包含所有方法的快速实现，但实现的是 `MessageLite` 接口——它只包含 `Message` 方法的一个子集。特别是，它不支持描述符（descriptor）、嵌套构建器（builder）或反射。不过在这种模式下，生成代码只需链接 `libprotobuf-lite.jar`，而无需链接 `libprotobuf.jar`。“lite” 库比完整库小得多，更适合手机等资源受限的系统。

`Message` 接口定义了一组方法，让你能够检查、操作、读取或写入整个消息。除这些方法之外，`Foo` 类还定义了以下静态方法：

-   `static Foo getDefaultInstance()`：返回 `Foo` 的*单例*实例。该实例的内容与你调用 `Foo.newBuilder().build()` 所得到的结果完全相同（因此所有单数字段（singular field）都未设置，所有可重复字段都为空）。注意，可以把消息的默认实例当作工厂使用，方法是调用它的 `newBuilderForType()` 方法。
-   `static Descriptor getDescriptor()`：返回该类型的描述符。其中包含该类型的信息，包括它拥有哪些字段以及这些字段的类型。它可以与 `Message` 的反射方法（例如 `getField()`）配合使用。
-   `static Foo parseFrom(...)`：从给定数据源解析（parse）出一个 `Foo` 类型的消息并返回它。`Message.Builder` 接口中 `mergeFrom()` 的每个变体都各有一个对应的 `parseFrom` 方法。注意，`parseFrom()` 绝不会抛出 `UninitializedMessageException`；如果要解析的消息缺少 required 字段，它会抛出 `InvalidProtocolBufferException`。这使得它与调用 `Foo.newBuilder().mergeFrom(...).build()` 有细微差别。
-   `static Parser parser()`：返回一个 `Parser` 实例，它实现了各种 `parseFrom()` 方法。
-   `Foo.Builder newBuilder()`：创建一个新的构建器（详见下文）。
-   `Foo.Builder newBuilder(Foo prototype)`：创建一个新的构建器，其中所有字段（field）都初始化为与 `prototype` 中相同的值。由于内嵌消息对象和字符串对象是不可变的，因此它们在原始对象与副本之间共享。

### 构建器 {#builders}

消息对象——例如上文所述 `Foo` 类的实例——是不可变的，就像 Java 的 `String` 一样。要构造消息对象，你需要使用*构建器*。每个消息类都有自己的构建器类——因此在我们 `Foo` 的例子中，Protobuf 编译器会生成一个嵌套类 `Foo.Builder`，可以用它来构建 `Foo`。`Foo.Builder` 实现了 `Message.Builder` 接口。它继承自 `GeneratedMessage.Builder` 类，但同样，这应被视为实现细节。与 `Foo` 一样，`Foo.Builder` 可能依赖 `GeneratedMessage.Builder` 中的通用方法实现；或者在使用 `optimize_for` 选项时，依赖生成的速度快得多的定制代码。你可以通过调用静态方法 `Foo.newBuilder()` 来获得 `Foo.Builder`。

`Foo.Builder` 不定义任何静态方法。它的接口与 `Message.Builder` 接口所定义的完全一致，唯一区别是返回类型更具体：`Foo.Builder` 中修改构建器自身的方法返回 `Foo.Builder` 类型，而 `build()` 返回 `Foo` 类型。

修改构建器内容的方法——包括字段设置器——总是返回对构建器自身的引用（即 `return this;`）。这使得多个方法调用可以链式地写在同一行中。例如：`builder.mergeFrom(obj).setFoo(1).setBar("abc").clearBaz();`

注意，构建器不是线程安全的，因此当多个不同的线程需要修改同一个构建器的内容时，应当使用 Java 同步机制。

### 子构建器 {#sub-builders}

对于包含子消息的消息，编译器还会生成子构建器。这让你可以反复修改深层嵌套的子消息，而无需重新构建它们。例如：

```proto
message Foo {
  int32 val = 1;
  // 其他一些字段。
}

message Bar {
  Foo foo = 1;
  // 其他一些字段。
}

message Baz {
  Bar bar = 1;
  // 其他一些字段。
}
```

如果你已经有一个 `Baz` 消息，并且想修改 `Foo` 中深层嵌套的 `val`，与其写成：

```java
baz = baz.toBuilder().setBar(
    baz.getBar().toBuilder().setFoo(
        baz.getBar().getFoo().toBuilder().setVal(10).build()
    ).build()).build();
```

不如写成：

```java
Baz.Builder builder = baz.toBuilder();
builder.getBarBuilder().getFooBuilder().setVal(10);
baz = builder.build();
```

### 嵌套类型 {#nested}

一个消息可以声明在另一个消息内部。例如：

```proto
message Foo {
  message Bar { }
}
```

在这种情况下，编译器只是把 `Bar` 生成为嵌套在 `Foo` 内部的内部类。

## 字段 {#fields}

除上一节描述的方法之外，Protobuf 编译器还会为 `.proto` 文件中消息内定义的每个字段生成一组访问器（accessor）方法。读取字段值的方法同时定义在消息类及其对应的构建器中；修改值的方法则只定义在构建器中。

注意，方法名始终采用驼峰命名，即使 `.proto` 文件中的字段名（field name）采用带下划线的小写形式（[理应如此](/programming-guides/style)）。大小写转换规则如下：

*   名称中的每个下划线都会被移除，其后的字母转为大写。
*   如果名称会附加前缀（例如 “get”），则首字母转为大写；否则转为小写。
*   方法名中每个数字的最后一位之后的字母转为大写。

因此，字段 `foo_bar_baz` 会变成 `fooBarBaz`；加上 `get` 前缀后则是 `getFooBarBaz`；而 `foo_ba23r_baz` 会变成 `fooBa23RBaz`。

除访问器方法之外，编译器还会为每个字段生成一个整型常量，其值为该字段的字段编号（field number）。常量名是转换为大写形式的字段名再加上 `_FIELD_NUMBER`。例如，给定字段 `int32 foo_bar = 5;`，编译器会生成常量 `public static final int FOO_BAR_FIELD_NUMBER = 5;`。

以下各节按照显式存在性（explicit presence）与隐式存在性（implicit presence）来划分。proto2 具有显式存在性，proto3 默认采用隐式存在性；版次默认为显式存在性，但你可以使用 [`features.field_presence`](/editions/features#field_presence) 覆盖这一默认行为。

<a id="singular-proto2"></a>

### 具有显式存在性的单数字段 {#singular-explicit}

对于以下任意一种字段定义：

```proto
optional int32 foo = 1;
required int32 foo = 1;
```

编译器会在消息类及其构建器中都生成以下访问器方法：

-   `boolean hasFoo()`：如果该字段已设置，则返回 `true`。
-   `int getFoo()`：返回该字段的当前值。如果该字段未设置，则返回默认值（default value）。

编译器只会在消息的构建器中生成以下方法：

-   `Builder setFoo(int value)`：设置该字段的值。调用此方法后，`hasFoo()` 将返回 `true`，`getFoo()` 将返回 `value`。
-   `Builder clearFoo()`：清除该字段的值。调用此方法后，`hasFoo()` 将返回 `false`，`getFoo()` 将返回默认值。

对于其他简单字段类型，对应的 Java 类型按 [标量值类型表](/programming-guides/proto2#scalar) 选择。对于消息和枚举类型，值类型会被替换为相应的消息类或枚举类。

#### 嵌入消息字段 {#embedded-message-proto2}

对于消息类型，`setFoo()` 还接受该消息构建器类型的实例作为参数。这只是个快捷方式，等价于对该构建器调用 `.build()`，然后把结果传给该方法。进一步修改传给 `setFoo` 的子构建器，其改动**不会**反映到消息类的构建器中。消息类的构建器会“接管”该子消息。

如果该字段未设置，`getFoo()` 将返回一个没有任何字段被设置的 Foo 实例（可能就是 `Foo.getDefaultInstance()` 返回的实例）。

此外，编译器还会生成两个访问器方法，让你能够访问消息类型的相关子构建器。以下方法同时生成在消息类及其构建器中：

-   `FooOrBuilder getFooOrBuilder()`：返回该字段的构建器（如果已存在），否则返回该消息。在构建器上调用此方法不会为该字段创建子构建器。

编译器只会在消息的构建器中生成以下方法。

-   `Builder getFooBuilder()`：返回该字段的构建器。

<a id="singular-proto3"></a>

### 具有隐式存在性的单数字段 {#singular-implicit}

对于以下字段定义：

```proto
int32 foo = 1;
```

编译器会在消息类及其构建器中都生成以下访问器方法：

-   `int getFoo()`：返回该字段的当前值。如果该字段未设置，则返回该字段类型的默认值。

编译器只会在消息的构建器中生成以下方法：

-   `Builder setFoo(int value)`：设置该字段的值。调用此方法后，`getFoo()` 将返回 `value`。
-   `Builder clearFoo()`：清除该字段的值。调用此方法后，`getFoo()` 将返回该字段类型的默认值。

对于其他简单字段类型，对应的 Java 类型按 [标量值类型表](/programming-guides/proto2#scalar) 选择。对于消息和枚举类型，值类型会被替换为相应的消息类或枚举类。

#### 枚举字段 {#enum-proto3}

对于枚举字段类型，消息类及其构建器中还会额外生成一个访问器方法：

-   `int getFooValue()`：返回该枚举的整数值。

编译器只会在消息的构建器中生成以下额外方法：

-   `Builder setFooValue(int value)`：设置该枚举的整数值。

此外，如果枚举值未知，`getFoo()` 将返回 `UNRECOGNIZED`——这是 proto3 编译器添加到生成的[枚举类型](#enum)中的一个特殊附加值。

### 可重复字段 {#repeated}

对于以下字段定义：

```proto
repeated int32 foos = 1;
```

编译器会在消息类及其构建器中都生成以下访问器方法：

*   `int getFoosCount()`：返回该字段中当前的元素数量。
*   `int getFoos(int index)`：返回给定的从零开始的索引处的元素。
*   `java.util.List<java.lang.Integer> getFoosList()`：以 java.util.List 的形式返回整个字段。如果该字段未设置，则返回一个空列表。

编译器只会在消息的构建器中生成以下方法：

*   `Builder setFoos(int index, int value)`：设置给定的从零开始的索引处元素的值。
*   `Builder addFoos(int value)`：把一个具有给定值的新元素追加到该字段。
*   `Builder addAllFoos(Iterable<? extends Integer> value)`：把给定 Iterable 中的所有元素追加到该字段。
*   `Builder clearFoos()`：移除该字段中的所有元素。调用此方法后，getFoosCount() 将返回零。

对于其他简单字段类型，对应的 Java 类型按标量值类型表选择。对于消息和枚举类型，类型即为消息类或枚举类。

对于 `repeated string` 字段，`getList()` 访问器会返回一个 `ProtocolStringList`，它是一个继承自 `java.util.List<String>` 的特殊接口，同时还允许直接访问底层的 `ByteString` 表示形式。其他基本类型的可重复字段则返回 `java.util.List`。

#### 可重复的嵌入消息字段 {#repeated-embedded}

对于消息类型，`setFoos()` 和 `addFoos()` 还接受该消息构建器类型的实例作为参数。这只是个快捷方式，等价于对该构建器调用 `.build()`，然后把结果传给该方法。此外还会生成一个额外的方法：

-   `Builder addFoos(int index, Field value)`：在给定的从零开始的索引处插入一个新元素。把当前位于该位置的元素（如果有）及其后的所有元素向右移（它们的索引各加 1）。

此外，对于消息类型，编译器还会在消息类及其构建器中生成以下额外的访问器方法，让你能够访问相关的子构建器：

-   `FooOrBuilder getFoosOrBuilder(int index)`：返回指定元素的构建器（如果该构建器已存在）；如果不存在，则抛出 `IndexOutOfBoundsException`。如果从消息类调用此方法，它将始终返回消息（或抛出异常）而不是构建器。在构建器上调用此方法不会为该字段创建子构建器。
-   `List<FooOrBuilder> getFoosOrBuilderList()`：以构建器的不可修改列表（如果可用）或消息列表（如果不可用）的形式返回整个字段。如果从消息类调用此方法，它将始终返回消息的不可变列表，而不是构建器的不可修改列表。

编译器只会在消息的构建器中生成以下方法：

-   `Builder getFoosBuilder(int index)`：返回指定索引处元素的构建器；如果索引越界，则抛出 `IndexOutOfBoundsException`。
-   `Builder addFoosBuilder(int index)`：在指定索引处插入并返回一个针对该可重复消息默认消息实例的构建器。现有条目会被移到更高的索引处，为插入的构建器腾出空间。
-   `Builder addFoosBuilder()`：追加并返回一个针对该可重复消息默认消息实例的构建器。
-   `Builder removeFoos(int index)`：移除给定的从零开始的索引处的元素。
-   `List<Builder> getFoosBuilderList()`：以构建器的不可修改列表的形式返回整个字段。

#### 可重复枚举字段（仅限 proto3）{#repeated-enum-proto3}

编译器会在消息类及其构建器中同时生成以下额外方法：

-   `int getFoosValue(int index)`：返回指定索引处枚举的整数值。
-   `List<java.lang.Integer> getFoosValueList()`：以整数列表的形式返回整个字段。

编译器只会在消息的构建器中生成以下额外方法：

-   `Builder setFoosValue(int index, int value)`：设置指定索引处枚举的整数值。

#### 名称冲突 {#conflicts}

如果另一个非可重复字段的名称与该可重复字段生成的某个方法名冲突，那么这两个字段名的末尾都会追加各自的 Protobuf 字段编号。

对于以下字段定义：

```proto
int32 foos_count = 1;
repeated string foos = 2;
```

编译器会先把它们重命名为如下形式：

```proto
int32 foos_count_1 = 1;
repeated string foos_2 = 2;
```

随后，访问器方法将按上文所述方式生成。

<a id="oneof"></a>

### oneof 字段 {#oneof-fields}

对于以下 oneof 字段定义：

```proto
oneof choice {
    int32 foo_int = 4;
    string foo_string = 9;
    ...
}
```

`choice` oneof 中的所有字段会共用一个私有字段来存放它们的值。此外，Protobuf 编译器还会为该 oneof 分支（case）生成一个 Java 枚举类型，如下所示：

```java
public enum ChoiceCase
        implements com.google.protobuf.Internal.EnumLite {
      FOO_INT(4),
      FOO_STRING(9),
      ...
      CHOICE_NOT_SET(0);
      ...
    };
```

该枚举类型的值具有以下特殊方法：

-   `int getNumber()`：返回对象在 .proto 文件中定义的数值。
-   `static ChoiceCase forNumber(int value)`：返回与给定数值对应的枚举对象（对于其他数值则返回 `null`）。

编译器会在消息类及其构建器中都生成以下访问器方法：

-   `boolean hasFooInt()`：如果 oneof 分支为 `FOO_INT`，则返回 `true`。
-   `int getFooInt()`：如果 oneof 分支为 `FOO_INT`，则返回 `foo` 的当前值；否则返回该字段的默认值。
-   `ChoiceCase getChoiceCase()`：返回指示哪个字段被设置的枚举。如果它们都没有被设置，则返回 `CHOICE_NOT_SET`。

编译器只会在消息的构建器中生成以下方法：

-   `Builder setFooInt(int value)`：把 `Foo` 设置为该值，并把 oneof 分支设置为 `FOO_INT`。调用此方法后，`hasFooInt()` 将返回 `true`，`getFooInt()` 将返回 `value`，`getChoiceCase()` 将返回 `FOO_INT`。
-   `Builder clearFooInt()`：
    -   如果 oneof 分支不是 `FOO_INT`，则不会做任何更改。
    -   如果 oneof 分支是 `FOO_INT`，则把 `Foo` 设置为 null，并把 oneof 分支设置为 `CHOICE_NOT_SET`。调用此方法后，`hasFooInt()` 将返回 `false`，`getFooInt()` 将返回默认值，`getChoiceCase()` 将返回 `CHOICE_NOT_SET`。
-   `Builder.clearChoice()`：重置 `choice` 的值并返回构建器。

对于其他简单字段类型，对应的 Java 类型按 [标量值类型表](/programming-guides/proto2#scalar) 选择。对于消息和枚举类型，值类型会被替换为相应的消息类或枚举类。

### map 字段 {#map-fields}

对于以下 map 字段定义：

```proto
map<int32, int32> weight = 1;
```

编译器会在消息类及其构建器中都生成以下访问器方法：

-   `Map<Integer, Integer> getWeightMap();`：返回一个不可修改的 `Map`。
-   `int getWeightOrDefault(int key, int default);`：返回键（key）对应的值（value）；如果不存在，则返回默认值。
-   `int getWeightOrThrow(int key);`：返回键对应的值；如果不存在，则抛出 IllegalArgumentException。
-   `boolean containsWeight(int key);`：指示该键是否存在于该字段中。
-   `int getWeightCount();`：返回该 map 中的元素数量。

编译器只会在消息的构建器中生成以下方法：

-   `Builder putWeight(int key, int value);`：把 weight 添加到该字段。
-   `Builder putAllWeight(Map<Integer, Integer> value);`：把给定 map 中的所有条目添加到该字段。
-   `Builder removeWeight(int key);`：从该字段中移除 weight。
-   `Builder clearWeight();`：从该字段中移除所有 weight。
-   `@Deprecated Map<Integer, Integer> getMutableWeight();`：返回一个可修改的 `Map`。注意，多次调用此方法可能会返回不同的 map 实例。返回的 map 引用可能会因后续对构建器的任何方法调用而失效。

#### 值为消息类型的 map 字段 {#message-value-map-fields}

对于以消息类型为值的 map，编译器会在消息的构建器中额外生成一个方法：

-   `Foo.Builder putFooBuilderIfAbsent(int key);`：确保映射中存在 `key`；如果尚不存在，则插入一个新的 `Foo.Builder`。对返回的 `Foo.Builder` 所做的更改会反映到最终的消息中。

## Any {#any-fields}

给定如下一个 [`Any`](/programming-guides/proto3#any) 字段：

```proto
import "google/protobuf/any.proto";

message ErrorStatus {
  string message = 1;
  google.protobuf.Any details = 2;
}
```

在我们的生成代码中，`details` 字段的 getter 返回一个 `com.google.protobuf.Any` 实例。它提供以下特殊方法来打包（pack）和解包（unpack）`Any` 的值：

```java
class Any {
  // 使用默认类型 URL 前缀“type.googleapis.com”把给定消息打包进一个 Any。
  public static Any pack(Message message);
  // 使用给定的类型 URL 前缀把给定消息打包进一个 Any。
  public static Any pack(Message message,
                         String typeUrlPrefix);

  // 检查此 Any 消息的载荷是否为给定类型。
  public <T extends Message> boolean is(class<T> clazz);

  // 检查此 Any 消息的载荷是否与给定消息具有相同的类型。
  public boolean isSameTypeAs(Message message);

  // 把 Any 解包为与给定消息类型相同的消息。
  // 如果类型不匹配或解析载荷失败，则抛出异常。
  public <T extends Message> T unpackSameTypeAs(T message)
      throws InvalidProtocolBufferException;

  // 把 Any 解包为给定的消息类型。如果类型不匹配
  // 或解析载荷失败，则抛出异常。
  public <T extends Message> T unpack(class<T> clazz)
      throws InvalidProtocolBufferException;
}
```

## 枚举 {#enum}

给定如下枚举定义：

```proto
enum Foo {
  VALUE_A = 0;
  VALUE_B = 5;
  VALUE_C = 1234;
}
```

Protobuf 编译器将生成一个名为 `Foo` 的 Java 枚举类型，其值集合与原定义相同。如果你使用 proto3，它还会向该枚举类型添加特殊值 `UNRECOGNIZED`。在版次中，`OPEN` 枚举同样拥有一个 `UNRECOGNIZED` 值，而 `CLOSED` 枚举则没有。生成的枚举类型的值具有以下特殊方法：

-   `int getNumber()`：返回对象在 `.proto` 文件中定义的数值。
-   `EnumValueDescriptor getValueDescriptor()`：返回该枚举值的描述符，其中包含该值的名称、编号和类型信息。
-   `EnumDescriptor getDescriptorForType()`：返回该枚举类型的描述符，其中包含诸如每个已定义值的信息。

此外，`Foo` 枚举类型还包含以下静态方法：

-   `static Foo forNumber(int value)`：返回与给定数值对应的枚举对象。当不存在对应的枚举对象时返回 null。
-   `static Foo valueOf(int value)`：返回与给定数值对应的枚举对象。该方法已弃用，建议改用 `forNumber(int value)`，并将在即将发布的版本中移除。
-   `static Foo valueOf(EnumValueDescriptor descriptor)`：返回与给定值描述符对应的枚举对象。可能比 `valueOf(int)` 更快。在 proto3 和 `OPEN` 枚举中，如果传入未知的值描述符，则返回 `UNRECOGNIZED`。
-   `EnumDescriptor getDescriptor()`：返回该枚举类型的描述符，其中包含诸如每个已定义值的信息。（它与 `getDescriptorForType()` 的区别仅在于它是一个静态方法。）

还会为每个枚举值生成一个以 \_VALUE 为后缀的整型常量。

注意，`.proto` 语言允许多个枚举符号拥有相同的数值。具有相同数值的符号互为同义词。例如：

```proto
enum Foo {
  BAR = 0;
  BAZ = 0;
}
```

在这种情况下，`BAZ` 是 `BAR` 的同义词。在 Java 中，`BAZ` 将被定义为一个 static final 字段，如下所示：

```java
static final Foo BAZ = BAR;
```

因此，`BAR` 与 `BAZ` 比较相等，且 `BAZ` 绝不应出现在 switch 语句中。编译器总是选择用给定数值定义的第一个符号作为该符号的“规范化（canonical）”版本；后续所有具有相同编号的符号都只是别名。

枚举可以定义在消息类型内部。此时编译器会把 Java 枚举定义生成在该消息类型的类中。

**注意：生成 Java 代码时，Protobuf 枚举可包含的值的数量上限可能低得出人意料**——最坏情况下，该上限略高于 1,700 个值。这一限制源于 Java 字节码的单方法大小限制，并且它会随 Java 实现、Protobuf 套件的不同版本以及 `.proto` 文件中为该枚举设置的任何选项而变化。

## 扩展 {#extension}

给定一个带有扩展区间（extension range）的消息：

```proto
edition = "2023";

message Foo {
  extensions 100 to 199;
}
```

Protobuf 编译器会让 `Foo` 继承 `GeneratedMessage.ExtendableMessage`，而不是通常的 `GeneratedMessage`。类似地，`Foo` 的构建器将继承 `GeneratedMessage.ExtendableBuilder`。你绝不应按名称直接引用这些基类型（`GeneratedMessage` 被视为实现细节）。不过，这些超类定义了许多额外的方法，你可以用它们来操作扩展。

具体来说，`Foo` 和 `Foo.Builder` 将继承 `hasExtension()`、`getExtension()` 和 `getExtensionCount()` 方法。此外，`Foo.Builder` 还将继承 `setExtension()` 和 `clearExtension()` 方法。这些方法中的每一个都把一个扩展标识符（extension identifier，本节后文描述）作为其第一个参数，用于标识一个扩展字段。其余参数和返回值，与为类型与该扩展标识符相同的普通（非扩展）字段所生成的对应访问器方法的参数和返回值完全相同。

给定如下扩展定义：

```proto
edition = "2023";

import "foo.proto";

extend Foo {
  int32 bar = 123;
}
```

Protobuf 编译器会生成一个名为 `bar` 的“扩展标识符”，你可以将它与 `Foo` 的扩展访问器搭配使用来访问该扩展，如下所示：

```java
Foo foo =
  Foo.newBuilder()
     .setExtension(bar, 1)
     .build();
assert foo.hasExtension(bar);
assert foo.getExtension(bar) == 1;
```

（扩展标识符的具体实现相当复杂，涉及对泛型的巧妙运用——不过，无需了解扩展标识符的工作原理，你也可以使用它们。）

注意，`bar` 会如上文所述被声明为该 `.proto` 文件包装类的静态字段；示例中我们省略了包装类名。

扩展可以声明在另一个类型的作用域内，以便为其生成的符号名添加前缀。例如，一种常见模式是在字段类型声明的*内部*用该字段来扩展一个消息：

```proto
edition = "2023";

import "foo.proto";

message Baz {
  extend Foo {
    Baz foo_ext = 124;
  }
}
```

在这种情况下，一个标识符为 `foo_ext`、类型为 `Baz` 的扩展声明在 `Baz` 的声明内部；引用 `foo_ext` 时需要加上 `Baz.` 前缀：

```java
Baz baz = createMyBaz();
Foo foo =
  Foo.newBuilder()
     .setExtension(Baz.fooExt, baz)
     .build();
assert foo.hasExtension(Baz.fooExt);
assert foo.getExtension(Baz.fooExt) == baz;
```

解析可能包含扩展的消息时，你必须提供一个已在其中注册了所有你希望能够解析的扩展的 [`ExtensionRegistry`](/reference/java/api-docs/com/google/protobuf/ExtensionRegistry.html)。否则，这些扩展将被视为未知字段（unknown fields）处理，观察扩展的方法的表现也会如同它们不存在一样。

```java
ExtensionRegistry registry = ExtensionRegistry.newInstance();
registry.add(Baz.fooExt);
Foo foo = Foo.parseFrom(input, registry);
assert foo.hasExtension(Baz.fooExt);
```

```java
ExtensionRegistry registry = ExtensionRegistry.newInstance();
Foo foo = Foo.parseFrom(input, registry);
assert foo.hasExtension(Baz.fooExt) == false;
```

## 服务 {#service}

如果 `.proto` 文件包含如下一行：

```proto
option java_generic_services = true;
```

那么 Protobuf 编译器将按照本节的描述，基于文件中的服务定义生成代码。但是，生成的代码可能并不理想，因为它不与任何特定的远程过程调用（RPC）系统绑定，因此相比针对单一系统定制的代码需要更多的间接层。如果你*不*希望生成这些代码，请在文件中添加以下行：

```proto
option java_generic_services = false;
```

如果上述两行都未给出，该选项默认为 `false`，因为通用服务已弃用。（注意，在 2.4.0 之前，该选项默认为 `true`。）弃用背后的原因请参见[通用服务的设计决策](/design-decisions/insertion-points-and-generic-services#generic-services)。

基于 `.proto` 语言服务定义的 RPC 系统应当提供[插件（plugin）](/reference/cpp/api-docs/google.protobuf.compiler.plugin.pb)来生成适合该系统的代码。这些插件很可能要求禁用抽象服务，以便它们能够生成自己的同名类。

本节余下部分描述在启用抽象服务时 Protobuf 编译器生成的内容。

### 接口 {#interface}

给定如下服务定义：

```proto
service Foo {
  rpc Bar(FooRequest) returns(FooResponse);
}
```

Protobuf 编译器会生成一个抽象类 `Foo` 来表示此服务。`Foo` 会为服务定义中定义的每个方法提供一个抽象方法。在本例中，方法 `Bar` 的定义如下：

```java
abstract void bar(RpcController controller, FooRequest request,
                  RpcCallback<FooResponse> done);
```

这些参数与 `Service.CallMethod()` 的参数等价，只是 `method` 参数是隐含的，而 `request` 和 `done` 指定了它们的确切类型。

`Foo` 继承自 `Service` 接口。Protobuf 编译器会按如下方式自动生成 `Service` 各方法的实现：

-   `getDescriptorForType`：返回该服务的 `ServiceDescriptor`。
-   `callMethod`：根据提供的方法描述符确定正在调用的是哪个方法并直接调用它，把请求消息和回调向下转型（down-cast）为正确的类型。
-   `getRequestPrototype` 和 `getResponsePrototype`：返回给定方法所对应的正确类型的请求或响应的默认实例。

还会生成以下静态方法：

-   `static ServiceDescriptor getServiceDescriptor()`：返回该类型的描述符，其中包含此服务有哪些方法以及它们的输入和输出类型的信息。

`Foo` 还会包含一个嵌套接口 `Foo.Interface`。这是一个纯接口，同样包含与服务定义中每个方法对应的方法。但该接口并不继承 `Service` 接口。这会带来一个问题：RPC 服务器实现通常是用抽象的 `Service` 对象编写的，而不是针对你的特定服务。为解决这个问题，如果你有一个实现了 `Foo.Interface` 的对象 `impl`，可以调用 `Foo.newReflectiveService(impl)` 来构造一个 `Foo` 实例，它只是简单地委托给 `impl`，并实现了 `Service`。

概括来说，实现你自己的服务时有两种选择：

-   继承 `Foo` 并按需实现其方法，然后把你的子类实例直接交给 RPC 服务器实现。这通常最简单，但有些人认为它不够“纯粹”。
-   实现 `Foo.Interface` 并使用 `Foo.newReflectiveService(Foo.Interface)` 构造一个包装它的 `Service`，然后把该包装器传给你的 RPC 实现。

### 存根 {#stub}

Protobuf 编译器还会为每个服务接口生成一个“存根”（stub）实现，供希望向实现该服务的服务器发送请求的客户端使用。对于（上文中的）`Foo` 服务，存根实现 `Foo.Stub` 将被定义为一个嵌套类。

`Foo.Stub` 是 `Foo` 的子类，它还实现了以下方法：

-   `Foo.Stub(RpcChannel channel)`：构造一个新的存根，在给定的通道（channel）上发送请求。
-   `RpcChannel getChannel()`：返回此存根的通道，即传递给构造函数的那个通道。

此外，该存根把服务的每个方法都实现为围绕通道的包装器。调用其中一个方法只是简单地调用 `channel.callMethod()`。

Protobuf 库本身不包含 RPC 实现。不过，它包含了把生成的服务类接入你所选的任意 RPC 实现所需的全部工具。你只需提供 `RpcChannel` 和 `RpcController` 的实现。

### 阻塞式接口 {#blocking}

上文描述的 RPC 类都具有非阻塞语义：调用方法时，你需要提供一个回调对象，方法一旦完成该对象就会被调用。通常，使用阻塞语义编写代码更容易（尽管可扩展性可能较差）：在阻塞语义下，方法在完成之前不会返回。为适应这种情况，Protobuf 编译器还会生成服务类的阻塞版本。`Foo.BlockingInterface` 等价于 `Foo.Interface`，区别在于每个方法直接返回结果，而不是调用回调。例如，`bar` 的定义如下：

```java
abstract FooResponse bar(RpcController controller, FooRequest request)
                         throws ServiceException;
```

与非阻塞服务类似，`Foo.newReflectiveBlockingService(Foo.BlockingInterface)` 会返回一个包装了某个 `Foo.BlockingInterface` 的 `BlockingService`。最后，`Foo.BlockingStub` 返回 `Foo.BlockingInterface` 的存根实现，它会向特定的 `BlockingRpcChannel` 发送请求。

## 插件插入点 {#plugins}

希望扩展 Java 代码生成器（code generator）输出的[代码生成器插件](/reference/cpp/api-docs/google.protobuf.compiler.plugin.pb)，可以使用给定的插入点名称插入以下类型的代码。

-   `outer_class_scope`：属于该文件包装类的成员声明。
-   `class_scope:TYPENAME`：属于某个消息类的成员声明。`TYPENAME` 是完整的 proto 名称，例如 `package.MessageType`。
-   `builder_scope:TYPENAME`：属于某个消息构建器类的成员声明。`TYPENAME` 是完整的 proto 名称，例如 `package.MessageType`。
-   `enum_scope:TYPENAME`：属于某个枚举类的成员声明。`TYPENAME` 是完整的 proto 枚举名称，例如 `package.EnumType`。
-   `message_implements:TYPENAME`：某个消息类的类实现声明。`TYPENAME` 是完整的 proto 名称，例如 `package.MessageType`。
-   `builder_implements:TYPENAME`：某个构建器类的类实现声明。`TYPENAME` 是完整的 proto 名称，例如 `package.MessageType`。

生成代码不能包含 import 语句，因为这些语句容易与生成代码自身定义的类型名发生冲突。因此，在引用外部类时，必须始终使用其完全限定名。

Java 代码生成器中确定输出文件名的逻辑相当复杂。你最好查看 `protoc` 的源代码（尤其是 `java_headers.cc`），以确保覆盖了所有情况。

不要生成依赖标准代码生成器所声明的私有类成员的代码，因为这些实现细节在 Protobuf 的未来版本中可能会发生变化。

## 实用工具类 {#utility-classes}

Protobuf 提供了一些[实用工具类](/reference/java/api-docs/com/google/protobuf/util/package-summary.html)，可用于消息比较、JSON 转换以及处理[知名类型（well-known types，针对常见用例预定义的 Protobuf 消息）](/reference/protobuf/google.protobuf)。
