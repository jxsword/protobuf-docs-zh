+++
title = "跨版本运行时保证"
weight = 930
description = "语言对跨版本运行时兼容性所作的保证。"
type = "docs"
source_url = "https://protobuf.dev/support/cross-version-runtime-guarantee/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-20"
status = "translated"
translator = "agent"
+++

<link rel="stylesheet" href="/includes/version-tables.css">

Protobuf 语言绑定由两个部分组成：生成代码（generated code，简称 生成代码），以及为这些生成代码实现公共功能的运行时（runtime）库。当这两者来自不同的 protobuf 发布版本时，就处于"跨版本运行时"（cross version runtime）的情境。

我们打算在大多数语言上提供以下保证。这些是默认保证；不过，protobuf 代码生成器（code generator）和运行时的所有者可以显式覆盖它们，改为针对该语言的更具体的保证。[C++ 与 Rust](#cpp) 的保证比常规情况更严格，而 [Python](#python) 的则更宽松。

超出这些保证范围的 Protobuf 跨版本用法**容易出错且不受支持**。版本偏差（version skew）可能导致难以诊断的*偶发故障和未定义行为*，即便在没有做出任何源不兼容变更的情况下，它往往*看起来*也能正常工作。对 Protobuf 而言，大量工具和服务依赖使用不受支持的 Protobuf 语言绑定，这阻碍了 protobuf 团队针对缺陷报告或安全漏洞更新 protobuf 实现。

## 新生成代码 + 旧运行时 = 绝不允许 {#backwards}

我们可以在任何类型的发布（主版本 major、次版本 minor 或补丁版本 patch）中添加新的运行时 API。该发布中的 生成代码 允许使用这些新 API。其结果是：生成代码 所配对的运行时绝不能早于生成这些绑定所用的 `protoc` 和插件（plugin）。

我们会在可能的情况下加入“毒丸”（poison pill）机制，以阻止将较新的生成代码（gencode）与较旧的运行时配对的尝试。

## 主版本 {#major}

Protobuf 针对主版本实现了滑动窗口（sliding window）兼容性。为主版本 V 生成的代码（完整版本：V.x.y）将得到主版本为 V 和 V+1 的 protobuf 运行时的支持。

Protobuf **不会**支持将版本 V 的生成代码用于 &gt;= V+2 的运行时，并会使用“毒丸”机制：当软件程序集（software assembly）尝试使用这种配置时，以清晰的错误信息宣告失败。

例如：

*   protobuf 版本 3.0.0 生成的 Java 代码可与 3.0.0 至 4.x.y 的运行时协同工作，但**不能**与 2.0.0 至 2.x.y 的运行时或 &gt;= 5.0.0 的运行时协同工作。
*   protobuf 版本 4.27.2 生成的 Java 代码可与 4.27.2 至 5.x.y 的运行时协同工作，但**不能**与 2.0.0 至 4.27.1 的运行时或 &gt;= 6.0.0 的运行时协同工作

在与旧 生成代码 的兼容性*无法*维持的情况下可以破例，例如需要更新 生成代码 的[安全](#exception)修复。

**注意：** 毒丸机制是在 protobuf 26.0 发布中引入的。早于 4.26.0 的 Java 生成代码与早于该生成代码的运行时搭配时可能*看起来*能正常工作。然而，[较新生成代码与较旧运行时](#backwards)的组合可能存在严重的缺陷，直到实际运行阶段才会显现出来。

**注意：** [C++ 与 Rust](#cpp) 不支持兼容窗口，而 [Python](#python) 支持的兼容窗口要长得多。

## 次版本 {#minor}

在同一个主版本的运行时之内，由较旧版本 `protoc` 生成的代码可以在较新的运行时上运行。

**注意：** [C++ 与 Rust](#cpp) 不支持跨次版本的兼容性。

## 安全例外 {#exception}

出于安全原因，我们保留违反上述承诺的权利。我们预计这类例外会很少发生，但始终会将安全置于这些保证之上。例如，[footmitten CVE](https://cve.report/CVE-2022-3510) 就要求对 Java 的运行时和生成代码进行成对更新。其结果是，由 3.20.3 生成的代码（包含 footmitten 修复）无法与运行时库 3.21.6（早于 footmitten 修复）一同加载，从而形成了以下兼容性矩阵：

<table>
  <tr>
    <td colspan="2" rowspan="2"></td>
    <td colspan="4">生成代码版本</td>
  </tr>
  <tr>
    <td class="gray">3.20.2</td>
    <td class="gray">3.20.3</td>
    <td class="gray">3.21.6</td>
    <td class="gray">3.21.7</td>
  </tr>
  <tr>
    <td rowspan="4">运行时<br>版本</td>
    <td class="gray">3.20.2</td>
    <td class="yellow">存在漏洞</td>
    <td class="red"><b>!无法运行!</b></td>
    <td class="yellow"><b>!存在漏洞!</b></td>
    <td class="red"><b>!无法运行!</b></td>
  </tr>
  <tr>
    <td class="gray">3.20.3</td>
    <td class="yellow">存在漏洞</td>
    <td class="green">正常运行</td>
    <td class="yellow"><b>!存在漏洞!</b></td>
    <td class="green"><b>!正常运行?!</b></td>
  </tr>
  <tr>
    <td class="gray">3.21.6</td>
    <td class="yellow">存在漏洞</td>
    <td class="red">无法运行</td>
    <td class="yellow">存在漏洞</td>
    <td class="red"><b>!无法运行!</b></td>
  </tr>
  <tr>
    <td class="gray">3.21.7</td>
    <td class="yellow">存在漏洞</td>
    <td class="green">正常运行</td>
    <td class="yellow">存在漏洞</td>
    <td class="green">正常运行</td>
  </tr>
</table>

*   “存在漏洞”表示该组合能够成功启动，但安全漏洞依然存在。
*   "正常运行"表示该组合能够成功启动，且不具有该漏洞。
*   "无法运行"表示该组合无法成功启动。
*   **!加粗!**表示较新 生成代码 与较旧运行时混用的配置，这些配置从未被预期可以协同工作。

## 不支持多个主版本运行时共存 {#coexist}

**不支持**在同一进程中共存多个主版本。

## C++ 与 Rust 特有的保证 {#cpp}

Protobuf C++ 与 Rust 声明不提供任何跨运行时支持，并要求生成代码版本与运行时版本在任何时候都完全匹配。

此外，Protobuf C++ 不对任何发布（主版本、次版本或微版本）之间的 ABI 稳定性作出任何保证。

## Python 特有的保证 {#python}

自 3.20.0 发布起，Protobuf Python 生成代码变成了围绕内嵌 `FileDescriptorProto` 的一个薄封装。由于这些 proto 受支持的时间跨度极长，通常并不需要我们惯常的[主版本兼容窗口](#major)。

Python 可能会在未来的特定主版本发布中破坏生成代码的兼容性，但会提前伴随毒丸警告与错误一同出现。截至 6.32.0，自 3.20.0 起生成的所有代码都将获得支持，至少支持到 8.x.y。
