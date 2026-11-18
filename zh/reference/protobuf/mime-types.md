+++
title = "Protobuf MIME 类型"
weight = 830
linkTitle = "MIME 类型"
description = "Protobuf 各序列化格式对应的标准 MIME 类型。"
type = "docs"
source_url = "https://protobuf.dev/reference/protobuf/mime-types/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

所有 Protobuf 文档的 MIME 类型（MIME type）都应为 `application`，子类型（subtype）应为 `protobuf`；采用 JSON 编码（encoding）时，还应依据[该标准](https://datatracker.ietf.org/doc/draft-murray-dispatch-mime-protobuf/)添加 `+json` 后缀，其后可接以下参数：

-   `encoding` 参数只能设置为 `binary` 或 `json`，分别表示相应的格式。
    +   子类型为 `protobuf+json` 时，`encoding` 的默认值（default value）为 `json`，且不能设置为 `binary`；子类型为 `protobuf`（不带 `+json`）时，`encoding` 的默认值为 `binary`，且不能设置为 `json`。
    +   即使在为缓解 CORB 而使用了解析中断符（parser breaker）的 HTTP 响应中，JSON 也应使用 `+json`。
-   对于所有 JSON 编码与文本格式（text format）编码，都应将 `charset` 设置为 `utf-8`；对于二进制编码，则切勿设置该参数。
    +   如果未指定 `charset`，则假定其为 UTF-8。最好始终指定 `charset`，因为当 proto 用于 HTTP 响应时，这样做有助于防范某些攻击向量（attack vector）。
-   Protobuf 为自身线路格式（wire format）将来可能的版本化保留了 `version` 参数。在线路格式正式引入版本机制之前，请勿设置该参数。

因此，常见 Protobuf 编码对应的标准 MIME 类型为：

-   `application/protobuf`：用于已序列化（serialized）的二进制 proto。
-   `application/protobuf+json; charset=utf-8`：用于 JSON 格式的 proto。

读取 Protobuf 的服务（service）还应能够处理 `application/json`，该类型也可能用于编码 JSON 格式的 proto。

如果 MIME 参数（`encoding`、`charset` 或 `version`）的取值未知或非法，解析器（parser）必须失败。

当二进制 proto 通过 HTTP 传输时，Protobuf 强烈建议先对其进行 Base64 编码，并设置 `X-Content-Type-Options: nosniff`，以防 XSS，因为 proto 有可能被解析为活动内容（active content）。

如有需要，也可以向这些 MIME 类型传递附加参数，例如用于指示内容模式（schema）的类型 URL；但 MIME 类型参数***不得***包含编码选项（options）。
