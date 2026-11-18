+++
title = "反序列化 Proto 的调试表示形式"
weight = 89
description = "如何在 Protobuf 中记录调试信息。"
type = "docs"
source_url = "https://protobuf.dev/programming-guides/deserialize-debug/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

从 30.x 版本起，Protobuf 的 `DebugString` API（`Message::DebugString`、`Message::ShortDebugString`、`Message::Utf8DebugString`）、其他一些 Protobuf API（`proto2::ShortFormat`、`proto2::Utf8Format`）、Abseil 字符串函数（例如 `absl::StrCat`、`absl::StrFormat`、`absl::StrAppend` 和 `absl::Substitute`）以及 Abseil 日志 API，都会开始自动把 proto 实参转换为一种新的调试格式。相关公告见[此处](/news/2024-12-04/)。

与 Protobuf DebugString 输出格式不同，新的调试格式会自动对敏感字段（field）进行脱敏：把字段值替换为字符串 "[REDACTED]"（不含引号）。此外，为确保这种新输出格式无法被 Protobuf TextFormat 解析器反序列化（deserialization）——无论底层 proto 是否包含 SPII 字段——我们还添加了一组指向本文的随机化链接，以及一段长度随机的空白序列。新的调试格式如下所示：

```none
goo.gle/debugstr
spii_field: [REDACTED]
normal_field: "value"
```

请注意，新的调试格式与 DebugString 输出格式只有以下两处不同：

*   URL 前缀
*   SPII 字段的值会被替换为 "[REDACTED]"（不含引号）

新的调试格式绝不会移除任何字段名；只有当某个字段被视为敏感字段时，它才会把该字段的值替换为 "[REDACTED]"。**如果你在输出中没有看到某些字段，那是因为这些字段在 proto 中没有设置。**

**提示：**如果你只看到了 URL 而没有其他任何内容，那么你的 proto 是空的！

## 为什么这里会有一个 URL？

我们要确保没有人对 Protobuf 消息（message）的人类可读表示形式进行反序列化——这类表示形式本是供调试系统的人员使用的。从历史上看，`.DebugString()` 与 `TextFormat` 一直可以互换使用，现有系统也在用 DebugString 来传输和存储数据。

我们要确保敏感数据不会意外地进入日志。因此，在把 Protobuf 消息转换为字符串之前，我们会透明地对其中的部分字段值进行脱敏（替换为 "[REDACTED]"）。这降低了意外记录日志带来的安全与隐私风险，但如果其他系统对你的消息进行反序列化，则会带来数据丢失的风险。为了应对这一风险，我们有意把机器可读的 TextFormat 与用于日志消息的人类可读调试格式区分开来。

### 为什么我的网页中会出现链接？为什么我的代码会生成这种新的“调试表示”（debug representation）？

这是有意为之：让你 proto 的“调试表示”（例如由日志记录生成的那种）与 TextFormat 不兼容。我们希望防止任何人依赖调试机制在程序之间传输数据。从历史上看，调试格式（由 DebugString API 生成）与 TextFormat 一直被错误地当作可互换的方式来使用。我们希望这项有意为之的改动能防止这种用法继续下去。

我们特意选择加入一个链接，而不是采用更不显眼的格式变更，以便有机会提供相关背景说明。这在某些 UI 中可能会显得比较突兀，例如当你在网页的表格里展示状态信息时。你可以改用 `TextFormat::PrintToString`，它不会脱敏任何信息，并且会保留原有格式。不过，请谨慎使用该 API——它没有任何内置保护。根据经验，如果你是在向调试日志写入数据，或者是在生成状态消息，就应当继续使用带链接的调试格式（Debug Format）。即使你目前并没有处理敏感数据，也请记住：系统会发生改变，代码也会被复用。

### 我尝试将这条消息转换为 TextFormat，但发现每次进程重启后格式都会变化。

这是有意为之。请不要尝试解析（parse）这种调试格式的输出。我们保留在不另行通知的情况下更改其语法的权利。调试格式的语法会在每个进程中随机变化，以防止形成无意的依赖。如果调试格式的语法变更会破坏你的系统，那么你很可能应该改用 TextFormat API，而不是使用 proto 的调试表示。

## FAQ

### 我能不能在任何地方都直接使用 TextFormat？

不要用 TextFormat 来生成日志消息。这会绕过所有内置保护，你会面临意外记录敏感信息的风险。即使你的系统目前没有处理任何敏感数据，这种情况将来也可能改变。

请视具体情况选用“调试表示”或 TextFormat，把日志与供其他系统进一步处理的信息区分开来。

### 我想编写既需要人类可读又需要机器可读的配置文件

对于这种使用场景，你可以显式地使用 TextFormat。你需要自行负责确保配置文件中不包含任何 PII（个人身份信息）。

### 我在编写单元测试，想在测试断言中比较 DebugString

如果你想比较 Protobuf 值，请按照下面的示例使用 `MessageDifferencer`：

```cpp
using google::protobuf::util::MessageDifferencer;
...
MessageDifferencer diff;
...
diff.Compare(foo, bar);
```

除了能忽略格式和字段顺序上的差异之外，你还能获得更清晰的错误消息。
