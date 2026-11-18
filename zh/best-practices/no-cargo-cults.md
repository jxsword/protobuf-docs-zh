+++
title = "避免盲目照搬（Cargo Culting）"
weight = 90
description = "避免使用并非必需的特性。"
type = "docs"
source_url = "https://protobuf.dev/best-practices/no-cargo-cults/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-18"
status = "translated"
translator = "agent"
+++

不要在 proto 文件中[盲目照搬（cargo cult）](https://en.wikipedia.org/wiki/Cargo_cult_programming)各项设置。如果你要基于现有的模式（schema）定义创建新的 proto 文件，请不要套用选项（option）设置，除非你理解为什么需要这些设置。

## 版次（Editions）特有的最佳实践 {#editions}

除非确实有必要，否则请避免应用[版次特性（editions features）](/editions/features)。`.proto` 文件中的特性设置表明使用了实验性的未来行为，或已弃用的过往行为。最新版次的最佳实践始终会作为默认值。新的 proto 模式定义内容应保持不设置任何特性，除非你想提前采用某项特性，以获得正在逐步推出的未来行为。

在不理解这些特性为何设置的情况下照搬沿用特性设置，可能导致你的代码出现意外行为。
