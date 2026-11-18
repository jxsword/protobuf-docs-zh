+++
title = "Abseil 支持"
weight = 530
linkTitle = "Abseil 支持"
description = "Protobuf 的 C++ 实现显式依赖 Abseil。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/abseil/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

从 [版本 22.x](/news/v22#abseil-dep) 起，C++ Protobuf 对 Abseil 添加了显式依赖。

## Bazel 支持 {#bazel}

如果你使用 Bazel，要确定你的 Protobuf 版本支持哪个 Abseil 版本，可以使用 `bazel mod` 命令：

```shell
$ bazel mod deps abseil-cpp --enable_bzlmod
<root> (protobuf@30.0-dev)
└───abseil-cpp@20240722.0
    ├───bazel_skylib@1.7.1
    ├───googletest@1.15.2
    └───platforms@0.0.10
```

`bazel mod graph` 会生成完整输出：

```shell
$ bazel mod graph --enable_bzlmod
<root> (protobuf@30.0-dev)
├───abseil-cpp@20240722.0
│   ├───bazel_skylib@1.7.1 (*)
│   ├───googletest@1.15.2 (*)
│   └───platforms@0.0.10 (*)
├───bazel_features@1.18.0
│   └───bazel_skylib@1.7.1 (*)
├───bazel_skylib@1.7.1
│   ├───platforms@0.0.10 (*)
│   └───rules_license@1.0.0 (*)
├───googletest@1.15.2
│   ├───abseil-cpp@20240722.0 (*)
│   ├───platforms@0.0.10 (*)
│   └───re2@2024-07-02
...
```

## CMake 支持 {#cmake}

与 Bazel 相比，我们的 CMake 支持属于尽力而为（best-effort）。要检查是否受支持，请尝试以下步骤：

1.  运行 `cmake .` 命令。
2.  打开 `_deps/absl-src/CMakeLists.txt`。

查找如下内容：

```
project(absl LANGUAGES CXX VERSION 20240722)
set(ABSL_SOVERSION "2407.0.0")
include(CTest)
```
