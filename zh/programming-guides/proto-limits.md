+++
title = "Proto 限制"
weight = 45
description = "介绍 proto 模式中受支持元素的数量限制。"
type = "docs"
source_url = "https://protobuf.dev/programming-guides/proto-limits/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

本主题记录 proto 模式（schema）中受支持元素的数量限制，这些元素包括字段（field）、枚举值（enum value）等。

本文内容汇集了许多工程师发现的各类限制，但并不详尽，某些部分可能不正确或已过时。如果你在工作中发现了新的限制，欢迎将其贡献到本文档中，以帮助他人。

## 字段数量 {#fields}

所有消息（message）最多只能包含 65,535 个字段。

仅含单数（singular）proto 字段的消息（例如 Boolean）：

*   约 2100 个字段（proto2）
*   约 3100 个（proto3，未使用 optional 字段）

通过单数字段扩展的空消息（例如 Boolean）：

*   约 4100 个字段（proto2）

proto3 不支持扩展（extension）。

要测试这一限制，可创建一个字段数超过该上限的 proto 消息，并使用 Java proto 规则进行编译。该限制来自 JVM 规范。

## 字段编号 {#field-numbers}

常规字段可使用 1 到 2<sup>29</sup> - 1（536,870,911）之间的编号，因为字段编号（field number）与 3 位的线路类型（wire type）共享同一个以可变长度整数（varint）编码的 32 位标签（tag）。更多信息请参阅[编码主题](/programming-guides/encoding#structure)。

### MessageSet

使用 `message_set_wire_format` 的消息（即 MessageSet）的扩展不受此限制，因为这类扩展的编号不会打包进标签，而是被编码为一个单独的 varint（`type_id`），因此线路格式（wire format）本可允许编号高达 2<sup>32</sup> - 1。实际适用的是描述符（descriptor）表示形式的以下两项限制：

1.  `FieldDescriptorProto.number` 是 `int32` 类型，因此编号最大只能为 2<sup>31</sup> - 1（`INT32_MAX`）。
2.  `DescriptorProto.ExtensionRange.end` 是 `int32` 类型且为排他边界（不含该值），因此任何扩展范围所能包含的最大编号为 2<sup>31</sup> - 2（`INT32_MAX - 1`）。MessageSet 消息上的 `extensions 4 to max` 会解析为该值，而显式写出的 `extensions 4 to 2147483647` 则会被拒绝。

MessageSet 已被弃用：不要在新的消息中使用 `message_set_wire_format`。

## 枚举中的取值数量 {#enum}

最低的限制约为 1700 个值，出现在 Java 中。其他语言的限制各不相同。

## 消息的总大小 {#total}

序列化后的任何 proto 都必须小于 2 GiB，因为这是所有实现所支持的最大大小。建议为请求和响应的大小设置上限。

## Proto 反序列化的深度限制 {#depth}

*   Java：
    100
*   C++：
    100
*   Go：
    10000
    （有计划将其降至 100）

如果你尝试反序列化一条嵌套深度超过该限制的消息，反序列化将会失败。
