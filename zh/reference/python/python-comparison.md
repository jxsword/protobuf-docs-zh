+++
title = "Python 比较"
weight = 751
linkTitle = "Python 比较"
description = "描述 Python 如何比较对象。"
type = "docs"
source_url = "https://protobuf.dev/reference/python/python-comparison/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

由于 proto 数据的序列化（serialization）方式，你无法依赖 proto 消息（message）实例的线路表示来判断其内容是否与另一个实例相同。线路格式（wire format）的 proto 消息实例可能产生差异的方式包括以下几种（仅为其中一部分）：

*   Protobuf 模式（schema）以某些方式发生变化。
*   map 字段以不同的顺序存储其值。
*   二进制文件以不同的标志构建（例如 opt 与 debug）。
*   Protobuf 库进行了更新。

由于序列化数据可能以这些方式产生差异，判断相等性需要借助其他方法。

## 比较方法 {#methods}

你可以使用标准的 Python `==` 运算符来比较 Protobuf 消息是否相等。使用 `==` 运算符比较两个对象时，比较通过 `message.ListFields()` 进行。在测试中，你可以使用 `self.assertEqual(msg1, msg2)`。

如果两个消息的类型相同且所有对应字段都相等，则这两个消息被视为相等。不等运算符 `!=` 正好是 `==` 的反向。

消息相等性是递归的：要使两个消息相等，其中包含的任何嵌套消息（nested messages）也必须相等。

## 字段相等性与存在性

字段的相等性检查基于值进行。对于具有[显式存在性（explicit presence）](#singular-explicit)的字段，其存在性也会被纳入考量。

被显式设置为默认值（default value）的字段与未设置的字段**不**视为相等。

例如，考虑下面这条含有显式存在性字段的消息：

```proto
edition = "2023";
message MyMessage {
  int32 value = 1; // 在 Editions 中默认为 'explicit' 存在性
}
```

如果你创建两个实例，其中一个未设置 `value`，另一个将 `value` 显式设置为 `0`，那么二者将不相等：

```python
msg1 = MyMessage()
msg2 = MyMessage()
msg2.value = 0

assert not msg1.HasField("value")
assert msg2.HasField("value")
assert msg1 != msg2
```

同样的原则也适用于子消息（sub-message）字段：未设置的子消息不等于已存在但为空的子消息（即该子消息类的默认实例）。

对于具有[隐式存在性（implicit presence）](#singular-implicit)的字段，由于无法追踪其存在性，该字段始终按值与另一个消息中的对应字段进行比较。

这种把存在性纳入相等性检查的行为，有别于某些其他语言或 Protobuf 库可能采取的相等性处理方式——后者有时会把未设置的字段与设置为默认值的字段视为等价（通常是为了保证线路格式兼容性）。在 Python 中，`==` 会执行更严格的检查。

## 其他字段类型 {#other-types}

*   **可重复字段（repeated fields）**在元素数量相同且每个对应元素都相等时视为相等。元素的顺序很重要。
*   **map 字段**在键值对（key-value pairs）集合相同时视为相等。键值对的顺序无关紧要。
*   **浮点数字段（floating-point fields）**（`float` 和 `double`）按值进行比较。请留意浮点数比较中常见的陷阱。
