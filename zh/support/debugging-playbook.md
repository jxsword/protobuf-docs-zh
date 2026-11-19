+++
title = "调试"
weight = 915
description = "调试 Protobuf 中的常见问题。"
type = "docs"
source_url = "https://protobuf.dev/support/debugging-playbook/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-20"
status = "translated"
translator = "agent"
+++

Protobuf 用户经常遇到的常见问题与调试场景。

<!--*
# Document freshness: For more information, see go/fresh-source.
freshness: { owner: 'sangki' reviewed: '2026-05-18' }
*-->

## Bazel：解决预构建 protoc 的相关问题 {#prebuilt-protoc}

如[这篇新闻文章](/news/2026-01-16)所述，Bazel 7 及更高版本支持使用预构建 protoc 进行构建。在一切配置正确的情况下，这可以节省大量构建时间、减少日志量，并消除非 C++ 实现对 C++ 工具链（toolchain）的需求。

为防止 protoc 从源码编译，请将以下内容添加到你的 `.bazelrc` 文件中：

```bazel
common --per_file_copt=external/.*protobuf.*@--PROTOBUF_WAS_NOT_SUPPOSED_TO_BE_BUILT
common --host_per_file_copt=external/.*protobuf.*@--PROTOBUF_WAS_NOT_SUPPOSED_TO_BE_BUILT
common --per_file_copt=external/.*grpc.*@--GRPC_WAS_NOT_SUPPOSED_TO_BE_BUILT
common --host_per_file_copt=external/.*grpc.*@--GRPC_WAS_NOT_SUPPOSED_TO_BE_BUILT
```

当依赖图中存在可到达 `@com_google_protobuf//:protoc` 的硬编码引用时，protoc 会在这些情况下被强制从源码构建，从而使这一优势失效。要解决这个问题，你需要找到这些依赖所在的位置，并请求更新相应的规则集。

要查找你在何处依赖 protoc，请使用以下命令：

```none
bazel cquery 'somepath("//...", "@com_google_protobuf//:all")'
```

**注意：** 预构建产物仅适用于我们的标准平台集合。使用非标准平台的用户必须从源码构建 protoc。

## Protostats Flume 流水线

Protostats 流水线通过一个 Plx 工作流运行在 borg 上，该工作流由 google3/net/proto2/tools/internal/protostats 中的文件定义，并且运行需要配额。配额取自 `gpi-flex-pool`。目前，Borg 配额已为 `protobuf-stats` 用户在 3 个不同的 cell（集群单元）中注册：`yq`、`viatlrb` 和 `vibrura`。后两者是 go/virtual-cells（虚拟 cell）。cell 的多样性与虚拟 cell 的使用都是为了提供冗余，以防范由真实资源约束或偶发 DiRT 演练造成的资源短缺（stockout）。如需调整注册，请参阅 google3/net/proto2/tools/internal/protostats/BUILD 中的说明。
