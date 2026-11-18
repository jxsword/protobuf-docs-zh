+++
title = "实现版次支持"
weight = 43
description = "关于在运行时和插件中实现版次支持的说明。"
type = "docs"
source_url = "https://protobuf.dev/editions/implementation/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-18"
status = "translated"
translator = "agent"
+++

本主题介绍如何在新的运行时（runtime）和生成器（generator）中实现版次（edition）支持。

## 概览 {#overview}

### 2023 版次 {#edition-2023}

首个发布的版次是 2023 版次，其设计目标是统一 proto2 与 proto3 语法。我们为覆盖二者行为差异而添加的特性（feature）详见[版次特性设置](/editions/features)。

### 特性定义 {#feature-definition}

除了*支持*版次和我们已定义的全局特性之外，你可能还想定义自己的特性来利用这套基础设施。这将允许你定义任意特性，供你的生成器和运行时用来控制新行为。第一步是为 `descriptor.proto` 中的 `FeatureSet` 消息（message）认领一个大于 9999 的扩展（extension）编号。你可以在 GitHub 上向我们提交 pull request，它将包含在我们的下一个发布（release）中（例如参见 [#15439](https://github.com/protocolbuffers/protobuf/pull/15439)）。

拿到扩展编号后，你就可以创建自己的特性 proto 文件（类似于 [cpp_features.proto](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/cpp_features.proto)）。它们通常形如：

```proto
edition = "2023";

package foo;

import "google/protobuf/descriptor.proto";

extend google.protobuf.FeatureSet {
  MyFeatures features = <extension #>;
}

message MyFeatures {
  enum FeatureValue {
    FEATURE_VALUE_UNKNOWN = 0;
    VALUE1 = 1;
    VALUE2 = 2;
  }

  FeatureValue feature_value = 1 [
    targets = TARGET_TYPE_FIELD,
    targets = TARGET_TYPE_FILE,
    feature_support = {
      edition_introduced: EDITION_2023,
      edition_deprecated: EDITION_2024,
      deprecation_warning: "Feature will be removed in 2025",
      edition_removed: EDITION_2025,
    },
    edition_defaults = { edition: EDITION_LEGACY, value: "VALUE1" },
    edition_defaults = { edition: EDITION_2024, value: "VALUE2" }
  ];
}
```

这里我们定义了一个新的枚举（enum）特性 `foo.feature_value`（目前仅支持布尔和枚举类型）。除了定义它可以取的值之外，你还需要指定它的使用方式：

*   **目标（targets）** - 指定该特性可以附加到的 proto 描述符（descriptor）类型。这决定了用户可以在哪些位置显式指定该特性。每种类型都必须显式列出。
*   **特性支持（feature_support）** - 指定该特性相对于版次的生命周期。你必须指定其引入时所处的版次，在此之前它不允许被使用。你也可以选择在后续版次中弃用（deprecate）或移除该特性。
*   **版次默认值（edition_defaults）** - 指定该特性默认值的各项变更。这必须覆盖每个受支持的版次，但默认值未发生变化的版次可以省略。注意，可以在此处指定 `EDITION_PROTO2` 和 `EDITION_PROTO3`，为“传统”（legacy）版次提供默认值（参见[传统版次](#legacy_editions)）。

#### 什么是特性？ {#what-feature}

特性的设计目的是提供一种机制，在版次边界上随时间逐步收紧不良行为。虽然真正移除某个特性的时间点可能是数年（甚至数十年）之后，但任何特性的期望目标都应当是最终将其移除。当发现某个不良行为时，你可以引入一个新特性来守护相应的修复。在下一个版次（或者更晚）中，你可以翻转默认值，同时仍允许用户在升级时保留旧有行为。在未来的某个时间点，你可以将该特性标记为弃用，这会向任何覆盖它的用户触发一条自定义警告。再往后的某个版次中，你可以将其标记为已移除，阻止用户再覆盖它（但默认值仍然生效）。直到在某个破坏性发布中停止支持最后一个版次为止，该特性对仍停留在旧版次上的 proto 文件将保持可用，为它们留出迁移时间。

对于你无意移除、用于控制可选行为的开关，更好的实现方式是[自定义选项](/programming-guides/proto2/#customoptions)。这也与我们把特性限定为布尔或枚举类型的原因有关。任何由（相对）无界数量的取值所控制的行为，恐怕都不太适合版次框架，因为最终要关停这么多不同的行为并不现实。

对此需要注意的一点是涉及线路边界的行为。使用语言特定的特性来控制序列化（serialization）或解析（parsing）行为可能很危险，因为线路的另一端可能是任何其他语言。线路格式（wire format）的变更应当始终由 `descriptor.proto` 中的全局特性控制，以便每种运行时都能一致地遵循。

### 生成器 {#generators}

用 C++ 编写的生成器有许多现成的便利，因为它们使用 C++ 运行时。它们无需自行处理[特性解析](#feature_resolution)；如果需要任何特性扩展，可以在其 CodeGenerator 的 `GetFeatureExtensions` 中注册。在代码生成中，它们通常可以使用 `GetResolvedSourceFeatures` 访问某个描述符的已解析特性，并使用 `GetUnresolvedSourceFeatures` 访问其自身的未解析特性。

使用与其所生成代码对应的运行时相同语言编写的插件（plugin），可能需要为其特性定义进行一些自定义引导（bootstrapping）。

#### 显式声明支持 {#explicit-support}

生成器必须准确声明自己支持哪些版次。这让你可以在某个版次发布之后，按自己的时间表安全地添加对它的支持。如果生成器未在其 `CodeGeneratorResponse` 的 `supported_features` 字段中包含 `FEATURE_SUPPORTS_EDITIONS`，protoc 会拒绝向其发送任何版次 proto 文件。此外，我们还提供 `minimum_edition` 和 `maximum_edition` 字段，用于精确声明你所支持的版次范围。当你为新版次定义好全部代码和特性变更后，就可以调高 `maximum_edition` 来宣告这一支持。

#### 代码生成测试 {#codegen-tests}

我们提供了一组代码生成测试，用于确保 2023 版次不会产生意外的功能性变更。对于 C++ 和 Java 这类大量功能位于生成代码（gencode）中的语言，这些测试非常有用。另一方面，对于 Python 这类 gencode 基本上只是一组序列化描述符的语言，这些测试就没那么有用了。

这套基础设施目前尚不可复用，但计划在未来的发布中实现。届时你将可以用它们来验证迁移到版次不会带来任何意外的代码生成变更。

### 运行时 {#runtimes}

没有反射（reflection）或动态消息的运行时应当无需执行任何操作即可实现版次支持。所有这些逻辑都应当由代码生成器（code generator）处理。

*有*反射但*没有*动态消息的语言需要已解析的特性，但可以选择只在各自的生成器中处理。做法是在代码生成期间将已解析和未解析的特性集都传递给运行时。这避免了在运行时中重新实现[特性解析](#feature_resolution)，主要缺点是效率较低，因为它会为每个描述符创建一个独一无二的特性集。

具有动态消息的语言必须完整实现版次支持，因为它们需要能够在运行时构建描述符。

#### 语法反射 {#syntax_reflection}

在具有反射的运行时中实现版次支持的第一步，是移除所有对 `syntax` 关键字的直接检查。所有这些检查都应迁移到粒度更细的特性辅助函数中，这些辅助函数在必要时可以继续使用 `syntax`。

应在描述符上实现以下特性辅助函数，并采用符合相应语言习惯的命名：

*   `FieldDescriptor::has_presence` - 字段是否具有显式存在性（explicit presence）
    *   repeated 字段*从不*具有存在性
    *   消息、扩展和 oneof 字段*总是*具有显式存在性
    *   其余字段当且仅当 `field_presence` 不为 `IMPLICIT` 时具有存在性
*   `FieldDescriptor::is_required` - 字段是否为 required
*   `FieldDescriptor::requires_utf8_validation` - 字段是否应进行 utf8 有效性检查
*   `FieldDescriptor::is_packed` - repeated 字段是否采用紧凑编码（packed）
*   `FieldDescriptor::is_delimited` - 消息字段是否采用分隔编码（delimited）
*   `EnumDescriptor::is_closed` - 字段是否封闭

{{% alert title="Note" color="note" %}}在大多数语言中，消息编码特性目前仍通过 `TYPE_GROUP` 来表示，required 字段也仍会设置 `LABEL_REQUIRED`。这并不理想，这么做是为了让下游迁移更容易。最终，这些应当迁移到相应的辅助函数以及 `TYPE_MESSAGE/LABEL_OPTIONAL`。{{% /alert %}}

下游使用者应迁移到这些新的辅助函数，而不是直接使用 syntax。以下几类现有的描述符 API 理想情况下应被弃用并最终移除，因为它们泄露了语法信息：

*   `FileDescriptor` 的 syntax
*   Proto3 optional API
    *   `FieldDescriptor::has_optional_keyword`
    *   `OneofDescriptor::is_synthetic`
    *   `Descriptor::*real_oneof*` - 应重命名为“oneof”，并且现有的“oneof”辅助函数应当被移除，因为它们会泄露合成 oneof（synthetic oneof）的相关信息（版次中不存在合成 oneof）。
*   组（group）类型
    *   `TYPE_GROUP` 枚举值应当被移除，由 `is_delimited` 辅助函数取代。
*   required 标签
    *   `LABEL_REQUIRED` 枚举值应当被移除，由 `is_required` 辅助函数取代。

包含这些检查的用户代码有很多类，但它们与版次并*不*冲突。例如，由于 proto3 `optional` 采用合成 oneof 的实现方式而需要对其特殊处理的代码，只要其判断方向（polarity）类似于 `syntax == "proto3"`（而不是检查 `syntax != "proto2"`），就不会与版次冲突。

如果无法完全移除这些 API，则应将其弃用并劝阻使用。

#### 特性可见性 {#visibility}

如[版次特性可见性](https://github.com/protocolbuffers/protobuf/blob/main/docs/design/editions/editions-feature-visibility.md)中所述，特性 proto 文件应当始终是任何 Protobuf 实现的内部细节。它们所控制的*行为*应当通过描述符方法暴露，而 proto 本身则不应暴露。值得注意的是，这意味着任何暴露给用户的选项（option）都需要剥离其中的 `features` 字段。

我们允许特性外泄的唯一情况，是在序列化描述符的时候。由此得到的描述符 proto 应当是对原始 proto 文件的忠实表示，并且应在选项内部包含*未解析特性*。

#### 传统版次 {#legacy_editions}

如[传统语法版次](https://github.com/protocolbuffers/protobuf/blob/main/docs/design/editions/legacy-syntax-editions.md)中更详细的讨论，尽早为版次实现建立覆盖的一个好办法，是将 proto2、proto3 与版次统一起来。这实际上在底层将 proto2 和 proto3 迁移到了版次，并使[语法反射](#syntax_reflection)中实现的所有辅助函数完全基于特性工作（而不是基于 syntax 分支）。做法是在[特性解析](#feature_resolution)中插入一个*特性推断*阶段，让 proto 文件的各个方面来决定哪些特性是合适的。随后可将这些特性合并进父级的特性，从而得到已解析的特性集。

虽然我们已经为 proto2/proto3 提供了合理的默认值，但对于 2023 版次，还需要以下额外推断：

*   required - 当字段带有 `LABEL_REQUIRED` 时，我们推断其存在性为 `LEGACY_REQUIRED`
*   groups - 当字段带有 `TYPE_GROUP` 时，我们推断其消息编码为 `DELIMITED`
*   packed - 当 `packed` 选项为 true 时，我们推断其编码为 `PACKED`
*   expanded - 当 proto3 字段将 `packed` 显式设为 false 时，我们推断其编码为 `EXPANDED`

#### 一致性测试 {#conformance-tests}

版次专属的一致性测试（conformance test）已经添加，但需要主动选择启用。可以向测试运行器传入 `--maximum_edition 2023` 标志来启用这些测试。你需要配置被测端二进制程序，使其能够处理以下新消息类型：

*   `protobuf_test_messages.editions.proto2.TestAllTypesProto2` - 与旧的 proto2 消息相同，但已转换为 2023 版次
*   `protobuf_test_messages.editions.proto3.TestAllTypesProto3` - 与旧的 proto3 消息相同，但已转换为 2023 版次
*   `protobuf_test_messages.editions.TestAllTypesEdition2023` - 用于覆盖 2023 版次特有的测试用例

### 特性解析 {#feature-resolution}

版次使用词法作用域（lexical scoping）来定义特性，这意味着任何需要实现版次支持的非 C++ 代码都必须重新实现我们的*特性解析*算法。不过，大部分工作由 protoc 自身完成：可以配置 protoc 输出一个中间 `FeatureSetDefaults` 消息。该消息包含对一组特性定义文件的“编译”结果，列出了每个版次的默认特性值。

例如，上面的特性定义会编译为 proto2 到 2025 版次之间的以下默认值，以文本格式（text format）记法表示：

```
defaults {
  edition: EDITION_PROTO2
  overridable_features { [foo.features] {} }
  fixed_features {
    // Global feature defaults…
    [foo.features] { feature_value: VALUE1 }
  }
}
defaults {
  edition: EDITION_PROTO3
  overridable_features { [foo.features] {} }
  fixed_features {
    // Global feature defaults…
    [foo.features] { feature_value: VALUE1 }
  }
}
defaults {
  edition: EDITION_2023
  overridable_features {
    // Global feature defaults…
    [foo.features] { feature_value: VALUE1 }
  }
}
defaults {
  edition: EDITION_2024
  overridable_features {
    // Global feature defaults…
    [foo.features] { feature_value: VALUE2 }
  }
}
defaults {
  edition: EDITION_2025
  overridable_features {
    // Global feature defaults…
  }
  fixed_features { [foo.features] { feature_value: VALUE2 } }
}
minimum_edition: EDITION_PROTO2
maximum_edition: EDITION_2025

```

为节省篇幅，全局特性默认值在上面被省略了，但它们同样会出现在实际输出中。该对象包含指定范围内每个具有唯一默认值集合的版次的有序列表（某些版次最终可能不会出现）。每组默认值都会拆分为*可覆盖*（overridable）与*固定*（fixed）特性。前者是该版次所支持的、可由用户自由覆盖的特性；固定特性则是那些尚未引入或已被移除的特性，无法被用户覆盖。

我们提供了一个用于编译这些中间对象的 Bazel 规则：

```
load("@com_google_protobuf//editions:defaults.bzl", "compile_edition_defaults")

compile_edition_defaults(
    name = "my_defaults",
    srcs = ["//some/path:lang_features_proto"],
    maximum_edition = "PROTO2",
    minimum_edition = "2024",
)
```

输出的 `FeatureSetDefaults` 可以以原始字符串字面量（raw string literal）的形式，嵌入到你需要在其中执行特性解析的任何语言中。我们还提供了 `embed_edition_defaults` 宏来完成这项工作：

```
embed_edition_defaults(
    name = "embed_my_defaults",
    defaults = ":my_defaults",
    output = "my_defaults.h",
    placeholder = "DEFAULTS_DATA",
    template = "my_defaults.h.template",
)
```

或者，你也可以在 Bazel 之外直接调用 protoc 来生成这些数据：

```
protoc --edition_defaults_out=defaults.binpb --edition_defaults_minimum=PROTO2 --edition_defaults_maximum=2023 <feature files...>
```

在你的代码接入并解析默认值消息之后，对给定版次的文件描述符进行特性解析只需遵循一个简单的算法：

1.  校验版次处于合适的范围 [`minimum_edition`, `maximum_edition`] 内
2.  在有序的 `defaults` 字段中二分查找小于或等于该版次的最大条目
3.  将所选默认值中的 `overridable_features` 合并进 `fixed_features`
4.  合并描述符上显式设置的任何特性（文件选项中的 `features` 字段）

在此基础上，你可以为所有其他描述符递归地解析特性：

1.  以父描述符的特性集作为初始值
2.  合并描述符上显式设置的任何特性（选项中的 `features` 字段）

至于如何确定“父”描述符，可以参考我们的 [C++ 实现](https://github.com/protocolbuffers/protobuf/blob/27.x/src/google/protobuf/descriptor.cc#L1129)。大多数情况下这很直接，但扩展的情况有点出乎意料：它们的父级是外围作用域（enclosing scope），而不是被扩展者（extendee）。oneof 也需要被视为其字段的父级。

#### 一致性测试 {#conformance-tests}

在未来的发布中，我们计划添加用于跨语言验证特性解析的一致性测试。在此之前，我们常规的[一致性测试](#conformance_tests)确实能提供部分覆盖，而我们的[示例继承单元测试](https://github.com/protocolbuffers/protobuf/blob/27.x/python/google/protobuf/internal/descriptor_test.py#L1386)也可以移植过来，以提供更全面的覆盖。

### 示例 {#examples}

下面是一些真实的示例，展示了我们如何在自家运行时和插件中实现版次支持。

#### Java {#java}

*   [#14138](https://github.com/protocolbuffers/protobuf/pull/14138) - 使用 C++ 生成代码为 Java 特性 proto 引导编译器
*   [#14377](https://github.com/protocolbuffers/protobuf/pull/14377) - 在 Java、Kotlin 和 Java Lite 代码生成器中使用特性，包括代码生成测试
*   [#15210](https://github.com/protocolbuffers/protobuf/pull/15210) - 在 Java 完整运行时中使用特性，涵盖 Java 特性引导、特性解析和传统版次，并附带单元测试和一致性测试

#### 纯 Python {#python}

*   [#14546](https://github.com/protocolbuffers/protobuf/pull/14546) - 提前搭建代码生成测试
*   [#14547](https://github.com/protocolbuffers/protobuf/pull/14547) - 一次性完整实现版次支持，并附带单元测试和一致性测试

#### 𝛍pb {#upb}

*   [#14638](https://github.com/protocolbuffers/protobuf/pull/14638) - 版次实现的首次尝试，涵盖特性解析和传统版次
*   [#14667](https://github.com/protocolbuffers/protobuf/pull/14667) - 对字段标签（label）/类型提供了更完整的处理，加入了对 upb 代码生成器的支持以及一些测试
*   [#14678](https://github.com/protocolbuffers/protobuf/pull/14678) - 将 upb 接入 Python 运行时，并增加了更多单元测试和一致性测试

#### Ruby {#ruby}

*   [#16132](https://github.com/protocolbuffers/protobuf/pull/16132) - 将 upb/Java 接入全部四个 Ruby 运行时，实现完整的版次支持
