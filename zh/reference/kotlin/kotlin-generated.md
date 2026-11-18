+++
title = "Kotlin 生成代码指南"
weight = 680
linkTitle = "生成代码指南"
description = "准确描述 Protobuf 编译器针对任意给定协议定义、在 Java 生成代码之外额外生成的 Kotlin 代码。"
type = "docs"
source_url = "https://protobuf.dev/reference/kotlin/kotlin-generated/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

proto2、proto3 与版次（edition）生成代码之间的任何差异都会重点标出——请注意，这些差异存在于本文档所描述的生成代码（generated code）中，而非基础消息（message）类/接口——后者在两种版本（version）中都是相同的。阅读本文档之前，请先阅读 [proto2 语言指南](/programming-guides/proto2)、[proto3 语言指南](/programming-guides/proto3)和/或 [版次语言指南](/programming-guides/editions)。

## 编译器调用 {#invocation}

Protobuf 编译器生成的 Kotlin 代码构建在 Java 代码之上。因此，调用它时必须带上两个命令行标志：`--java_out=` 和 `--kotlin_out=`。`--java_out=` 选项的参数是你希望编译器写入 Java 输出的目录，`--kotlin_out=` 亦然。对于每个输入的 `.proto` 文件，编译器都会创建一个包装用的 `.java` 文件，其中包含一个表示该 `.proto` 文件本身的 Java 类。

**无论**你的 `.proto` 文件中是否包含如下一行：

```proto
option java_multiple_files = true;
```

编译器都会为它针对 `.proto` 文件中声明的每个顶层消息所生成的各个类和工厂方法，分别创建单独的 `.kt` 文件。

如 [Java 生成代码参考](/reference/java/java-generated#package) 中所述，每个文件的 Java 包名与生成 Java 代码所使用的包名相同。

输出文件的选定方式是：把 `--kotlin_out=` 的参数、包名（把其中的句点 [.] 替换为斜杠 [/]）以及 `Kt.kt` 文件名后缀拼接而成。

举例来说，假设你按如下方式调用编译器：

```shell
protoc --proto_path=src --java_out=build/gen/java --kotlin_out=build/gen/kotlin src/foo.proto
```

如果 `foo.proto` 的 Java 包是 `com.example`，并且它包含一个名为 `Bar` 的消息，那么 Protobuf 编译器将生成文件 `build/gen/kotlin/com/example/BarKt.kt`。必要时，Protobuf 编译器会自动创建 `build/gen/kotlin/com` 和 `build/gen/kotlin/com/example` 目录；但它不会创建 `build/gen/kotlin`、`build/gen` 或 `build`，这些目录必须已经存在。你可以在一次调用中指定多个 `.proto` 文件；所有输出文件会一次性全部生成。

## 消息 {#message}

给定如下简单消息声明：

```proto
message FooBar {}
```

Protobuf 编译器——除生成 Java 代码之外——还会生成一个名为 `FooBarKt` 的 object，以及两个具有如下结构的顶层函数：

```kotlin
object FooBarKt {
  class Dsl private constructor { ... }
}
inline fun fooBar(block: FooBarKt.Dsl.() -> Unit): FooBar
inline fun FooBar.copy(block: FooBarKt.Dsl.() -> Unit): FooBar
```

### 嵌套类型

消息可以声明在另一个消息内部。例如：

```proto
message Foo {
  message Bar { }
}
```

在这种情况下，编译器会把 `BarKt` object 和 `bar` 工厂方法嵌套在 `FooKt` 内部，而 `copy` 方法仍保持顶层：

```kotlin
object FooKt {
  class Dsl { ... }
  object BarKt {
    class Dsl private constructor { ... }
  }
  inline fun bar(block: FooKt.BarKt.Dsl.() -> Unit): Foo.Bar
}
inline fun foo(block: FooKt.Dsl.() -> Unit): Foo
inline fun Foo.copy(block: FooKt.Dsl.() -> Unit): Foo
inline fun Foo.Bar.copy(block: FooKt.BarKt.Dsl.() -> Unit): Foo.Bar
```

## 字段

除上一节所述的方法之外，Protobuf 编译器还会在 DSL 中为 `.proto` 文件里消息内定义的每个字段生成可变属性。（Kotlin 已经可以根据 Java 生成的 getter，在消息对象上推断出只读属性。）

请注意，属性始终采用驼峰命名（camel case），即使 `.proto` 文件中的字段名（field name）使用带下划线的小写形式（[理应如此](/programming-guides/style)）。大小写转换规则如下：

1.  名称中的每个下划线都会被移除，其后的字母改为大写。
2.  如果名称要附加前缀（例如 “clear”），则首字母大写；否则首字母小写。

因此，字段 `foo_bar_baz` 会变成 `fooBarBaz`。

在少数特殊情况下，如果字段名与 Kotlin 的保留字或 Protobuf 库中已定义的方法冲突，则会追加一个额外的下划线。例如，名为 `in` 的字段，其 clearer（清除方法）为 `clearIn_()`。

### 单数字段

对于以下字段定义：

```proto
int32 foo = 1;
```

编译器将在 DSL 中生成以下访问器（accessor）：

-   `fun hasFoo(): Boolean`：如果该字段已设置，则返回 `true`。对于使用隐式存在性（implicit presence）的字段，不会生成此方法。
-   `var foo: Int`：该字段的当前值。如果该字段未设置，则返回默认值（default value）。
-   `fun clearFoo()`：清除该字段的值。调用此方法后，`hasFoo()` 将返回 `false`，`foo` 将返回默认值。

对于其他简单字段类型，对应的 Java 类型按 [标量值类型表](/programming-guides/proto2#scalar) 选择。对于消息和枚举（enum）类型，值类型会被替换为相应的消息类或枚举类。由于消息类型仍在 Java 中定义，为了与 Java 及旧版本的 Kotlin 保持兼容，消息中的无符号类型在 DSL 中使用对应的标准有符号类型来表示。

#### 嵌入消息字段

请注意，对子消息（submessage）没有任何特殊处理。例如，如果你有一个字段

```proto
optional Foo my_foo = 1;
```

你必须写

```kotlin
myFoo = foo {
  ...
}
```

总的来说，这是因为编译器无从知晓 `Foo` 是否拥有 Kotlin DSL，抑或只生成了 Java API。这意味着你不必等待你所依赖的消息添加 Kotlin 代码生成。

### 可重复字段 {#repeated}

对于以下字段定义：

```proto
repeated string foo = 1;
```

编译器将在 DSL 中生成以下成员：

-   `class FooProxy: DslProxy`，一种不可构造、仅用于泛型的类型
-   `val fooList: DslList<String, FooProxy>`，可重复字段中当前元素列表的只读视图
-   `fun DslList<String, FooProxy>.add(value: String)`，一个允许向可重复字段添加元素的扩展函数（extension function）
-   `operator fun DslList<String, FooProxy>.plusAssign(value: String)`，`add` 的别名
-   `fun DslList<String, FooProxy>.addAll(values: Iterable<String>)`，一个允许把元素的 `Iterable` 添加到可重复字段的扩展函数
-   `operator fun DslList<String, FooProxy>.plusAssign(values: Iterable<String>)`，`addAll` 的别名
-   `operator fun DslList<String, FooProxy>.set(index: Int, value: String)`，一个设置给定从零开始的索引处元素值的扩展函数
-   `fun DslList<String, FooProxy>.clear()`，一个清空可重复字段内容的扩展函数

这种不寻常的构造使 `fooList` 在 DSL 的作用域内可以“表现得像”一个可变列表，只支持底层构建器（builder）所支持的方法，同时又防止可变性“逃逸”出 DSL 而造成令人困惑的副作用。

对于其他简单字段类型，对应的 Java 类型按 [标量值类型表](/programming-guides/proto2#scalar) 选择。对于消息和枚举类型，类型即为消息类或枚举类。

### oneof 字段

对于以下 oneof 字段定义：

```proto
oneof oneof_name {
    int32 foo = 1;
    ...
}
```

编译器将在 DSL 中生成以下访问器方法：

-   `val oneofNameCase: OneofNameCase`：获取 `oneof_name` 的各字段中（如果有的话）哪一个已被设置；返回类型参见 [Java 代码参考](/reference/java/java-generated#oneof)
-   `fun hasFoo(): Boolean`：如果 oneof 分支（case）为 `FOO`，则返回 `true`。
-   `val foo: Int`：如果 oneof 分支为 `FOO`，则返回 `oneof_name` 的当前值；否则返回该字段的默认值。

对于其他简单字段类型，对应的 Java 类型按 [标量值类型表](/programming-guides/proto2#scalar) 选择。对于消息和枚举类型，值类型会被替换为相应的消息类或枚举类。

### map 字段

对于以下 map 字段定义：

```proto
map<int32, int32> weight = 1;
```

编译器将在 DSL 类中生成以下成员：

-   `class WeightProxy private constructor(): DslProxy()`，一种不可构造、仅用于泛型的类型
-   `val weight: DslMap<Int, Int, WeightProxy>`，该 map 字段中当前条目的只读视图
-   `fun DslMap<Int, Int, WeightProxy>.put(key: Int, value: Int)`：向该 map 字段添加此条目
-   `operator fun DslMap<Int, Int, WeightProxy>.put(key: Int, value: Int)`：使用运算符语法的 `put` 别名
-   `fun DslMap<Int, Int, WeightProxy>.remove(key: Int)`：移除与 `key` 相关联的条目（如果存在）
-   `fun DslMap<Int, Int, WeightProxy>.putAll(map: Map<Int, Int>)`：把指定 map 中的所有条目添加到该 map 字段，并覆盖已有键的原值
-   `fun DslMap<Int, Int, WeightProxy>.clear()`：清空该 map 字段中的所有条目

## 扩展 {#extension}

给定一个带有扩展区间（extension range）的 proto2 或版次消息：

```proto
message Foo {
  extensions 100 to 199;
}
```

Protobuf 编译器将向 `FooKt.Dsl` 添加以下方法：

-   `operator fun <T> get(extension: ExtensionLite<Foo, T>): T`：获取 DSL 中扩展字段的当前值
-   `operator fun <T> get(extension: ExtensionLite<Foo, List<T>>): ExtensionList<T, Foo>`：以只读 `List` 的形式获取 DSL 中可重复扩展字段的当前值
-   `operator fun <T : Comparable<T>> set(extension: ExtensionLite<Foo, T>)`：设置 DSL 中扩展字段的当前值（适用于 `Comparable` 字段类型）
-   `operator fun <T : MessageLite> set(extension: ExtensionLite<Foo, T>)`：设置 DSL 中扩展字段的当前值（适用于消息字段类型）
-   `operator fun set(extension: ExtensionLite<Foo, ByteString>)`：设置 DSL 中扩展字段的当前值（适用于 `bytes` 字段）
-   `operator fun contains(extension: ExtensionLite<Foo, *>): Boolean`：如果扩展字段有值，则返回 true
-   `fun clear(extension: ExtensionLite<Foo, *>)`：清空扩展字段
-   `fun <E> ExtensionList<Foo, E>.add(value: E)`：向可重复扩展字段添加一个值
-   `operator fun <E> ExtensionList<Foo, E>.plusAssign(value: E)`：使用运算符语法的 `add` 别名
-   `operator fun <E> ExtensionList<Foo, E>.addAll(values: Iterable<E>)`：向可重复扩展字段添加多个值
-   `operator fun <E> ExtensionList<Foo, E>.plusAssign(values: Iterable<E>)`：使用运算符语法的 `addAll` 别名
-   `operator fun <E> ExtensionList<Foo, E>.set(index: Int, value: E)`：设置可重复扩展字段中指定索引处的元素
-   `inline fun ExtensionList<Foo, *>.clear()`：清空可重复扩展字段中的元素

这里的泛型比较复杂，但实际效果是：`this[extension] = value` 适用于除可重复扩展之外的所有扩展类型；而可重复扩展则拥有“自然”的列表语法，其工作方式与 [非扩展的可重复字段](#repeated) 类似。

给定如下扩展定义：

```proto
extend Foo {
  int32 bar = 123;
}
```

Java 会生成一个“扩展标识符”（extension identifier）`bar`，上文中的各项扩展操作都以它作为“键”。
