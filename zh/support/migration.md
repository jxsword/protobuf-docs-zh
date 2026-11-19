+++
title = "迁移指南"
weight = 920
description = "对各库版本所作破坏性变更的清单，以及如何更新你的代码以适应这些变更。"
aliases = "/programming-guides/migration/"
type = "docs"
source_url = "https://protobuf.dev/support/migration/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

## v34.0 中的变更 {#v34}

以下是各库版本中破坏性变更（breaking change）的清单，以及如何更新你的代码以适应这些变更。

本文涵盖 [v34.x 新闻公告](/news/2025-09-19)和 [v34.0 发布说明](https://github.com/protocolbuffers/protobuf/releases/tag/v34.0)中宣布的破坏性变更。

### C++ 中的变更 {#v34-cpp}

C++ 在 7.34.0 发布（release）中将主版本（major version）提升至 7。6.33 是 6.x 系列的最后一个次版本发布。

#### 移除 Future 宏

以下宏是为分阶段推出破坏性变更而引入的，现已被移除，其行为已成为默认行为：

*   `PROTOBUF_FUTURE_RENAME_ADD_UNUSED_IMPORT`
*   `PROTOBUF_FUTURE_REMOVE_ADD_IGNORE_CRITERIA`
*   `PROTOBUF_FUTURE_STRING_VIEW_DESCRIPTOR_DATABASE`
*   `PROTOBUF_FUTURE_NO_RECURSIVE_MESSAGE_COPY`
*   `PROTOBUF_FUTURE_REMOVE_REPEATED_PTR_FIELD_ARENA_CONSTRUCTOR`
*   `PROTOBUF_FUTURE_REMOVE_MAP_FIELD_ARENA_CONSTRUCTOR`
*   `PROTOBUF_FUTURE_REMOVE_REPEATED_FIELD_ARENA_CONSTRUCTOR`

#### RepeatedPtrField 的新布局 {#cpp-repeatedptrfield-layout}

`RepeatedPtrField` 已迁移到新的内部元素布局：元素存储在连续的预分配内存块中，类似于 `std::deque`。这导致部分 API 的拷贝/移动语义发生变化，并且一些 `UnsafeArena` API 可能会在功能上变得与其 arena 安全版本等价，进而被弃用（deprecated）。

#### RepeatedField::Get 与 RepeatedPtrField::Get 上的 MSB 加固检查 {#cpp-repeatedfield-get-hardening}

Protobuf 通过为可重复字段（repeated field）访问添加全面的边界检查，强化了对越界（OOB）错误的防护。

#### 从 Repeated/Map 字段中移除启用 arena 的构造函数 {#cpp-remove-arena-ctors}

`RepeatedField(Arena*)`、`RepeatedPtrField(Arena*)` 和 `Map(Arena*)` 构造函数已被删除。

#### 移除已弃用的 API {#cpp-remove-apis}

我们移除了以下公开的运行时（runtime）API。

##### AddUnusedImportTrackFile() 与 ClearUnusedImportTrackFiles()

**API：** `AddUnusedImportTrackFile()`、`ClearUnusedImportTrackFiles()`

**替代方案：** `AddDirectInputFile()` 和 `ClearDirectInputFiles()`

##### 消息差异比较器（message differencer）中的 AddIgnoreCriteria

我们曾为该破坏性变更引入 `PROTOBUF_FUTURE_REMOVE_ADD_IGNORE_CRITERIA` 宏，现已将其移除。

**API：** `AddIgnoreCriteria()`

**替代方案：** 将裸指针封装在 `unique_ptr` 中。

##### FieldDescriptor::has_optional_keyword()

**API：** `FieldDescriptor::has_optional_keyword()`

**替代方案：** `has_presence()`

##### FieldDescriptor::label()

**API：** `FieldDescriptor::label()`

**替代方案：** `is_repeated()` 或 `is_required()`

##### FieldDescriptor::is_optional()

**API：** `FieldDescriptor::is_optional()`

**替代方案：** `!is_required() && !is_repeated()`

##### UseDeprecatedLegacyJsonFieldConflicts()

**API：** `UseDeprecatedLegacyJsonFieldConflicts()`

**替代方案：** 无替代方案。

#### 更严格的名称长度限制 {#cpp-name-limits}

为防止潜在问题，Protobuf 编译器对字段名（field name）等符号名称的长度强制执行更严格的限制。如果任何字段名的长度 > 2^16，就会生成错误。

#### 在 CMake 中隐藏私有生成器头文件 {#cpp-cmake-headers}

protoc 生成器头文件不再由 CMake 安装。这对大多数用户应无影响。

#### 逻辑常量操作上的 [[nodiscard]] {#cpp-nodiscard}

多个逻辑上恒定的 Protobuf API 已添加 `[[nodiscard]]`——在这些 API 上，未使用返回值往往意味着存在 bug。这遵循了 C++ 标准库中常用的模式。

### Python 中的变更 {#v34-python}

Python 在 7.34.0 发布中将主版本提升至 7。6.33 是 6.x 系列的最后一个次版本发布。

#### 停止支持 Python 3.9

最低支持的 Python 版本为 3.10，用户应升级。

#### 放宽毒丸（poison pill）警告

我们放宽了毒丸机制。对于 7.34.x，旧的生成文件不会再触发任何警告或错误。

#### 以不正确的类型转换为 Timestamp 或 Duration 时抛出 TypeError

现在，将错误的类型转换为 `Timestamp` 或 `Duration` 时，会抛出 `TypeError` 而不是 `AttributeError`。

#### 拒绝将 bool 赋给 enum 和 int 字段

现在，我们拒绝用布尔值为 `enum` 或 `int` 字段赋值。API 会抛出错误，而不是进行隐式转换。

#### 从 json_format 中移除 float_precision

我们从 `json_format` 序列化器中移除了已弃用的 `float_precision` 选项。其他 ProtoJSON 序列化器中不存在该选项，且其语义容易引起混淆。

#### 从 text_format 中移除 float_format/double_format

我们从 `text_format` 中移除了已弃用的 `float_format` 和 `double_format` 选项。这些选项在其他 proto 文本格式（text format）序列化器中也不可用。

#### 移除已弃用的 API {#v34-php-remove-apis}

我们移除了以下公开的运行时 API。

##### FieldDescriptor.label

**API：** `FieldDescriptor.label`

**替代方案：** `is_repeated()` 或 `is_required()`

### PHP 中的变更 {#v34-php}

PHP 在 5.34.0 发布中将主版本提升至 5。4.33 是 4.x 系列的最后一个次版本发布。

#### 停止支持 PHP 8.1

最低支持的 PHP 版本为 8.2，用户应升级。

#### 移除已弃用的 API {#v34-php-remove-apis}

我们移除了以下公开的运行时 API。

##### FieldDescriptor getLabel

**API：** `FieldDescriptor getLabel`

**替代方案：** `isRepeated()` 或 `isRequired()`

##### Google\Protobuf\Field_Kind

**API：** `Google\Protobuf\Field_Kind`

**替代方案：** `Google\Protobuf\Field\Kind`

##### Google\Protobuf\Field_Cardinality

**API：** `Google\Protobuf\Field_Cardinality`

**替代方案：** `Google\Protobuf\Field\Cardinality`

##### Google\Protobuf\Internal\RepeatedField

**API：** `Google\Protobuf\Internal\RepeatedField`

**替代方案：** `Google\Protobuf\RepeatedField`

#### 修复默认值被静默忽略的问题

我们修复了 PHP 运行时，使其遵循 proto2 与 Editions 中标量（scalar）字段的默认值，而不是静默忽略它们。

#### 类型检查对齐

纯 PHP 实现与 upb-PHP 实现的类型检查现已对齐。值得注意的是，纯 PHP 实现现在会拒绝为字符串字段设置 `null`，与 upb-PHP 的行为保持一致。

### Objective-C 中的变更 {#v34-objc}

Objective-C 在 5.34.0 发布中将主版本提升至 5。4.33 是 4.x 系列的最后一个次版本发布。

#### 可空性注解

某些 `GPB*Dictionary` API 的可空性（nullability）注解已得到修正，以标明 API 何时可能返回 `nil`。这会使 Swift 代码获得 Swift 的 `Optional<T>`。对于 Objective-C 调用者而言，该注解修正不太可能对源代码产生任何影响。

#### 移除已弃用的 API {#v34-objc-remove-apis}

我们移除了以下公开的运行时 API。

##### GPBFieldDescriptor optional

**API：** -[`GPBFieldDescriptor optional`]

**替代方案：** `!required && fieldType == GPBFieldTypeSingle`

### 其他变更 {#v34-other}

#### 停止支持 Bazel 7

最低支持的 Bazel 版本为 8，这会将默认方式从 WORKSPACE 改为 Bzlmod。用户应升级到 Bazel 8 或更高版本，并迁移到 Bzlmod。

#### Bazel：移除已弃用的 ProtoInfo.transitive_imports

`ProtoInfo` 中已弃用的 `transitive_imports` 字段已被移除。用户应迁移到 `transitive_sources`。

#### 移除 protobuf_allow_msvc 标志并继续支持 Bazel+MSVC

由于 Bazel 近期在 Windows 上的改进，我们现将继续支持 Bazel+MSVC。`--define=protobuf_allow_msvc` 标志已被移除。

## v30.0 中的变更 {#v30}

以下是各库版本中破坏性变更的清单，以及如何更新你的代码以适应这些变更。

本文涵盖 [v30.x 新闻公告](/news/v30)和 [v30.0 发布说明](https://github.com/protocolbuffers/protobuf/releases/tag/v30.0)中宣布的破坏性变更。

### C++ 中的变更 {#v30-cpp}

#### 用拉取的依赖取代 CMake 子模块

此前，我们默认的 CMake 行为是使用 Git 子模块获取固定版本的依赖。指定 `-Dprotobuf_ABSL_PROVIDER=package` 会将 CMake 配置切换为查找本机安装的 Abseil（jsoncpp 和 gtest 也有类似选项）。这些选项已不复存在；现在的默认行为是先查找所有依赖的已有安装，必要时再回退为从 GitHub 拉取固定版本。

要禁止任何回退拉取（类似于旧的 `package` 行为），可以这样调用 CMake：

```cmake
cmake . -Dprotobuf_LOCAL_DEPENDENCIES_ONLY=ON
```

要*始终*以固定版本拉取依赖（类似于旧的默认行为），可以这样调用 CMake：

```cmake
cmake . -Dprotobuf_FORCE_FETCH_DEPENDENCIES=ON
```

#### string_view 返回类型

以下描述符（descriptor）API 的返回类型现在是 `absl::string_view`（字符串视图），这带来了节省内存的空间：

*   `MessageLite::GetTypeName`
*   `UnknownField::length_delimited`
*   描述符 API 的名称函数，例如 `FieldDescriptor::full_name`

我们预计未来的破坏性发布将继续把更多 API 迁移到 `absl::string_view`。

在大多数情况下，应在安全的前提下尽量将类型更新为使用 `absl::string_view`，必要时再显式拷贝回原类型。如果某函数返回该类型，可能还需要相应更新其调用方。

如果受影响 API 方法返回的字符串被用作以下类型：

<table>
  <tr>
    <th>类型</th>
    <th>迁移方式</th>
  </tr>
  <tr>
    <td>
      <p><code>std::string</code></p>
    </td>
    <td>
      <p>显式转换为 <code>std::string</code>，以保持现有行为。</p>
      <p>或者，切换到性能更好的 <code>absl::string_view</code>。</p>
    </td>
  </tr>
  <tr>
    <td>
      <p><code>const std::string&</code></p>
    </td>
    <td>
      <p>迁移到 <code>absl::string_view</code>。</p>
      <p>如果不可行（例如由于依赖数量庞大），拷贝为 <code>std::string</code> 可能更容易。</p>
    </td>
  </tr>
  <tr>
    <td>
      <p><code>const std::string*</code></p>
      <p><code>const char*</code></p>
    </td>
    <td>
      <p>如果可为空（nullable），迁移到 <code>std::optional&lt;absl::string_view&gt;</code>。</p>
      <p>否则，迁移到 <code>absl::string_view</code>。</p>
      <p>调用 <code>data()</code> 时要小心，因为 <code>absl::string_view</code> 不保证以空字符结尾。
    </td>
  </tr>
</table>

对于常见容器和其他 API，或许可以迁移到与 `absl::string_view` 兼容的变体。下面是一些常见示例。

<table>
  <tr>
    <th>类别</th>
    <th>迁移前</th>
    <th>迁移方式</th>
  </tr>
  <tr>
    <td>向 <code>std::vector&lt;std::string&gt;</code> 插入</td>
    <td>
      <p><code>push_back()</code></p>
      <p><code>push_front()</code></p>
      <p><code>push()</code></p>
    </td>
    <td>
      <p><code>emplace_back()</code></p>
      <p><code>emplace_front()</code></p>
      <p><code>emplace()</code></p>
    </td>
  </tr>
  <tr>
    <td>map 或 set 的插入</td>
    <td>
      <p><code>set.insert(key)</code></p>
      <p><code>map.insert({key, value})</code></p>
      <p><code>map.insert({key,<br/>  {value_params...}})</code></p>
    </td>
    <td>
      <p><code>set.emplace(key)</code></p>
      <p><code>map.emplace(key, value)</code></p>
      <p><code>map.try_emplace(key,<br/>  value_params...)</code></p>
    </td>
  </tr>
  <tr>
    <td>map 或 set 的查找</td>
    <td>
      <p><code>find()</code></p>
      <p><code>count()</code></p>
      <p><code>contains()</code></p>
    </td>
    <td>
      <p>迁移到 Abseil 容器。</p>
      <p>或者，定义一个透明比较器。</p>
      <p><code>std::set&lt;std::string, std::less&lt;&gt;&gt;<br/>
      std::map&lt;std::string, T, std::less&lt;&gt;&gt;</code></p>
      <p>参见 <a href="https://abseil.io/tips/144">https://abseil.io/tips/144</a></p>
    </td>
  </tr>
  <tr>
    <td>字符串拼接</td>
    <td>
      <p><code>operator+</code></p>
      <p><code>operator+=</code></p>
    </td>
    <td>
      <p><code>absl::StrCat()</code></p>
      <p><code>absl::StrAppend()</code></p>
      <p>出于性能考虑，本来就推荐使用它们。参见 <a href="https://abseil.io/tips/3">https://abseil.io/tips/3</a>。</p>
   </td>
  </tr>
</table>

有关使用 `absl::string_view` 的一般技巧，另请参阅 [https://abseil.io/tips/1](https://abseil.io/tips/1)。

#### 封禁 MSVC + Bazel

Windows 上的 Bazel 用户应切换到 clang-cl，将以下内容添加到自己的项目中，可参考这个[示例](https://github.com/protocolbuffers/protobuf/commit/117e7bbe74ac7c7faa9b6f44c1b22de366302854#diff-48bcd3965c4a015a8f61ad82b225790209baef37363ee0478519536a620a85e5)。

**.bazelrc**

```bazel
common --enable_platform_specific_config build:windows
--extra_toolchains=@local_config_cc//:cc-toolchain-x64_windows-clang-cl
--extra_execution_platforms=//:x64_windows-clang-cl
```

**MODULE.bazel**

```bazel
bazel_dep(name = "platforms", version = "0.0.10")
bazel_dep(name = "rules_cc", version = "0.0.17")

# 用于 clang-cl 配置
cc_configure = use_extension("@rules_cc//cc:extensions.bzl", "cc_configure_extension")
use_repo(cc_configure, "local_config_cc")
```

**WORKSPACE**

```bazel
load("//:protobuf_deps.bzl", "PROTOBUF_MAVEN_ARTIFACTS", "protobuf_deps")

protobuf_deps()

load("@rules_cc//cc:repositories.bzl", "rules_cc_dependencies", "rules_cc_toolchains")

rules_cc_dependencies()

rules_cc_toolchains()
```

**BUILD**

适用于只需兼容 Bazel 8 的用户。

```bazel
platform(
    name = "x64_windows-clang-cl",
    constraint_values = [
        "@platforms//cpu:x86_64",
        "@platforms//os:windows",
        "@bazel_tools//tools/cpp:clang-cl",
    ],
)
```

适用于需要同时兼容 Bazel 7 和 8 的用户。

```bazel
platform(
    name = "x64_windows-clang-cl",
    constraint_values = [
        "@platforms//cpu:x86_64",
        "@platforms//os:windows",
        # 参见 https://github.com/bazelbuild/rules_cc/issues/330。
        "@rules_cc//cc/private/toolchain:clang-cl",
    ],
)
```

用户也可以通过设置选择性退出标志 `--define=protobuf_allow_msvc=true` 来临时屏蔽该错误，直到下一个破坏性发布为止。

另外，希望继续使用 MSVC 的用户可以改用 CMake。这可以通过 [Visual Studio](https://learn.microsoft.com/en-us/cpp/build/cmake-projects-in-visual-studio?view=msvc-170) 完成，或者在 CMake 命令行中指定 MSVC 生成器。例如：

```cmake
cmake -G "Visual Studio 17 2022" -A Win64 .
```

#### 从 FieldDescriptor 选项中移除 ctype {#ctype-removed}

我们不再从 `FieldDescriptor` 选项中暴露 `ctype`。你可以改用在 [v28 发布版本](https://github.com/protocolbuffers/protobuf/releases/tag/v28.0)中添加的 `FieldDescriptor::cpp_string_type()` API。

#### 修改调试 API 以对敏感字段脱敏 {#debug-redaction}

Protobuf C++ 调试 API（包括 Protobuf AbslStringify、`proto2::ShortFormat`、`proto2::Utf8Format`、`Message::DebugString`、`Message::ShortDebugString`、`Message::Utf8DebugString`）已更改为对标注了 `debug_redact` 的敏感字段进行脱敏（redact）；这些 API 的输出包含按进程随机化的前缀，并且不再能被 Protobuf TextFormat 解析器解析。在大多数需要人类可读输出的场景（例如日志记录）中，用户应采用新的脱敏调试格式，或者考虑改用二进制格式（binary format）进行序列化（serialization）与反序列化（deserialization）。需要旧的、可反序列化格式的用户可以使用 `TextFormat.printer().printToString(proto)`，但它不会对敏感字段脱敏，因此应谨慎使用。

更多信息请参阅[2024 年 12 月 4 日发布的新闻](/news/2024-12-04.md)。

#### 移除已弃用的 API {#v30-cpp-remove-apis}

我们移除了以下公开的运行时 API。这些 API 至少已在一个次版本或主版本周期前被标记为弃用（例如通过 `ABSL_DEPRECATED`），且已过时或已有替代。

**API：** [`Arena::CreateMessage`](https://github.com/protocolbuffers/protobuf/blob/f4b57b98b08aec8bc52e6a7b762edb7a1b9e8883/src/google/protobuf/arena.h#L179)

**替代方案：** [`Arena::Create`](https://github.com/protocolbuffers/protobuf/blob/f4b57b98b08aec8bc52e6a7b762edb7a1b9e8883/src/google/protobuf/arena.h#L191)

**API：** [`Arena::GetArena`](https://github.com/protocolbuffers/protobuf/blob/237332ef92daf83a53e76decd6ac43c3fcee782b/src/google/protobuf/arena.h#L346)

**替代方案：** `value->GetArena()`

**API：** [`RepeatedPtrField::ClearedCount`](https://github.com/protocolbuffers/protobuf/blame/f4b57b98b08aec8bc52e6a7b762edb7a1b9e8883/src/google/protobuf/repeated_ptr_field.h#L1157)

**替代方案：** 迁移到 arena（参见[迁移指南](https://protobuf.dev/support/migration/#cleared-elements)）。

**API：** [`JsonOptions`](https://github.com/protocolbuffers/protobuf/blob/f4b57b98b08aec8bc52e6a7b762edb7a1b9e8883/src/google/protobuf/util/json_util.h#L22)

**替代方案：** `JsonPrintOptions`

#### 停止支持 C++14 {#drop-cpp-14}

按照 [基础 C++ 支持矩阵](https://github.com/google/oss-policies-info/blob/main/foundational-cxx-support-matrix.md)，本发布不再以 C++14 作为最低支持版本，而是将其提升到 17。

用户应升级到 C++17。

#### 在 arena 上清空 oneof 消息后引入 ASAN 毒化

此变更添加了一项影响使用 arena 的 C++ Protobuf 消息的加固检查。分配在 Protobuf arena 上的 oneof 消息现在会在调试模式下被清空，并在 ASAN 模式下被毒化。调用 `clear` 之后，再尝试使用该内存区域将在 ASAN 中作为 use-after-free（释放后使用）错误引发崩溃。

该实现要求 C++17。

#### 停止发布 C++ CocoaPods

我们停止了 C++ CocoaPods 发布，该发布自 v4.x.x 起就已损坏。C++ 用户应直接改用我们的 [GitHub 发布页](https://github.com/protocolbuffers/protobuf/releases)。

### Python 中的变更 {#v30-python}

Python 的主版本从 5.29.x 提升到 6.30.x。

#### 停止支持 Python 3.8

最低支持的 Python 版本为 3.9，用户应升级。

#### 移除 bazel/system_python.bzl 别名 {#python-remove-alias}

我们移除了旧的 `bazel/system_python.bzl` 别名。

请移除对 `system_python.bzl` 的直接引用，改用 `protobuf_deps.bzl`。如果确实需要直接引用，可使用它在 [v5.27.0](https://github.com/protocolbuffers/protobuf/commit/d7f032ad1596ceeabd45ca1354516c39b97b2551) 中迁移到的 `python/dist/system_python.bzl`。

#### 字段设置器校验的变更 {#python-setter-validation}

Python 与 upb 的字段设置器现在会校验版次（edition）2023 下的封闭式枚举（closed enum）。使用无效值更新封闭式枚举字段会产生错误。

#### 移除已弃用的 py_proto_library 宏

`protobuf.bzl` 中已弃用的内部 Bazel 宏 `py_proto_library` 已被移除。它由官方的 `py_proto_library` 取代，后者在 v29.x 中被迁移到 Protobuf 的 `bazel/py_proto_library`。在 v29.x 之前，该实现位于 `rules_python` 中。

#### 移除已弃用的 API {#v30-python-remove-apis}

我们移除了以下公开的运行时 API，它们至少已在一个次版本或主版本周期前被标记为弃用。

##### 反射（reflection）方法

**API：** [`reflection.ParseMessage`](https://github.com/protocolbuffers/protobuf/blob/7f395af40e86e00b892e812beb67a03564884756/python/google/protobuf/reflection.py#L40)、[`reflection.MakeClass`](https://github.com/protocolbuffers/protobuf/blob/7f395af40e86e00b892e812beb67a03564884756/python/google/protobuf/reflection.py#L66)

**替代方案：** `message_factory.GetMessageClass()`

##### 远程过程调用（RPC）服务（service）接口

**API：** [`service.RpcException`](https://github.com/protocolbuffers/protobuf/blob/21c545c8c5cec0b052dc7715b778f0353d37d02c/python/google/protobuf/service.py#L23)、[`service.Service`](https://github.com/protocolbuffers/protobuf/blob/21c545c8c5cec0b052dc7715b778f0353d37d02c/python/google/protobuf/service.py#L28)、[`service.RpcController`](https://github.com/protocolbuffers/protobuf/blob/21c545c8c5cec0b052dc7715b778f0353d37d02c/python/google/protobuf/service.py#L97) 和 [`service.RpcChannel`](https://github.com/protocolbuffers/protobuf/blob/21c545c8c5cec0b052dc7715b778f0353d37d02c/python/google/protobuf/service.py#L180)

**替代方案：** 从 2.3.0 版本开始，RPC 实现就不应再基于这些接口构建，而应提供针对特定 RPC 实现生成专用代码的代码生成器（code generator）插件（plugin）。

##### MessageFactory 和 SymbolDatabase 方法

**API：** [`MessageFactory.GetPrototype`](https://github.com/protocolbuffers/protobuf/blob/7f395af40e86e00b892e812beb67a03564884756/python/google/protobuf/message_factory.py#L145)、[`MessageFactory.CreatePrototype`](https://github.com/protocolbuffers/protobuf/blob/7f395af40e86e00b892e812beb67a03564884756/python/google/protobuf/message_factory.py#L165)、[`MessageFactory.GetMessages`](https://github.com/protocolbuffers/protobuf/blob/7f395af40e86e00b892e812beb67a03564884756/python/google/protobuf/message_factory.py#L185)、[`SymbolDatabase.GetPrototype`](https://github.com/protocolbuffers/protobuf/blob/7f395af40e86e00b892e812beb67a03564884756/python/google/protobuf/symbol_database.py#L54)、[`SymbolDatabase.CreatePrototype`](https://github.com/protocolbuffers/protobuf/blob/7f395af40e86e00b892e812beb67a03564884756/python/google/protobuf/symbol_database.py#L60) 和 [`SymbolDatabase.GetMessages`](https://github.com/protocolbuffers/protobuf/blob/7f395af40e86e00b892e812beb67a03564884756/python/google/protobuf/symbol_database.py#L66)

**替代方案：** `message_factory.GetMessageClass()` 和
`message_factory.GetMessageClassesForFiles()`。

##### GetDebugString

**API：** [`GetDebugString`](https://github.com/protocolbuffers/protobuf/blob/7f395af40e86e00b892e812beb67a03564884756/python/google/protobuf/pyext/descriptor.cc#L1510)

**替代方案：**

无替代方案。它仅存在于不再发布的 Python C++ 实现中，纯 Python 与 UPB 实现均不支持。

#### Python 中 map 字段的 setdefault 行为变更

对于 `ScalarMap`，`setdefault` 与 `dict` 类似，区别在于键（key）和值（value）都必须设置。`MessageMaps` 则会拒绝 `setdefault`。

#### Python 嵌套消息类的 \_\_qualname\_\_ 包含外层消息名称

Python 嵌套消息类的 `__qualname__` 现在包含外层消息的名称。此前，对于嵌套消息，`__qualname__` 与 `__name__` 的结果相同，都不包含外层消息名称。

例如：

```python
message Foo {
  message Bar {
    bool bool_field = 1;
  }
}
nested = test_pb2.Foo.Bar()
self.assertEqual('Bar', nested.__class__.__name__)
self.assertEqual('Foo.Bar', nested.__class__.__qualname__) # 之前为 'Bar'
```

### Objective-C 中的变更 {#v30-objc}

**这是 Objective-C 的第一个破坏性发布**。

Objective-C 的主版本从 3.x.x 提升到 4.30.x。

#### 全面改造未知字段（unknown fields）处理 API 并弃用大部分现有 API {#objc-field-handling}

我们弃用了 `GPBUnknownFieldSet`，并以 `GPBUnknownFields` 取而代之。新类型会保留未知字段在原始输入或 API 调用中的顺序，以确保消息写回时顺序所承载的语义得以维持。

作为其中一部分，`GPBUnknownField` 类型的 API 也有变化：几乎所有现有 API 都被弃用，同时新增了新的 API。

已弃用的属性 API：

*   `varintList`
*   `fixed32List`
*   `fixed64List`
*   `lengthDelimitedList`
*   `groupList`

已弃用的修改 API：

*   `addVarint:`
*   `addFixed32:`
*   `addFixed64:`
*   `addLengthDelimited:`
*   `addGroup:`

已弃用的初始化方法 `initWithNumber:`。

新的属性 API：

*   `type`
*   `varint`
*   `fixed32`
*   `fixed64`
*   `lengthDelimited`
*   `group`

该类型在其值中对单个字段编号建模，而不是把给定字段编号的所有值*分组*在一起。用于创建新字段的 API 是 `GPBUnknownFields` 类上的 `add*` API。

我们还弃用了 `-[GPBMessage unknownFields]`。作为替代，新增了用于提取和更新消息未知字段的 API。

#### 移除已弃用的 API {#v30-objc-remove-apis}

我们移除了以下公开的运行时 API，它们至少已在一个次版本或主版本周期前被标记为弃用。

##### GPBFileDescriptor

**API：**
[-[`GPBFileDescriptor` syntax]](https://github.com/protocolbuffers/protobuf/blob/44bd65b2d3c0470d91a23cc14df5ffb1ab0af7cd/objectivec/GPBDescriptor.h#L118-L119)

**替代方案：** 已过时。

##### GPBMessage mergeFrom:extensionRegistry

**API：**
[-[`GPBMessage mergeFrom:extensionRegistry:`]](https://github.com/protocolbuffers/protobuf/blob/44bd65b2d3c0470d91a23cc14df5ffb1ab0af7cd/objectivec/GPBMessage.h#L258-L261)

**替代方案：**
[-[`GPBMessage mergeFrom:extensionRegistry:error:`]](https://github.com/protocolbuffers/protobuf/blob/44bd65b2d3c0470d91a23cc14df5ffb1ab0af7cd/objectivec/GPBMessage.h#L275-L277)

##### GPBDuration timeIntervalSince1970

**API：**
[-[`GPBDuration timeIntervalSince1970`]](https://github.com/protocolbuffers/protobuf/blob/29fca8a64b62491fb0a2ce61878e70eda88dde98/objectivec/GPBWellKnownTypes.h#L95-L100)

**替代方案：**
[-[`GPBDuration timeInterval`]](https://github.com/protocolbuffers/protobuf/blob/29fca8a64b62491fb0a2ce61878e70eda88dde98/objectivec/GPBWellKnownTypes.h#L74-L89)

##### GPBTextFormatForUnknownFieldSet

**API：**
[`GPBTextFormatForUnknownFieldSet()`](https://github.com/protocolbuffers/protobuf/blob/29fca8a64b62491fb0a2ce61878e70eda88dde98/objectivec/GPBUtilities.h#L32-L43)

**替代方案：** 已过时——请改用
[`GPBTextFormatForMessage()`](https://github.com/protocolbuffers/protobuf/blob/29fca8a64b62491fb0a2ce61878e70eda88dde98/objectivec/GPBUtilities.h#L20-L30)，
其中包含所有未知字段。

##### GPBUnknownFieldSet

**API：**
[`GPBUnknownFieldSet`](https://github.com/protocolbuffers/protobuf/blob/224573d66a0cc958c76cb43d8b2eb3aa7cdb89f2/objectivec/GPBUnknownFieldSet.h)

**替代方案：**
[`GPBUnknownFields`](https://github.com/protocolbuffers/protobuf/blob/224573d66a0cc958c76cb43d8b2eb3aa7cdb89f2/objectivec/GPBUnknownFields.h)

##### GPBMessage unknownFields

**API：**
[`GPBMessage unknownFields` 属性](https://github.com/protocolbuffers/protobuf/blob/224573d66a0cc958c76cb43d8b2eb3aa7cdb89f2/objectivec/GPBMessage.h#L73-L76)

**替代方案：**
[-[`GPBUnknownFields initFromMessage:`]](https://github.com/protocolbuffers/protobuf/blob/224573d66a0cc958c76cb43d8b2eb3aa7cdb89f2/objectivec/GPBUnknownFields.h#L30-L38)、
[-[`GPBMessage mergeUnknownFields:extensionRegistry:error:`]](https://github.com/protocolbuffers/protobuf/blob/f26bdff7cc0bb7e8ed88253ba16f81614a26cf16/objectivec/GPBMessage.h#L506-L528)
和
[-[`GPBMessage clearUnknownFields`]](https://github.com/protocolbuffers/protobuf/blob/224573d66a0cc958c76cb43d8b2eb3aa7cdb89f2/objectivec/GPBMessage.h#L497-L504C9)

#### 移除针对旧生成代码（gencode）的已弃用运行时 API {#v30-objc-remove-apis-gencode}

本发布移除了为支持 3.22.x 发布之前的 Objective-C 生成代码（gencode）而提供的已弃用运行时方法。当旧的生成代码启动时，该库也会在运行时输出一条日志消息。

**API：** [`+[GPBFileDescriptor
allocDescriptorForClass:file:fields:fieldCount:storageSize:flags:]`](https://github.com/protocolbuffers/protobuf/blob/1b44ce0feef45a78ba99d09bd2e5ff5052a6541b/objectivec/GPBDescriptor_PackagePrivate.h#L213-L220)

**替代方案：** 使用当前版本的库重新生成。

**API：** [`+[GPBFileDescriptor
allocDescriptorForClass:rootClass:file:fields:fieldCount:storageSize:flags:]`](https://github.com/protocolbuffers/protobuf/blob/1b44ce0feef45a78ba99d09bd2e5ff5052a6541b/objectivec/GPBDescriptor_PackagePrivate.h#L221-L229)

**替代方案：** 使用当前版本的库重新生成。

**API：** [`+[GPBEnumDescriptor
allocDescriptorForName:valueNames:values:count:enumVerifier:]`](https://github.com/protocolbuffers/protobuf/blob/1b44ce0feef45a78ba99d09bd2e5ff5052a6541b/objectivec/GPBDescriptor_PackagePrivate.h#L285-L291)

**替代方案：** 使用当前版本的库重新生成。

**API：** [`+[GPBEnumDescriptor
allocDescriptorForName:valueNames:values:count:enumVerifier:extraTextFormatInfo:]`](https://github.com/protocolbuffers/protobuf/blob/1b44ce0feef45a78ba99d09bd2e5ff5052a6541b/objectivec/GPBDescriptor_PackagePrivate.h#L292-L299)

**替代方案：** 使用当前版本的库重新生成。

**API：**
[`-[GPBExtensionDescriptor initWithExtensionDescription:]`](https://github.com/protocolbuffers/protobuf/blob/1b44ce0feef45a78ba99d09bd2e5ff5052a6541b/objectivec/GPBDescriptor_PackagePrivate.h#L317-L320)

**替代方案：** 使用当前版本的库重新生成。

### 其他变更 {#v30-other}

#### 毒丸警告 {#poison}

我们更新了毒丸机制，使其针对“旧生成代码 + 新运行时”的组合发出警告：这些组合在新的滚动升级策略下可以工作，但在*下一个*主版本提升时会失效。例如，Python 4.x.x 生成代码应能配合 5.x.x 运行时工作，但在配合 6.x.x 运行时时会警告即将发生的破坏。

#### C# 与 Ruby 中 UTF-8 强制检查的变更 {#utf-8-enforcement}

我们加入了一个修复，使各语言对 UTF-8 的强制检查保持一致。字符串字段中存在非法非 UTF-8 数据的用户可能会更早暴露出 UTF-8 强制检查错误。

#### Ruby 与 PHP 在 JSON 解析中报错

我们按照 [JSON 规范](https://protobuf.dev/programming-guides/json/)修复了数值字段中字符串的 JSON 解析不符合规范的问题。

此修复并未伴随主版本提升，但 Ruby 和 PHP 现在会对数值字段中的非数字字符串（例如 `""`、`"12abc"`、`"abc"`）抛出错误。v29.x 会针对这些错误情形发出警告。

## v22.0 中的编译器变更 {#compiler-22}

### JSON 字段名冲突 {#json-field-names}

变更来源：[PR #11349](https://github.com/protocolbuffers/protobuf/pull/11349)、[PR #10750](https://github.com/protocolbuffers/protobuf/pull/10750)

在处理与 JSON 映射相关的字段名冲突方面，我们做了一些细微调整。在 proto3 中，我们部分放宽了限制，只有当字段名产生大小写敏感的 JSON 映射（即原名称的驼峰命名（camel case）形式）时才报错。现在我们还会检查 `json_name` 选项，并对大小写敏感的冲突报错。在 proto2 中，我们略微收紧了限制：如果两个 `json_name` 规范相互冲突，将会报错；如果隐式 JSON 映射（驼峰命名）存在冲突，在 proto2 中会给出警告。

我们提供了一个临时的消息/枚举选项，用于恢复旧有行为。如果你无法立即重命名冲突的字段，可以在相应的消息/枚举上设置 `deprecated_legacy_json_field_conflicts` 选项。该选项将在未来的发布中移除，但能为你争取更多迁移时间。

## v22.0 中的 C++ API 变更 {#cpp-22}

正如 [8 月公告](/news/2022-08-03#cpp-changes)中所宣布的，4.22.0 对 C++ 运行时和 protoc 包含破坏性变更。

### 停用 Autotools {#autotools}

变更来源：
[PR #10132](https://github.com/protocolbuffers/protobuf/pull/10132)

在 v22.0 中，我们从 Protobuf 编译器和 C++ 运行时中移除了全部 Autotools 支持。如果你正在使用 Autotools 构建其中之一，就必须迁移到 [CMake](http://cmake.org) 或 [Bazel](http://bazel.build)。我们提供了一些使用 CMake 设置 Protobuf 的[专门说明](https://github.com/protocolbuffers/protobuf/blob/main/cmake/README.md)。

### Abseil 依赖 {#abseil}

变更来源：
[PR #10416](https://github.com/protocolbuffers/protobuf/pull/10416)

在 v22.0 中，我们对 [Abseil](https://github.com/abseil/abseil-cpp) 形成了显式依赖。这让我们得以移除大部分[存根（stub）](https://github.com/protocolbuffers/protobuf/tree/21.x/src/google/protobuf/stubs)——它们从旧内部代码分叉而来，而那些代码后来演变成了 Abseil。这带来了一些细微的行为变化，但大多数对用户应是透明的。一些值得注意的变化包括：

*   **string_view（字符串视图）** —— 在我们的许多 API 中，`absl::string_view` 已取代 `const std::string&`。这最常见于输入参数，对用户而言不应有可感知的变化。在少数情况下（例如虚方法参数或返回类型），用户可能需要显式修改代码以使用新签名。

*   **表格（tables）** —— 我们不再使用 STL 的 set/map，而是改用 Abseil 的 `flat_hash_map`、`flat_hash_set`、`btree_map` 和 `btree_set`。它们效率更高，并支持[异构查找（heterogeneous lookup）](https://abseil.io/tips/144)。这对用户基本不可见，但可能引起一些与表顺序相关的细微行为变化。

*   **日志（logging）** —— Abseil 的[日志库](https://abseil.io/docs/cpp/guides/logging)与我们旧的日志代码非常相似，只是拼写略有不同（例如用 `ABSL_CHECK` 代替 `GOOGLE_CHECK`）。最大的区别是它不支持异常，并且在 `FATAL` 断言失败时现在总是崩溃（此前我们提供过 `PROTOBUF_USE_EXCEPTIONS` 标志来切换为异常）。由于这些情况只在遇到严重问题时才会出现，我们认为无条件崩溃是合适的应对方式。

    日志相关变更来源：[PR #11623](https://github.com/protocolbuffers/protobuf/pull/11623)

*   **构建依赖** —— 新的构建依赖总是可能给下游（downstream）用户造成破坏。构建时我们要求 [Abseil LTS 20230125](https://github.com/abseil/abseil-cpp/releases/tag/20230125.0) 或更高版本。

    *   对于 Bazel 构建，当你在 `WORKSPACE` 中运行 [`protobuf_deps`](https://github.com/protocolbuffers/protobuf/blob/main/protobuf_deps.bzl) 时，Abseil 会自动下载并按固定的 LTS 发布版本构建。这应当是透明的，但如果你依赖的是较旧版本的 Abseil，就需要升级依赖。

    *   对于 CMake 构建，我们会先查找由顶层 CMake 配置引入的现有 Abseil 安装（参见[说明](https://github.com/abseil/abseil-cpp/blob/master/CMake/README#traditional-cmake-set-up)）。否则，如果 `protobuf_ABSL_PROVIDER` 被设置为 `module`（其默认值），我们会尝试从 git [子模块（submodule）](https://github.com/protocolbuffers/protobuf/tree/main/third_party)构建并链接 Abseil；如果 `protobuf_ABSL_PROVIDER` 被设置为 `package`，我们会查找系统中预装的 Abseil。

### GetCurrentTime 方法的变化 {#getcurrenttime}

在 Windows 上，`GetCurrentTime()` 是系统提供的某个宏的名称。在 v22.x 之前，Protobuf 错误地移除了 `GetCurrentTime()` 的宏定义，导致 Windows 开发者在包含 `<protobuf/util/time_util.h>` 之后无法使用该宏。从 v22.x 开始，Protobuf 会保留该宏定义。这可能会破坏依赖先前行为的客户代码，例如使用了 [`google::protobuf::util::TimeUtil::GetCurrentTime()`](/reference/cpp/api-docs/google.protobuf.util.time_util#TimeUtil) 表达式的情况。

要将你的应用迁移到新行为，请修改代码，采取以下措施之一：

*   如果已定义 `GetCurrent` 宏，请显式取消定义 `GetCurrentTime` 宏
*   使用 `(google::protobuf::util::TimeUtil::GetCurrentTime)()` 或类似表达式来阻止宏展开

#### 示例：取消宏定义

如果你并不使用来自 Windows 的该宏，可以使用这种方法。

之前：

```cpp
#include <google/protobuf/util/time_util.h>

void F() {
  auto time = google::protobuf::util::TimeUtil::GetCurrentTime();
}
```

之后：

```cpp
#include <google/protobuf/util/time_util.h>
#ifdef GetCurrentTime
#undef GetCurrentTime
#endif

void F() {
  auto time = google::protobuf::util::TimeUtil::GetCurrentTime();
}
```

**示例 2：阻止宏展开**

之前：

```cpp
#include <google/protobuf/util/time_util.h>

void F() {
  auto time = google::protobuf::util::TimeUtil::GetCurrentTime();
}
```

之后：

```cpp
#include <google/protobuf/util/time_util.h>

void F() {
  auto time = (google::protobuf::util::TimeUtil::GetCurrentTime)();
}
```

## C++20 支持 {#cpp20}

变更来源：[PR #10796](https://github.com/protocolbuffers/protobuf/pull/10796)

为了支持 C++20，我们在 C++ 生成的 Protobuf 代码中保留了新的[关键字（keyword）](https://en.cppreference.com/w/cpp/keyword)。与其他保留字一样，如果你将它们用作任何字段、枚举或消息的名称，我们会为其添加下划线后缀，使其成为合法的 C++。例如，`concept` 字段会生成 `concept_()` getter。如果你现有的 proto 使用了这些关键字，就需要更新引用它们的 C++ 代码，补上相应的下划线。

### final 类 {#final-classes}

变更来源：[PR #11604](https://github.com/protocolbuffers/protobuf/pull/11604)

作为强化 Protobuf 库内部假设这一更大工作的一部分，我们将一些从未打算被继承的类标记为了 `final`。目前没有已知的继承这些类的用例，这样做也很可能引发问题。如果你的代码正在继承这些类，没有缓解手段可用；但如果你认为自己进行这种继承有正当理由，可以[提交 issue](https://github.com/protocolbuffers/protobuf/issues)。

### 容器静态断言 {#container-static-assertions}

变更来源：[PR #11550](https://github.com/protocolbuffers/protobuf/pull/11550)

作为强化 Protobuf 库内部假设这一更大工作的一部分，我们为 `Map`、`RepeatedField` 和 `RepeatedPtrField` 容器添加了静态断言。如[我们的文档](https://protobuf.dev/programming-guides/proto/#maps)所述，这些断言确保这些容器只与预期类型一起使用。如果触发了这些静态断言，应将代码迁移为使用 Abseil 或 STL 容器：对于可重复字段容器，`std::vector` 是很好的直接替代品；对于 `Map`，可使用 `std::unordered_map` 或 `absl::flat_hash_map`（前者提供类似的指针稳定性，而后者效率更高）。

### 已清空元素的弃用 {#cleared-elements}

变更来源：[PR #11588](https://github.com/protocolbuffers/protobuf/pull/11588)、[PR #11639](https://github.com/protocolbuffers/protobuf/pull/11639)

`RepeatedPtrField` 中围绕“已清空字段”（cleared fields）的 API 已被弃用，并将在后续破坏性发布中完全移除。它最初是作为在元素被清空后复用元素的优化而加入的，但最终效果不佳。如果你正在使用该 API，应考虑迁移到 arena，以获得更好的内存复用。

### UnsafeArena 的弃用 {#unsafe-arena}

变更来源：[PR #10325](https://github.com/protocolbuffers/protobuf/pull/10325)

作为移除 arena 不安全 API 这一更大工作的一部分，我们隐藏了 `RepeatedField::UnsafeArenaSwap`。这是目前为止移除的唯一一个，但在后续发布中我们会继续移除其他此类 API，并提供辅助工具来处理跨 arena 的高效借用模式。在同一个 arena（或栈/堆）内，`Swap` 与 `UnsafeArenaSwap` 效率相当。它的好处是，即使你意外地跨不同 arena 调用它，也不会引发无效的内存操作。

### MapPair 升级 {#map-pairs}

变更来源：[PR #11625](https://github.com/protocolbuffers/protobuf/pull/11625)

在 v22.0 中，我们开始清理 `Map` API，使其与 Abseil 和 STL 更加一致。值得注意的是，我们用 `std::pair` 的别名取代了 `MapPair` 类。这对大多数用户应当是透明的，但如果你直接使用该类，可能需要更新代码。

### 新 JSON 解析器 {#json-parser}

变更来源：[PR #10729](https://github.com/protocolbuffers/protobuf/pull/10729)

本发布重写了 C++ JSON 解析器。这大体上应是一个无感知的变更，但难免会有一些未写入文档的怪癖行为发生变化，请据此进行测试。解析不符合 RFC-8219 JSON 的文档（例如缺少引号或使用非标准布尔值的文档）已被弃用，并将在未来的发布中移除。字段的序列化顺序现在保证与字段编号顺序一致，而此前的确定性（deterministic）较低。

作为此次迁移的一部分，[util/internal](https://github.com/protocolbuffers/protobuf/tree/21.x/src/google/protobuf/util/internal) 下的所有文件已被删除。它们曾被旧解析器使用，从来不是为外部使用而设计的。

### `Arena::Init` {#arena-init}

变更来源：[PR #10623](https://github.com/protocolbuffers/protobuf/pull/10623)

`Arena` 中的 `Init` 方法原本什么都不做，现已被移除。如果你曾调用该方法，你很可能本想直接使用一组 `ArenaOptions` 调用 `Arena` 构造函数。你应当删除该调用，或迁移到该构造函数。

### ErrorCollector 迁移 {#error-collector}

变更来源：[PR #11555](https://github.com/protocolbuffers/protobuf/pull/11555)

作为 Abseil 迁移的一部分，我们正在从 `const std::string&` 迁移到 `absl::string_view`。对我们的三个错误收集器（error collector）类而言，若不破坏现有代码就无法完成这一迁移。因此在 v22.0 中，我们决定同时发布两种变体，并将方法从 `AddError` 和 `AddWarning` 重命名为 `RecordError` 和 `RecordWarning`。旧签名已被标记为弃用，效率会略低（因为需要字符串拷贝），但在其他方面仍可正常工作。你应当迁移到新版本，因为 `Add*` 方法将在后续破坏性发布中被移除。
