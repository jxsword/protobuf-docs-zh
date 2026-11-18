+++
title = "Java Proto 名称"
weight = 655
linkTitle = "生成的 Proto 名称"
description = "由 protoc 的 Java 插件生成的名称。"
type = "docs"
source_url = "https://protobuf.dev/reference/java/java-proto-names/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

本文介绍在不同的 proto 选项下，proto 的完全限定 Java 名称是什么。该名称对应于使用该消息（message）时需要导入的包。

## 建议 { #recommendation }

从版次 2024（Edition 2024）开始，最佳实践是：

*   设置 `option java_package = "com.example.package"`
*   **不要设置** `java_outer_classname` 或 `features.(pb.java).nest_in_file_class = YES`。

除上述内容外，版次 2024 中的各项默认行为也都已改进，因此如今的默认行为本身即可视为当前最佳实践。

使用 Proto2、Proto3 或版次 2023 时，最佳实践是：

*   设置 `option java_multiple_files = true;`
*   设置 `option java_outer_classname = "FileNameProto";`
*   设置 `option java_package = "com.google.package";`

### 说明 {#explanation}

#### 多文件 {#multiple-files}

设置 `java_multiple_files = true` 后，为每个消息生成的 Java 类都会放入单独的 `.java` 文件中。这样，把消息从一个 `.proto` 文件移动到另一个 `.proto` 文件就容易得多了。

从版次 2024 开始，这一行为已被 `features.(pb.java).nest_in_file_class` 特性（feature）取代，该特性的默认值为 `NO`，与旧语法中 `java_multiple_files = true` 的行为一致。

#### 外部类名 {#outer-classname}

`.proto` 文件本身也会生成一个 Java 类。如果不指定，该文件对应的类名将自动生成。然而，该名称的生成规则过于复杂，且不直观。最佳做法是显式设置 `java_outer_classname` 选项，其值为 `.proto` 文件名去掉 `'.'` 并转换为 PascalCase 后的结果。例如：

*   文件 `student_record_request.proto` 应设置：

    ```proto
    option java_outer_classname = "StudentRecordRequestProto";
    ```

从版次 2024 开始，`java_outer_classname` 仍然可用，但其默认行为已改为与本建议一致，因此无需再进行设置。

#### Java 包 {#java-package}

生成的绑定所使用的 Java 包会自动设置为 proto 包。但这通常不符合 Java 的命名惯例。为确保 Java 包名符合惯例，我们建议显式设置 `java_package` 选项。例如，在 Google 内部，惯例是在 proto 包名前面加上 `com.google.` 前缀。

## 不可变 API 消息名 { #immutable-api-message-names }

protoc 的 Java 插件会按照下表生成名称。

java_multiple_files | java_package | java_outer_classname | 生成的完整消息名称
:-----------------: | ------------ | -------------------- | ---------------------------
true                | 未定义        | *被忽略*              | `com.google.protos.$package.$message`
true                | 已定义        | *被忽略*              | `$java_package.$message`
false               | 未定义        | 未定义                | `com.google.protos.$package.$derived_outer_class.$message`
false               | 未定义        | 已定义                | `com.google.protos.$package.$java_outer_classname.$message`
false               | 已定义        | 未定义                | `$java_package.$derived_outer_class.$message`
false               | 已定义        | 已定义                | `$java_package.$java_outer_classname.$message`

**图例**

*   `$message` 是 proto 消息的实际名称。
*   `$package` 是 proto 包的名称。这是 proto 文件中 `package` 指令所指定的名称，该指令通常位于文件顶部。
*   `$derived_outer_class` 是根据 proto 文件名生成的名称。通常的计算方式是去掉文件名中的标点符号，并转换为 PascalCase。例如，若 proto 为 `foo_bar.proto`，则 `$derived_outer_class` 的值为 `FooBar`。

    如果生成的类名与 proto 文件中定义的某个消息同名，`derived_outer_class` 会追加 `OuterClass` 后缀。例如，若 proto 为 `foo_bar.proto` 且包含 `FooBar` 消息，则 `$derived_outer_class` 的值为 `FooBarOuterClass`。使用 v1 API 时同样会追加 `OuterClass` 后缀，无论类名是否与已定义的某个消息同名。

*   其余所有 `$names` 均为 `.proto` 文件中定义的相应文件选项的值。
