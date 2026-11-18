+++
title = "构建 Rust Proto"
weight = 784
linkTitle = "构建 Rust Proto"
description = "介绍如何使用 Cargo 或 Bazel 构建 Rust Proto。"
type = "docs"
source_url = "https://protobuf.dev/reference/rust/building-rust-protos/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

## Cargo

有关如何设置构建的示例，请参见 [protobuf-example](https://docs.rs/crate/protobuf-example/latest/source/) crate。

## Bazel

为 Protobuf 定义构建 Rust 库的过程与其他编程语言类似：

1.  使用与语言无关的 `proto_library` 规则：

    ```build
    proto_library(
        name = "person_proto",
        srcs = ["person.proto"],
    )
    ```

2.  创建一个 Rust 库：

    ```build {highlight="lines:1,8-11"}
    load("//third_party/protobuf/rust:defs.bzl", "rust_proto_library")

    proto_library(
        name = "person_proto",
        srcs = ["person.proto"],
    )

    rust_proto_library(
        name = "person_rust_proto",
        deps = [":person_proto"],
    )
    ```

3.  通过将该库包含在 Rust 二进制程序中来使用它：

    ```build {highlight="lines:1,14-20"}
    load("//devtools/rust/build_defs:rules.bzl", "rust_binary")
    load("//third_party/protobuf/rust:defs.bzl", "rust_proto_library")

    proto_library(
        name = "person_proto",
        srcs = ["person.proto"],
    )

    rust_proto_library(
        name = "person_rust_proto",
        deps = [":person_proto"],
    )

    rust_binary(
        name = "greet",
        srcs = ["greet.rs"],
        deps = [
            ":person_rust_proto",
        ],
    )
    ```

{{% alert title="Note" color="note" %}} 不要直接使用 `rust_upb_proto_library` 或 `rust_cc_proto_library`。`rust_proto_library` 会检查全局构建标志，为你选择合适的后端。 {{% /alert %}}
