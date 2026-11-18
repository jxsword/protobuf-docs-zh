+++
title = "Java 中的 UTF-8 校验"
weight = 650
linkTitle = "Java 中的 UTF-8 校验"
description = "描述 Java protobuf 在所有语法、版次与选项/特性设置下对 UTF-8 字符串的处理行为。"
type = "docs"
source_url = "https://protobuf.dev/reference/java/java-utf8-validation/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

.

Proto2 同时提供了 string 和 bytes 两种类型，并且从一开始，文档就规定 string 必须始终包含 UTF-8 编码的文本。
这项要求在各语言中的执行情况各不相同（详见本主题后文），这意味着尽管规范有明文规定，实践中许多 string 字段（field）仍包含非 UTF-8 数据。

对于 proto3，最终决定所有解析器（parser）都必须校验 UTF-8。这一决定是在 proto3 在 google3 中首次亮相近一年之后才作出的，因此这项变更要求先开展一个项目，为所有现有的 string 字段设置 `enforce_utf8=false`，之后才能把默认值翻转为 `enforce_utf8=true`。LSC 的一项目标就是清理所有 `enforce_utf8=false` 的用法，并最终移除该选项（option）。

以下是 Java Protobuf 在各种语法（syntax）与版次（edition）下的 UTF-8 校验行为总结。该行为对标准 string 字段和 string 类型的扩展（extension）均保持一致：

语法 / 版次             | `features.utf8_validation`  | `features.(pb.java).utf8_validation`    | `java_string_check_utf8`   | `enforce_utf8`            | Java UTF-8 校验行为
:---------------------- | :-------------------------- | :-------------------------------------- | :------------------------- | :------------------------ | :-----------------------------
**proto2**              | *不允许*                     | *不允许*                                 | 未设置或 `false`（默认）    | *被忽略*                  | **不校验**（proto2 默认）
**proto2**              | *不允许*                     | *不允许*                                 | `true`                     | *被忽略*                  | **启用校验***
**proto3**              | *不允许*                     | *不允许*                                 | *被忽略*                   | 未设置或 `true`（默认）    | **启用校验**（proto3 默认）
**proto3**              | *不允许*                     | *不允许*                                 | *被忽略*                   | `false`                   | **不校验**
**版次 2023 / 2024**    | 未设置或 `VERIFY`（默认）    | 未设置、`DEFAULT`（默认）或 `VERIFY`     | *不允许*                   | *不允许*                  | **启用校验****（版次默认）
**版次 2023 / 2024**    | `NONE`                      | 未设置或 `DEFAULT`（默认）               | *不允许*                   | *不允许*                  | **不校验**
**版次 2023 / 2024**    | `NONE`                      | `VERIFY`                                | *不允许*                   | *不允许*                  | **启用校验**（仅在 Java 中校验）

\* 在 Java Lite 中，当 `java_string_check_utf8=true` 时，`proto2` 中 string 类型的扩展**不会**进行校验。

\** 在 Java Lite 中，在版次 2023 与 2024 下，string 类型的扩展在任何选项组合下都**不会**进行校验。这是一个疏忽，应在未来的版次中加以纠正。

### 未校验时的行为

JavaLite 与 Java 对 string 字段使用相同的 API，但使用的对象表示形式不同：

*   **仅 String 模式：** JavaLite 始终将字符串存储为 `java.lang.String`。这意味着该字段无法保留无效的 UTF-8。如果解析到了无效的 UTF-8，或通过 `setFoo(ByteString)` 赋入了无效的 UTF-8，它都会立即经历一次有损转换，变成替换字符（replacement character）。
*   **双模式：** Java “完整”版支持双重表示，即 `java.lang.Object` 字段既可以是 `java.lang.String`，也可以是 `java.lang.ByteString`。这意味着在解析 proto2 时可以保留无效的 UTF-8，并且 `ByteString getFooBytes()` 会返回从线路（wire）上解析出的原始内容。

### 遗留选项

-   **`java_string_check_utf8`** 是一个**文件级选项**，仅适用于 `proto2`。该选项可以在 proto3 文件中设置，但不会产生任何效果。Java Lite **不会**校验 string 类型的扩展。
-   **`enforce_utf8`** 是一个**字段级选项**，仅适用于 `proto3`。将其设为 `false` 是在 proto3 中禁用校验的唯一方式，但该选项已被弃用（deprecated），后续会被移除，并且要求已列入允许名单（allowlist）。该选项可以在 proto2 文件中设置，但不会产生任何效果。
-   这两个遗留选项在**版次机制（Editions）下均不允许使用**，此时必须改用特性（features）框架。

### 版次特性

-   **`features.utf8_validation`** 是一个文件级或字段级特性（feature），用于控制**所有**语言的 UTF-8 校验。
-   **`features.(pb.java).utf8_validation`** 是一个文件级或字段级特性，用于控制**仅 Java** 的 UTF-8 校验。默认情况下，Java 会使用 `features.utf8_validation` 的设置。该特性应逐步淘汰，改用 `features.utf8_validation`。
-   这两个特性在 **proto2 和 proto3 下均不允许使用**（所有版次特性都是如此）。
