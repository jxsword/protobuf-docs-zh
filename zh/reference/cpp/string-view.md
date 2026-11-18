+++
title = "字符串视图 API"
weight = 510
description = "涵盖各项 string_view 迁移"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/string-view/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

使用 `std::string` 的 C++ 字符串字段（field）API 严重制约着 Protobuf 的内部实现及其演进。例如，`mutable_string_field()` 返回 `std::string*`，这迫使我们使用 `std::string` 来存储该字段。这使其在 arena 上的交互变得复杂，我们不得不维护 arena 捐赠（donation）状态，以追踪字符串载荷（payload）的分配究竟来自 arena 还是堆。

从长远来看，我们希望将所有运行时（runtime）API 和生成代码 API 都迁移为接受 `string_view` 作为输入，并由访问器（accessor）返回 `string_view`。本文档描述了截至 30.x 发布（release）时这项迁移的状态。

## 字符串字段访问器 {#string-type}

作为版次（edition）2023 的一部分，[`string_type`](/editions/features#string_type) 特性（feature）随 `VIEW` 选项一同发布，以支持渐进式迁移到生成的 `string_view` API。使用该特性会影响 `string` 和 `bytes` 字段的 [C++ 生成代码（C++ Generated Code）](/reference/cpp/cpp-generated)。

### 与 ctype 的交互 {#ctype}

在版次 2023 中，你仍然可以在字段级指定 `ctype`，而 `string_type` 则既可以在文件级指定，也可以在字段级指定。不允许在同一个字段上同时指定两者。如果在文件级设置了 `string_type`，那么字段上指定的 `ctype` 将优先生效。

除 `VIEW` 选项之外，`string_type` 的所有可能取值都有一个拼写相同、行为一致的对应 `ctype` 取值。例如，两个枚举中都有一个 `CORD` 取值。

从版次 2024 开始，将无法再指定 `ctype`。

### 生成的单数字段（singular field）{#singular-view}

对于版次 2023 中以下任一字段定义：

```proto
bytes foo = 1 [features.(pb.cpp).string_type=VIEW];
string foo = 1 [features.(pb.cpp).string_type=VIEW];
```

编译器将生成以下访问器方法：

-   `::absl::string_view foo() const`：返回该字段的当前值。如果该字段未设置，则返回默认值（default value）。
-   `void clear_foo()`：清除该字段的值。调用此方法后，`foo()` 将返回默认值。
-   `bool has_foo()`：如果该字段已设置，则返回 `true`。
-   `void set_foo(::absl::string_view value)`：设置该字段的值。调用此方法后，`has_foo()` 将返回 `true`，且 `foo()` 将返回 `value` 的副本。
-   `void set_foo(const string& value)`：设置该字段的值。调用此方法后，`has_foo()` 将返回 `true`，且 `foo()` 将返回 `value` 的副本。
-   `void set_foo(string&& value)`：设置该字段的值，从传入的字符串移动。调用此方法后，`has_foo()` 将返回 `true`，且 `foo()` 将返回 `value`。
-   `void set_foo(const char* value)`：使用以 null 结尾的 C 风格字符串设置该字段的值。调用此方法后，`has_foo()` 将返回 `true`，且 `foo()` 将返回 `value` 的副本。

### 生成的 repeated 字段 {#repeated-view}

对于以下任一字段定义：

```proto
repeated string foo = 1 [features.(pb.cpp).string_type=VIEW];
repeated bytes foo = 1 [features.(pb.cpp).string_type=VIEW];
```

编译器将生成以下访问器方法：

-   `int foo_size() const`：返回该字段中当前的元素数量。
-   `::absl::string_view foo(int index) const`：返回给定从零开始的索引处的元素。当传入的索引超出 `[0, foo_size()-1]` 范围时调用此方法，会产生未定义行为。
-   `void set_foo(int index, ::absl::string_view value)`：设置给定从零开始的索引处元素的值。
-   `void set_foo(int index, const string& value)`：设置给定从零开始的索引处元素的值。
-   `void set_foo(int index, string&& value)`：设置给定从零开始的索引处元素的值，从传入的字符串移动。
-   `void set_foo(int index, const char* value)`：使用以 null 结尾的 C 风格字符串设置给定从零开始的索引处元素的值。
-   `void add_foo(::absl::string_view value)`：把具有给定值的新元素追加到该字段的末尾。
-   `void add_foo(const string& value)`：把具有给定值的新元素追加到该字段的末尾。
-   `void add_foo(string&& value)`：把新元素追加到该字段的末尾，从传入的字符串移动。
-   `void add_foo(const char* value)`：使用以 null 结尾的 C 风格字符串把新元素追加到该字段的末尾。
-   `void clear_foo()`：移除该字段中的所有元素。调用此方法后，`foo_size()` 将返回零。
-   `const RepeatedPtrField<string>& foo() const`：返回存储该字段元素的底层 [`RepeatedPtrField`](/reference/cpp/api-docs/google.protobuf.repeated_field#RepeatedPtrField)。该容器类提供 STL 风格的迭代器及其他方法。
-   `RepeatedPtrField<string>* mutable_foo()`：返回指向存储该字段元素的底层可变 `RepeatedPtrField` 的指针。该容器类提供 STL 风格的迭代器及其他方法。

### 生成的 oneof 字段 {#oneof-view}

对于以下任意一种 [oneof](#oneof) 字段定义：

```proto
oneof example_name {
    string foo = 1 [features.(pb.cpp).string_type=VIEW];
    ...
}
oneof example_name {
    bytes foo = 1 [features.(pb.cpp).string_type=VIEW];
    ...
}
```

编译器将生成以下访问器方法：

-   `bool has_foo() const`：如果 oneof 分支（case） 为 `kFoo`，则返回 `true`。
-   `::absl::string_view foo() const`：如果 oneof 分支 为 `kFoo`，返回该字段的当前值；否则返回默认值。
-   `void set_foo(::absl::string_view value)`：
    -   如果同一个 oneof 中有任何其他 oneof 字段已设置，则调用 `clear_example_name()`。
    -   设置该字段的值，并将 oneof 分支 设置为 `kFoo`。
    -   `has_foo()` 将返回 `true`，`foo()` 将返回 `value` 的副本，并且 `example_name_case()` 将返回 `kFoo`。
-   `void set_foo(const string& value)`：与第一个 `set_foo()` 类似，但从 `const string` 引用复制。
-   `void set_foo(string&& value)`：与第一个 `set_foo()` 类似，但从传入的字符串移动。
-   `void set_foo(const char* value)`：与第一个 `set_foo()` 类似，但从以 null 结尾的 C 风格字符串复制。
-   `void clear_foo()`：
    -   如果 oneof 分支 不是 `kFoo`，则不会发生任何更改。
    -   如果 oneof 分支 是 `kFoo`，则释放该字段并清除 oneof 分支。`has_foo()` 将返回 `false`，`foo()` 将返回默认值，并且 `example_name_case()` 将返回 `EXAMPLE_NAME_NOT_SET`。

## 枚举名称辅助函数 {#enum-name}

从版次 2024 开始，引入了新特性 `enum_name_uses_string_view`，并且默认为 true。除非将其禁用，否则对于如下枚举：

```proto
enum Foo {
  VALUE_A = 0;
  VALUE_B = 5;
  VALUE_C = 1234;
}
```

除 `Foo` 枚举之外，Protobuf 编译器还会在标准 [生成代码（generated code）](/reference/cpp/cpp-generated#enum) 之外生成以下新函数：

-   `::absl::string_view Foo_Name(int value)`：返回给定数值对应的名称。如果不存在这样的值，则返回空字符串。如果多个值具有该数值，则返回最先定义的那个。在上面的示例中，`Foo_Name(5)` 将返回 `VALUE_B`。

可以通过添加如下特性覆盖（feature override）来恢复旧行为：

```proto
enum Foo {
  option features.(pb.cpp).enum_name_uses_string_view = false;

  VALUE_A = 0;
  VALUE_B = 5;
  VALUE_C = 1234;
}
```

在这种情况下，名称辅助函数将切换回 `const string& Foo_Name(int value)`。
