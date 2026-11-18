+++
title = "Rust 中的脱敏"
weight = 783
linkTitle = "Rust 中的脱敏"
description = "介绍 Rust 中的脱敏。"
type = "docs"
source_url = "https://protobuf.dev/reference/rust/rust-redaction/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

<!--*
# Document freshness: For more information, see go/fresh-source.
freshness: { owner: 'esrauch' reviewed: '2024-07-26' }
*-->

在 Protobuf 消息（message）上使用标准的 `fmt::Debug`（格式化字符串中的 "`{:?}`"）来生成人类可读的字符串，适用于日志、错误消息、异常及类似用例。此类调试信息的输出并非面向机器可读（与 `TextFormat` 和 `JSON` 不同，这两者[不应被用于调试输出](/best-practices/dos-donts#text-format-interchange)）。

使用 `fmt::Debug` 可以对部分敏感字段（field）进行脱敏（redaction）。

请注意，在 upb 内核下这一脱敏功能尚未实现，但预计将来会增加。
