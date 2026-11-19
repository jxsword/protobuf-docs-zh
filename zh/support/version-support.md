+++
title = "版本支持"
weight = 910
description = "各语言实现所获支持窗口的列表。"
aliases = "/version-support/"
type = "docs"
source_url = "https://protobuf.dev/support/version-support/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

<link rel="stylesheet" href="/includes/version-tables.css">

## 当前受支持的发布版本 {#currently-supported}

语言 | 活跃支持 | 仅维护 | 最低生成代码版本
-------- | -------------- | --------------------- | ---------------
protoc   | 36.x           | 33.x、25.x（适用于 Java） |
C++      | 7.36.x         | 6.33.x                | 精确匹配
C#       | 3.36.x         |                       | 3.0.0
Go       | 1.36.x         |                       | 1.20.0
Java     | 4.36.x         | 3.25.x                | 3.0.0
ObjC     | 5.36.x         | 4.33.x                | 4.30.0
PHP      | 5.36.x         | 4.33.x                | 4.26.0
Python   | 7.36.x         | 6.33.x                | [3.20.0](https://protobuf.dev/support/cross-version-runtime-guarantee#python)
Ruby     | 4.36.x         |                       | 3.0.0

### 最低支持的生成代码 {#min-gencode}

每种语言的运行时（runtime）都有一个最低支持的生成代码（gencode）版本，但我们建议你在每次发布更新时都重新生成自己的生成代码。对旧生成代码的支持只是为了保障现有项目的向后兼容（backward compatibility），而不是供新项目采用旧的生成代码版本。

更多信息参见[跨版本运行时保证](/support/cross-version-runtime-guarantee)。

## 受支持的版次 {#supported-editions}

Protobuf 的发布版本（release version）与各版次（edition）的"版本"相互独立，后者决定 .proto 文件所使用的语法（proto2、proto3、2023、2024、2026）。

目前，最新的 protoc 能够处理以上所有情况。将来某个时候，protoc 的某个发布版本可能会放弃对某组 .proto 输入的支持，但我们目前尚无这样做的具体计划。

随着新版次的加入，要使用采用了该版次的文件，就需要足够新的 protoc：

版次 | 最低支持的 protoc | 发布日期
------- | ------------------------ | -------------
2026    | 36.0                     | 2026 年 8 月 20 日
2024    | 32.0                     | 2025 年 5 月 23 日
2023    | 27.0                     | 2024 年 8 月 13 日
proto3  | 3.0                      | 2016
proto2  | 2.0                      | 2008

## 版本编号方案 {#numbering}

版本号遵循 [SemVer](https://semver.org) 约定。在版本 "3.21.7" 中，"3" 是主版本号，"21" 是次版本号，"7" 是补丁号。

Protobuf 发布版本只使用 `minor.point` 格式，例如 `34.1`。

每种语言的运行时共享同一个 `minor.point`，但使用各自语言专属的主版本号。例如，Protobuf 发布版本 `34.1` 对应 Java 运行时 `4.34.1` 和 C# 运行时 `3.34.1`。我们建议将 `protoc` `34.1` 与 Java `4.34.1`、C# `3.34.1` 搭配使用。

这一方案在统一所有语言发布版本号的同时，将主版本号的变更解耦开来。例如，发布版本 `30.0` 包含针对 Python 的破坏性变更（breaking change），但不影响 Java。因此，Python 从 `5.29.0` 升级到 `6.30.0`，而 Java 从 `4.29.0` 升级到 `4.30.0`。

我们在 2022 年随发布版本 21 引入了这一版本编号方案。在此之前，所有语言都使用主版本号 3。

## 发布节奏 {#cadence}

Protobuf 每季度发布更新。我们将重大（破坏性）发布的目标时间定在第一季度。安全修复和其他紧急需求会需要额外的发布。

我们的[库破坏性变更政策](https://opensource.google/documentation/policies/library-breaking-change)定义了我们的支持窗口。

执行已成文的语言、工具链、平台和库支持政策*并不*属于破坏性变更。例如，我们可以在不上调主版本号的情况下，停止支持已到达生命周期终点（EOL）的语言版本。

## 发布中会有哪些变更？ {#changes}

**二进制线路格式（wire format）永不改变。** 你可以用较新的 Protobuf 版本读取旧的二进制线路格式数据；只要相应的 .proto 语法受支持，你也可以用较旧的 Protobuf 版本读取新的二进制线路格式数据。ProtoJSON 格式提供同样的稳定性保证。TextProto 的设计用途是配置类使用场景，不应作为两个服务器之间的线路格式使用。

**`descriptor.proto` 模式（schema）可以变化。** 在次版本或补丁版本发布中，我们可能新增或弃用（deprecate）某些元素：消息（message）、字段（field）、枚举（enum）、枚举取值（enum value）、版次，或版次的[特性](/editions/features)（feature）。在包含破坏性变更的发布（主版本发布）中，我们可能移除已弃用的元素。

**`.proto` 语言语法会随新版次而变化**。次版本发布中可能会加入对新版次的支持，这会引入新的语言构造，或弃用既有行为。采用新版次可能需要更新客户端代码。未来的某个发布版本可能会放弃对旧语法的支持，但我们目前没有这样做的具体计划。

**生成代码与运行时 API 可以变化。** 次版本和补丁版本发布只包含纯增量或源码兼容的更新，你只需重新编译代码即可。包含破坏性变更的发布（主版本发布）会引入不兼容的 API 变更，需要更新调用点（callsite）。我们会尽量减少这类变更。针对未定义行为的缺陷修复不需要发布主版本。

**操作系统、编程语言和工具链支持可以变化。** 次版本或补丁版本发布可能会新增或停止对特定操作系统、编程语言或工具的支持。受支持的语言详见[基础支持矩阵](https://github.com/google/oss-policies-info/tree/main)。

总体而言：

*   基于我们的[跨版本运行时保证](https://protobuf.dev/support/cross-version-runtime-guarantee/#minor)，次版本或补丁版本发布只包含纯增量或源码兼容的更新。
*   主版本发布可能会移除功能或特性，或以需要更新调用点的方式变更 API。

## 支持时长 {#duration}

我们始终支持最新的发布版本。新的次版本一经发布，对上一个次版本的支持立即终止。主版本发布后，对上一个主版本的支持将在四个季度后终止。

例如，Protobuf Python 5.26.0 于 2024 年第一季度发布。因此，Protobuf Python 4.25.x 的支持已于 [2025 年第一季度](#python)终止。

以下各节详细列出每种语言的支持时间线。未来计划以*斜体*显示，且可能会变化。

**图例**

<table class="legend">
  <tr class="active">
    <th>活跃</th>
    <td>包含新特性、兼容性变更和缺陷修复的次版本与补丁版本发布。</td>
  </tr>
  <tr class="maintenance">
    <th>维护</th>
    <td>包含关键缺陷修复和安全漏洞修复的补丁版本发布。</td>
  </tr>
  <tr class="end-of-life">
    <th>生命周期终止</th>
    <td>该发布已不受支持。用户应升级到受支持的发布版本。</td>
  </tr>
  <tr class="future">
    <th>未来</th>
    <td>预计中的发布。仅供规划参考。</td>
  </tr>
</table>

## C++ {#cpp}

**发布支持日期**

<table class="version-table">
  <tr>
    <th>Protobuf C++</th>
    <th>发布日期</th>
    <th>支持截止日期</th>
  </tr>
  <tr class="end-of-life">
    <th>3.x</th>
    <td>2022 年 5 月 25 日</td>
    <td>2024 年 3 月 31 日</td>
  </tr>
  <tr class="end-of-life">
    <th>4.x</th>
    <td>2023 年 2 月 16 日</td>
    <td>2025 年 3 月 31 日</td>
  </tr>
  <tr class="end-of-life">
    <th>5.x</th>
    <td>2024 年 3 月 13 日</td>
    <td>2026 年 3 月 31 日</td>
  </tr>
  <tr class="maintenance">
    <th>6.x</th>
    <td>2025 年 3 月 4 日</td>
    <td>2027 年 3 月 31 日</td>
  </tr>
  <tr class="active">
    <th>7.x</th>
    <td>2026 年 2 月 25 日</td>
    <td>待定</td>
  </tr>
</table>

**发布支持图表**

<table class="version-chart">
  <tr>
    <th>Protobuf C++</th>
    <th>protoc</th>
    <th class="y23q4"><span>23Q4</span></th>
    <th class="y24q1"><span>24Q1</span></th>
    <th class="y24q2"><span>24Q2</span></th>
    <th class="y24q3"><span>24Q3</span></th>
    <th class="y24q4"><span>24Q4</span></th>
    <th class="y25q1"><span>25Q1</span></th>
    <th class="y25q2"><span>25Q2</span></th>
    <th class="y25q3"><span>25Q3</span></th>
    <th class="y25q4"><span>25Q4</span></th>
    <th class="y26q1"><span>26Q1</span></th>
    <th class="y26q2"><span>26Q2</span></th>
    <th class="y26q3"><span>26Q3</span></th>
  </tr>
  <tr class="end-of-life">
    <th>4.x</th>
    <td>22.x-25.x</td>
    <td class="y23q4 active">4.25</td>
    <td class="y24q1 maintenance" colspan=4>4.25</td>
    <td class="y25q1"></td>
    <td class="y25q2"></td>
    <td class="y25q3"></td>
    <td class="y25q4"></td>
    <td class="y26q1"></td>
    <td class="y26q2"></td>
    <td class="y26q3"></td>
  </tr>
  <tr class="end-of-life">
    <th>5.x</th>
    <td>26.x-29.x</td>
    <td class="y23q4"></td>
    <td class="y24q1 active">5.26</td>
    <td class="y24q2 active">5.27</td>
    <td class="y24q3 active">5.28</td>
    <td class="y24q4 active">5.29</td>
    <td class="y25q1 maintenance" colspan=4>5.29</td>
    <td class="y26q1"></td>
    <td class="y26q2"></td>
    <td class="y26q3"></td>
  </tr>
  <tr class="maintenance">
    <th>6.x</th>
    <td>30.x-33.x</td>
    <td class="y23q4"></td>
    <td class="y24q1"></td>
    <td class="y24q2"></td>
    <td class="y24q3"></td>
    <td class="y24q4"></td>
    <td class="y25q1 active">6.30</td>
    <td class="y25q2 active">6.31</td>
    <td class="y25q3 active">6.32</td>
    <td class="y25q4 active">6.33</td>
    <td class="y26q1 maintenance">6.33</td>
    <td class="y26q2 maintenance">6.33</td>
    <td class="y26q3 maintenance">6.33</td>
  </tr>
  <tr class="active">
    <th>7.x</th>
    <td>34.x+</td>
    <td class="y23q4"></td>
    <td class="y24q1"></td>
    <td class="y24q2"></td>
    <td class="y24q3"></td>
    <td class="y24q4"></td>
    <td class="y25q1"></td>
    <td class="y25q2"></td>
    <td class="y25q3"></td>
    <td class="y25q4"></td>
    <td class="y26q1 active">7.34</td>
    <td class="y26q2 active">7.35</td>
    <td class="y26q3 active">7.36</td>
  </tr>
</table>

### C++ 工具链、平台与库支持 {#cpp-tooling}

Protobuf 遵循[基础 C++ 支持政策](https://opensource.google/documentation/policies/cplusplus-support)。受支持的版本详见[基础 C++ 支持矩阵](https://github.com/google/oss-policies-info/blob/main/foundational-cxx-support-matrix.md)。

## C&#35; {#csharp}

**发布支持日期**

<table class="version-table">
  <tr>
    <th>Protobuf C#</th>
    <th>发布日期</th>
    <th>支持截止日期</th>
  </tr>
  <tr class="active">
    <th>3.x</th>
    <td>2022 年 5 月 25 日</td>
    <td>待定</td>
  </tr>
</table>

**发布支持图表**

<table class="version-chart">
  <tr>
    <th>Protobuf C#</th>
    <th>protoc</th>
    <th class="y23q4"><span>23Q4</span></th>
    <th class="y24q1"><span>24Q1</span></th>
    <th class="y24q2"><span>24Q2</span></th>
    <th class="y24q3"><span>24Q3</span></th>
    <th class="y24q4"><span>24Q4</span></th>
    <th class="y25q1"><span>25Q1</span></th>
    <th class="y25q2"><span>25Q2</span></th>
    <th class="y25q3"><span>25Q3</span></th>
    <th class="y25q4"><span>25Q4</span></th>
    <th class="y26q1"><span>26Q1</span></th>
    <th class="y26q2"><span>26Q2</span></th>
    <th class="y26q3"><span>26Q3</span></th>
  </tr>
  <tr class="active">
    <th>3.x</th>
    <td>21.x+</td>
    <td class="y23q4 active">3.25</td>
    <td class="y24q1 active">3.26</td>
    <td class="y24q2 active">3.27</td>
    <td class="y24q3 active">3.28</td>
    <td class="y24q4 active">3.29</td>
    <td class="y25q1 active">3.30</td>
    <td class="y25q2 active">3.31</td>
    <td class="y25q3 active">3.32</td>
    <td class="y25q4 active">3.33</td>
    <td class="y26q1 active">3.34</td>
    <td class="y26q2 active">3.35</td>
    <td class="y26q3 active">3.36</td>
  </tr>
</table>

### C&#35; 平台与库支持 {#csharp-support}

Protobuf 致力于遵循 [.NET 支持政策](https://opensource.google/documentation/policies/dotnet-support)中所述的平台和库支持政策。受支持的具体版本详见[基础 .NET 支持矩阵](https://github.com/google/oss-policies-info/blob/main/foundational-dotnet-support-matrix.md)。

## Go {#go}

**发布支持日期**

<table class="version-table">
  <tr>
    <th>Protobuf Go</th>
    <th>发布日期</th>
    <th>支持截止日期</th>
  </tr>
  <tr class="active">
    <th>1.x</th>
    <td>2024 年 12 月 16 日</td>
    <td>待定</td>
  </tr>
</table>

**发布支持图表**

<table class="version-chart">
  <tr>
    <th>Protobuf Go</th>
    <th>protoc</th>
    <th class="y23q3"><span>23Q3</span></th>
    <th class="y23q4"><span>23Q4</span></th>
    <th class="y24q1"><span>24Q1</span></th>
    <th class="y24q2"><span>24Q2</span></th>
    <th class="y24q3"><span>24Q3</span></th>
    <th class="y24q4"><span>24Q4</span></th>
    <th class="y25q1"><span>25Q1</span></th>
    <th class="y25q2"><span>25Q2</span></th>
    <th class="y25q3"><span>25Q3</span></th>
    <th class="y25q4"><span>25Q4</span></th>
    <th class="y26q1"><span>26Q1</span></th>
    <th class="y26q2"><span>26Q2</span></th>
    <th class="y26q3"><span>26Q3</span></th>
  </tr>
  <tr class="active">
    <th>1.x</th>
    <td>36.x+</td>
    <td class="y23q3 active">1.31</td>
    <td class="y23q4 active">1.32</td>
    <td class="y24q1 active">1.33</td>
    <td class="y24q2 active">1.34</td>
    <td class="y24q3 active">1.34</td>
    <td class="y24q4 active">1.36</td>
    <td class="y25q1 active">1.36</td>
    <td class="y25q2 active">1.36</td>
    <td class="y25q3 active">1.36</td>
    <td class="y25q4 active">1.36</td>
    <td class="y26q1 active">1.36</td>
    <td class="y26q2 active">1.36</td>
    <td class="y26q3 active">1.36</td>
  </tr>
</table>

{{% alert title="Note" color="note" %}}Go Protobuf 自 1.37.x 起开始采用季度发布节奏。与其他 Protobuf 语言不同，Go Protobuf 目前不使用发布分支，且仅支持当前发布版本。所有发布（包括补丁发布）都是从 `HEAD` 汇总而来，而非真正的 cherry-pick。我们打算在未来改变这一做法，以与 Protobuf 的其余部分保持一致。{{% /alert %}}

### Go 平台与库支持 {#go-support}

Protobuf 遵循 [Go 支持政策](https://docs.cloud.google.com/go/getting-started/supported-go-versions)。受支持的版本详见[基础 Go 支持矩阵](https://github.com/google/oss-policies-info/blob/main/foundational-go-support-matrix.md)。

## Java {#java}

**发布支持日期**

<table class="version-table">
  <tr>
    <th>Protobuf Java</th>
    <th>发布日期</th>
    <th>支持截止日期</th>
  </tr>
  <tr class="maintenance">
    <th>3.x</th>
    <td>2022 年 5 月 25 日</td>
    <td>2027 年 3 月 31 日*</td>
  </tr>
  <tr class="active">
    <th>4.x</th>
    <td>2024 年 3 月 13 日</td>
    <td>2028 年 3 月 31 日</td>
  </tr>
  <tr class="future">
    <th>5.x</th>
    <td>2027 年第一季度*</td>
    <td>2029 年 3 月 31 日</td>
  </tr>
</table>

**发布支持图表**

<table class="version-chart">
  <tr>
    <th>Protobuf Java</th>
    <th>protoc</th>
    <th class="y23q4"><span>23Q4</span></th>
    <th class="y24q1"><span>24Q1</span></th>
    <th class="y24q2"><span>24Q2</span></th>
    <th class="y24q3"><span>24Q3</span></th>
    <th class="y24q4"><span>24Q4</span></th>
    <th class="y25q1"><span>25Q1</span></th>
    <th class="y25q2"><span>25Q2</span></th>
    <th class="y25q3"><span>25Q3</span></th>
    <th class="y25q4"><span>25Q4</span></th>
    <th class="y26q1"><span>26Q1</span></th>
    <th class="y26q2"><span>26Q2</span></th>
    <th class="y26q3"><span>26Q3</span></th>
  </tr>
  <tr class="maintenance">
    <th>3.x</th>
    <td>21.x-25.x</td>
    <td class="y23q4 active">3.25</td>
    <td class="y24q1 maintenance" colspan=11>3.25</td>
  </tr>
  <tr class="active">
    <th>4.x</th>
    <td>26.x+</td>
    <td class="y23q4"></td>
    <td class="y24q1 active">4.26</td>
    <td class="y24q2 active">4.27</td>
    <td class="y24q3 active">4.28</td>
    <td class="y24q4 active">4.29</td>
    <td class="y25q1 active">4.30</td>
    <td class="y25q2 active">4.31</td>
    <td class="y25q3 active">4.32</td>
    <td class="y25q4 active">4.33</td>
    <td class="y26q1 active">4.34</td>
    <td class="y26q2 active">4.35</td>
    <td class="y26q3 active">4.36</td>
  </tr>
</table>

{{% alert title="Note" color="note" %}}
Protobuf Java 3.x 发布线的维护支持窗口为 36 个月，而非通常的 12 个月。{{% /alert %}}

### Java 平台与库支持 {#java-support}

Protobuf 遵循 [Java 支持政策](https://cloud.google.com/java/docs/supported-java-versions)。受支持的版本详见[基础 Java 支持矩阵](https://github.com/google/oss-policies-info/blob/main/foundational-java-support-matrix.md)。

在 Android 上，Protobuf 支持 [Google Play services](https://developers.google.com/android/guides/setup) 定义的最低 SDK 版本，或 [Jetpack](https://android.googlesource.com/platform/frameworks/support/+/refs/heads/androidx-main/docs/api_guidelines/modules#module-minsdkversion) 中的默认值，以两者中较低的版本为准。

## Objective-C {#objc}

**发布支持日期**

<table class="version-table">
  <tr>
    <th>Protobuf Objective-C</th>
    <th>发布日期</th>
    <th>支持截止日期</th>
  </tr>
  <tr class="end-of-life">
    <th>3.x</th>
    <td>2022 年 5 月 25 日</td>
    <td>2026 年 3 月 31 日</td>
  </tr>
  <tr class="maintenance">
    <th>4.x</th>
    <td>2025 年 3 月 4 日</td>
    <td>2027 年 3 月 31 日</td>
  </tr>
  <tr class="active">
    <th>5.x</th>
    <td>2026 年 2 月 25 日</td>
    <td>2027 年第四季度</td>
  </tr>
</table>

**发布支持图表**

<table class="version-chart">
  <tr>
    <th>Protobuf Objective-C</th>
    <th>protoc</th>
    <th class="y23q4"><span>23Q4</span></th>
    <th class="y24q1"><span>24Q1</span></th>
    <th class="y24q2"><span>24Q2</span></th>
    <th class="y24q3"><span>24Q3</span></th>
    <th class="y24q4"><span>24Q4</span></th>
    <th class="y25q1"><span>25Q1</span></th>
    <th class="y25q2"><span>25Q2</span></th>
    <th class="y25q3"><span>25Q3</span></th>
    <th class="y25q4"><span>25Q4</span></th>
    <th class="y26q1"><span>26Q1</span></th>
    <th class="y26q2"><span>26Q2</span></th>
    <th class="y26q3"><span>26Q3</span></th>
  </tr>
  <tr class="end-of-life">
    <th>3.x</th>
    <td>21.x-29.x</td>
    <td class="y23q4 active">3.25</td>
    <td class="y24q1 active">3.26</td>
    <td class="y24q2 active">3.27</td>
    <td class="y24q3 active">3.28</td>
    <td class="y24q4 active">3.29</td>
    <td class="y25q1 maintenance" colspan=4>3.29</td>
    <td class="y26q1"></td>
    <td class="y26q2"></td>
    <td class="y26q3"></td>
  </tr>
  <tr class="maintenance">
    <th>4.x</th>
    <td>30.x-33.x</td>
    <td class="y23q4"></td>
    <td class="y24q1"></td>
    <td class="y24q2"></td>
    <td class="y24q3"></td>
    <td class="y24q4"></td>
    <td class="y25q1 active">4.30</td>
    <td class="y25q2 active">4.31</td>
    <td class="y25q3 active">4.32</td>
    <td class="y25q4 active">4.33</td>
    <td class="y26q1 maintenance">4.33</td>
    <td class="y26q2 maintenance">4.33</td>
    <td class="y26q3 maintenance">4.33</td>
  </tr>
  <tr class="active">
    <th>5.x</th>
    <td>34.x-37.x</td>
    <td class="y23q4"></td>
    <td class="y24q1"></td>
    <td class="y24q2"></td>
    <td class="y24q3"></td>
    <td class="y24q4"></td>
    <td class="y25q1"></td>
    <td class="y25q2"></td>
    <td class="y25q3"></td>
    <td class="y25q4"></td>
    <td class="y26q1 active">5.34</td>
    <td class="y26q2 active">5.35</td>
    <td class="y26q3 active">5.36</td>
  </tr>
</table>

{{% alert title="Note" color="note" %}}
自 38.x 发布起，将不再支持 Objective-C。在此之前，Objective-C 会继续对较旧的分支提供维护支持，直至各自的支持截止日期。更多细节参见 [GitHub 议题](https://github.com/protocolbuffers/protobuf/issues/30118)。{{% /alert %}}

## PHP {#php}

**发布支持日期**

<table class="version-table">
  <tr>
    <th>Protobuf PHP</th>
    <th>发布日期</th>
    <th>支持截止日期</th>
  </tr>
  <tr class="end-of-life">
    <th>3.x</th>
    <td>2022 年 5 月 25 日</td>
    <td>2025 年 3 月 31 日</td>
  </tr>
  <tr class="maintenance">
    <th>4.x</th>
    <td>2024 年 3 月 13 日</td>
    <td>2026 年 3 月 31 日</td>
  </tr>
  <tr class="active">
    <th>5.x</th>
    <td>2026 年 2 月 25 日</td>
    <td>待定</td>
  </tr>
</table>

**发布支持图表**

<table class="version-chart">
  <tr>
    <th>Protobuf PHP</th>
    <th>protoc</th>
    <th class="y23q4"><span>23Q4</span></th>
    <th class="y24q1"><span>24Q1</span></th>
    <th class="y24q2"><span>24Q2</span></th>
    <th class="y24q3"><span>24Q3</span></th>
    <th class="y24q4"><span>24Q4</span></th>
    <th class="y25q1"><span>25Q1</span></th>
    <th class="y25q2"><span>25Q2</span></th>
    <th class="y25q3"><span>25Q3</span></th>
    <th class="y25q4"><span>25Q4</span></th>
    <th class="y26q1"><span>26Q1</span></th>
    <th class="y26q2"><span>26Q2</span></th>
    <th class="y26q3"><span>26Q3</span></th>
  </tr>
  <tr class="end-of-life">
    <th>3.x</th>
    <td>21.x-25.x</td>
    <td class="y23q4 active">3.25</td>
    <td class="y24q1 maintenance" colspan=4>3.25</td>
    <td class="y25q1"></td>
    <td class="y25q2"></td>
    <td class="y25q3"></td>
    <td class="y25q4"></td>
    <td class="y26q1"></td>
    <td class="y26q2"></td>
    <td class="y26q3"></td>
  </tr>
  <tr class="maintenance">
    <th>4.x</th>
    <td>26.x - 33.x</td>
    <td class="y23q4"></td>
    <td class="y24q1 active">4.26</td>
    <td class="y24q2 active">4.27</td>
    <td class="y24q3 active">4.28</td>
    <td class="y24q4 active">4.29</td>
    <td class="y25q1 active">4.30</td>
    <td class="y25q2 active">4.31</td>
    <td class="y25q3 active">4.32</td>
    <td class="y25q4 active">4.33</td>
    <td class="y26q1 maintenance">4.33</td>
    <td class="y26q2 maintenance">4.33</td>
    <td class="y26q3 maintenance">4.33</td>
  </tr>
    <tr class="active">
    <th>5.x</th>
    <td>34.x+</td>
    <td class="y23q4"></td>
    <td class="y24q1"></td>
    <td class="y24q2"></td>
    <td class="y24q3"></td>
    <td class="y24q4"></td>
    <td class="y25q1"></td>
    <td class="y25q2"></td>
    <td class="y25q3"></td>
    <td class="y25q4"></td>
    <td class="y26q1 active">5.34</td>
    <td class="y26q2 active">5.35</td>
    <td class="y26q3 active">5.36</td>
  </tr>
</table>

### PHP 平台与库支持 {#php-support}

Protobuf 遵循 [PHP 支持政策](https://cloud.google.com/php/getting-started/supported-php-versions)。受支持的版本详见[基础 PHP 支持矩阵](https://github.com/google/oss-policies-info/blob/main/foundational-php-support-matrix.md)。

## Python {#python}

**发布支持日期**

<table class="version-table">
  <tr>
    <th>Protobuf Python</th>
    <th>发布日期</th>
    <th>支持截止日期</th>
  </tr>
  <tr class="end-of-life">
    <th>4.x</th>
    <td>2022 年 5 月 25 日</td>
    <td>2025 年 3 月 31 日</td>
  </tr>
  <tr class="end-of-life">
    <th>5.x</th>
    <td>2024 年 3 月 13 日</td>
    <td>2026 年 3 月 31 日</td>
  </tr>
  <tr class="maintenance">
    <th>6.x</th>
    <td>2025 年 3 月 4 日</td>
    <td>2027 年 3 月 31 日</td>
  </tr>
  <tr class="active">
    <th>7.x</th>
    <td>2026 年 2 月 25 日</td>
    <td>待定</td>
  </tr>
</table>

**发布支持图表**

<table class="version-chart">
  <tr>
    <th>Protobuf Python</th>
    <th>protoc</th>
    <th class="y23q4"><span>23Q4</span></th>
    <th class="y24q1"><span>24Q1</span></th>
    <th class="y24q2"><span>24Q2</span></th>
    <th class="y24q3"><span>24Q3</span></th>
    <th class="y24q4"><span>24Q4</span></th>
    <th class="y25q1"><span>25Q1</span></th>
    <th class="y25q2"><span>25Q2</span></th>
    <th class="y25q3"><span>25Q3</span></th>
    <th class="y25q4"><span>25Q4</span></th>
    <th class="y26q1"><span>26Q1</span></th>
    <th class="y26q2"><span>26Q2</span></th>
    <th class="y26q3"><span>26Q3</span></th>
  </tr>
  <tr class="end-of-life">
    <th>4.x</th>
    <td>21.x-25.x</td>
    <td class="y23q4 active">4.25</td>
    <td class="y24q1 maintenance" colspan=4>4.25</td>
    <td class="y25q1"></td>
    <td class="y25q2"></td>
    <td class="y25q3"></td>
    <td class="y25q4"></td>
    <td class="y26q1"></td>
    <td class="y26q2"></td>
    <td class="y26q3"></td>
  </tr>
  <tr class="end-of-life">
    <th>5.x</th>
    <td>26.x-29.x</td>
    <td class="y23q4"></td>
    <td class="y24q1 active">5.26</td>
    <td class="y24q2 active">5.27</td>
    <td class="y24q3 active">5.28</td>
    <td class="y24q4 active">5.29</td>
    <td class="y25q1 maintenance" colspan=4>5.29</td>
    <td class="y26q1"></td>
    <td class="y26q2"></td>
    <td class="y26q3"></td>
  </tr>
  <tr class="maintenance">
    <th>6.x</th>
    <td>30.x-33.x</td>
    <td class="y23q4"></td>
    <td class="y24q1"></td>
    <td class="y24q2"></td>
    <td class="y24q3"></td>
    <td class="y24q4"></td>
    <td class="y25q1 active">6.30</td>
    <td class="y25q2 active">6.31</td>
    <td class="y25q3 active">6.32</td>
    <td class="y25q4 active">6.33</td>
    <td class="y26q1 maintenance">6.33</td>
    <td class="y26q2 maintenance">6.33</td>
    <td class="y26q3 maintenance">6.33</td>
  </tr>
    <tr class="active">
    <th>7.x</th>
    <td>34.x+</td>
    <td class="y23q4"></td>
    <td class="y24q1"></td>
    <td class="y24q2"></td>
    <td class="y24q3"></td>
    <td class="y24q4"></td>
    <td class="y25q1"></td>
    <td class="y25q2"></td>
    <td class="y25q3"></td>
    <td class="y25q4"></td>
    <td class="y26q1 active">7.34</td>
    <td class="y26q2 active">7.35</td>
    <td class="y26q3 active">7.36</td>
  </tr>
</table>

### Python 平台与库支持 {#python-support}

Protobuf 遵循 [Python 支持政策](https://cloud.google.com/python/docs/supported-python-versions)。受支持的版本详见[基础 Python 支持矩阵](https://github.com/google/oss-policies-info/blob/main/foundational-python-support-matrix.md)。

## Ruby {#ruby}

**发布支持日期**

<table class="version-table">
  <tr>
    <th>Protobuf Ruby</th>
    <th>发布日期</th>
    <th>支持截止日期</th>
  </tr>
  <tr class="end-of-life">
    <th>3.x</th>
    <td>2022 年 5 月 25 日</td>
    <td>2025 年 3 月 31 日</td>
  </tr>
  <tr class="active">
    <th>4.x</th>
    <td>2024 年 3 月 13 日</td>
    <td>待定</td>
  </tr>
</table>

**发布支持图表**

<table class="version-chart">
  <tr>
    <th>Protobuf Ruby</th>
    <th>protoc</th>
    <th class="y23q4"><span>23Q4</span></th>
    <th class="y24q1"><span>24Q1</span></th>
    <th class="y24q2"><span>24Q2</span></th>
    <th class="y24q3"><span>24Q3</span></th>
    <th class="y24q4"><span>24Q4</span></th>
    <th class="y25q1"><span>25Q1</span></th>
    <th class="y25q2"><span>25Q2</span></th>
    <th class="y25q3"><span>25Q3</span></th>
    <th class="y25q4"><span>25Q4</span></th>
    <th class="y26q1"><span>26Q1</span></th>
    <th class="y26q2"><span>26Q2</span></th>
    <th class="y26q3"><span>26Q3</span></th>
  </tr>
  <tr class="end-of-life">
    <th>3.x</th>
    <td>21.x-25.x</td>
    <td class="y23q4 active">3.25</td>
    <td class="y24q1 maintenance" colspan=4>3.25</td>
    <td class="y25q1"></td>
    <td class="y25q2"></td>
    <td class="y25q3"></td>
    <td class="y25q4"></td>
    <td class="y26q1"></td>
    <td class="y26q2"></td>
    <td class="y26q3"></td>
  </tr>
  <tr class="active">
    <th>4.x</th>
    <td>26.x+</td>
    <td class="y23q4"></td>
    <td class="y24q1 active">4.26</td>
    <td class="y24q2 active">4.27</td>
    <td class="y24q3 active">4.28</td>
    <td class="y24q4 active">4.29</td>
    <td class="y25q1 active">4.30</td>
    <td class="y25q2 active">4.31</td>
    <td class="y25q3 active">4.32</td>
    <td class="y25q4 active">4.33</td>
    <td class="y26q1 active">4.34</td>
    <td class="y26q2 active">4.35</td>
    <td class="y26q3 active">4.36</td>
  </tr>
</table>

### Ruby 平台与库支持 {#ruby-support}

Protobuf 遵循 [Ruby 支持政策](https://cloud.google.com/ruby/getting-started/supported-ruby-versions)。受支持的版本详见[基础 Ruby 支持矩阵](https://github.com/google/oss-policies-info/blob/main/foundational-ruby-support-matrix.md)。

我们不官方支持 JRuby，但对最新的 JRuby 版本提供非官方的尽力支持，目标是与我们所支持的最低 Ruby 版本保持兼容。
